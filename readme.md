# PDF to CBZ

Convierte archivos PDF a formato **CBZ** (ZIP con imágenes comprimidas), ideal para usar en lectores de cómics como **YACReader**, **Komga**, **Kavita**, **Ubooquity** y similares.

## Características

- ✅ Conversión por lotes de todos los PDFs en un directorio
- ✅ Procesamiento paralelo (multithreading) configurable
- ✅ Compresión automática a formato CBZ
- ✅ Eliminación opcional del PDF original tras la conversión
- ✅ Sobrescritura forzada de archivos existentes
- ✅ Soporte para PDFs protegidos (se omiten automáticamente)
- ✅ Barra de progreso con `tqdm`
- ✅ Registro detallado de actividades (logging)

## Requisitos

- **Python 3.8+**
- Dependencias listadas en `requirements.txt`

## Instalación

### Windows

Ejecuta directamente `run.bat`. El script crea automáticamente un entorno virtual (`.venv/`), instala las dependencias necesarias y ejecuta el programa.

```batch
run.bat
```

### Manual (cualquier SO)

```bash
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\activate      # Windows

pip install -r requirements.txt
python main.py
```

## Uso

Coloca los archivos PDF en la carpeta `todo/` y ejecuta:

```bash
python main.py
```

Los archivos CBZ convertidos aparecerán en la carpeta `done/`.

### Estructura de directorios

```
pdf-to-cbz/
├── main.py              # Script principal
├── run.bat              # Lanzador para Windows
├── requirements.txt     # Dependencias
├── todo/                # Coloca aquí los PDFs a convertir
├── done/                # Los CBZ convertidos se guardan aquí
└── .venv/               # Entorno virtual (creado automáticamente)
```

### Ejemplos

**Uso básico** — convierte todos los PDFs en `todo/`:

```bash
python main.py
```

**Especificar directorios personalizados**:

```bash
python main.py -i mis_pdfs -o mis_cbzs
```

**Ajustar calidad y resolución**:

```bash
python main.py --dpi 300 --quality 95
```

**Procesar con 8 workers en paralelo**:

```bash
python main.py --workers 8
```

**No eliminar los PDF originales**:

```bash
python main.py --keep-pdf
```

**Sobrescribir CBZs existentes sin preguntar**:

```bash
python main.py --force
```

**Combinar varias opciones**:

```bash
python main.py -i comics -o cbzs --dpi 300 --quality 92 --workers 6 --force --keep-pdf
```

## Opciones de línea de comandos

| Argumento        | Por defecto | Descripción                                  |
|------------------|-------------|----------------------------------------------|
| `-i`, `--input`  | `todo`      | Directorio de entrada con los PDFs           |
| `-o`, `--output` | `done`      | Directorio de salida para los CBZs           |
| `--dpi`          | `200`       | Resolución en DPI para la conversión         |
| `--quality`      | `90`        | Calidad de compresión JPEG (1–100)           |
| `--workers`      | `4`         | Número de workers en paralelo                |
| `--force`        | —           | Sobrescribe CBZs existentes sin preguntar    |
| `--keep-pdf`     | —           | Conserva el PDF original después de convertir|

## Licencia

MIT
