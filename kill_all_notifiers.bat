@echo off
echo [JUPITER NOTIFIER] Killing all notification processes...
echo.

REM Kill all Python processes
echo Terminating python.exe processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel%==0 (
    echo - Successfully terminated python.exe processes
) else (
    echo - No python.exe processes found
)

REM Kill pythonw.exe (GUI Python apps)
echo Terminating pythonw.exe processes...
taskkill /F /IM pythonw.exe 2>nul
if %errorlevel%==0 (
    echo - Successfully terminated pythonw.exe processes
) else (
    echo - No pythonw.exe processes found
)

REM Kill by window title (backup method)
echo Terminating by window title...
taskkill /F /FI "WINDOWTITLE eq JUPITER NOTIFICATION" 2>nul

REM List remaining Python processes
echo.
echo Checking for remaining Python processes...
tasklist /FI "IMAGENAME eq python.exe" 2>nul | findstr /I python
if %errorlevel%==0 (
    echo.
    echo WARNING: Some Python processes are still running!
    echo You may need to terminate them manually from Task Manager
) else (
    echo.
    echo All Python processes have been terminated successfully
)

echo.
pause