# LocalSubs — Local AI Subtitle & Video Editor

LocalSubs is a creator-focused subtitle editor built with React, Vite, TypeScript and FastAPI. It includes a responsive dashboard, dark/light mode, an installable PWA shell, custom authentication, media upload/preview, local Whisper transcription, subtitle editing, and SRT/VTT/ASS/TXT exports.

## Live preview

- Web app: https://localsubs-frontend.onrender.com
- API health: https://localsubs-api.onrender.com/health
- API documentation: https://localsubs-api.onrender.com/docs

The hosted preview sends media to the configured Render API. For a genuinely local workflow, run the app on your own computer using the steps below.

## Run locally

Prerequisites: Python 3.11+, Node.js 20+. The project includes `imageio-ffmpeg` as an FFmpeg binary fallback; installing system FFmpeg is still recommended.

Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```

Windows: run `start.bat`.

Open http://localhost:5173. The API docs are at http://127.0.0.1:8000/docs. Whisper downloads its model the first time transcription is used; the local default is `small`.

## Default admin login

The login screen pre-fills `admin@localsubs.app`. The administrator account is created only when `ADMIN_EMAIL` and a strong `ADMIN_PASSWORD` (at least 16 characters) are configured; the app intentionally does not ship with a public, guessable admin password.

For the hosted app, open the [Render API service](https://dashboard.render.com/web/srv-dbgq9dff3r2c73adgqg0), go to **Environment**, set `ADMIN_PASSWORD` to a strong unique password, and save/redeploy. `ADMIN_EMAIL` is already configured as `admin@localsubs.app`. Once the API restarts, it creates that admin account if it does not already exist, or grants the admin role to the matching existing account without overwriting its password.

For local use, add `ADMIN_EMAIL=admin@localsubs.app` and `ADMIN_PASSWORD=your-strong-password` to `backend/.env`, then restart the API. Never commit the password to GitHub.

## Current features

- Custom register/login/logout and refresh-token rotation
- Private projects and media uploads with seekable streaming
- Whisper speech transcription with word timestamps and subtitle grouping
- Subtitle text/timing editor and SRT, VTT, ASS and TXT exports
- Light/dark theme switch with remembered preference
- Install-app button, manifest and service worker for the installable PWA
- MOGRT upload under **New caption style**

## MOGRT note

A Premiere Pro `.mogrt` file is stored as a style asset and is not directly executable by FFmpeg. Actual MOGRT rendering requires compatible Adobe Premiere Pro/After Effects tooling. The current app renders standard subtitle exports; it does not yet render MOGRT templates into an MP4.

## Hosting and storage

Render services on the free plan use ephemeral storage here. Projects, SQLite data, uploaded videos, and uploaded style assets may be lost when the service is recreated or its filesystem is cleared. Do not use this hosted preview for irreplaceable media. For durable hosted storage, add a suitable persistent disk/database; for full local-first privacy, run it on your own machine. Configure secrets only as environment variables and keep HTTPS secure-cookie settings enabled in hosted environments.
