from __future__ import annotations

import pandas as pd
import streamlit as st

from bank_guarantee_tool.src.export.excel_exporter import build_excel_report


def render_export(guarantees_df: pd.DataFrame, bank_limits_df: pd.DataFrame, suppliers_df: pd.DataFrame, validation_df: pd.DataFrame) -> None:
    st.header("Экспорт")
    if guarantees_df.empty:
        st.info("Нет данных для экспорта.")
        return

    report = build_excel_report(guarantees_df, bank_limits_df, suppliers_df, validation_df)
    st.download_button(
        "Скачать полный Excel-отчёт",
        data=report,
        file_name="bg_limits_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button("CSV: Реестр БГ", guarantees_df.to_csv(index=False).encode("utf-8-sig"), "guarantees.csv", "text/csv")
    st.download_button("CSV: Лимиты банков", bank_limits_df.to_csv(index=False).encode("utf-8-sig"), "bank_limits.csv", "text/csv")
    st.download_button("CSV: Поставщики", suppliers_df.to_csv(index=False).encode("utf-8-sig"), "suppliers.csv", "text/csv")
