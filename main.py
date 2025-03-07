import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from docx import Document
from PIL import Image
import easyocr
import os
import shutil

app = FastAPI()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file_name):
    pdf_document = fitz.open(pdf_file_name)
    pdf_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pdf_text += page.get_text()
    pdf_document.close()
    return pdf_text

# Function to extract text from DOCX
def extract_text_from_docx(docx_file_name):
    doc = Document(docx_file_name)
    doc_text = ""
    for para in doc.paragraphs:
        doc_text += para.text + "\n"
    return doc_text

# Function to extract text from image using EasyOCR
def extract_text_from_image(image_file_name):
    reader = easyocr.Reader(['en', 'it'])  # Add more languages as needed
    result = reader.readtext(image_file_name)
    image_text = ""
    for detection in result:
        image_text += detection[1] + "\n"
    return image_text

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # Save the uploaded file to a temporary location
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Determine the file type and extract text accordingly
    file_extension = os.path.splitext(temp_file_path)[1].lower()
    extracted_text = ""

    if file_extension == '.pdf':
        extracted_text = extract_text_from_pdf(temp_file_path)
    elif file_extension == '.docx':
        extracted_text = extract_text_from_docx(temp_file_path)
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        extracted_text = extract_text_from_image(temp_file_path)
    else:
        extracted_text = "Unsupported file type."

    # Clean up the temporary file
    os.remove(temp_file_path)

    return {"extracted_text": extracted_text}

@app.get("/")
async def main():
    content = """
    <html>
        <head>
            <title>File Upload</title>
        </head>
        <body>
            <h1>Upload a PDF, DOCX, or Image file</h1>
            <form action="/uploadfile/" enctype="multipart/form-data" method="post">
            <input name="file" type="file" accept=".pdf,.docx,.png,.jpg,.jpeg">
            <input type="submit">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=content)

# To run the app, use the command: uvicorn your_script_name:app --reload