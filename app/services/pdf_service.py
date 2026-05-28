import hashlib
from io import BytesIO

import pikepdf
import pdfplumber


def generate_pdf_hash(pdf_bytes: bytes) -> str:
    return hashlib.sha256(pdf_bytes).hexdigest()


def unlock_pdf(pdf_bytes: bytes, password: str) -> bytes:
    try:
        with pikepdf.open(BytesIO(pdf_bytes), password=password) as pdf:
            output = BytesIO()
            pdf.save(output)
            return output.getvalue()
    except pikepdf.PasswordError:
        raise ValueError("Contraseña incorrecta o inválida")
    except Exception as e:
        raise ValueError(f"Error al abrir el PDF: {e}")


def extract_pdf_content(pdf_bytes: bytes, password: str = "") -> dict:
    try:
        if password:
            try:
                with pikepdf.open(BytesIO(pdf_bytes), password=password) as pdf:
                    decrypted = BytesIO()
                    pdf.save(decrypted)
                    decrypted.seek(0)
                    clean_bytes = decrypted.read()
            except pikepdf.PasswordError:
                raise ValueError("Contraseña incorrecta o inválida")
        else:
            clean_bytes = pdf_bytes

        with pdfplumber.open(BytesIO(clean_bytes)) as pdf:
            tables = []
            all_text = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
                all_text.append(page.extract_text() or "")
            return {"tables": tables, "text": "\n".join(all_text), "error": None}
    except Exception as e:
        return {"tables": [], "text": "", "error": str(e)}
