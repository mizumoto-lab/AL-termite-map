@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo Alabama Termite Map - External Data Update
echo ============================================
echo.
echo This will:
echo   1. Download Alabama county boundaries if missing
echo   2. Download a fresh iNaturalist Research Grade snapshot
echo   3. Save snapshot metadata
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 update_external_data.py
    goto :done
)

where python >nul 2>nul
if %errorlevel%==0 (
    python update_external_data.py
    goto :done
)

echo ERROR: Python was not found.
echo Install Python, or run update_external_data.py manually.
echo.

:done
echo.
echo Finished.
pause
