@echo off
setlocal
cd /d "%~dp0.."

echo Starting AI Research Assistant backend (auth + upload on :8000)...
set PYTHONPATH=%CD%
python -m uvicorn backend.dev_server:app --reload --host 0.0.0.0 --port 8000
