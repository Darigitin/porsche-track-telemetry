#!/usr/bin/env python3
"""
Track Evolution MCP Server Bridge for Google Antigravity & AI Assistants.
Proxies JSON-RPC MCP messages over stdio to https://trackevolution.app/mcp,
handling OAuth 2.1 PKCE authorization and transparent token refreshing.
"""

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser

BASE_URL = "https://trackevolution.app"
MCP_ENDPOINT = f"{BASE_URL}/mcp"
REGISTER_ENDPOINT = f"{BASE_URL}/oauth/register"
AUTHORIZE_ENDPOINT = f"{BASE_URL}/oauth/authorize"
TOKEN_ENDPOINT = f"{BASE_URL}/oauth/token"
RESOURCE_URL = f"{BASE_URL}/mcp"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKENS_FILE = os.path.join(SCRIPT_DIR, ".trackevolution_tokens.json")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity-TrackEvolution-MCP/1.0"


def log(msg: str):
    """Log to stderr so stdout remains clean for MCP JSON-RPC."""
    sys.stderr.write(f"[TrackEvolution-MCP] {msg}\n")
    sys.stderr.flush()


def generate_code_verifier() -> str:
    # 43-128 unreserved characters
    token = secrets.token_urlsafe(64)
    return token[:96]


def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return challenge


def load_tokens() -> dict:
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Error reading tokens file: {e}")
    return {}


def save_tokens(data: dict):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def make_request(url: str, payload: dict | None = None, headers: dict | None = None) -> tuple[int, dict]:
    req_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=req_headers)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            try:
                return status, json.loads(body)
            except Exception:
                return status, {"raw": body}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}
    except Exception as e:
        return 500, {"error": str(e)}


def refresh_access_token(tokens: dict) -> dict | None:
    refresh_token = tokens.get("refresh_token")
    client_id = tokens.get("client_id")
    if not refresh_token or not client_id:
        log("Cannot refresh token: missing refresh_token or client_id")
        return None

    log("Refreshing access token...")
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "resource": RESOURCE_URL,
    }
    status, res = make_request(TOKEN_ENDPOINT, payload)
    if status == 200 and "access_token" in res:
        tokens["access_token"] = res["access_token"]
        if "refresh_token" in res:
            tokens["refresh_token"] = res["refresh_token"]
        expires_in = res.get("expires_in", 3600)
        tokens["expires_at"] = time.time() + expires_in
        save_tokens(tokens)
        log("Access token successfully refreshed.")
        return tokens
    else:
        log(f"Token refresh failed ({status}): {res}")
        return None


def get_valid_access_token() -> str | None:
    tokens = load_tokens()
    if not tokens or "access_token" not in tokens:
        return None

    # Check expiration (with 60-second buffer)
    expires_at = tokens.get("expires_at", 0)
    if time.time() >= (expires_at - 60):
        refreshed = refresh_access_token(tokens)
        if refreshed:
            return refreshed["access_token"]
        return None

    return tokens["access_token"]


def perform_oauth_login(port: int = 8998) -> bool:
    redirect_uri = f"http://127.0.0.1:{port}/callback"

    # Step 1: Register client dynamically
    log(f"Registering client with redirect URI: {redirect_uri}...")
    reg_payload = {
        "client_name": "Antigravity IDE",
        "redirect_uris": [redirect_uri],
    }
    status, reg_res = make_request(REGISTER_ENDPOINT, reg_payload)
    if status != 201 or "client_id" not in reg_res:
        log(f"Registration failed ({status}): {reg_res}")
        return False

    client_id = reg_res["client_id"]
    log(f"Registered client ID: {client_id}")

    # Step 2: Prepare PKCE & State
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    state = secrets.token_urlsafe(16)

    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": "read",
        "resource": RESOURCE_URL,
    }
    auth_url = f"{AUTHORIZE_ENDPOINT}?{urllib.parse.urlencode(auth_params)}"

    auth_code_holder = {}
    auth_event = threading.Event()

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # suppress standard http logging

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/callback":
                query = urllib.parse.parse_qs(parsed.query)
                code = query.get("code", [None])[0]
                rec_state = query.get("state", [None])[0]
                error = query.get("error", [None])[0]
                error_desc = query.get("error_description", [None])[0]

                if error:
                    auth_code_holder["error"] = error_desc or error
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body style='font-family:sans-serif;padding:40px;text-align:center;'>"
                        b"<h2 style='color:#e53e3e;'>Authorization Failed</h2>"
                        b"<p>" + (error_desc or error).encode("utf-8") + b"</p>"
                        b"<p>You can close this tab and return to your terminal.</p>"
                        b"</body></html>"
                    )
                elif rec_state != state or not code:
                    auth_code_holder["error"] = "Invalid state or missing code."
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body style='font-family:sans-serif;padding:40px;text-align:center;'>"
                        b"<h2 style='color:#e53e3e;'>State Mismatch</h2>"
                        b"<p>Authentication response validation failed.</p>"
                        b"</body></html>"
                    )
                else:
                    auth_code_holder["code"] = code
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body style='font-family:sans-serif;padding:40px;text-align:center;background:#0f172a;color:#f8fafc;'>"
                        b"<div style='max-width:500px;margin:50px auto;padding:30px;background:#1e293b;border-radius:12px;border:1px solid #334155;'>"
                        b"<h2 style='color:#38bdf8;margin-top:0;'>Connected to Track Evolution!</h2>"
                        b"<p>Your MCP connection has been successfully approved.</p>"
                        b"<p style='color:#94a3b8;font-size:14px;'>You can now close this tab and return to Antigravity.</p>"
                        b"</div>"
                        b"</body></html>"
                    )
                auth_event.set()
            else:
                self.send_response(404)
                self.end_headers()

    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    log(f"Opening browser for authorization: {auth_url}")
    print("\n" + "=" * 60)
    print("Please authorize Track Evolution in your browser.")
    print("If it does not open automatically, visit:")
    print(auth_url)
    print("=" * 60 + "\n", file=sys.stderr)

    webbrowser.open(auth_url)

    # Wait up to 120 seconds
    completed = auth_event.wait(timeout=120)
    server.shutdown()
    server.server_close()

    if not completed:
        log("Timed out waiting for authorization callback.")
        return False

    if "error" in auth_code_holder:
        log(f"Authorization error: {auth_code_holder['error']}")
        return False

    code = auth_code_holder["code"]
    log("Authorization code received. Trading for tokens...")

    # Step 3: Trade code for tokens
    token_payload = {
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": verifier,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "resource": RESOURCE_URL,
    }
    status, token_res = make_request(TOKEN_ENDPOINT, token_payload)
    if status == 200 and "access_token" in token_res:
        tokens = {
            "client_id": client_id,
            "access_token": token_res["access_token"],
            "refresh_token": token_res.get("refresh_token"),
            "scope": token_res.get("scope", "read"),
            "expires_at": time.time() + token_res.get("expires_in", 3600),
        }
        save_tokens(tokens)
        log("Authentication successful! Tokens saved.")
        return True
    else:
        log(f"Failed to trade token ({status}): {token_res}")
        return False


