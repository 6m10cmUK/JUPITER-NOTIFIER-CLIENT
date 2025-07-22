@echo off
REM This script runs setup-autostart.bat with admin privileges

cd /d "%~dp0"

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    REM Not admin, request elevation
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && setup-autostart.bat' -Verb RunAs"
    exit /b
)

REM Already admin, run directly
call setup-autostart.bat