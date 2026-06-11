from __future__ import annotations

from datetime import date

import pandas as pd


def _is_active_guarantee(df: pd.DataFrame, current_date: date) -> pd.Series:
    status_active = df.get("status", pd.Series(index=df.index, dtype="object")).isin(["active", "unknown", "planned"])
    not_expired = df.get("end_date", pd.Series(pd.NaT, index=df.index)).isna() | (df["end_date"] >= pd.Timestamp(current_date))
    return status_active & not_expired


def calculate_bank_limits(banks_df: pd.DataFrame, guarantees_df: pd.DataFrame, current_date: date | None = None) -> pd.DataFrame:
    current_date = current_date or date.today()
    banks = banks_df.copy()
    for column in ["bank_name", "legal_entity_name"]:
        if column not in banks.columns:
            banks[column] = ""
    for column in ["total_limit", "reserved_limit"]:
        if column not in banks.columns:
            banks[column] = 0.0
        banks[column] = banks[column].fillna(0.0).astype(float)

    if guarantees_df.empty:
        used = pd.DataFrame(columns=["bank_name", "legal_entity_name", "used_limit"])
    else:
        active_guarantees = guarantees_df[_is_active_guarantee(guarantees_df, current_date)].copy()
        used = (
            active_guarantees.groupby(["bank_name", "legal_entity_name"], dropna=False)["amount"]
            .sum()
            .reset_index(name="used_limit")
        )

    result = banks.merge(used, on=["bank_name", "legal_entity_name"], how="left")
    result["used_limit"] = result["used_limit"].fillna(0.0)
    result["available_limit"] = result["total_limit"] - result["used_limit"] - result["reserved_limit"]
    result["limit_usage_percent"] = result.apply(
        lambda row: row["used_limit"] / row["total_limit"] if row["total_limit"] else None, axis=1
    )
    result["available_limit_percent"] = result.apply(
        lambda row: row["available_limit"] / row["total_limit"] if row["total_limit"] else None, axis=1
    )

    def flags(row: pd.Series) -> str:
        values: list[str] = []
        if row["available_limit"] < 0:
            values.append("LIMIT_OVERUSED")
        available_percent = row["available_limit_percent"]
        if pd.notna(available_percent) and available_percent <= 0.10:
            values.append("LOW_AVAILABLE_LIMIT")
        if row["total_limit"] == 0:
            values.append("LIMIT_NOT_LOADED")
        return ", ".join(values)

    result["risk_flags"] = result.apply(flags, axis=1)
    return result
