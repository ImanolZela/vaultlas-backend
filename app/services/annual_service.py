from datetime import date
from sqlalchemy.orm import Session
from app.db.models import MonthlyBudget


def get_annual_summary(user_id: int, year: int, db: Session) -> dict:
    months_data = []
    total_income = 0.0
    total_expenses = 0.0
    total_saved = 0.0

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
            saved = income - expenses

            total_income += income
            total_expenses += expenses
            total_saved += saved

            months_data.append({
                "month": mes,
                "income": income,
                "expenses": expenses,
                "saved": saved,
                "savings_rate": round(saved / income * 100, 1) if income > 0 else 0,
                "needs": budget.actual_needs,
                "wants": budget.actual_wants,
                "savings_bucket": budget.actual_savings,
                "debt": budget.actual_debt,
            })

    return {
        "year": year,
        "months_completed": len(months_data),
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_saved": total_saved,
        "annual_savings_rate": round(total_saved / total_income * 100, 1) if total_income > 0 else 0,
        "months": months_data,
    }
