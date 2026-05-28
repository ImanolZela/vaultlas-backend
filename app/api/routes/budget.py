from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.api.schemas import MonthlyBudgetCreate, MonthlyBudgetUpdate, MonthlyBudgetResponse
from app.core.deps import get_current_user
from app.db.models import MonthlyBudget, User
from app.db.session import get_db
from app.services.budget_service import (
    calculate_budget_amounts,
    calculate_monthly_income,
    update_actual_spending,
)

router = APIRouter(prefix="/api/budget", tags=["budget"])


@router.post("/", response_model=MonthlyBudgetResponse)
def create_or_update_budget(
    budget_data: MonthlyBudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.user_id == current_user.id,
        MonthlyBudget.month == budget_data.month,
    ).first()

    if budget:
        for key, value in budget_data.dict().items():
            setattr(budget, key, value)
    else:
        budget = MonthlyBudget(user_id=current_user.id, **budget_data.dict())
        db.add(budget)

    budget.total_income = calculate_monthly_income(
        current_user.id, budget_data.month.month, budget_data.month.year, db
    )
    calculate_budget_amounts(budget)
    update_actual_spending(budget, db)
    budget.status = "active"

    db.commit()
    db.refresh(budget)
    return budget


@router.get("/", response_model=list[MonthlyBudgetResponse])
def list_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(MonthlyBudget).filter(
        MonthlyBudget.user_id == current_user.id,
    ).order_by(MonthlyBudget.month.desc()).all()


@router.get("/{mes}/{ano}", response_model=MonthlyBudgetResponse)
def get_budget(
    mes: int,
    ano: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.user_id == current_user.id,
        MonthlyBudget.month == date(ano, mes, 1),
    ).first()

    if not budget:
        budget = MonthlyBudget(
            user_id=current_user.id,
            month=date(ano, mes, 1),
            total_income=0,
            status="draft",
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
    else:
        update_actual_spending(budget, db)
        db.commit()

    return budget


@router.put("/{mes}/{ano}", response_model=MonthlyBudgetResponse)
def update_budget(
    mes: int,
    ano: int,
    budget_data: MonthlyBudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.user_id == current_user.id,
        MonthlyBudget.month == date(ano, mes, 1),
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

    for key, value in budget_data.dict(exclude_unset=True).items():
        setattr(budget, key, value)

    calculate_budget_amounts(budget)
    update_actual_spending(budget, db)

    db.commit()
    db.refresh(budget)
    return budget