def run_stdio_mcp_bridge():
    """Runs the MCP server over stdio, forwarding requests to Track Evolution."""
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8")
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    supported_upstream_versions = ["2025-11-25", "2025-06-18", "2025-03-26"]
    upstream_protocol_version = "2025-06-18"

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        try:
            req_data = json.loads(line)
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
            continue

        is_notification = isinstance(req_data, dict) and req_data.get("id") is None
        client_requested_version = None

        # Check if initialize method to negotiate protocolVersion
        if isinstance(req_data, dict) and req_data.get("method") == "initialize":
            params = req_data.get("params") or {}
            client_requested_version = params.get("protocolVersion")
            if client_requested_version in supported_upstream_versions:
                upstream_protocol_version = client_requested_version
            else:
                # Upstream only supports 2025-03-26+, translate legacy client requests (e.g. 2024-11-05)
                upstream_protocol_version = "2025-06-18"
                if "params" in req_data and isinstance(req_data["params"], dict):
                    req_data["params"]["protocolVersion"] = upstream_protocol_version

        token = get_valid_access_token()
        if not token:
            if not is_notification:
                msg_id = req_data.get("id") if isinstance(req_data, dict) else None
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32000,
                        "message": "Track Evolution authentication required. Run 'python trackevolution_mcp.py --login' to sign in.",
                    },
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
            continue

        # Forward request to Track Evolution
        headers = {
            "Authorization": f"Bearer {token}",
            "MCP-Protocol-Version": upstream_protocol_version,
        }

        status, resp_data = make_request(MCP_ENDPOINT, payload=req_data, headers=headers)

        # If 401, token might have been invalidated; attempt refresh and retry once
        if status == 401:
            tokens = load_tokens()
            refreshed = refresh_access_token(tokens)
            if refreshed:
                token = refreshed["access_token"]
                headers["Authorization"] = f"Bearer {token}"
                status, resp_data = make_request(MCP_ENDPOINT, payload=req_data, headers=headers)

        # Notifications (no id) never receive a response in JSON-RPC
        if is_notification:
            continue

        if status == 200:
            if client_requested_version and isinstance(resp_data, dict) and "result" in resp_data:
                # Mirror client's requested version so client accepts the handshake
                if isinstance(resp_data["result"], dict) and "protocolVersion" in resp_data["result"]:
                    resp_data["result"]["protocolVersion"] = client_requested_version
            sys.stdout.write(json.dumps(resp_data) + "\n")
            sys.stdout.flush()
        elif status == 202:
            # 202 Accepted without response body
            pass
        else:
            msg_id = req_data.get("id") if isinstance(req_data, dict) else None
            err_msg = resp_data.get("error", f"HTTP {status}") if isinstance(resp_data, dict) else str(resp_data)
            err_resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32603, "message": f"Track Evolution error: {err_msg}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Track Evolution MCP Bridge")
    parser.add_argument("--login", action="store_true", help="Perform OAuth login via browser")
    parser.add_argument("--status", action="store_true", help="Check authentication status")
    args = parser.parse_args()

    if args.login:
        success = perform_oauth_login()
        if success:
            print("Track Evolution MCP authenticated successfully.")
            sys.exit(0)
        else:
            print("Track Evolution MCP authentication failed.")
            sys.exit(1)

    if args.status:
        token = get_valid_access_token()
        if token:
            tokens = load_tokens()
            exp = tokens.get("expires_at", 0)
            remaining = int(exp - time.time())
            print(f"Authenticated! Access token valid for ~{remaining // 60} more minutes.")
            print("Refresh token is active (renews automatically).")
            sys.exit(0)
        else:
            print("Not authenticated. Run with --login to authenticate.")
            sys.exit(1)

    # Default: stdio MCP bridge
    run_stdio_mcp_bridge()


if __name__ == "__main__":
    main()
