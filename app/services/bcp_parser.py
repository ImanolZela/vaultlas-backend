import re
from typing import Dict, List, Optional


def _parse_amount(value) -> Optional[float]:
    if not value:
        return None
    text = str(value).strip().replace(" ", "").replace(",", ".")
    text = re.sub(r"[^\d.]", "", text)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_bcp_movements(tables: List[List]) -> List[Dict]:
    movements = []
    for table in tables:
        for row in table:
            if not row or len(row) < 5:
                continue
            try:
                fecha = str(row[0]).strip() if row[0] else ""
                descripcion = str(row[1]).strip() if row[1] else ""
                codigo = str(row[2]).strip() if len(row) > 2 and row[2] else None
                cargo_raw = row[3] if len(row) > 3 else None
                abono_raw = row[4] if len(row) > 4 else None

                if not fecha or not descripcion or fecha.lower() in ("fecha", "date", ""):
                    continue
                if not re.search(r"\d{2}[/\-]\d{2}", fecha):
                    continue

                cargo = _parse_amount(cargo_raw)
                abono = _parse_amount(abono_raw)

                if abono and abono > 0:
                    monto = abono
                    tipo = "ingreso"
                elif cargo and cargo > 0:
                    monto = cargo
                    tipo = "egreso"
                else:
                    continue

                movements.append({
                    "fecha": fecha,
                    "descripcion": descripcion,
                    "codigo_operacion": codigo,
                    "monto": monto,
                    "tipo": tipo,
                })
            except (ValueError, IndexError, TypeError):
                continue
    return movements


def detect_periodo(movements: List[Dict]) -> Optional[str]:
    if not movements:
        return None
    fecha = movements[0]["fecha"]
    parts = re.split(r"[/\-]", fecha)
    if len(parts) == 3:
        return f"{parts[2]}-{parts[1].zfill(2)}"
    return None
