import base64

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
    broker_connection_retry_on_startup=True,
)


@celery_app.task(name="process_pdf")
def process_pdf(document_id: int, pdf_bytes_b64: str, password: str) -> dict:
    from app.db.session import SessionLocal
    from app.db.models import Document, Movement
    from app.services.pdf_service import unlock_pdf, extract_pdf_content
    from app.services.bcp_parser import parse_bcp_movements, detect_periodo

    db = SessionLocal()
    doc = None
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return {"status": "error", "message": "Document not found"}

        pdf_bytes = base64.b64decode(pdf_bytes_b64)
        unlock_pdf(pdf_bytes, password)
        extraction = extract_pdf_content(pdf_bytes, password)

        if extraction["error"]:
            raise ValueError(f"Error extrayendo PDF: {extraction['error']}")

        movements_data = parse_bcp_movements(extraction["tables"])
        periodo = detect_periodo(movements_data)

        for m in movements_data:
            movement = Movement(
                document_id=document_id,
                fecha=m["fecha"],
                descripcion=m["descripcion"],
                codigo_operacion=m.get("codigo_operacion"),
                monto=m["monto"],
                tipo=m["tipo"],
                confirmed=False,
            )
            db.add(movement)

        doc.status = "done"
        if periodo:
            doc.periodo = periodo
        db.commit()

        return {"status": "done", "movements_count": len(movements_data)}

    except Exception as e:
        if doc:
            doc.status = "error"
            db.commit()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
