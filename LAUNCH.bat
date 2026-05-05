@echo off
title RL Map Loader
echo ============================================
echo    RL Map Loader - Setup ^& Launch
echo ============================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found!
    echo Download it from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Checking dependencies...
pip install customtkinter Pillow --quiet --upgrade 2>nul
if errorlevel 1 (
    echo Trying with --user flag...
    pip install customtkinter Pillow --quiet --upgrade --user 2>nul
)
echo Dependencies OK.
echo.

:: Launch the app
echo Starting RL Map Loader...
echo.
python "%~dp0rl_map_loader.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Something went wrong. Check the error messages above.
    pause
)
