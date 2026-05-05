@echo off
title RL Map Loader - Build .exe
echo ============================================
echo    Building RL Map Loader .exe
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found!
    echo Download it from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install build dependencies
echo Installing dependencies...
pip install customtkinter Pillow pyinstaller --quiet --upgrade 2>nul
if errorlevel 1 (
    pip install customtkinter Pillow pyinstaller --quiet --upgrade --user 2>nul
)
echo Dependencies OK.
echo.

:: Find customtkinter path for --collect-data
echo Locating customtkinter package...
for /f "delims=" %%i in ('python -c "import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))"') do set CTK_PATH=%%i
echo Found: %CTK_PATH%
echo.

:: Build
echo Building executable...
echo This may take a minute or two...
echo.

pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "RLMapLoader" ^
    --icon "NONE" ^
    --collect-data customtkinter ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    rl_map_loader.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check the errors above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo    Build complete!
echo ============================================
echo.
echo Your .exe is at:  dist\RLMapLoader.exe
echo.
echo You can share this single file - no Python needed!
echo.
pause
