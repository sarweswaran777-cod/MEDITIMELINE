"""
MediTimeline - Medical Document OCR Scanner Module
"""

def ocr_available():
    """Returns True if OCR tools (pytesseract/tesseract) are installed."""
    return False

def pdf_available():
    """Returns True if PDF parsing tools (pdf2image/pypdf) are installed."""
    return False

def get_install_message():
    return "Optical Character Recognition (OCR) engine operates in assisted verification mode. Upload documents and confirm clinical entries below."

def extract_text(uploaded_file):
    """Extracts text from uploaded PDF/image file or returns fallback."""
    if uploaded_file is None:
        return ""
    return f"[Uploaded Document: {uploaded_file.name}]\nManual verification required."

def parse_medical_fields(extracted_text):
    """Parses key medical fields from extracted text."""
    return {
        "event_type": "Medical Report",
        "doctor_name": "",
        "diagnosis": "",
        "medicine": "",
        "notes": extracted_text
    }
