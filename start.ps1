# Barni Coffee - Start Script
# Run: powershell -ExecutionPolicy Bypass -File start.ps1

Write-Host "Starting Barni Coffee..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'C:\Users\Admin\Downloads\Smart_Barni\BARNI_BACKEND_FOLDER'; `$env:DJANGO_SETTINGS_MODULE='config.settings.dev'; & '.\venv\Scripts\python.exe' manage.py runserver 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'C:\Users\Admin\Downloads\Smart_Barni\frontend'; node .\node_modules\vite\bin\vite.js"

Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host ""
