@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================================
echo  Ai-Builder 빌드
echo ============================================================
echo.

REM [1/4] Git 브랜치 표시
echo [1/4] Git 브랜치 확인
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set BRANCH=%%i
if defined BRANCH (
    echo   현재 브랜치: %BRANCH%
) else (
    echo   Git 정보를 가져올 수 없습니다.
)
echo.

REM [2/4] UI 컴파일
echo [2/4] UI 컴파일
python scripts\compile_ui.py
if %ERRORLEVEL% NEQ 0 (
    echo   ❌ UI 컴파일 실패
    goto :error
)
echo.

REM [3/4] PyInstaller 빌드
echo [3/4] PyInstaller 빌드
if exist "scripts\build\AiBuilder.spec" (
    pyinstaller scripts\build\AiBuilder.spec --noconfirm
) else (
    pyinstaller --onefile --windowed --name AiBuilder --icon=resources\icon.ico --add-data "conf;conf" main.py
)
if %ERRORLEVEL% NEQ 0 (
    echo   ❌ PyInstaller 빌드 실패
    goto :error
)
echo.

REM [4/4] 빌드 결과 확인
echo [4/4] 빌드 결과 확인
if exist "dist\AiBuilder.exe" (
    echo   ✅ 빌드 성공: dist\AiBuilder.exe
) else (
    echo   ❌ 빌드 결과물을 찾을 수 없습니다.
    goto :error
)

echo.
echo ============================================================
echo  빌드 완료
echo ============================================================
goto :end

:error
echo.
echo ============================================================
echo  빌드 실패
echo ============================================================
exit /b 1

:end
exit /b 0
