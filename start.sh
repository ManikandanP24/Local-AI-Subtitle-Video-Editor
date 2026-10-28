#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null || { echo "Python 3.11+ is required"; exit 1; }
command -v node >/dev/null || { echo "Node.js 20+ is required"; exit 1; }
[ -f "$ROOT/backend/.env" ] || cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"
if [ ! -d "$ROOT/backend/.venv" ]; then python3 -m venv "$ROOT/backend/.venv"; fi
"$ROOT/backend/.venv/bin/pip" install -r "$ROOT/backend/requirements.txt"
(cd "$ROOT/frontend" && npm install)
(cd "$ROOT/backend" && .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000) &
API_PID=$!
trap 'kill "$API_PID" 2>/dev/null || true' EXIT
(cd "$ROOT/frontend" && npm run dev -- --host 127.0.0.1)
