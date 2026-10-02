# GridShield AI - Master Service Launcher
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         GridShield AI - Starting AIoT Power Grid           " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Start Backend in separate window
Write-Host "[1/3] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location 'D:\gridshield-ai\backend'; `$env:PYTHONPATH='D:\gridshield-ai;D:\gridshield-ai\backend'; Write-Host '--- GridShield Backend ---' -ForegroundColor Cyan; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
)

# Wait 4 seconds for backend to start up
Start-Sleep -Seconds 4

# 2. Start Sensor Simulator
Write-Host "[2/3] Launching Virtual IoT Sensor Simulator..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location 'D:\gridshield-ai'; `$env:PYTHONPATH='D:\gridshield-ai;D:\gridshield-ai\backend'; Write-Host '--- Virtual IoT Sensor Simulator ---' -ForegroundColor Cyan; python iot\sensor_simulator\run_simulator.py"
)

# 3. Start Frontend Dashboard
Write-Host "[3/3] Launching React Vite Frontend Dashboard on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location 'D:\gridshield-ai\frontend'; Write-Host '--- Frontend Dashboard ---' -ForegroundColor Cyan; npm run dev"
)

Start-Sleep -Seconds 3

# 4. Open browser
Write-Host ""
Write-Host "All components launched successfully!" -ForegroundColor Yellow
Write-Host "Dashboard: http://localhost:5173" -ForegroundColor White
Write-Host "API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "Login:     admin / admin123" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "http://localhost:5173"
