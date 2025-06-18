@echo off
echo Setting up Enhanced Auto-Committer...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check if Git is installed
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed or not in PATH. Please install Git.
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your API keys and credentials.
)

REM Update repository path in config
if exist auto_committer_config.yaml (
    echo Updating repository path in config...
    REM Use PowerShell to update the repository path
    powershell -Command "(Get-Content auto_committer_config.yaml) -replace 'path: \".*\"', 'path: \"%CD%\"' | Set-Content auto_committer_config.yaml"
)

echo Setup complete!
echo To start the auto-committer, run:
echo   venv\Scripts\activate.bat
echo   python auto_committer.py
echo.
echo To run once and exit:
echo   python auto_committer.py --once
echo.
echo To use a custom config:
echo   python auto_committer.py --config C:\path\to\custom_config.yaml 