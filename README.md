# PDF Text Extractor API

A small FastAPI service that extracts text from PDFs using `pdfplumber` and falls back to OCR via `pdf2image` + `pytesseract` when needed.

## Features

- Extracts selectable PDF text with `pdfplumber`.
- If a page has little or no text, converts that page to an image and runs OCR using Tesseract.
- Returns JSON with per-page extracted text and OCR diagnostics when applicable.

## Requirements

- Python 3.8+
-- Python packages
  - Preferred: install the pinned versions from `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

  - Or install core packages individually:
    - fastapi
    - uvicorn[standard]
    - pdfplumber
    - pdf2image
    - pytesseract

Recommended to install into a virtual environment.

### System packages

- Poppler (provides `pdftoppm`/`pdftocairo`) — required by `pdf2image` on most systems.
  - Debian/Ubuntu: `sudo apt install poppler-utils`
  - macOS: `brew install poppler`
  - Windows: Download Poppler for Windows and add the `bin` folder to PATH.

- Tesseract OCR — required for OCR fallback.
  - Debian/Ubuntu: `sudo apt install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: Install Tesseract and add to PATH.

## Quick install

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn[standard] pdfplumber pdf2image pytesseract
```

If you prefer a `requirements.txt`, you can generate one after installing packages.

## Run locally

Start the FastAPI server with Uvicorn (project root):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The service exposes a POST endpoint to extract text:

- POST /extract-text
  - Form field: `file` — the PDF file to upload (multipart/form-data)

Example `curl` upload:

```bash
curl -X POST "http://localhost:8000/extract-text" -F "file=@/path/to/document.pdf" 
```

Example successful response shape:

```json
{
  "filename": "document.pdf",
  "total_pages": 3,
  "data": [
    {"page": 1, "text": "..."},
    {"page": 2, "text": "[--- OCR Result (Image Text) ---]\n..."},
    {"page": 3, "text": "[Blank Page]"}
  ]
}
```
