@echo off
chcp 65001 >nul 2>&1
cls
echo.
echo  ========================================
echo     VulnSentinel 11-S - One-Click Start
echo  ========================================
echo.
echo  Tip: You can also double-click static\index.html
echo       for offline demo (no backend needed)
echo       Account: demo / demo123
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo IMPORTANT: check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
python -m pip install --quiet -r requirements.txt 2>nul

echo [2/3] Starting server...
echo.
echo  ========================================
echo  Open browser: http://localhost:8000
echo  Test account: demo / demo123
echo  Offline demo: double-click static\index.html
echo  Press Ctrl+C to stop
echo  ========================================
echo.

python main.py
pause
