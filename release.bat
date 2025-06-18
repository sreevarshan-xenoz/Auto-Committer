@echo off
REM Enhanced Auto-Committer Release Script for Windows
REM This script helps create a new release on GitHub

set VERSION=0.1.0-alpha
set RELEASE_DATE=%date:~-4%-%date:~3,2%-%date:~0,2%
set RELEASE_TITLE=Enhanced Auto-Committer v%VERSION% (Alpha)
set RELEASE_BRANCH=main

echo ## What's New in Alpha Release > release_notes.txt
echo. >> release_notes.txt
echo This is the initial alpha release of the Enhanced Auto-Committer. Key features include: >> release_notes.txt
echo. >> release_notes.txt
echo - Core auto-committing functionality >> release_notes.txt
echo - Real-time file monitoring >> release_notes.txt
echo - Configurable scheduling >> release_notes.txt
echo - Security scanning for sensitive data >> release_notes.txt
echo - AI-powered commit message generation (optional) >> release_notes.txt
echo - Multiple deployment options (direct, Docker, system service) >> release_notes.txt
echo - Comprehensive logging >> release_notes.txt
echo - Quick start scripts for Windows and Unix-like systems >> release_notes.txt
echo. >> release_notes.txt
echo ## Installation >> release_notes.txt
echo. >> release_notes.txt
echo See the README.md file for detailed installation instructions. >> release_notes.txt
echo. >> release_notes.txt
echo ## Known Issues >> release_notes.txt
echo. >> release_notes.txt
echo - This is an alpha release and may contain bugs >> release_notes.txt
echo - Some advanced features may not be fully tested >> release_notes.txt
echo - Performance may vary depending on repository size >> release_notes.txt
echo. >> release_notes.txt
echo ## Feedback >> release_notes.txt
echo. >> release_notes.txt
echo Please report any issues or suggestions on the GitHub repository. >> release_notes.txt

REM Update version in setup.py
powershell -Command "(Get-Content setup.py) -replace 'version=\".*\"', 'version=\"%VERSION%\"' | Set-Content setup.py"

REM Update CHANGELOG.md with release date
powershell -Command "(Get-Content CHANGELOG.md) -replace '## \[%VERSION%\] - .*', '## \[%VERSION%\] - %RELEASE_DATE%' | Set-Content CHANGELOG.md"

REM Create a release commit
git add setup.py CHANGELOG.md
git commit -m "Prepare for %VERSION% release"

REM Create a tag
git tag -a "v%VERSION%" -m "Release v%VERSION%"

REM Push changes and tag
git push origin %RELEASE_BRANCH%
git push origin "v%VERSION%"

echo Release preparation complete!
echo Now go to https://github.com/sreevarshan-xenoz/Auto-Committer/releases/new
echo Select the v%VERSION% tag
echo Set the release title to: %RELEASE_TITLE%
echo Add the release notes from release_notes.txt
echo.
echo Then publish the release. 