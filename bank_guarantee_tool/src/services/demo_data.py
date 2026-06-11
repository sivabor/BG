from __future__ import annotations

from datetime import date
from io import BytesIO

import pandas as pd


def build_demo_workbook() -> bytes:
    today = pd.Timestamp(date.today())
    guarantees = pd.DataFrame(
        [
            ["BG-2026-001", "Сбербанк", "МеталлИнвест", "7701000001", "ООО Технострой", 125_000_000, today - pd.Timedelta(days=120), today + pd.Timedelta(days=25), "8,4%", 2_900_000, "Действует"],
            ["BG-2026-002", "ВТБ", "СтройКомплект", "7702000002", "ООО Технострой", 85_000_000, today - pd.Timedelta(days=90), today + pd.Timedelta(days=70), "9,1%", 1_850_000, "Действует"],
            ["BG-2026-003", "Газпромбанк", "Логистика Плюс", "7703000003", "АО Промснаб", 210_000_000, today - pd.Timedelta(days=30), today + pd.Timedelta(days=140), "8,9%", 4_500_000, "Действует"],
            ["BG-2025-004", "Альфа-Банк", "ЭнергоСервис", "7704000004", "АО Промснаб", 45_000_000, today - pd.Timedelta(days=380), today - pd.Timedelta(days=5), "9,4%", 1_100_000, "Действует"],
            ["BG-2026-005", "Сбербанк", "МеталлИнвест", "7701000001", "ООО Технострой", 60_000_000, today - pd.Timedelta(days=15), today + pd.Timedelta(days=95), "8,2%", 980_000, "Действует"],
        ],
        columns=["Номер БГ", "Банк", "Поставщик", "ИНН поставщика", "Юрлицо", "Сумма БГ", "Дата начала", "Дата окончания", "Ставка", "Комиссия", "Статус"],
    )
    limits = pd.DataFrame(
        [
            ["Сбербанк", "ООО Технострой", 250_000_000, 10_000_000, "Норма"],
            ["ВТБ", "ООО Технострой", 100_000_000, 5_000_000, "Норма"],
            ["Газпромбанк", "АО Промснаб", 260_000_000, 20_000_000, "Норма"],
            ["Альфа-Банк", "АО Промснаб", 50_000_000, 0, "Норма"],
        ],
        columns=["Банк", "Юрлицо", "Общий лимит", "Резерв", "Статус лимита"],
    )
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
        guarantees.to_excel(writer, sheet_name="БГ", index=False)
        limits.to_excel(writer, sheet_name="Лимиты", index=False)
    return output.getvalue()
