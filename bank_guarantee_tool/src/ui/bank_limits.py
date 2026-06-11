from __future__ import annotations

import pandas as pd
import streamlit as st

from bank_guarantee_tool.src.ui.formatting import display_dataframe


def render_bank_limits(bank_limits_df: pd.DataFrame) -> None:
    st.header("Лимиты банков")
    if bank_limits_df.empty:
        st.info("Нет данных по лимитам банков.")
        return

    df = bank_limits_df.copy()
    with st.expander("Фильтры", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            banks = sorted(df["bank_name"].dropna().unique())
            selected_banks = st.multiselect("Банк", banks)
            if selected_banks:
                df = df[df["bank_name"].isin(selected_banks)]
        with col2:
            entities = sorted(df["legal_entity_name"].dropna().unique())
            selected_entities = st.multiselect("Юрлицо", entities)
            if selected_entities:
                df = df[df["legal_entity_name"].isin(selected_entities)]
        with col3:
            only_risky = st.checkbox("Только проблемные лимиты")
            if only_risky:
                df = df[df["risk_flags"].astype(str) != ""]

    st.subheader("Таблица лимитов")
    st.dataframe(display_dataframe(df), use_container_width=True, hide_index=True)
    st.subheader("Использование по банкам")
    st.bar_chart(df.groupby("bank_name", dropna=False)[["used_limit", "available_limit", "reserved_limit"]].sum())
