from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "vaultlas",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="process_pdf")
def process_pdf(document_id: int, pdf_bytes: bytes, password: str) -> dict:
    """Process a BCP PDF statement and extract movements."""
    from sqlalchemy.orm import Session
    from app.db.session import SessionLocal
    from app.db.models import Document, Movement
    import pdfplumber
    import pypdf
    import io

    db: Session = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"status": "error", "message": "Document not found"}

        pdf_stream = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(pdf_stream)
        if reader.is_encrypted:
            reader.decrypt(password)

        pdf_stream.seek(0)
        with pdfplumber.open(pdf_stream, password=password) as pdf:
            movements = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row and len(row) >= 5:
                            fecha = row[0]
                            descripcion = row[1]
                            codigo = row[2] if len(row) > 2 else None
                            cargo = row[3] if len(row) > 3 else None
                            abono = row[4] if len(row) > 4 else None

                            if not fecha or not descripcion:
                                continue

                            try:
                                if abono and abono.strip():
                                    monto = float(abono.replace(",", "").replace(" ", ""))
                                    tipo = "ingreso"
                                elif cargo and cargo.strip():
                                    monto = float(cargo.replace(",", "").replace(" ", ""))
                                    tipo = "egreso"
                                else:
                                    continue
                            except (ValueError, AttributeError):
                                continue

                            movements.append(Movement(
                                document_id=document_id,
                                fecha=str(fecha).strip(),
                                descripcion=str(descripcion).strip(),
                                codigo_operacion=str(codigo).strip() if codigo else None,
                                monto=monto,
                                tipo=tipo,
                                confirmed=False,
                            ))

        for m in movements:
            db.add(m)

        document.status = "done"
        db.commit()
        return {"status": "done", "movements_count": len(movements)}

    except Exception as e:
        if document:
            document.status = "error"
            db.commit()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
