@echo off
echo === Installing Background Monitor Dependencies ===
echo.

pip install pywin32
pip install psutil  
pip install websockets

echo.
echo Installation complete!
pause