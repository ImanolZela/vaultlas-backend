from datetime import date
from sqlalchemy.orm import Session
from app.db.models import MonthlyBudget


def get_annual_summary(user_id: int, year: int, db: Session) -> dict:
    months_data = []
    total_income = 0.0
    total_expenses = 0.0
    total_savings = 0.0

    for mes in range(1, 13):
        budget = db.query(MonthlyBudget).filter(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.month == date(year, mes, 1),
        ).first()

        if budget and budget.status == "closed":
            income = budget.total_income
            expenses = (
                budget.actual_needs +
                budget.actual_wants +
                budget.actual_savings +
                budget.actual_debt
            )
            net = income - expenses

            total_income += income
            total_expenses += expenses
            total_savings += budget.actual_savings

            months_data.append({
                "month": date(year, mes, 1).isoformat(),
                "total_income": income,
                "total_needs": budget.actual_needs,
                "total_wants": budget.actual_wants,
                "total_savings": budget.actual_savings,
                "total_debt": budget.actual_debt,
                "net": net,
            })

    return {
        "year": year,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_savings": total_savings,
        "net": total_income - total_expenses,
        "months": months_data,
    }
