@echo off
REM Process manager script for Windows
REM Provides automatic restart on crashes and proper signal handling

set PROJECT_DIR=%~dp0
set LOG_DIR=%PROJECT_DIR%logs
set PID_FILE=%PROJECT_DIR%server.pid
set MAX_RESTARTS=5
set RESTART_DELAY=5

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%date% %time%] Starting Django server manager...

REM Check if virtual environment is activated
if defined VIRTUAL_ENV (
    echo [%date% %time%] Virtual environment detected: %VIRTUAL_ENV%
) else (
    echo [%date% %time%] Warning: No virtual environment detected. Consider activating one.
)

REM Function to start the server
:StartServer
echo [%date% %time%] Starting Django server...

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM Run startup validation first
python validate_startup.py
if %errorlevel% neq 0 (
    echo [%date% %time%] Startup validation failed
    goto :Error
)

REM Start the server
start /B python manage.py runserver 127.0.0.1:8000
echo [%date% %time%] Server started successfully
goto :Monitor

:Monitor
REM Monitor the server and restart if needed
set restart_count=0

:MonitorLoop
REM Check if the server process is running by testing the health endpoint
curl -s http://127.0.0.1:8000/health/ >nul 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] Server health check failed. Attempting restart...
    set /a restart_count+=1
    
    if %restart_count% geq %MAX_RESTARTS% (
        echo [%date% %time%] Maximum restart attempts reached. Giving up.
        goto :End
    )
    
    echo [%date% %time%] Waiting %RESTART_DELAY% seconds before restart...
    timeout /t %RESTART_DELAY% /nobreak >nul
    goto :StartServer
)

REM Wait before next check
timeout /t 10 /nobreak >nul
goto :MonitorLoop

:Error
echo [%date% %time%] Server startup failed
exit /b 1

:End
echo [%date% %time%] Server manager stopped
exit /b 0
