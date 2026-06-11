from __future__ import annotations

import pandas as pd


def build_banks_from_guarantees(guarantees_df: pd.DataFrame) -> pd.DataFrame:
    if guarantees_df.empty:
        return pd.DataFrame(columns=["bank_id", "bank_name", "legal_entity_name", "total_limit", "reserved_limit", "limit_status"])
    cols = ["bank_name", "legal_entity_name"]
    banks = guarantees_df[cols].drop_duplicates().copy()
    banks = banks[(banks["bank_name"] != "") | (banks["legal_entity_name"] != "")]
    banks.insert(0, "bank_id", [f"BANK-{i:04d}" for i in range(1, len(banks) + 1)])
    banks["total_limit"] = 0.0
    banks["reserved_limit"] = 0.0
    banks["limit_status"] = "not_loaded"
    return banks


def merge_bank_directory_with_limits(banks_df: pd.DataFrame, limits_df: pd.DataFrame | None) -> pd.DataFrame:
    if limits_df is None or limits_df.empty:
        return banks_df.copy()

    limits = limits_df.copy()
    for column in ["bank_name", "legal_entity_name"]:
        if column not in limits.columns:
            limits[column] = ""
    for column in ["total_limit", "reserved_limit"]:
        if column not in limits.columns:
            limits[column] = 0.0
    if "limit_status" not in limits.columns:
        limits["limit_status"] = "loaded"

    limit_cols = ["bank_name", "legal_entity_name", "total_limit", "reserved_limit", "limit_status"]
    limits = limits[limit_cols].drop_duplicates(subset=["bank_name", "legal_entity_name"], keep="last")

    merged = banks_df.drop(columns=["total_limit", "reserved_limit", "limit_status"], errors="ignore").merge(
        limits, on=["bank_name", "legal_entity_name"], how="outer"
    )
    if "bank_id" not in merged.columns:
        merged.insert(0, "bank_id", "")
    missing_id = merged["bank_id"].isna() | (merged["bank_id"].astype(str) == "")
    merged.loc[missing_id, "bank_id"] = [f"BANK-LIMIT-{i:04d}" for i in range(1, int(missing_id.sum()) + 1)]
    merged["total_limit"] = merged["total_limit"].fillna(0.0)
    merged["reserved_limit"] = merged["reserved_limit"].fillna(0.0)
    merged["limit_status"] = merged["limit_status"].fillna("not_loaded")
    return merged
