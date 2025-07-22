@echo off
chcp 65001 >nul
echo ===================================
echo Installing screeninfo module
echo ===================================
echo.

REM Try with virtual environment first
if exist venv\Scripts\activate.bat (
    echo Using virtual environment...
    call venv\Scripts\activate.bat
    pip install screeninfo
    if %errorlevel% equ 0 (
        echo.
        echo Installation successful!
        echo You can now run: run.bat
        pause
        exit /b 0
    )
)

REM If venv fails or doesn't exist, try global install
echo.
echo Installing globally...
pip install screeninfo
if %errorlevel% equ 0 (
    echo.
    echo Installation successful!
    echo You can now run: run.bat
) else (
    echo.
    echo [ERROR] Failed to install screeninfo
    echo Please try running: pip install screeninfo
)

pause