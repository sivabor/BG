from __future__ import annotations

from datetime import date

import pandas as pd


def _add_issue(issues: list[dict], level: str, row_number: int, field: str, message: str) -> None:
    issues.append({
        "level": level,
        "entity_type": "guarantee",
        "row_number": row_number,
        "field": field,
        "message": message,
    })


def validate_guarantees(guarantees_df: pd.DataFrame, current_date: date | None = None) -> pd.DataFrame:
    current_date = current_date or date.today()
    issues: list[dict] = []
    for index, row in guarantees_df.iterrows():
        row_number = int(index) + 2
        if not str(row.get("guarantee_number", "")).strip():
            _add_issue(issues, "error", row_number, "guarantee_number", "Не указан номер банковской гарантии")
        if not str(row.get("bank_name", "")).strip():
            _add_issue(issues, "error", row_number, "bank_name", "Не указан банк")
        if not str(row.get("supplier_name", "")).strip():
            _add_issue(issues, "error", row_number, "supplier_name", "Не указан поставщик/бенефициар")
        if pd.isna(row.get("amount")) or float(row.get("amount", 0) or 0) <= 0:
            _add_issue(issues, "error", row_number, "amount", "Сумма БГ отсутствует или меньше/равна нулю")
        start_date = row.get("start_date")
        end_date = row.get("end_date")
        if pd.isna(end_date):
            _add_issue(issues, "error", row_number, "end_date", "Не указана дата окончания")
        if pd.notna(start_date) and pd.notna(end_date) and end_date < start_date:
            _add_issue(issues, "error", row_number, "end_date", "Дата окончания раньше даты начала")
        if pd.notna(end_date) and end_date < pd.Timestamp(current_date) and row.get("status") == "active":
            _add_issue(issues, "warning", row_number, "status", "БГ истекла, но статус указан как active")
    return pd.DataFrame(issues, columns=["level", "entity_type", "row_number", "field", "message"])
