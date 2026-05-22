import argparse
import logging
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF
from PIL import Image
from tqdm import tqdm

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── Configuración por defecto ───────────────────────────────────────────────
DEFAULT_INPUT_DIR = Path("todo")
DEFAULT_OUTPUT_DIR = Path("done")
DEFAULT_DPI = 200
DEFAULT_IMG_QUALITY = 90
DEFAULT_MAX_WORKERS = 4


# ─── Funciones auxiliares ────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convierte archivos PDF a CBZ (imágenes comprimidas)."
    )
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Directorio de entrada con PDFs (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directorio de salida para los CBZ (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help=f"Resolución DPI para la conversión (default: {DEFAULT_DPI})",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_IMG_QUALITY,
        help=f"Calidad JPEG 1-100 (default: {DEFAULT_IMG_QUALITY})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_MAX_WORKERS,
        help=f"Número de workers paralelos (default: {DEFAULT_MAX_WORKERS})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribir archivos CBZ existentes sin preguntar",
    )
    parser.add_argument(
        "--keep-pdf",
        action="store_true",
        help="No eliminar el PDF original después de la conversión",
    )
    return parser.parse_args()


def get_files(directory: Path, pattern: str = "*") -> List[Path]:
    """
    Obtiene una lista de archivos en un directorio que coinciden con un patrón.
    """
    if not directory.exists():
        logger.warning(f"El directorio no existe: {directory}")
        return []
    return [f for f in sorted(directory.glob(pattern)) if f.is_file()]


def check_output_exists(output_dir: Path, pdf_name: str, force: bool) -> bool:
    """Verifica si el .cbz ya existe y maneja la decisión de sobrescribir."""
    cbz_path = output_dir / f"{pdf_name}.cbz"
    if cbz_path.exists():
        if force:
            return True  # sobrescribir
        logger.warning(f"⚠️  {cbz_path.name} ya existe. Usa --force para sobrescribir.")
        return False
    return True


def pdf_to_images(
    pdf_path: Path,
    output_base_folder: Path,
    dpi: int,
    quality: int,
) -> Optional[Path]:
    """
    Convierte cada página de un PDF en una imagen JPEG.
    """
    try:
        # Crear subcarpeta para las imágenes del PDF
        target_folder = output_base_folder / pdf_path.stem
        target_folder.mkdir(parents=True, exist_ok=True)

        with fitz.open(pdf_path) as doc:
            if len(doc) == 0:
                logger.warning(f"⚠️  El PDF {pdf_path.name} está vacío.")
                return None

            if doc.is_encrypted:
                logger.error(f"🔒 {pdf_path.name} está protegido con contraseña. Se omite.")
                shutil.rmtree(target_folder)
                return None

            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=dpi)

                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

                if pix.alpha:
                    img = img.convert("RGB")

                image_path = target_folder / f"{i + 1:03d}.jpg"
                img.save(image_path, format="JPEG", quality=quality)

            logger.info(f"🖼️  Convertido: {pdf_path.name} ({len(doc)} páginas)")
            return target_folder

    except fitz.FileDataError:
        logger.error(f"❌ {pdf_path.name} está corrupto o no es un PDF válido.")
        if 'target_folder' in locals() and target_folder.exists():
            shutil.rmtree(target_folder)
        return None
    except Exception as e:
        logger.error(f"❌ Error procesando {pdf_path.name}: {e}")
        if 'target_folder' in locals() and target_folder.exists():
            shutil.rmtree(target_folder)
        return None


def compress_to_cbz(folder_path: Path, output_dir: Path) -> bool:
    """
    Comprime el contenido de una carpeta en un archivo .cbz y elimina la carpeta.
    """
    cbz_path = output_dir / f"{folder_path.stem}.cbz"

    try:
        with zipfile.ZipFile(cbz_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in sorted(folder_path.rglob("*")):
                zf.write(file, arcname=file.relative_to(folder_path))

        shutil.rmtree(folder_path)
        logger.info(f"📦 Comprimido: {cbz_path.name}")
        return True
    except Exception as e:
        logger.error(f"❌ Error comprimiendo {folder_path.name}: {e}")
        return False


def process_single_pdf(
    pdf: Path,
    args: argparse.Namespace,
) -> bool:
    """
    Procesa un PDF individual: convierte a imágenes -> comprime a CBZ -> limpia.
    Retorna True si todo salió bien.
    """
    # Verificar si ya existe el .cbz
    if not check_output_exists(args.output, pdf.stem, args.force):
        return False

    temp_folder = pdf_to_images(pdf, args.output, args.dpi, args.quality)
    if temp_folder is None:
        return False

    success = compress_to_cbz(temp_folder, args.output)
    if success and not args.keep_pdf:
        pdf.unlink()  # Solo borramos el original si todo salió bien

    return success


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # Asegurar que los directorios existen
    args.input.mkdir(exist_ok=True)
    args.output.mkdir(exist_ok=True)

    # Obtener PDFs
    pdf_files = get_files(args.input, "*.pdf")
    if not pdf_files:
        logger.info("No se encontraron archivos PDF para procesar.")
        return

    logger.info(
        f"Procesando {len(pdf_files)} PDFs "
        f"(workers={args.workers}, dpi={args.dpi}, quality={args.quality})"
    )

    if args.workers > 1:
        # ── Modo paralelo ──
        ok = 0
        fail = 0
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            fut_map = {
                executor.submit(process_single_pdf, pdf, args): pdf
                for pdf in pdf_files
            }
            with tqdm(total=len(pdf_files), unit="pdf", desc="Procesando") as pbar:
                for future in as_completed(fut_map):
                    pdf = fut_map[future]
                    try:
                        if future.result():
                            ok += 1
                        else:
                            fail += 1
                    except Exception as e:
                        logger.error(f"❌ Error inesperado en {pdf.name}: {e}")
                        fail += 1
                    pbar.set_postfix(ok=ok, fail=fail)
                    pbar.update(1)

        logger.info(f"✅ {ok} convertidos, ❌ {fail} fallos")
    else:
        # ── Modo secuencial (con barra de progreso) ──
        ok = 0
        fail = 0
        for pdf in tqdm(pdf_files, unit="pdf", desc="Procesando"):
            if process_single_pdf(pdf, args):
                ok += 1
            else:
                fail += 1

        logger.info(f"✅ {ok} convertidos, ❌ {fail} fallos")


if __name__ == "__main__":
    main()
