@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop.ps1"
if errorlevel 1 (
  echo.
  echo Failed to stop Python Exam Agent. Please check the message above.
  pause
  exit /b 1
)
echo.
pause
