from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.api.schemas import IncomeCreate, IncomeUpdate, IncomeResponse
from app.core.deps import get_current_user
from app.db.models import Income, User
from app.db.session import get_db

router = APIRouter(prefix="/api/income", tags=["income"])


@router.post("/", response_model=IncomeResponse)
def create_income(
    income_data: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = Income(user_id=current_user.id, **income_data.dict())
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@router.get("/", response_model=list[IncomeResponse])
def list_income(
    mes: int = Query(None),
    ano: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Income).filter(Income.user_id == current_user.id)

    if mes and ano:
        start = date(ano, mes, 1)
        end = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
        query = query.filter(Income.date >= start, Income.date < end)

    return query.order_by(Income.date.desc()).all()


@router.get("/{income_id}", response_model=IncomeResponse)
def get_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    if not income:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    return income


@router.put("/{income_id}", response_model=IncomeResponse)
def update_income(
    income_id: int,
    income_data: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    if not income:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    for key, value in income_data.dict(exclude_unset=True).items():
        setattr(income, key, value)

    db.commit()
    db.refresh(income)
    return income


@router.delete("/{income_id}")
def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    if not income:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    db.delete(income)
    db.commit()
    return {"detail": "Ingreso eliminado"}
