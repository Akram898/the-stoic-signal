#!/usr/bin/env python3
"""Upload a Short to YouTube (or dry-run).

  python youtube/upload_short.py --file final/short3.mp4 --title "My title" --privacy unlisted
  python youtube/upload_short.py --file final/short3.mp4 --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

env_path = ROOT / ".env.local"
if env_path.is_file():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
CLIENT_SECRETS = Path(
    os.environ.get("YOUTUBE_CLIENT_SECRETS", ROOT / "youtube" / "client_secret.json")
)
TOKEN_PATH = ROOT / "youtube" / "token.json"


def get_creds():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CLIENT_SECRETS.is_file():
        raise SystemExit(f"Missing {CLIENT_SECRETS} — see youtube/YOUTUBE_API_SETUP.md")

    creds = None
    if TOKEN_PATH.is_file():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Path to mp4")
    ap.add_argument("--title", default="The Stoic Signal")
    ap.add_argument("--description", default="")
    ap.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    ap.add_argument("--category", default="27", help="27=Education")
    ap.add_argument("--tags", default="stoicism,discipline,shorts,mindset")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        # try relative to ROOT
        path = ROOT / args.file
    if not path.is_file():
        print(f"FAIL: file not found: {args.file}")
        return 1

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    body = {
        "snippet": {
            "title": args.title[:100],
            "description": args.description or f"{args.title}\n\n#shorts #stoicism",
            "tags": tags,
            "categoryId": args.category,
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    print(f"File     : {path} ({path.stat().st_size // 1024} KB)")
    print(f"Title    : {body['snippet']['title']}")
    print(f"Privacy  : {args.privacy}")
    print(f"Tags     : {tags}")

    if args.dry_run:
        print("\nDRY-RUN: would upload. No API call.")
        return 0

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_creds()
    yt = build("youtube", "v3", credentials=creds)
    media = MediaFileUpload(str(path), mimetype="video/mp4", resumable=True, chunksize=1024 * 1024)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print("Uploading…")
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    vid = resp.get("id")
    print(f"\nOK: uploaded video id = {vid}")
    print(f"  https://studio.youtube.com/video/{vid}/edit")
    print(f"  https://youtu.be/{vid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
