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
