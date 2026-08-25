@echo off
setlocal EnableDelayedExpansion
title BMS Unified System Launcher

echo ===================================================
echo     Intelligent BMS Unified Startup Script
echo ===================================================
echo.

:: 1. Move to the correct project directory reliably
cd /d "%~dp0"
set "BASE_DIR=%~dp0"
echo [OK] Working directory: !BASE_DIR!

:: 2. Check Python and npm
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm is required for the frontend but not found.
    pause
    exit /b 1
)

:: 3. Prevent duplicate instances (Idempotent start)
echo [*] Checking for existing instances on ports 5000, 8000, 5173...
for %%P in (5000 8000 5173) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr /R /C:"TCP.*:%%P.*LISTENING"') do (
        set PID=%%a
        if not "!PID!"=="" (
            echo [!] Port %%P is occupied by PID: !PID!. Safely closing ghost process...
            taskkill /F /PID !PID! >nul 2>nul
            ping 127.0.0.1 -n 2 >nul
        )
    )
)

:: 4. Start Backend Services
echo.
echo [1/4] Starting Flask Backend (Port 5000)...
start "Flask Backend (5000)" /D "!BASE_DIR!..\backend" cmd /k "python bms_dashboard_backend.py"

echo [2/4] Starting FastAPI Backend (Port 8000)...
start "FastAPI Backend (8000)" /D "!BASE_DIR!..\frontend\battery-dashboard\backend" cmd /k "python main.py"

echo [*] Starting Bluetooth Gateway (Errors here won't stop the frontend)...
start "Bluetooth Gateway" /D "!BASE_DIR!..\backend" cmd /k "python bms_bluetooth_gateway.py"

:: 5. Poll Backend Health
echo [*] Waiting for Backend APIs to respond...
set RETRY_COUNT=0
:POLL_BACKEND
curl.exe -s http://127.0.0.1:5000/health >nul
set FLASK_OK=%errorlevel%
curl.exe -s http://127.0.0.1:8000/health >nul
set FASTAPI_OK=%errorlevel%

if %FLASK_OK% equ 0 if %FASTAPI_OK% equ 0 (
    echo [OK] Backends are fully ready!
    goto START_FRONTEND
)

set /a RETRY_COUNT+=1
if %RETRY_COUNT% geq 30 (
    echo [WARNING] Backends took too long to respond. Starting frontend anyway...
    goto START_FRONTEND
)
ping 127.0.0.1 -n 2 >nul
goto POLL_BACKEND

:START_FRONTEND
:: 6. Start Vite Frontend
echo.
echo [3/4] Starting React/Vite Frontend (Port 5173)...
set "FRONTEND_DIR=!BASE_DIR!..\frontend\battery-dashboard\frontend"
if not exist "!FRONTEND_DIR!\node_modules" (
    echo [*] Installing npm packages...
    cd /d "!FRONTEND_DIR!"
    call npm install
    cd /d "!BASE_DIR!"
)

:: Use cmd /k to keep window open, use --host 0.0.0.0 to ensure LAN access
start "Vite Frontend (5173)" /D "!FRONTEND_DIR!" cmd /k "npm run dev -- --host 0.0.0.0"

:: 7. Poll Frontend Health
echo [*] Waiting for React Frontend to become available...
set FRONTEND_RETRIES=0
:POLL_FRONTEND
curl.exe -s http://127.0.0.1:5173/ >nul
if %errorlevel% equ 0 (
    echo [OK] Vite running on port 5173
    goto DASHBOARD_READY
)

set /a FRONTEND_RETRIES+=1
if %FRONTEND_RETRIES% geq 30 (
    echo [ERROR] Frontend failed to start on port 5173.
    pause
    exit /b 1
)
ping 127.0.0.1 -n 2 >nul
goto POLL_FRONTEND

:DASHBOARD_READY
:: 8. Get Local IP and Open Browser
echo.
echo [4/4] Opening dashboard...
for /f "usebackq tokens=*" %%a in (`powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -match 'Wi-Fi|Ethernet' } | Select-Object -First 1).IPAddress"`) do set LOCAL_IP=%%a

if "!LOCAL_IP!"=="" set LOCAL_IP=127.0.0.1

echo.
echo ======================================================================
echo   [OK] BMS Unified System is LIVE!
echo.
echo   Local Dashboard URL : http://127.0.0.1:5173
echo   Network URL (Mobile): http://!LOCAL_IP!:5173
echo.
echo   Do NOT close the running cmd.exe windows!
echo ======================================================================

start http://!LOCAL_IP!:5173

