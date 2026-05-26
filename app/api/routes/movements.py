from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ConfirmMovementRequest, MovementListResponse
from app.core.deps import get_current_user
from app.db.models import Document, Movement, User
from app.db.session import get_db

router = APIRouter(prefix="/api/movements", tags=["movements"])


@router.get("/document/{document_id}", response_model=MovementListResponse)
def list_movements(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    query = db.query(Movement).filter(Movement.document_id == document_id)
    total = query.count()
    movements = query.offset(skip).limit(limit).all()
    return {"movements": movements, "total": total}


@router.post("/confirm")
def confirm_movements(
    request: ConfirmMovementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    movements = db.query(Movement).filter(Movement.id.in_(request.movement_ids)).all()

    for mov in movements:
        doc = db.query(Document).filter(
            Document.id == mov.document_id,
            Document.user_id == current_user.id,
        ).first()
        if not doc:
            raise HTTPException(status_code=403, detail="No autorizado")

    for mov in movements:
        mov.confirmed = True
    db.commit()

    return {"message": f"{len(movements)} movimientos confirmados"}


@router.post("/confirm-all/{document_id}")
def confirm_all_movements(
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

    count = db.query(Movement).filter(
        Movement.document_id == document_id
    ).update({"confirmed": True})
    db.commit()

    return {"message": "Todos los movimientos confirmados", "count": count}
