# Feedstock.AI Application PowerShell Launcher
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " FEEDSTOCK.AI - Industry 4.0 Vision Transformer Defect Detection" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Starting application server on http://127.0.0.1:8000 ..." -ForegroundColor Green

Start-Process "http://127.0.0.1:8000"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
