import hashlib
from io import BytesIO

import pdfplumber
from pypdf import PdfReader


def generate_pdf_hash(pdf_bytes: bytes) -> str:
    return hashlib.sha256(pdf_bytes).hexdigest()


def unlock_pdf(pdf_bytes: bytes, password: str) -> bytes:
    reader = PdfReader(BytesIO(pdf_bytes))
    if reader.is_encrypted:
        result = reader.decrypt(password)
        if result == 0:
            raise ValueError("Contraseña incorrecta o inválida")
    return pdf_bytes


def extract_pdf_content(pdf_bytes: bytes, password: str = "") -> dict:
    try:
        kwargs = {"password": password} if password else {}
        with pdfplumber.open(BytesIO(pdf_bytes), **kwargs) as pdf:
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
            return {"tables": tables, "error": None}
    except Exception as e:
        return {"tables": [], "error": str(e)}
