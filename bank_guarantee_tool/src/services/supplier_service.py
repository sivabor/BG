from __future__ import annotations

import pandas as pd


def build_suppliers_from_guarantees(guarantees_df: pd.DataFrame) -> pd.DataFrame:
    if guarantees_df.empty:
        return pd.DataFrame(columns=["supplier_id", "supplier_name", "inn", "requires_bank_guarantee", "guarantee_count", "guarantee_amount"])
    suppliers = (
        guarantees_df.groupby(["supplier_name", "supplier_inn"], dropna=False)
        .agg(guarantee_count=("guarantee_id", "count"), guarantee_amount=("amount", "sum"))
        .reset_index()
        .rename(columns={"supplier_inn": "inn"})
    )
    suppliers = suppliers[(suppliers["supplier_name"] != "") | (suppliers["inn"] != "")]
    suppliers.insert(0, "supplier_id", [f"SUP-{i:05d}" for i in range(1, len(suppliers) + 1)])
    suppliers["requires_bank_guarantee"] = suppliers["guarantee_count"] > 0
    return suppliers
