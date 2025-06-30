@echo off
echo Starting Subtitle Editor...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    echo.
    pause
    exit /b 1
)

REM Run the application
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application ended with error
    pause
) 