@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Run py -3.12 setup.py first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m autoshift
pause
