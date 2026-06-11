from __future__ import annotations

import re
from typing import BinaryIO

import pandas as pd

from bank_guarantee_tool.src.services.normalization_service import normalize_guarantees, normalize_money_column, normalize_text_column, normalize_date_column


COLUMN_ALIASES = {
    "guarantee_number": ["номер бг", "№ бг", "гарантия", "номер гарантии", "bg number", "guarantee_number"],
    "bank_name": ["банк", "банк-гарант", "bank", "bank_name"],
    "supplier_name": ["поставщик", "бенефициар", "контрагент", "beneficiary", "supplier", "supplier_name"],
    "supplier_inn": ["инн поставщика", "инн", "inn", "supplier_inn"],
    "legal_entity_name": ["юрлицо", "юридическое лицо", "принципал", "legal entity", "legal_entity_name"],
    "amount": ["сумма", "сумма бг", "лимит бг", "amount"],
    "start_date": ["дата начала", "начало", "действует с", "start_date"],
    "end_date": ["дата окончания", "окончание", "срок до", "действует до", "end_date"],
    "rate": ["ставка", "ставка %", "rate"],
    "actual_fee": ["комиссия", "факт комиссия", "actual_fee"],
    "status": ["статус", "status"],
    "total_limit": ["общий лимит", "лимит", "total_limit"],
    "reserved_limit": ["резерв", "зарезервировано", "reserved_limit"],
    "limit_start_date": ["начало лимита", "дата начала лимита", "limit_start_date"],
    "limit_end_date": ["окончание лимита", "дата окончания лимита", "limit_end_date"],
    "limit_status": ["статус лимита", "limit_status"],
}


def _clean_column_name(column: object) -> str:
    text = str(column).strip().lower().replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\n", " ")
    return text


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cleaned = {_clean_column_name(column): column for column in df.columns}
    rename_map = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            source = cleaned.get(_clean_column_name(alias))
            if source is not None:
                rename_map[source] = canonical
                break
    return df.rename(columns=rename_map)


def load_excel_file(uploaded_file: BinaryIO) -> dict[str, pd.DataFrame]:
    return pd.read_excel(uploaded_file, sheet_name=None)


def detect_guarantee_sheet(sheets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame]:
    preferred_names = {"бг", "гарантии", "bank guarantees", "guarantees"}
    for name, df in sheets.items():
        if _clean_column_name(name) in preferred_names:
            return name, df
    first_name = next(iter(sheets))
    return first_name, sheets[first_name]


def detect_limits_sheet(sheets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame] | None:
    preferred = {"лимиты", "лимиты банков", "bank limits", "limits"}
    for name, df in sheets.items():
        if _clean_column_name(name) in preferred:
            return name, df
    return None


def prepare_guarantees_from_sheets(sheets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame]:
    sheet_name, raw_df = detect_guarantee_sheet(sheets)
    normalized = normalize_columns(raw_df)
    return sheet_name, normalize_guarantees(normalized)


def prepare_limits_from_sheets(sheets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame] | None:
    detected = detect_limits_sheet(sheets)
    if detected is None:
        return None
    sheet_name, raw_df = detected
    df = normalize_columns(raw_df)
    for column in ["bank_name", "legal_entity_name", "limit_status"]:
        if column not in df.columns:
            df[column] = ""
        df[column] = normalize_text_column(df[column])
    for column in ["total_limit", "reserved_limit"]:
        if column not in df.columns:
            df[column] = 0.0
        df[column] = normalize_money_column(df[column])
    for column in ["limit_start_date", "limit_end_date"]:
        if column in df.columns:
            df[column] = normalize_date_column(df[column])
    return sheet_name, df
