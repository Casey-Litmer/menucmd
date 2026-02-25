@echo off
REM Run Python inside the repository's virtualenv if present, otherwise use system python.
REM Usage: run_in_venv.bat -m <module> [args...]   OR   run_in_venv.bat your_script.py [args...]
SETLOCAL ENABLEDELAYEDEXPANSION

set REPO_DIR=%~dp0
if exist "%REPO_DIR%.venv\Scripts\python.exe" (
  set "PYTHON=%REPO_DIR%.venv\Scripts\python.exe"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python not found. Activate a virtualenv or install Python.
    pause
    exit /b 1
  ) else (
    set "PYTHON=python"
  )
)


n"%PYTHON%" %*