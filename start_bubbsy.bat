@echo off
title Bubbsy Start Page Launcher
color 0B

echo ================================================================
echo           BUBBSY START PAGE - LOCAL OSINT COMMAND CENTER
echo ================================================================
echo.
echo  * Loading 1,699+ Curated OSINT Tools...
echo  * Initializing Threat Radar & AI Intelligence Engine...
echo  * Starting Local Server at http://localhost:7777 ...
echo.

cd /d "%~dp0"

:: Start browser after brief delay in background
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:7777"

:: Launch Python local server
python server.py

if errorlevel 1 (
    echo.
    echo [!] Python was not found or encountered an error.
    echo Launching standalone index.html directly in browser...
    start index.html
    pause
)
