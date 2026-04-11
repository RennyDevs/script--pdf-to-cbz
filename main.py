import logging
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF
from PIL import Image

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Configuración de directorios
INPUT_DIR = Path("todo")
OUTPUT_DIR = Path("done")

# Configuración de procesamiento
DPI = 200
IMG_QUALITY = 90

def get_files(directory: Path, pattern: str = "*") -> List[Path]:
    """
    Obtiene una lista de archivos en un directorio que coinciden con un patrón.
    """
    if not directory.exists():
        logger.warning(f"El directorio no existe: {directory}")
        return []
    return [f for f in directory.glob(pattern) if f.is_file()]

def list_folders(path: Path, exclude: Optional[List[str]] = None) -> List[Path]:
    """
    Devuelve una lista de carpetas dentro de `path` excluyendo las especificadas.
    """
    if exclude is None:
        exclude = []

    if not path.exists():
        return []

    return [d for d in path.iterdir() if d.is_dir() and d.name not in exclude]

def pdf_to_images(pdf_path: Path, output_base_folder: Path) -> Optional[Path]:
    """
    Convierte cada página de un PDF en una imagen JPEG.
    """
    try:
        # Crear subcarpeta para las imágenes del PDF
        target_folder = output_base_folder / pdf_path.stem
        target_folder.mkdir(parents=True, exist_ok=True)

        with fitz.open(pdf_path) as doc:
            if len(doc) == 0:
                logger.warning(f"⚠️ El PDF {pdf_path.name} está vacío.")
                return None

            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=DPI)

                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

                if pix.alpha:
                    img = img.convert("RGB")

                image_path = target_folder / f"{i + 1:03d}.jpg"  # Padding para orden correcto
                img.save(image_path, format="JPEG", quality=IMG_QUALITY)

        logger.info(f"🖼️  Convertido: {pdf_path.name} ({len(doc)} páginas)")
        return target_folder

    except Exception as e:
        logger.error(f"❌ Error procesando {pdf_path.name}: {e}")
        if 'target_folder' in locals() and target_folder.exists():
            shutil.rmtree(target_folder)
        return None

def compress_to_cbz(folder_path: Path) -> bool:
    """
    Comprime el contenido de una carpeta en un archivo .cbz y elimina la carpeta.
    """
    cbz_path = folder_path.with_suffix(".cbz")

    try:
        with zipfile.ZipFile(cbz_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in folder_path.rglob("*"):
                zf.write(file, arcname=file.relative_to(folder_path))

        shutil.rmtree(folder_path)
        logger.info(f"📦 Comprimido: {cbz_path.name}")
        return True
    except Exception as e:
        logger.error(f"❌ Error comprimiendo {folder_path.name}: {e}")
        return False

def main():
    # Asegurar que los directorios existen
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1. Procesar PDFs
    pdf_files = get_files(INPUT_DIR, "*.pdf")
    if not pdf_files:
        logger.info("No se encontraron archivos PDF para procesar.")

    for pdf in pdf_files:
        # Pipeline atómico por archivo
        temp_folder = pdf_to_images(pdf, OUTPUT_DIR)
        if temp_folder:
            success = compress_to_cbz(temp_folder)
            if success:
                pdf.unlink()  # Solo borramos el original si todo salió bien

if __name__ == "__main__":
    main()
