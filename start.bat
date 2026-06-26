@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"
if errorlevel 1 (
  echo.
  echo Failed to start Python Exam Agent. Please check the message above.
  pause
  exit /b 1
)
echo.
echo Servers are running in the background. Close this window when you are ready.
pause
