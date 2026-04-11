import fitz # PyMuPDF
import os
from PIL import Image

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

if __name__ == "__main__":
    files = get_files(directory="todo")
    for f in files:
        if f.endswith(".pdf"):
            print(f)
            pdf_to_image(f)
            break
