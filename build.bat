@echo off
REM MyMT5 Build Script for Windows

echo ======================================================================
echo                       MyMT5 BUILD SCRIPT
echo ======================================================================
echo.

REM Step 1: Clean
echo [1/5] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"
echo [OK] Clean complete
echo.

REM Step 2: Check tools
echo [2/5] Checking build tools...
python -m pip install --upgrade pip setuptools wheel build twine --quiet
echo [OK] Build tools ready
echo.

REM Step 3: Build
echo [3/5] Building package...
python -m build
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    exit /b %errorlevel%
)
echo [OK] Build successful
echo.

REM Step 4: Check
echo [4/5] Checking package...
twine check dist/*
if %errorlevel% neq 0 (
    echo [ERROR] Package check failed
    exit /b %errorlevel%
)
echo [OK] Package check passed
echo.

REM Step 5: List artifacts
echo [5/5] Build artifacts:
dir /b dist
echo.

echo ======================================================================
echo                       BUILD COMPLETE!
echo ======================================================================
echo.
echo Next steps:
echo   * Test: pip install dist\mymt5-1.0.0-py3-none-any.whl
echo   * Upload to Test PyPI: twine upload --repository testpypi dist/*
echo   * Upload to PyPI: twine upload dist/*
echo.
pause

