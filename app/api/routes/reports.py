from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import HistoricReportResponse, MonthlyReportResponse
from app.core.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.services.report_service import get_historic_report, get_user_monthly_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReportResponse)
def monthly_report(
    mes: int = None,
    ano: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if mes is None or ano is None:
        today = datetime.now()
        mes = today.month
        ano = today.year
    return get_user_monthly_report(current_user.id, mes, ano, db)


@router.get("/historic", response_model=HistoricReportResponse)
def historic_report(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reports = get_historic_report(current_user.id, months, db)
    return {"reportes": reports}
