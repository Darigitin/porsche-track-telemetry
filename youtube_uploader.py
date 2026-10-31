#!/usr/bin/env python3
"""
Official YouTube Data API v3 Uploader for Track Videos.
Supports:
- Resumable video upload with progress display
- Setting title, description, tags, categoryId (17 = Sports / 2 = Autos & Vehicles)
- Setting privacy status (public, unlisted, private)
- Token caching (only requires one-time browser OAuth login)
"""

import os
import sys
import argparse
import http.client
import httplib2
import random
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.oauth2.credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]
BASE_DIR = os.path.dirname(__file__)
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secrets.json")
CONFIG_SECRETS_FILE = os.path.join(BASE_DIR, "config", "client_secrets.json")
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")
CONFIG_TOKEN_FILE = os.path.join(BASE_DIR, "config", "youtube_token.json")

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

def get_authenticated_service():
    creds = None
    token_path = TOKEN_FILE if os.path.exists(TOKEN_FILE) else CONFIG_TOKEN_FILE
    secrets_path = CLIENT_SECRETS_FILE if os.path.exists(CLIENT_SECRETS_FILE) else CONFIG_SECRETS_FILE
    if os.path.exists(token_path):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        refreshed = False
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                refreshed = True
            except Exception as e:
                print(f"[WARN] Cached YouTube token expired/revoked ({e}). Launching browser re-authentication...")

        if not refreshed:
            if not os.path.exists(secrets_path):
                print(f"\n[ERROR] '{secrets_path}' not found!")
                print("To enable 1-click automated YouTube uploading:")
                print("1. Go to https://console.cloud.google.com/apis/credentials")
                print("2. Create an OAuth 2.0 Client ID (Application type: Desktop App)")
                print("3. Download JSON and save it as 'client_secrets.json' in this project folder.\n")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        if os.path.exists(os.path.dirname(CONFIG_TOKEN_FILE)):
            with open(CONFIG_TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags=None, category="2", privacy="unlisted"):
    """
    Uploads a video to YouTube.
    Category 2 = Autos & Vehicles, Category 17 = Sports
    Privacy: 'public', 'unlisted', 'private'
    """
    if not os.path.exists(file_path):
        print(f"[ERROR] Video file not found: {file_path}")
        return None

    youtube = get_authenticated_service()

    # Sanitize title and description for YouTube API (< and > forbidden, max 100 chars)
    clean_title = title.replace("<", "").replace(">", "").strip()[:100]
    clean_desc = description.replace("<", "").replace(">", "").strip() if description else ""

    body = {
        "snippet": {
            "title": clean_title,
            "description": clean_desc,
            "tags": tags or ["Porsche", "718 Cayman GT4", "High Plains Raceway", "Track Day", "Telemetry"],
            "categoryId": category
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=1024*1024*8, resumable=True)
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    print(f"\nUploading '{os.path.basename(file_path)}' to YouTube ({privacy.upper()})...")
    print(f"Title: {title}")

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%...")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            print(error)
            retry += 1
            if retry > 5:
                print("Exceeded maximum retries.")
                return None
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f"Sleeping {sleep_seconds:.1f} seconds and then retrying...")
            time.sleep(sleep_seconds)
            error = None

    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"\nSUCCESS! Video uploaded successfully: {video_url}")
    return video_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload track video to YouTube.")
    parser.add_argument("--file", required=True, help="Path to video file")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--desc", default="", help="Video description")
    parser.add_argument("--desc-file", help="Path to text file containing description")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    desc = args.desc
    if args.desc_file:
        with open(args.desc_file, "r", encoding="utf-8") as f:
            desc = f.read()

    upload_video(args.file, args.title, desc, privacy=args.privacy)
