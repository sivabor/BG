from __future__ import annotations

import pandas as pd


def money(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):,.0f} ₽".replace(",", " ")


def percent(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.1%}"


def display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.columns:
        if pd.api.types.is_datetime64_any_dtype(result[column]):
            result[column] = result[column].dt.date
    return result
