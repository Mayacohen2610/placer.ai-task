@echo off
rem start-dev.bat — create venv if missing, start backend and frontend in new windows

rem Ensure script runs from repository root
cd /d %~dp0

rem Backend setup
echo ===== Backend =====
cd backend
if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)
echo Activating backend venv and ensuring requirements
call .venv\Scripts\activate
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1

rem Start backend in new window
echo Starting backend (uvicorn) in new window...
start "backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate && python -m uvicorn src.app:app --reload --port 8000"

rem Frontend setup and start in new window
echo ===== Frontend =====
cd ..\frontend
echo Starting frontend (Vite) in new window...
start "frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"

echo All servers started. Check the new windows for logs. Frontend: http://localhost:5173, Backend: http://localhost:8000
