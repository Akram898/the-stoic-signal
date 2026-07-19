# YouTube Data API — setup & test (before auto-upload)

Uploads **cannot** use only `google_api_key`. You need **OAuth 2.0 Desktop** credentials so the channel owner grants `youtube.upload`.

## A. Google Cloud (one-time, ~10 min)

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project (e.g. `the-stoic-signal`)
3. **APIs & Services → Library** → enable **YouTube Data API v3**
4. **APIs & Services → OAuth consent screen**
   - User type: **External** (or Internal if Workspace)
   - App name: `The Stoic Signal Uploader`
   - Support email: yours
   - Scopes later: add `.../auth/youtube.upload` and `.../auth/youtube.readonly`
   - Test users: add **your Google account** that owns the YouTube channel
5. **Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Name: `stoic-signal-desktop`
6. Download JSON → save as:

```
youtube/client_secret.json
```

(Do **not** commit this file. It is gitignored.)

## B. Env vars (optional)

`.env.local` may keep:

```
google_api_key=...          # optional; used only for non-OAuth probes
YOUTUBE_CLIENT_SECRETS=youtube/client_secret.json
```

## C. Install & first auth test

```powershell
cd d:\Workspace\experiments\the-stoic-signal
python -m pip install -r requirements-youtube.txt
python youtube/test_youtube_auth.py
```

Browser opens → sign in as the **channel Brand Account** owner → Allow.

On success you should see:

- channel title / id  
- subscriber count (if public)  
- `OK: YouTube OAuth works`

Token is stored at `youtube/token.json` (gitignored). Re-run without browser until token expires/revoked.

## D. Dry-run upload (optional, unlisted)

```powershell
python youtube/upload_short.py --file final/short3.mp4 --title "TEST upload — delete me" --privacy unlisted --dry-run
# then real:
python youtube/upload_short.py --file final/short3.mp4 --title "Test upload — delete me" --privacy unlisted
```

Delete the test video in Studio after confirming.

## E. Before full automation

| Check | Pass? |
|-------|--------|
| `test_youtube_auth.py` OK | |
| Unlisted test upload appears on channel | |
| Upload as correct Brand Account (not personal) | |
| Quota: default **10,000 units/day** (~6 uploads; insert costs ~1600) | |

If you hit quota, request increase in Google Cloud → YouTube Data API → Quotas.
