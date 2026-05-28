from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from app.api.schemas import GoalCreate, GoalResponse
from app.core.deps import get_current_user
from app.db.models import Goal, User
from app.db.session import get_db

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.post("/", response_model=GoalResponse)
def create_or_update_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.mes == goal_data.mes,
        Goal.ano == goal_data.ano,
    ).first()

    if goal:
        goal.meta_ingresos = goal_data.meta_ingresos
    else:
        goal = Goal(
            user_id=current_user.id,
            mes=goal_data.mes,
            ano=goal_data.ano,
            meta_ingresos=goal_data.meta_ingresos,
        )
        db.add(goal)

    db.commit()
    db.refresh(goal)
    return goal


@router.get("/{mes}/{ano}", response_model=Optional[GoalResponse])
def get_goal(
    mes: int,
    ano: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.mes == mes,
        Goal.ano == ano,
    ).first()
