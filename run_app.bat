@echo off
title FEEDSTOCK.AI - Vision Transformer Defect Detection System
echo =====================================================================
echo  FEEDSTOCK.AI - Industry 4.0 Vision Transformer Defect Detection System
echo =====================================================================
echo Starting FastAPI application server on http://localhost:8000 ...
echo Press Ctrl+C in this terminal window to stop the server.
echo.

start "" "http://localhost:8000"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
pause
