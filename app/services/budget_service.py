from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import MonthlyBudget, Expense, ExpenseFixedMonthly, Income


def calculate_budget_amounts(budget: MonthlyBudget) -> None:
    if budget.total_income <= 0:
        budget.budgeted_needs = 0
        budget.budgeted_wants = 0
        budget.budgeted_savings = 0
        return
    budget.budgeted_needs = budget.total_income * (budget.needs_percent / 100)
    budget.budgeted_wants = budget.total_income * (budget.wants_percent / 100)
    budget.budgeted_savings = budget.total_income * (budget.savings_percent / 100)


def _month_range(month: date):
    if month.month == 12:
        return month, date(month.year + 1, 1, 1)
    return month, date(month.year, month.month + 1, 1)


def update_actual_spending(budget: MonthlyBudget, db: Session) -> None:
    start, end = _month_range(budget.month)

    expenses = db.query(Expense).filter(
        Expense.user_id == budget.user_id,
        Expense.date >= start,
        Expense.date < end,
    ).all()

    needs = sum(e.amount for e in expenses if e.bucket == "needs")
    wants = sum(e.amount for e in expenses if e.bucket == "wants")
    savings = sum(e.amount for e in expenses if e.bucket == "savings")
    debt = sum(e.amount for e in expenses if e.bucket == "debt")

    fixed = db.query(ExpenseFixedMonthly).filter(
        ExpenseFixedMonthly.user_id == budget.user_id,
        ExpenseFixedMonthly.is_active == True,
        ExpenseFixedMonthly.start_date <= start,
    ).all()

    for f in fixed:
        if f.end_date is None or f.end_date >= start:
            if f.bucket == "needs":
                needs += f.amount
            elif f.bucket == "wants":
                wants += f.amount
            elif f.bucket == "savings":
                savings += f.amount
            elif f.bucket == "debt":
                debt += f.amount

    budget.actual_needs = needs
    budget.actual_wants = wants
    budget.actual_savings = savings
    budget.actual_debt = debt


def calculate_monthly_income(user_id: int, mes: int, ano: int, db: Session) -> float:
    start = date(ano, mes, 1)
    end = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)

    incomes = db.query(Income).filter(
        Income.user_id == user_id,
        Income.date >= start,
        Income.date < end,
    ).all()

    return sum(i.amount for i in incomes)
