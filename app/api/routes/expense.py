from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.api.schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    ExpenseFixedMonthlyCreate, ExpenseFixedMonthlyResponse,
)
from app.core.deps import get_current_user
from app.db.models import Expense, ExpenseFixedMonthly, User
from app.db.session import get_db

router = APIRouter(prefix="/api/expense", tags=["expense"])


# ── GASTOS DIARIOS ──────────────────────────────────────────

@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = Expense(user_id=current_user.id, **expense_data.dict())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=list[ExpenseResponse])
def list_expense(
    mes: int = Query(None),
    ano: int = Query(None),
    bucket: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Expense).filter(Expense.user_id == current_user.id)

    if mes and ano:
        start = date(ano, mes, 1)
        end = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
        query = query.filter(Expense.date >= start, Expense.date < end)

    if bucket:
        query = query.filter(Expense.bucket == bucket)

    return query.order_by(Expense.date.desc()).all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    for key, value in expense_data.dict(exclude_unset=True).items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    db.delete(expense)
    db.commit()
    return {"detail": "Gasto eliminado"}


# ── GASTOS FIJOS MENSUALES ──────────────────────────────────

@router.post("/fixed/", response_model=ExpenseFixedMonthlyResponse)
def create_fixed_expense(
    expense_data: ExpenseFixedMonthlyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = ExpenseFixedMonthly(user_id=current_user.id, **expense_data.dict())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/fixed/", response_model=list[ExpenseFixedMonthlyResponse])
def list_fixed_expense(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(ExpenseFixedMonthly).filter(
        ExpenseFixedMonthly.user_id == current_user.id,
        ExpenseFixedMonthly.is_active == True,
    ).all()


@router.get("/fixed/{expense_id}", response_model=ExpenseFixedMonthlyResponse)
def get_fixed_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.query(ExpenseFixedMonthly).filter(
        ExpenseFixedMonthly.id == expense_id,
        ExpenseFixedMonthly.user_id == current_user.id,
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto fijo no encontrado")
    return expense


@router.put("/fixed/{expense_id}", response_model=ExpenseFixedMonthlyResponse)
def update_fixed_expense(
    expense_id: int,
    expense_data: ExpenseFixedMonthlyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.query(ExpenseFixedMonthly).filter(
        ExpenseFixedMonthly.id == expense_id,
        ExpenseFixedMonthly.user_id == current_user.id,
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto fijo no encontrado")

    for key, value in expense_data.dict(exclude_unset=True).items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/fixed/{expense_id}")
def delete_fixed_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.query(ExpenseFixedMonthly).filter(
        ExpenseFixedMonthly.id == expense_id,
        ExpenseFixedMonthly.user_id == current_user.id,
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto fijo no encontrado")

    db.delete(expense)
    db.commit()
    return {"detail": "Gasto fijo eliminado"}
