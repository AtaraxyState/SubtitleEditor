@echo off
echo Starting Subtitle Editor...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if FFmpeg is available
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found in PATH
    echo For full functionality, download FFmpeg and place ffmpeg.exe in this folder
    echo Download from: https://www.gyan.dev/ffmpeg/builds/
    echo.
    echo The application will still start, but video processing features may not work.
    echo.
    pause
)

REM Run the application
echo Launching Subtitle Editor...
SubtitleEditor.exe

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application ended with error code %errorlevel%
    echo.
    echo This might be due to:
    echo - Missing FFmpeg (required for video processing)
    echo - Corrupted video files
    echo - Insufficient permissions
    echo.
    pause
)
