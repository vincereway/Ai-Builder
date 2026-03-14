@echo off
chcp 65001 >nul 2>&1
echo UI 컴파일 시작...
"%~dp0.venv\Scripts\python.exe" "%~dp0scripts\compile_ui.py"
echo.
pause
