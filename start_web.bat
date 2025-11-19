@echo off
REM 不强制设置UTF-8，避免字符问题
echo ======================================
echo AI Chat Guardian - Web Service
echo ======================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found, please install Python 3.8+
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Flask and dependencies...
    pip install flask flask-cors
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [2/4] Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama service is not running
    echo [INFO] Trying to start Ollama...
    start /B "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    timeout /t 3 >nul
)

echo [3/4] Setting environment variables...
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000
set FLASK_DEBUG=False

echo [4/4] Starting web service...
echo.
echo ======================================
echo Service Info:
echo - Local:    http://localhost:5000
echo - Network:  http://YOUR-IP:5000
echo.
echo Press Ctrl+C to stop
echo ======================================
echo.

cd web
python app.py

pause
