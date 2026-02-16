@echo off
title Flask Server + Cloudflared
cd /d "%~dp0"

set "PYTHON_EXE="

echo Searching for virtual environment...

set "DIR=%cd%"

:search_loop

if exist "%DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%DIR%\.venv\Scripts\python.exe"
    goto found
)

if exist "%DIR%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%DIR%\venv\Scripts\python.exe"
    goto found
)

cd ..
if "%cd%"=="%DIR%" goto not_found
set "DIR=%cd%"
goto search_loop


:found
cd /d "%~dp0"

echo Found venv:
echo %PYTHON_EXE%
echo.

echo Checking Flask...
"%PYTHON_EXE%" -c "import flask; print('Flask:', flask.__version__)" >nul 2>&1
if errorlevel 1 (
    echo Flask not found. Installing...
    "%PYTHON_EXE%" -m pip install flask
)

echo Starting Flask server...
start "Flask Server" cmd /k ""%PYTHON_EXE%" "%~dp0server.py""

timeout /t 3 > nul

echo Starting Cloudflare Tunnel...
start "Cloudflared" cmd /k cloudflared tunnel --url http://127.0.0.1:5000

pause
exit /b


:not_found
echo ERROR: No virtual environment found.
echo.
echo Expected one of:
echo   .venv\Scripts\python.exe
echo   venv\Scripts\python.exe
echo.
echo Current folder:
echo %~dp0
echo.
pause
exit /b 1
