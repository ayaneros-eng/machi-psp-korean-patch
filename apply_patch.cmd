@echo off
setlocal
if "%~1"=="" goto usage
py -3.11 -X utf8 "%~dp0apply_patch.py" --source "%~f1" --output "%~dp0Machi_R42_Korean.cso"
if errorlevel 1 goto failed
echo.
echo Done: Machi_R42_Korean.cso
pause
exit /b 0
:failed
echo.
echo Patch failed. Read the error above and README.md.
pause
exit /b 1
:usage
echo Drag your original Japanese ISO onto this file.
echo Python 3.11 with Python Launcher is required.
pause
exit /b 1
