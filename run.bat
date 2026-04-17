@echo off
setlocal

rem --- Configuración ---
set VENV_DIR=.venv
set VENV_PY=%~dp0%VENV_DIR%\Scripts\python.exe
set VENV_PIP=%~dp0%VENV_DIR%\Scripts\pip.exe
set MAIN_PY=%~dp0main.py
set REQS=%~dp0requirements.txt

rem --- Crear venv si no existe ---
if not exist "%~dp0%VENV_DIR%\" (
    echo [INFO] Creando entorno virtual en %VENV_DIR%...
    rem Usa python o python3 si python no está en PATH como tal
    where python >nul 2>&1
    if errorlevel 1 (
        where python3 >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] No se encontro Python en PATH.
            pause
            exit /b 1
        ) else (
            python3 -m venv "%~dp0%VENV_DIR%"
        )
    ) else (
        python -m venv "%~dp0%VENV_DIR%"
    )

    rem --- Instalar dependencias solo al crear el venv ---
    if exist "%VENV_PIP%" (
        echo [INFO] Actualizando pip e instalando dependencias...
        "%VENV_PIP%" install --upgrade pip
        if exist "%REQS%" (
            "%VENV_PIP%" install -r "%REQS%"
        )
    ) else (
        echo [ERROR] pip no encontrado tras crear el entorno.
        pause
        exit /b 1
    )
)

rem --- Preparar directorios ---
if not exist "%~dp0todo" mkdir "%~dp0todo"
if not exist "%~dp0done" mkdir "%~dp0done"

echo.
echo [INFO] Entorno listo. Ejecutando script...
echo.

rem --- Ejecutar main.py con el python del venv para asegurar dependencias ---
if exist "%VENV_PY%" (
    "%VENV_PY%" "%MAIN_PY%"
) else (
    echo [ERROR] No se encontro el ejecutable Python en %VENV_DIR%\Scripts.
    pause
    exit /b 1
)

echo.
echo [INFO] Proceso finalizado.
pause
endlocal
