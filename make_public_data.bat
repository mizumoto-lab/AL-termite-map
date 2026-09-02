@echo off
setlocal
cd /d "%~dp0"

echo Creating privacy-filtered AU-termite-samples.csv and Google My Maps data...
echo.

where py >nul 2>nul
if errorlevel 1 goto :try_python
py -3 make_public_data.py
set "EXITCODE=%errorlevel%"
goto :done

:try_python
where python >nul 2>nul
if errorlevel 1 goto :no_python
python make_public_data.py
set "EXITCODE=%errorlevel%"
goto :done

:no_python
echo ERROR: Python was not found.
echo Install Python or run make_public_data.py manually.
set "EXITCODE=1"

:done
echo.
if not "%EXITCODE%"=="0" echo ERROR: Public-data generation did not complete successfully.
pause
exit /b %EXITCODE%
