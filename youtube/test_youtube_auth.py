#!/usr/bin/env python3
"""Test YouTube OAuth + channel access (no upload).

Usage:
  python youtube/test_youtube_auth.py

Requires: youtube/client_secret.json  (see YOUTUBE_API_SETUP.md)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Load .env.local if present
env_path = ROOT / ".env.local"
if env_path.is_file():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]
CLIENT_SECRETS = Path(
    os.environ.get("YOUTUBE_CLIENT_SECRETS", ROOT / "youtube" / "client_secret.json")
)
TOKEN_PATH = ROOT / "youtube" / "token.json"


def main() -> int:
    print("=== THE STOIC SIGNAL — YouTube auth test ===\n")

    if not CLIENT_SECRETS.is_file():
        print("FAIL: Missing OAuth client secrets.")
        print(f"  Expected: {CLIENT_SECRETS}")
        print("  Steps: see youtube/YOUTUBE_API_SETUP.md")
        print("  (google_api_key alone cannot upload videos.)")
        api_key = os.environ.get("google_api_key") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            print("\n  Note: google_api_key is present in env — useful for some")
            print("  public Data API reads, but NOT for youtube.videos.insert.")
        return 1

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("FAIL: packages missing. Run:")
        print("  python -m pip install -r requirements-youtube.txt")
        return 1

    creds = None
    if TOKEN_PATH.is_file():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token…")
            creds.refresh(Request())
        else:
            print("Opening browser for Google sign-in…")
            print("  Use the Google account that OWNS the YouTube channel / Brand Account.")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        print(f"Saved token → {TOKEN_PATH}")

    yt = build("youtube", "v3", credentials=creds)
    resp = yt.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()
    items = resp.get("items") or []
    if not items:
        print("FAIL: OAuth worked but no channel on this account.")
        print("  Switch to Brand Account when consenting, or create a channel first.")
        return 1

    ch = items[0]
    sn = ch["snippet"]
    st = ch.get("statistics", {})
    print("OK: YouTube OAuth works\n")
    print(f"  Channel title : {sn.get('title')}")
    print(f"  Channel id    : {ch.get('id')}")
    print(f"  Custom URL    : {sn.get('customUrl', '(none yet)')}")
    print(f"  Subscribers   : {st.get('subscriberCount', '?')}")
    print(f"  Videos        : {st.get('videoCount', '?')}")
    print(f"  Views         : {st.get('viewCount', '?')}")
    print("\nNext: optional unlisted test upload")
    print("  python youtube/upload_short.py --file final/short3.mp4 --privacy unlisted --title \"API test\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
