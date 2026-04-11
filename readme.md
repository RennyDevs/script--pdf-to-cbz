Crear un entorno virtual en Python con `venv` es una práctica excelente para mantener tus dependencias aisladas y organizadas. Aquí te dejo los pasos detallados 👇:

---

## 🛠 Pasos para crear un entorno con `venv`

1. **Verifica que tienes Python instalado**
   En tu terminal o consola:
   ```bash
   python --version
   ```
   o en algunos sistemas:
   ```bash
   python3 --version
   ```

2. **Crea el entorno virtual**
   En la carpeta de tu proyecto, ejecuta:
   ```bash
   python -m venv env
   ```
   - Aquí `env` es el nombre del entorno. Puedes llamarlo como quieras (ej. `.venv`, `virtual`, etc.).

3. **Activa el entorno virtual**
   Dependiendo de tu sistema operativo:

   - **Windows (CMD o PowerShell):**
     ```bash
     .\env\Scripts\activate
     ```
   - **Linux / macOS (bash/zsh):**
     ```bash
     source env/bin/activate
     ```

   Si todo salió bien, verás el nombre del entorno (`env`) al inicio de tu línea de comandos.

4. **Instala tus dependencias dentro del entorno**
   Por ejemplo:
   ```bash
   pip install pymupdf
   pip install requests
   ```
   Cada paquete quedará aislado en tu entorno.

5. **Desactiva el entorno cuando termines**
   Simplemente ejecuta:
   ```bash
   deactivate
   ```

---

## 📦 Buenas prácticas
- Guarda tus dependencias en un archivo `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```
- Para restaurarlas en otro entorno:
  ```bash
  pip install -r requirements.txt
  ```

---


--------------------------------------------------------------------------------

Aquí tienes dos opciones: Makefile (Linux/macOS/WSL/Git Bash) y .bat para Windows. Ambos crean un virtualenv, lo activan (cuando sea posible) e instalan dependencias desde requirements.txt.

Makefile (usa python3; abre una nueva shell para activar):
```
PY=python3
VENV=.venv

.PHONY: create activate install shell clean

create:
	$(PY) -m venv $(VENV)

install: create
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

# Abre una nueva shell con el venv activado
shell: install
	@echo "Abriendo shell con el entorno virtual activado..."
	. $(VENV)/bin/activate && exec ${SHELL}

clean:
	rm -rf $(VENV)
```

Uso:
- make install — crea el venv e instala dependencias.
- make shell — abre una nueva shell con el venv activado.

Windows .bat (cmd.exe):
Save as setup_env.bat in project root (usa python en PATH).
```
@echo off
set VENV=.venv

REM Crear venv si no existe
if not exist "%VENV%" (
    python -m venv "%VENV%"
)

REM Instalar paquetes
"%VENV%\Scripts\pip.exe" install --upgrade pip
"%VENV%\Scripts\pip.exe" install -r requirements.txt

echo.
echo Entorno creado e paquetes instalados en %VENV%.
echo Para activarlo en CMD:
echo    %VENV%\Scripts\activate.bat
echo Para PowerShell:
echo    %VENV%\Scripts\Activate.ps1
pause
```

Opcional: .ps1 para PowerShell (permite activar en la misma sesión):
Save as setup_env.ps1
```powershell
$venv = ".\.venv"

if (-not (Test-Path $venv)) {
    python -m venv $venv
}

& "$venv\Scripts\pip.exe" install --upgrade pip
& "$venv\Scripts\pip.exe" install -r requirements.txt

Write-Host "Entorno listo. Activando..."
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& "$venv\Scripts\Activate.ps1"
```
