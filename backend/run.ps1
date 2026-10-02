# GridShield Backend Launcher
Write-Host "Starting GridShield AI Backend..." -ForegroundColor Cyan
Set-Location -Path "D:\gridshield-ai\backend"
$env:PYTHONPATH = "D:\gridshield-ai;D:\gridshield-ai\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
