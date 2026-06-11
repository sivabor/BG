from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from bank_guarantee_tool.src.ui.formatting import display_dataframe


def _filter_multiselect(df: pd.DataFrame, label: str, column: str) -> pd.DataFrame:
    values = sorted([value for value in df[column].dropna().unique() if str(value).strip()]) if column in df else []
    selected = st.multiselect(label, values)
    if selected:
        return df[df[column].isin(selected)]
    return df


def render_guarantees(guarantees_df: pd.DataFrame, current_date: date) -> None:
    st.header("Реестр банковских гарантий")
    if guarantees_df.empty:
        st.info("Нет данных по банковским гарантиям.")
        return

    df = guarantees_df.copy()
    df["days_to_end"] = (df["end_date"] - pd.Timestamp(current_date)).dt.days

    with st.expander("Фильтры", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            df = _filter_multiselect(df, "Банк", "bank_name")
        with col2:
            df = _filter_multiselect(df, "Поставщик", "supplier_name")
        with col3:
            df = _filter_multiselect(df, "Юрлицо", "legal_entity_name")
        with col4:
            df = _filter_multiselect(df, "Статус", "status")
        end_before = st.date_input("Показать БГ с окончанием до", value=None)
        if end_before:
            df = df[df["end_date"] <= pd.Timestamp(end_before)]

    st.caption("Красные/жёлтые статусы отражены в колонках `days_to_end` и `status_warning`.")
    columns = [
        "guarantee_number", "bank_name", "supplier_name", "legal_entity_name", "amount",
        "start_date", "end_date", "days_to_end", "rate", "actual_fee", "status", "status_warning",
    ]
    st.dataframe(display_dataframe(df[[column for column in columns if column in df.columns]]), use_container_width=True, hide_index=True)
