@echo off
echo Starting Barni Coffee...
echo.

start "Barni Backend" powershell -NoExit -Command "Set-Location 'C:\Users\Admin\Downloads\Smart_Barni\BARNI_BACKEND_FOLDER'; $env:DJANGO_SETTINGS_MODULE='config.settings.dev'; cmd /c '.\venv\Scripts\python.exe' manage.py runserver 8000"

start "Barni Frontend" powershell -NoExit -Command "Set-Location 'C:\Users\Admin\Downloads\Smart_Barni\frontend'; node .\node_modules\vite\bin\vite.js"

echo Waiting for servers to start...
timeout /t 6 /nobreak >nul
start http://localhost:5173

echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo.
pause
