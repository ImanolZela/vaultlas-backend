from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import Document, Goal, Movement


def get_user_monthly_report(user_id: int, mes: int, ano: int, db: Session) -> Dict:
    periodo = f"{ano}-{mes:02d}"
    docs = db.query(Document).filter(
        Document.user_id == user_id,
        Document.status == "done",
        Document.periodo == periodo,
    ).all()
    doc_ids = [d.id for d in docs]

    movements: List[Movement] = []
    if doc_ids:
        movements = db.query(Movement).filter(
            Movement.document_id.in_(doc_ids),
            Movement.confirmed == True,
        ).all()

    total_ingresos = sum(m.monto for m in movements if m.tipo == "ingreso")
    total_egresos = sum(m.monto for m in movements if m.tipo == "egreso")
    neto = total_ingresos - total_egresos

    goal = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.mes == mes,
        Goal.ano == ano,
    ).first()

    cumplimiento_porcentaje: Optional[float] = None
    if goal and goal.meta_ingresos > 0:
        cumplimiento_porcentaje = (total_ingresos / goal.meta_ingresos) * 100

    return {
        "mes": mes,
        "ano": ano,
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "neto": neto,
        "meta_ingresos": goal.meta_ingresos if goal else None,
        "cumplimiento_porcentaje": cumplimiento_porcentaje,
    }


def get_historic_report(user_id: int, months: int, db: Session) -> List[Dict]:
    today = datetime.now()
    reports = []
    for i in range(months):
        date = today - timedelta(days=30 * i)
        report = get_user_monthly_report(user_id, date.month, date.year, db)
        reports.append(report)
    return reports
