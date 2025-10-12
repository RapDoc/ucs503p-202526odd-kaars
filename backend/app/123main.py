from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import json

app = FastAPI()

@app.post("/extract")
async def extract_data(file: UploadFile = File(...)):
    # Check if it’s a PDF
    if not file.filename.endswith(".pdf"):
        return JSONResponse(
            content={"error": "Please upload a PDF file."},
            status_code=400
        )

    # Read the uploaded file
    contents = await file.read()

    # Parse PDF
    try:
        from io import BytesIO
        pdf = PdfReader(BytesIO(contents))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to read PDF: {str(e)}"},
            status_code=500
        )

    # Convert text to structured JSON (you’ll customize this part)
    # For example: split text by lines
    data = []
    for line in text.split("\n"):
        if line.strip():
            data.append({"line": line.strip()})

    return JSONResponse(content=data)
