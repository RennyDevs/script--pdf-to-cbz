from PIL import Image
from typing import List
import fitz # PyMuPDF
import os
import shutil
import zipfile

def get_files(directory, recursive=False):
    results = []
    if recursive:
        for root, dirs, files in os.walk(directory):
            for f in files:
                results.append(os.path.join(root, f))
    else:
        try:
            for name in os.listdir(directory):
                path = os.path.join(directory, name)
                if os.path.isfile(path):
                    results.append(path)
        except (FileNotFoundError, PermissionError) as e:
            print(e)
    return results


def list_folders(path: str = '.', recursive: bool = False, full_path: bool = True, exclude: List[str] = None) -> List[str]:
    """
    Devuelve una lista de carpetas dentro de `path`.

    Parámetros:
    - path: ruta a inspeccionar (por defecto '.').
    - recursive: si True recorre recursivamente y devuelve todas las subcarpetas.
    - full_path: si True devuelve rutas absolutas, si False nombres relativos respecto a `path`.
    - exclude: lista opcional de nombres de carpetas a excluir (comparación por nombre de carpeta).

    Retorna: lista de carpetas (vacía si no hay).
    Lanza FileNotFoundError si `path` no existe o no es carpeta.
    """
    if exclude is None:
        exclude = []

    path = os.path.abspath(path)
    if not os.path.isdir(path):
        raise FileNotFoundError(f"No existe la carpeta: {path}")

    folders = []
    if recursive:
        for root, dirs, _ in os.walk(path):
            # dirs es modificable; filtrar en sitio para evitar entrar en exclusiones
            dirs[:] = [d for d in dirs if d not in exclude]
            for d in dirs:
                p = os.path.join(root, d)
                folders.append(p if full_path else os.path.relpath(p, path))
    else:
        for entry in os.listdir(path):
            p = os.path.join(path, entry)
            if os.path.isdir(p) and entry not in exclude:
                folders.append(p if full_path else entry)

    return folders


def pdf_to_image(pdf_path):
    # Abrir el PDF
    doc = fitz.open(pdf_path)
    # Crear carpeta con el nombre del PDF (sin extensión)
    output_folder = 'done\\' + os.path.splitext(os.path.basename(pdf_path))[0]
    os.makedirs(output_folder, exist_ok=True)

    # Recorrer páginas y renderizar
    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        pix = pagina.get_pixmap(dpi=200) # dpi controla la calidad max:300
        nombre = f"{num_pagina+1}.jpg" #nombres ascendentes: 1.jpg, 2.jpg ...
        path = os.path.join(output_folder, nombre)

        if pix.alpha:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(path, format="JPEG", quality=90)

    print(f"✅ Se guardaron {len(doc)} imágenes en la carpeta: {output_folder}")

    doc.close()

    if os.path.isfile(pdf_path):
        os.remove(pdf_path)


def zip_folder(folder_path: str, zip_path: str, include_root: bool = False) -> None:
    """
    Comprime la carpeta `folder_path` en el archivo `zip_path`.

    Parámetros:
    - folder_path: ruta de la carpeta a comprimir.
    - zip_path: ruta del archivo .zip de salida (p. ej. "salida.zip").
    - include_root: si True, la carpeta raíz se incluye dentro del zip;
                    si False, se almacenan solo sus contenidos.

    Lanza FileNotFoundError si folder_path no existe.
    """
    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"No existe la carpeta: {folder_path}")

    mode = "w"
    with zipfile.ZipFile(zip_path, mode, compression=zipfile.ZIP_DEFLATED) as zf:
        base_len = len(os.path.dirname(folder_path)) + 1 if include_root else len(folder_path) + 1
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = full_path[base_len:]
                if include_root:
                    # cuando include_root=True queremos que el nombre dentro del zip
                    # comience con el nombre de la carpeta raíz
                    arcname = os.path.join(os.path.basename(folder_path), arcname)
                zf.write(full_path, arcname)

    shutil.rmtree(folder_path)


if __name__ == "__main__":

    files = get_files(directory="todo")
    for f in files:
        if f.endswith(".pdf"):
            pdf_to_image(f)

    files = list_folders(path="done")
    for f in files:
        zip_folder(f, f"{f}.cbz")
