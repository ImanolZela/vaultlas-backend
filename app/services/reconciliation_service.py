def match_transactions(manual_expenses, pdf_expenses):
    """
    Intenta emparejar transacciones manuales vs PDF.
    Devuelve lista de transacciones PDF sin match (no detectadas).

    Criterios de match (en orden de prioridad):
    1. Monto exacto + fecha exacta
    2. Monto exacto + fecha ±1 día
    3. Monto similar (±2%) + fecha ±3 días
    """
    unmatched_pdf = list(pdf_expenses)

    for manual in manual_expenses:
        found = None

        for pdf in unmatched_pdf:
            if (abs(manual['amount'] - pdf['amount']) < 0.01 and
                    manual['date'] == pdf['date']):
                found = pdf
                break

        if not found:
            for pdf in unmatched_pdf:
                if (abs(manual['amount'] - pdf['amount']) < 0.01 and
                        abs((manual['date'] - pdf['date']).days) <= 1):
                    found = pdf
                    break

        if not found:
            for pdf in unmatched_pdf:
                max_amt = max(manual['amount'], pdf['amount'])
                if (max_amt > 0 and
                        abs(manual['amount'] - pdf['amount']) / max_amt <= 0.02 and
                        abs((manual['date'] - pdf['date']).days) <= 3):
                    found = pdf
                    break

        if found:
            unmatched_pdf.remove(found)

    return unmatched_pdf


def calculate_differences(manual_incomes, manual_expenses, pdf_incomes, pdf_expenses):
    manual_income_total = sum(i['amount'] for i in manual_incomes)
    manual_expense_total = sum(e['amount'] for e in manual_expenses)
    pdf_income_total = sum(i['amount'] for i in pdf_incomes)
    pdf_expense_total = sum(e['amount'] for e in pdf_expenses)

    return {
        'income_difference': abs(pdf_income_total - manual_income_total),
        'expense_difference': abs(pdf_expense_total - manual_expense_total),
        'manual_income_total': manual_income_total,
        'manual_expense_total': manual_expense_total,
        'pdf_income_total': pdf_income_total,
        'pdf_expense_total': pdf_expense_total,
    }
