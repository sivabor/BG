from __future__ import annotations

from io import BytesIO

import pandas as pd


def build_excel_report(
    guarantees_df: pd.DataFrame,
    banks_df: pd.DataFrame,
    suppliers_df: pd.DataFrame,
    validation_df: pd.DataFrame,
) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
        guarantees_df.to_excel(writer, sheet_name="Guarantees", index=False)
        banks_df.to_excel(writer, sheet_name="Bank Limits", index=False)
        suppliers_df.to_excel(writer, sheet_name="Suppliers", index=False)
        validation_df.to_excel(writer, sheet_name="Validation", index=False)
    return output.getvalue()
