from __future__ import annotations

from datetime import date
import re

import pandas as pd


ACTIVE_STATUSES = {"active", "действует", "действующая", "активна", "активный", "открыта"}
EXPIRED_STATUSES = {"expired", "истекла", "истек", "просрочена", "завершена"}
PLANNED_STATUSES = {"planned", "план", "плановая", "запланирована"}
CLOSED_STATUSES = {"closed", "закрыта", "закрыт", "отменена", "аннулирована"}


def normalize_money_value(value: object) -> float:
    """Convert common Russian Excel money formats into float."""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return 0.0
    text = text.replace("\u00a0", " ")
    text = re.sub(r"(?i)(руб\.?|₽|rub|р\.)", "", text)
    text = text.replace(" ", "").replace(",", ".")
    text = re.sub(r"[^0-9.\-]", "", text)
    if text in {"", "-", "."}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def normalize_money_column(series: pd.Series) -> pd.Series:
    return series.apply(normalize_money_value).astype(float)


def normalize_rate_value(value: object) -> float:
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value).strip().replace("\u00a0", " ").replace("%", "")
        text = text.replace(" ", "").replace(",", ".")
        text = re.sub(r"[^0-9.\-]", "", text)
        if not text:
            return 0.0
        number = float(text)
    return number / 100 if number > 1 else number


def normalize_rate_column(series: pd.Series) -> pd.Series:
    return series.apply(normalize_rate_value).astype(float)


def normalize_date_column(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def normalize_status_value(value: object) -> str:
    if pd.isna(value):
        return "unknown"
    status = str(value).strip().lower()
    if status in ACTIVE_STATUSES:
        return "active"
    if status in EXPIRED_STATUSES:
        return "expired"
    if status in PLANNED_STATUSES:
        return "planned"
    if status in CLOSED_STATUSES:
        return "closed"
    return status or "unknown"


def normalize_status_column(series: pd.Series) -> pd.Series:
    return series.apply(normalize_status_value)


def normalize_text_column(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def add_guarantee_ids(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "guarantee_id" not in df.columns:
        df.insert(0, "guarantee_id", [f"BG-{i:05d}" for i in range(1, len(df) + 1)])
    return df


def normalize_guarantees(df: pd.DataFrame, current_date: date | None = None) -> pd.DataFrame:
    current_date = current_date or date.today()
    df = add_guarantee_ids(df.copy())

    for column in ["guarantee_number", "bank_name", "supplier_name", "supplier_inn", "legal_entity_name"]:
        if column not in df.columns:
            df[column] = ""
        df[column] = normalize_text_column(df[column])

    for column in ["amount", "actual_fee"]:
        if column not in df.columns:
            df[column] = 0.0
        df[column] = normalize_money_column(df[column])

    if "rate" not in df.columns:
        df["rate"] = 0.0
    df["rate"] = normalize_rate_column(df["rate"])

    for column in ["start_date", "end_date"]:
        if column not in df.columns:
            df[column] = pd.NaT
        df[column] = normalize_date_column(df[column])

    if "status" not in df.columns:
        df["status"] = "unknown"
    df["status"] = normalize_status_column(df["status"])

    today = pd.Timestamp(current_date)
    expired_mask = df["end_date"].notna() & (df["end_date"] < today) & df["status"].isin(["active", "unknown"])
    df["status_warning"] = ""
    df.loc[expired_mask, "status_warning"] = "BG_EXPIRED_ACTIVE"
    return df
