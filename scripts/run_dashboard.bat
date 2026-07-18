@echo off
setlocal EnableDelayedExpansion
title BMS Unified System Launcher

echo ===================================================
echo     Intelligent BMS Unified Startup Script
echo ===================================================
echo.

:: 1. Move to the correct project directory
cd /d "%~dp0"
echo [*] Working directory: %CD%

:: 2. Check and Activate Virtual Environment
if exist "venv\Scripts\activate.bat" goto ACTIVATE_VENV
if exist ".venv\Scripts\activate.bat" goto ACTIVATE_DOT_VENV
echo [!] No virtual environment found. Using system Python.
goto SKIP_VENV

:ACTIVATE_VENV
echo [*] Activating Python virtual environment (venv)...
call venv\Scripts\activate.bat
goto SKIP_VENV

:ACTIVATE_DOT_VENV
echo [*] Activating Python virtual environment (.venv)...
call .venv\Scripts\activate.bat

:SKIP_VENV

:: 3. Check Python and npm
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

:: 4. Prevent duplicate instances
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

:: 5. Start Backend Servers
echo [*] Starting Flask Telemetry Backend (Port 5000)...
start "Prediction Backend (5000)" /D "%~dp0..\backend" python bms_dashboard_backend.py

echo [*] Starting FastAPI Backend (Port 8000)...
start "FastAPI Backend (8000)" /D "%~dp0..\frontend\battery-dashboard\battery-dashboard\backend" python main.py

echo [*] Starting VNet / Bluetooth Gateway...
start "VNet Bluetooth Gateway" /D "%~dp0..\backend" python bms_bluetooth_gateway.py

:: 6. Poll Backend Health Checks
echo [*] Waiting for Backend APIs to initialize...
set MAX_RETRIES=60
set RETRY_COUNT=0

:POLL_HEALTH
powershell -Command "try { $res1 = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/health' -Method Get -ProxyUseDefault $false -ErrorAction Stop; $resML = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/ml-health' -Method Get -ProxyUseDefault $false -ErrorAction Stop; $res2 = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -Method Get -ProxyUseDefault $false -ErrorAction Stop; if ($res1.status -eq 'healthy' -and $resML.status -eq 'running' -and $res2.status -eq 'ok') { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
if %errorlevel% equ 0 (
    echo [+] Backends are fully ready and healthy!
    goto BACKEND_READY
)

set /a RETRY_COUNT+=1
if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo [ERROR] Backends failed to start or health checks timed out.
    echo Please check the backend console windows for exact startup errors.
    pause
    exit /b 1
)
ping 127.0.0.1 -n 2 >nul
goto POLL_HEALTH

:BACKEND_READY

:: 7. Start React/Vite Frontend
echo [*] Starting React/Vite Frontend (Port 5173)...
cd ..\frontend\battery-dashboard\battery-dashboard\frontend
if not exist "node_modules" (
    echo [*] Installing npm packages...
    call npm install
)
start "Start Dashboard Frontend (5173)" npm run dev -- --host 0.0.0.0

:: 8. Poll Frontend Health Check
echo [*] Waiting for React Frontend to start...
set FRONTEND_RETRIES=0

:POLL_FRONTEND
powershell -Command "try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -ProxyUseDefault $false -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>nul
if %errorlevel% equ 0 (
    echo [+] Frontend is fully ready!
    goto FRONTEND_READY
)

set /a FRONTEND_RETRIES+=1
if %FRONTEND_RETRIES% geq 60 (
    echo [ERROR] Frontend failed to start or timed out.
    pause
    exit /b 1
)
ping 127.0.0.1 -n 2 >nul
goto POLL_FRONTEND

:FRONTEND_READY

:: 9. Get Local IP Address
for /f "usebackq tokens=*" %%a in (`powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -match 'Wi-Fi|Ethernet' } | Select-Object -First 1).IPAddress"`) do set LOCAL_IP=%%a

if "!LOCAL_IP!"=="" set LOCAL_IP=127.0.0.1

echo.
echo ======================================================================
echo   BMS Unified System is LIVE!
echo.
echo   Local Dashboard URL : http://127.0.0.1:5173
echo   Network URL (Mobile): http://!LOCAL_IP!:5173
echo.
echo   Do NOT close the running console windows to keep it active.
echo ======================================================================

:: 10. Open browser strictly to the Start Dashboard
start http://127.0.0.1:5173

ping 127.0.0.1 -n 6 >nul
