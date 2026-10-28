# LocalSubs — Local AI Subtitle & Video Editor

Local-first subtitle editor built with React + Vite + TypeScript and FastAPI. Includes light/dark mode, installable PWA shell, custom auth, project dashboard, upload/streaming, Whisper transcription, subtitle editing and subtitle file exports.

## Development

Prerequisites: Python 3.11+, Node.js 20+, FFmpeg.

```bash
chmod +x start.sh
./start.sh
```

Frontend: http://localhost:5173
Backend API docs: http://127.0.0.1:8000/docs

## Render deployment

The current architecture is local-first: uploads and SQLite are stored on local disk. Render services use ephemeral disks unless a persistent disk is configured; for durable hosted storage, configure a persistent disk and SQLite path, or migrate metadata to an appropriate database. Local Whisper may require a larger instance and model download. Keep secrets in Render environment variables and set secure cookies/HTTPS for hosted deployments.

## MOGRT support

Premiere Pro `.mogrt` files are motion-graphics templates, not video files. This project can accept/upload the file as a style asset, but rendering it requires a compatible Adobe Premiere Pro/After Effects workflow. FFmpeg rendering uses ASS subtitle styles and does not execute MOGRT templates directly.
