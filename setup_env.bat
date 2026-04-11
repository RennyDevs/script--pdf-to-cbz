@echo off
set VENV=.venv

REM Crear venv si no existe
if not exist "%VENV%" (
    python3 -m venv "%VENV%"
)

REM Instalar paquetes
"%VENV%\Scripts\pip.exe" install --upgrade pip
"%VENV%\Scripts\pip.exe" install -r requirements.txt

if not exist "todo" mkdir "todo"

echo.
echo Entorno creado e paquetes instalados en %VENV%.
echo Para activarlo en CMD:
echo    %VENV%\Scripts\activate.bat
echo Para PowerShell:
echo    %VENV%\Scripts\Activate.ps1
pause
