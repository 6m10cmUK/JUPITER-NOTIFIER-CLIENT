@echo off
:menu
cls
echo ============================================
echo    JUPITER NOTIFIER SYSTEM メニュー
echo ============================================
echo.
echo 1. システムを起動
echo 2. システムを停止
echo 3. 自動起動を設定
echo 4. 自動起動を解除
echo 5. WIN-MONITORをビルド
echo 6. 終了
echo.
set /p choice=選択してください (1-6): 

if "%choice%"=="1" goto start_system
if "%choice%"=="2" goto stop_system
if "%choice%"=="3" goto install_autostart
if "%choice%"=="4" goto uninstall_autostart
if "%choice%"=="5" goto build_monitor
if "%choice%"=="6" goto exit

echo 無効な選択です。
pause
goto menu

:start_system
call start_jupiter_notifier.bat
pause
goto menu

:stop_system
call stop_all.bat
pause
goto menu

:install_autostart
call install_autostart.bat
goto menu

:uninstall_autostart
call uninstall_autostart.bat
goto menu

:build_monitor
cd WIN-MONITOR
call build.bat
cd ..
goto menu

:exit
echo 終了します...
exit /b 0