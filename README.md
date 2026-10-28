# LocalSubs — Local AI Subtitle & Video Editor

LocalSubs is a personal subtitle-editing workspace built with React, Vite, TypeScript, Tailwind CSS, FastAPI, SQLite, FFmpeg and faster-whisper. The goal is to run it on your own computer so video and transcription work stay on that computer.

> **Local privacy note:** use the local run instructions below for local processing. The hosted preview sends uploaded media to the configured Render API and is not a local-only workflow.

## Phase 1 — foundation

The repository contains the frontend, backend, SQLite initialization, environment templates, local launch scripts, and basic development instructions. The editor UI already contains some features from later phases; not every feature in the complete build specification is implemented yet.

### Requirements

- Python 3.11 or newer
- Node.js 20 or newer (npm is included with Node.js)
- FFmpeg recommended. The Python dependencies include imageio-ffmpeg as a fallback, but a system FFmpeg install is useful for media workflows.
- Internet access on the first transcription run to download the selected Whisper model. After that model files are cached locally.

### Quick start — Linux and macOS

From the repository root:

\`\`\`bash
chmod +x start.sh
./start.sh
\`\`\`

The script creates a Python virtual environment, installs the backend dependencies and frontend packages, prepares backend/.env from the example when needed, starts the API, and launches Vite.

### Quick start — Windows

From the repository root, double-click start.bat, or run it from Command Prompt:

\`\`\`bat
start.bat
\`\`\`

The script creates a virtual environment, installs dependencies, starts the API, and launches the frontend.

### Open the app

- Frontend: http://127.0.0.1:5173
- API health check: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs

Keep the terminal windows open while using LocalSubs.

### Manual setup — backend

Linux/macOS, from the repository root:

\`\`\`bash
cp backend/.env.example backend/.env
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
\`\`\`

On Windows PowerShell, from the repository root:

\`\`\`powershell
Copy-Item backend/.env.example backend/.env
Set-Location backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
\`\`\`

For the local setup, the environment template uses SQLite and stores uploaded media under the repository's storage/ folder. The application creates the SQLite database automatically on first startup. If you need a bootstrapped admin account, set ADMIN_PASSWORD in backend/.env to a strong unique password before first startup. The admin email defaults to admin@localsubs.app. Otherwise, use the Create account flow to make a normal user.

### Manual setup — frontend

Open a second terminal from the repository root:

\`\`\`bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
\`\`\`

On Windows, run the same commands in PowerShell or Command Prompt after changing to the frontend folder.

For local use, frontend/.env.example points to http://127.0.0.1:8000. Copy it to frontend/.env only if you want to make the API URL explicit. Do not put server-side secrets in Vite environment variables; VITE_* values are included in frontend code sent to the browser.

### FFmpeg install (recommended)

- Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg
- macOS with Homebrew: brew install ffmpeg
- Windows with winget: winget install Gyan.FFmpeg

Open a new terminal after installing and check with ffmpeg -version.

## Admin credentials and secrets

The project intentionally does not publish a default admin password. Do not commit backend/.env, access tokens, API keys, or passwords. .env files are ignored by Git.

When using Render, configure ADMIN_PASSWORD in the API service's Environment settings and redeploy. For local mode, set it in backend/.env and restart the API. Admin setup creates a new account if needed or grants the admin role to an existing matching email; it does not overwrite an existing account's password.

## Current implemented features

- Custom registration/login/logout and refresh-token authentication
- Per-user projects, media uploads and seekable media streaming
- faster-whisper transcription with word timestamps and subtitle grouping
- Editable caption text and timings, with SRT/VTT/ASS/TXT export
- Caption styles previewed over the video player, including Classic, Pop and Karaoke options
- Light/dark theme, responsive layout and PWA install shell
- MOGRT upload as a style asset

## Features still in progress

The complete build specification includes features that are not all complete yet, such as a full timeline editor with drag handles, undo/redo history, saved style presets, translation tracks, configurable typography and safe areas, background transcription/export jobs with progress, and rendering a final MP4 with subtitles burned in to match all style settings. An uploaded .mogrt is stored as an asset; FFmpeg cannot render a Premiere Pro MOGRT template directly.

## Hosted preview (optional)

- Web app: https://localsubs-frontend.onrender.com
- API health: https://localsubs-api.onrender.com/health
- API documentation: https://localsubs-api.onrender.com/docs

The Render free service may sleep after inactivity and may have ephemeral storage. Avoid relying on the hosted preview for irreplaceable projects or media. Run locally for the intended personal, local-processing workflow.
