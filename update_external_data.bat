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
if errorlevel 1 goto :try_python
py -3 update_external_data.py
set "EXITCODE=%errorlevel%"
goto :done

:try_python
where python >nul 2>nul
if errorlevel 1 goto :no_python
python update_external_data.py
set "EXITCODE=%errorlevel%"
goto :done

:no_python
echo ERROR: Python was not found.
echo Install Python, or run update_external_data.py manually.
set "EXITCODE=1"

:done
echo.
if "%EXITCODE%"=="0" (
    echo Finished.
) else (
    echo ERROR: External-data update did not complete successfully.
)
pause
exit /b %EXITCODE%
