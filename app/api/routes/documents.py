import base64

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.schemas import DocumentListResponse, DocumentResponse
from app.core.deps import get_current_user
from app.db.models import Document, User
from app.db.session import get_db
from app.services.pdf_service import generate_pdf_hash
from app.worker.tasks import process_pdf

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    password: str = Form(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    pdf_bytes = await file.read()
    pdf_hash = generate_pdf_hash(pdf_bytes)

    existing = db.query(Document).filter(
        Document.pdf_hash == pdf_hash,
        Document.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Este estado de cuenta ya fue procesado",
        )

    doc = Document(
        user_id=current_user.id,
        pdf_hash=pdf_hash,
        filename=file.filename,
        bank="BCP",
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    pdf_b64 = base64.b64encode(pdf_bytes).decode()
    process_pdf.delay(doc.id, pdf_b64, password)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "message": "PDF encolado para procesamiento",
    }


@router.get("", response_model=DocumentListResponse)
def list_documents(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Document).filter(Document.user_id == current_user.id)
    total = query.count()
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return {"documents": documents, "total": total}


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
