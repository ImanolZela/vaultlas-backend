from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone

from app.api.schemas import (
    ReconciliationReportResponse,
    ReconciliationItemResponse,
    ReconciliationItemUpdate,
)
from app.core.deps import get_current_user
from app.db.models import (
    ReconciliationReport, ReconciliationItem,
    PdfMovement, Expense, Income, MonthlyBudget, User,
)
from app.db.session import get_db
from app.services.reconciliation_service import match_transactions, calculate_differences

router = APIRouter(prefix="/api/reconciliation", tags=["reconciliation"])


def _month_range(mes: int, ano: int):
    start = date(ano, mes, 1)
    end = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
    return start, end


@router.post("/{mes}/{ano}/start", response_model=ReconciliationReportResponse)
def start_reconciliation(
    mes: int,
    ano: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start, end = _month_range(mes, ano)

    manual_incomes = db.query(Income).filter(
        Income.user_id == current_user.id,
        Income.date >= start,
        Income.date < end,
    ).all()

    manual_expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start,
        Expense.date < end,
    ).all()

    pdf_movements = db.query(PdfMovement).filter(
        PdfMovement.user_id == current_user.id,
        PdfMovement.date >= start,
        PdfMovement.date < end,
    ).all()

    pdf_incomes = [m for m in pdf_movements if not m.is_debit]
    pdf_expenses = [m for m in pdf_movements if m.is_debit]

    diffs = calculate_differences(
        [{'amount': i.amount, 'date': i.date} for i in manual_incomes],
        [{'amount': e.amount, 'date': e.date} for e in manual_expenses],
        [{'amount': m.amount, 'date': m.date} for m in pdf_incomes],
        [{'amount': m.amount, 'date': m.date} for m in pdf_expenses],
    )

    unmatched = match_transactions(
        [{'amount': e.amount, 'date': e.date} for e in manual_expenses],
        [{'amount': m.amount, 'date': m.date, '_obj': m} for m in pdf_expenses],
    )

    existing = db.query(ReconciliationReport).filter(
        ReconciliationReport.user_id == current_user.id,
        ReconciliationReport.month == start,
    ).first()

    if existing:
        report = existing
        report.status = "in_progress"
        report.income_difference = diffs['income_difference']
        report.expense_difference = diffs['expense_difference']
        report.total_unmatched = len(unmatched)
        db.query(ReconciliationItem).filter(
            ReconciliationItem.report_id == report.id
        ).delete()
    else:
        report = ReconciliationReport(
            user_id=current_user.id,
            month=start,
            status="in_progress",
            total_unmatched=len(unmatched),
            income_difference=diffs['income_difference'],
            expense_difference=diffs['expense_difference'],
        )
        db.add(report)

    db.flush()

    for pdf_tx in unmatched:
        obj = pdf_tx.get('_obj')
        if obj:
            item = ReconciliationItem(
                report_id=report.id,
                user_id=current_user.id,
                pdf_date=obj.date,
                pdf_description=obj.description,
                pdf_amount=obj.amount,
                status="pending",
            )
            db.add(item)

    db.commit()
    db.refresh(report)

    return report


@router.get("/{mes}/{ano}", response_model=ReconciliationReportResponse)
def get_reconciliation_report(
    mes: int,
    ano: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start, _ = _month_range(mes, ano)
    report = db.query(ReconciliationReport).filter(
        ReconciliationReport.user_id == current_user.id,
        ReconciliationReport.month == start,
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report


@router.put("/item/{item_id}", response_model=ReconciliationItemResponse)
def update_reconciliation_item(
    item_id: int,
    item_data: ReconciliationItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(ReconciliationItem).filter(
        ReconciliationItem.id == item_id,
        ReconciliationItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    if (item_data.status == "categorized" and
            item_data.user_bucket and item_data.user_category):
        expense = Expense(
            user_id=current_user.id,
            date=item.pdf_date,
            amount=item.pdf_amount,
            bucket=item_data.user_bucket,
            category_name=item_data.user_category,
            description=item.pdf_description,
            payment_method="card",
        )
        db.add(expense)

        report = db.query(ReconciliationReport).filter(
            ReconciliationReport.id == item.report_id
        ).first()
        if report:
            report.total_categorized = (report.total_categorized or 0) + 1

    for key, value in item_data.dict(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.post("/{mes}/{ano}/complete", response_model=ReconciliationReportResponse)
def complete_reconciliation(
    mes: int,
    ano: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start, _ = _month_range(mes, ano)
    report = db.query(ReconciliationReport).filter(
        ReconciliationReport.user_id == current_user.id,
        ReconciliationReport.month == start,
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    report.status = "completed"
    report.completed_at = datetime.now(timezone.utc)

    budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.user_id == current_user.id,
        MonthlyBudget.month == start,
    ).first()
    if budget:
        budget.status = "closed"
        budget.pdf_received_date = datetime.now(timezone.utc)

    db.commit()
    db.refresh(report)
    return report
