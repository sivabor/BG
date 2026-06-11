from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from bank_guarantee_tool.src.ui.formatting import money, display_dataframe


def render_dashboard(guarantees_df: pd.DataFrame, bank_limits_df: pd.DataFrame, current_date: date) -> None:
    st.header("Дашборд портфеля")
    if guarantees_df.empty:
        st.info("Загрузите Excel-файл или включите демо-данные, чтобы увидеть дашборд.")
        return

    active = guarantees_df[
        guarantees_df["status"].isin(["active", "unknown", "planned"])
        & (guarantees_df["end_date"].isna() | (guarantees_df["end_date"] >= pd.Timestamp(current_date)))
    ]
    total_limit = bank_limits_df["total_limit"].sum() if "total_limit" in bank_limits_df else 0
    used_limit = bank_limits_df["used_limit"].sum() if "used_limit" in bank_limits_df else active["amount"].sum()
    available_limit = bank_limits_df["available_limit"].sum() if "available_limit" in bank_limits_df else 0
    expiring_30 = active[active["end_date"].between(pd.Timestamp(current_date), pd.Timestamp(current_date) + pd.Timedelta(days=30))]
    low_limit_count = bank_limits_df[bank_limits_df["risk_flags"].str.contains("LOW_AVAILABLE_LIMIT|LIMIT_OVERUSED", na=False)].shape[0] if "risk_flags" in bank_limits_df else 0

    cols = st.columns(5)
    cols[0].metric("Общий лимит", money(total_limit))
    cols[1].metric("Использовано", money(used_limit))
    cols[2].metric("Свободно", money(available_limit))
    cols[3].metric("Действующие БГ", f"{len(active)} шт.", money(active["amount"].sum()))
    cols[4].metric("Истекают ≤30 дней", f"{len(expiring_30)} шт.", f"Проблемных лимитов: {low_limit_count}")

    left, right = st.columns(2)
    with left:
        st.subheader("Использование лимитов по банкам")
        chart = bank_limits_df.groupby("bank_name", dropna=False)[["used_limit", "available_limit"]].sum()
        st.bar_chart(chart)
    with right:
        st.subheader("Ближайшие окончания БГ")
        upcoming = active.sort_values("end_date").head(10)[["guarantee_number", "bank_name", "supplier_name", "amount", "end_date"]]
        st.dataframe(display_dataframe(upcoming), use_container_width=True, hide_index=True)
