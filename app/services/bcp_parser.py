import re
from typing import Dict, List, Optional, Tuple


def _parse_amount(value: str) -> Tuple[Optional[float], str]:
    if not value:
        return None, ""
    value = str(value).strip()
    if re.match(r"^[-]+$", value):
        return None, ""
    is_egreso = value.endswith("-")
    cleaned = value.rstrip("-").replace(",", "")
    if cleaned.startswith("."):
        cleaned = "0" + cleaned
    try:
        amount = float(cleaned)
        if amount <= 0:
            return None, ""
        return amount, "egreso" if is_egreso else "ingreso"
    except ValueError:
        return None, ""


def _extract_year_month(text: str) -> Tuple[Optional[int], Optional[int]]:
    m = re.search(r"DEL\s*\d{2}/(\d{2})/(\d{4})", text)
    if m:
        return int(m.group(2)), int(m.group(1))
    return None, None


def parse_bcp_movements(tables: List[List], text: str = "") -> List[Dict]:
    year, month = _extract_year_month(text)
    movements = []

    for table in tables:
        for row in table:
            if not row or len(row) < 11:
                continue

            col0 = str(row[0] or "").strip()
            if not col0 or "\n" not in col0:
                continue
            if not re.match(r"\d{2}[-/]\d{2}", col0.split("\n")[0]):
                continue

            fechas = col0.split("\n")
            descripciones = str(row[2] or "").split("\n") if row[2] else []
            montos_raw = str(row[10] or "").split("\n") if len(row) > 10 and row[10] else []
            suc_age = [s.strip() for s in str(row[5] or "").split("\n")] if len(row) > 5 and row[5] else []
            num_ops_all = [n.strip() for n in str(row[6] or "").split("\n") if n.strip() and not re.match(r"^[-]+$", n.strip())] if len(row) > 6 and row[6] else []

            count = min(len(fechas), len(descripciones), len(montos_raw))
            num_op_idx = 0

            for i in range(count):
                fecha_raw = fechas[i].strip()
                if not re.match(r"\d{2}[-/]\d{2}", fecha_raw):
                    continue

                descripcion = descripciones[i].strip() if i < len(descripciones) else ""
                if not descripcion or re.match(r"^[-]+$", descripcion):
                    continue

                monto_str = montos_raw[i].strip() if i < len(montos_raw) else ""
                monto, tipo = _parse_amount(monto_str)
                if monto is None:
                    continue

                # Use SUC-AGE presence to decide if this row has a NUM OP
                suc = suc_age[i] if i < len(suc_age) else "-"
                has_num_op = bool(suc) and suc != "-" and not re.match(r"^[-]+$", suc)
                if has_num_op and num_op_idx < len(num_ops_all):
                    num_op = num_ops_all[num_op_idx]
                    num_op_idx += 1
                else:
                    num_op = None

                parts = re.split(r"[-/]", fecha_raw)
                if len(parts) == 2 and year:
                    fecha = f"{parts[0]}/{parts[1]}/{year}"
                else:
                    fecha = fecha_raw.replace("-", "/")

                movements.append({
                    "fecha": fecha,
                    "descripcion": descripcion,
                    "codigo_operacion": num_op,
                    "monto": monto,
                    "tipo": tipo,
                })

    return movements


def detect_periodo(movements: List[Dict], text: str = "") -> Optional[str]:
    year, month = _extract_year_month(text)
    if year and month:
        return f"{year}-{month:02d}"
    if movements:
        fecha = movements[0]["fecha"]
        parts = re.split(r"[-/]", fecha)
        if len(parts) >= 2:
            from datetime import date
            return f"{date.today().year}-{parts[1].zfill(2)}"
    return None
