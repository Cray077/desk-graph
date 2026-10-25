@echo off
setlocal enabledelayedexpansion

title Building DeskGraph Executable...
echo ========================================================
echo        DeskGraph - Windows Executable Builder (.exe)
echo ========================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your PATH!
    echo Please install Python 3.8+ or add Python to your system PATH.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo [*] Found: !PYTHON_VER!

:: 2. Check and install PyInstaller
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] PyInstaller not detected. Installing PyInstaller...
    python -m pip install --upgrade pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install PyInstaller via pip.
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python -m PyInstaller --version') do set PYINSTALLER_VER=%%i
    echo [*] Found PyInstaller: !PYINSTALLER_VER!
)

:: 3. Optional dependencies check
if exist "requirements.txt" (
    echo [*] Installing optional dependencies from requirements.txt...
    python -m pip install -q -r requirements.txt
)

echo.
echo [*] Building standalone executable with PyInstaller...
echo     Mode: --onefile --noconsole (No terminal popup)
echo     Target: dist\DeskGraph.exe
echo.

:: 4. Clean previous builds
if exist "dist\DeskGraph.exe" del /f /q "dist\DeskGraph.exe"
if exist "build" rmdir /s /q "build"

:: 5. Run PyInstaller
python -m PyInstaller ^
    --noconsole ^
    --onefile ^
    --clean ^
    --name "DeskGraph" ^
    main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ========================================================
    echo [ERROR] Build failed! Check the output logs above.
    echo ========================================================
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo [SUCCESS] Build completed successfully!
echo Executable location:
echo   %~dp0dist\DeskGraph.exe
echo ========================================================
echo.
pause
