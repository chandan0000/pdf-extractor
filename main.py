import logging
import shutil
import tempfile
import os

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import pdfplumber
import pytesseract
from pdf2image import convert_from_path


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Text Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_text_from_page(page, file_path, page_number):
    text = page.extract_text() or ""
    if len(text.strip()) < 50:
         
        try:
            
            
            images = convert_from_path(
                file_path, 
                first_page=page_number, 
                last_page=page_number
            )
            
            if images:
                ocr_text = pytesseract.image_to_string(images[0])
                if ocr_text.strip():
                    text += f"\n\n[--- OCR Result (Image Text) ---]\n{ocr_text}"
                else:
                     text += "\n[OCR executed but found no text]"

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Page {page_number}: OCR failed: {error_msg}")
            
            if "poppler" in error_msg.lower() or "pdftoppm" in error_msg.lower() or "not found" in error_msg.lower():
                text += "\n\n[ERROR: OCR FAILED]\n" \
                        "System is missing 'Poppler'.\n" \
                        "Windows: Download poppler, extract, and add 'bin' folder to System PATH.\n" \
                        "Mac: brew install poppler\n" \
                        "Linux: sudo apt install poppler-utils"
            elif "tesseract" in error_msg.lower():
                text += "\n\n[ERROR: OCR FAILED]\n" \
                        "System is missing 'Tesseract'.\n" \
                        "Windows: Download Tesseract installer and install.\n" \
                        "Mac: brew install tesseract\n" \
                        "Linux: sudo apt install tesseract-ocr"
            else:
                text += f"\n\n[OCR Error]: {error_msg}"

    return text

@app.post("/extract-text")
async def extract_text_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .pdf allowed.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        try:
            shutil.copyfileobj(file.file, temp_pdf)
            temp_path = temp_pdf.name
            logger.info(f"Processing file: {file.filename}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    extracted_data = []
    
    try:
        with pdfplumber.open(temp_path) as pdf:
            total_pages = len(pdf.pages)
            
            if total_pages == 0:
                 raise ValueError("PDF has no pages.")

            for i, page in enumerate(pdf.pages):
                page_num = i + 1
                
                page_text = extract_text_from_page(page, temp_path, page_num)
                
                extracted_data.append({
                    "page": page_num,
                    "text": page_text.strip() if page_text else "[Blank Page]"
                })

        return JSONResponse(content={
            "filename": file.filename,
            "total_pages": total_pages,
            "data": extracted_data
        })

    except Exception as e:
        logger.error(f"Critical error processing PDF: {e}")
        return JSONResponse(
            status_code=422, 
            content={"detail": "Corrupt PDF or Parsing Error. Ensure it is a valid PDF file."}
        )
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
@app.get("/")
async def root():
    return {"message": "PDF Extractor is running"}
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    print("--- STARTING PDF EXTRACTOR SERVER ---")
    uvicorn.run(app, host="0.0.0.0", port=8000)
