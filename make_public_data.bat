@echo off
setlocal
cd /d "%~dp0"

echo Creating privacy-filtered AU-termite-samples.csv...
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 make_public_data.py
    goto :done
)

where python >nul 2>nul
if %errorlevel%==0 (
    python make_public_data.py
    goto :done
)

echo ERROR: Python was not found.
echo Install Python or run make_public_data.py manually.

echo.

:done
echo.
pause
