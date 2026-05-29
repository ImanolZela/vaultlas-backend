from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models import User, Movement, Document
from app.services.export_service import (
    generate_pdf_report, generate_excel_report, build_filename,
    generate_budget_pdf_report, generate_budget_excel_report, MONTHS_ES,
)

router = APIRouter()


def _get_movements(
    db: Session,
    user_id: int,
    report_type: str,
    mes: Optional[int],
    ano: Optional[int],
) -> list:
    query = (
        db.query(Movement)
        .join(Document, Movement.document_id == Document.id)
        .filter(Document.user_id == user_id, Movement.confirmed == True)
    )

    if report_type == "ingresos":
        query = query.filter(Movement.tipo == "ingreso")
    elif report_type == "egresos":
        query = query.filter(Movement.tipo == "egreso")

    if mes and ano:
        periodo = f"{ano}-{mes:02d}"
        query = query.filter(Document.periodo == periodo)
    elif ano:
        query = query.filter(Document.periodo.like(f"{ano}-%"))

    return [
        {
            "fecha": m.fecha,
            "descripcion": m.descripcion,
            "codigo_operacion": m.codigo_operacion,
            "monto": float(m.monto),
            "tipo": m.tipo,
        }
        for m in query.order_by(Movement.fecha).all()
    ]


@router.get("/pdf")
def export_pdf(
    report_type: str = Query(..., regex="^(ingresos|egresos|ambos)$"),
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    movements = _get_movements(db, current_user.id, report_type, mes, ano)
    if not movements:
        raise HTTPException(status_code=404, detail="No hay movimientos para el período seleccionado")

    pdf_bytes = generate_pdf_report(movements, report_type, mes, ano)
    filename = build_filename(report_type, mes, ano, "pdf")

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/excel")
def export_excel(
    report_type: str = Query(..., regex="^(ingresos|egresos|ambos)$"),
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    movements = _get_movements(db, current_user.id, report_type, mes, ano)
    if not movements:
        raise HTTPException(status_code=404, detail="No hay movimientos para el período seleccionado")

    excel_bytes = generate_excel_report(movements, report_type, mes, ano)
    filename = build_filename(report_type, mes, ano, "xlsx")

    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── Budget 50-30-20 export helpers & routes ───────────────────────────────────

def _budget_to_dict(b):
    month_label = MONTHS_ES[b.month.month - 1]
    income  = b.total_income   or 0
    needs   = b.actual_needs   or 0
    wants   = b.actual_wants   or 0
    savings = b.actual_savings or 0
    debt    = b.actual_debt    or 0
    expenses = needs + wants + savings + debt
    return {
        "month_label":      month_label,
        "total_income":     income,
        "budgeted_needs":   b.budgeted_needs   or 0,
        "actual_needs":     needs,
        "budgeted_wants":   b.budgeted_wants   or 0,
        "actual_wants":     wants,
        "budgeted_savings": b.budgeted_savings or 0,
        "actual_savings":   savings,
        "actual_debt":      debt,
        "net":              income - expenses,
    }


from app.db.models import MonthlyBudget as MonthlyBudgetModel


@router.get("/budget/pdf")
def export_budget_pdf(
    ano: int = Query(..., ge=2000, le=2100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(MonthlyBudgetModel).filter(
        MonthlyBudgetModel.user_id == current_user.id,
        MonthlyBudgetModel.month.between(date(ano, 1, 1), date(ano, 12, 31)),
    )
    if mes:
        query = query.filter(MonthlyBudgetModel.month == date(ano, mes, 1))
    budgets = query.order_by(MonthlyBudgetModel.month).all()

    if not budgets:
        raise HTTPException(status_code=404, detail="No hay datos de presupuesto para el período")

    budgets_data = [_budget_to_dict(b) for b in budgets]
    pdf_bytes = generate_budget_pdf_report(budgets_data, ano, mes)
    filename = f"presupuesto_{ano}{'_' + str(mes).zfill(2) if mes else ''}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/budget/excel")
def export_budget_excel(
    ano: int = Query(..., ge=2000, le=2100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(MonthlyBudgetModel).filter(
        MonthlyBudgetModel.user_id == current_user.id,
        MonthlyBudgetModel.month.between(date(ano, 1, 1), date(ano, 12, 31)),
    )
    if mes:
        query = query.filter(MonthlyBudgetModel.month == date(ano, mes, 1))
    budgets = query.order_by(MonthlyBudgetModel.month).all()

    if not budgets:
        raise HTTPException(status_code=404, detail="No hay datos de presupuesto para el período")

    budgets_data = [_budget_to_dict(b) for b in budgets]
    excel_bytes = generate_budget_excel_report(budgets_data, ano, mes)
    filename = f"presupuesto_{ano}{'_' + str(mes).zfill(2) if mes else ''}.xlsx"
    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
