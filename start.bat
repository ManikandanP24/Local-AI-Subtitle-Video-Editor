@echo off
where python >nul 2>nul || (echo Python 3.11+ is required & exit /b 1)
where node >nul 2>nul || (echo Node.js 20+ is required & exit /b 1)
if not exist backend\.env copy backend\.env.example backend\.env
cd backend
if not exist .venv python -m venv .venv
call .venv\Scripts\pip install -r requirements.txt
start "LocalSubs API" .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
cd ..\frontend
call npm install
call npm run dev -- --host 127.0.0.1
