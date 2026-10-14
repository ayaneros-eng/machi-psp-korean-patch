@echo off
setlocal DisableDelayedExpansion
chcp 65001 >nul
if exist "%~dp0MachiPatch.exe" goto gui
if not exist "%~dp0apply_patch.py" goto incomplete
if not exist "%~dp0patch_core.py" goto incomplete
if "%~1"=="" goto ask_source
set "MACHI_SOURCE=%~f1"
goto find_python
:ask_source
echo ISO 파일을 이 창에 끌어다 놓고 Enter를 누르세요.
set /p "MACHI_SOURCE=원본 ISO: "
set "MACHI_SOURCE=%MACHI_SOURCE:"=%"
if not defined MACHI_SOURCE goto end_error
:find_python
set "MACHI_PYTHON="
call :probe "%~dp0runtime\python.exe"
if defined MACHI_PYTHON goto run
call :probe "%LocalAppData%\Programs\Python\Python311\python.exe"
if defined MACHI_PYTHON goto run
call :probe "%ProgramFiles%\Python311\python.exe"
if defined MACHI_PYTHON goto run
py -3.11 -I -B -X utf8 "%~dp0apply_patch.py" --runtime-check >nul 2>&1
if not errorlevel 1 goto run_py
for /f "delims=" %%P in ('where python.exe 2^>nul') do call :probe "%%P"
if defined MACHI_PYTHON goto run
echo.
echo [실행 환경 없음] 호환되는 Python을 찾지 못했습니다.
echo 간편 적용판 ZIP을 새 폴더에 모두 풀고 MachiPatch.exe를 실행해 주세요.
echo 간편 적용판은 Python을 따로 설치할 필요가 없습니다.
goto end_error
:probe
if defined MACHI_PYTHON exit /b 0
if not exist "%~1" exit /b 1
set "MACHI_CANDIDATE=%~1"
if not "%MACHI_CANDIDATE:WindowsApps=%"=="%MACHI_CANDIDATE%" exit /b 1
"%~1" -I -B -X utf8 "%~dp0apply_patch.py" --runtime-check >nul 2>&1
if not errorlevel 1 set "MACHI_PYTHON=%~1"
exit /b 0
:run
"%MACHI_PYTHON%" -I -B -X utf8 "%~dp0apply_patch.py" --source "%MACHI_SOURCE%" --output "%~dp0Machi_R42_Korean.cso"
if errorlevel 1 goto end_error
goto success
:run_py
py -3.11 -I -B -X utf8 "%~dp0apply_patch.py" --source "%MACHI_SOURCE%" --output "%~dp0Machi_R42_Korean.cso"
if errorlevel 1 goto end_error
goto success
:gui
if "%~1"=="" goto gui_empty
start "" /wait "%~dp0MachiPatch.exe" "%~f1"
exit /b %errorlevel%
:gui_empty
start "" /wait "%~dp0MachiPatch.exe"
exit /b %errorlevel%
:incomplete
echo [파일 누락] ZIP 안에서 바로 실행하지 말고 새 폴더에 전체 압축을 풀어 주세요.
:end_error
echo.
echo 적용하지 못했습니다. 위 오류와 처음_읽어주세요.txt를 확인해 주세요.
pause
exit /b 1
:success
echo.
echo 완료: Machi_R42_Korean.cso
pause
exit /b 0
