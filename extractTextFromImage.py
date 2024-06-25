import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

# Ruta al ejecutable de Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ajusta esta ruta según tu instalación

# Función para extraer texto de un PDF
def extract_text_from_pdf(pdf_path):
    # Abrir el archivo PDF
    document = fitz.open(pdf_path)
    text = ""

    # Recorrer cada página
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        pix = page.get_pixmap()
        
        # Convertir la página a imagen
        img = Image.open(io.BytesIO(pix.tobytes()))
        
        # Extraer texto de la imagen
        text += pytesseract.image_to_string(img, lang='spa')  # Cambia 'eng' a 'spa' para español

    return text

# Función para procesar todos los PDFs en una carpeta
def process_pdfs(input_folder, output_folder):
    # Crear la carpeta de destino si no existe
    os.makedirs(output_folder, exist_ok=True)

    # Recorrer todos los archivos en la carpeta de origen
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            extracted_text = extract_text_from_pdf(pdf_path)
            
            # Guardar el texto extraído en un archivo con el mismo nombre
            text_filename = os.path.splitext(filename)[0] + '.txt'
            text_path = os.path.join(output_folder, text_filename)
            with open(text_path, 'w', encoding='utf-8') as text_file:
                text_file.write(extracted_text)
            print(f"Texto extraído y guardado en '{text_path}'")

# Carpetas de origen y destino
input_folder = r'backend\Data\Gestión de calidad\pdf\Only Images'
output_folder = r'backend\Data\Gestión de calidad\text'

# Procesar los PDFs
process_pdfs(input_folder, output_folder)
