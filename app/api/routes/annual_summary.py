from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.services.annual_service import get_annual_summary

router = APIRouter(prefix="/api/annual", tags=["annual"])


@router.get("/{year}")
def get_annual_summary_endpoint(
    year: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_annual_summary(current_user.id, year, db)
