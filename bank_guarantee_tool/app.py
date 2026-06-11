from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bank_guarantee_tool.config import CONFIG
from bank_guarantee_tool.src.loaders.excel_loader import load_excel_file, prepare_guarantees_from_sheets, prepare_limits_from_sheets
from bank_guarantee_tool.src.services.bank_service import build_banks_from_guarantees, merge_bank_directory_with_limits
from bank_guarantee_tool.src.services.demo_data import build_demo_workbook
from bank_guarantee_tool.src.services.limit_service import calculate_bank_limits
from bank_guarantee_tool.src.services.supplier_service import build_suppliers_from_guarantees
from bank_guarantee_tool.src.services.validation_service import validate_guarantees
from bank_guarantee_tool.src.ui.bank_limits import render_bank_limits
from bank_guarantee_tool.src.ui.dashboard import render_dashboard
from bank_guarantee_tool.src.ui.export_page import render_export
from bank_guarantee_tool.src.ui.guarantees import render_guarantees
from bank_guarantee_tool.src.ui.suppliers import render_suppliers


st.set_page_config(page_title="BG & Limits", page_icon="🏦", layout="wide")


@st.cache_data(show_spinner=False)
def process_workbook(file_bytes: bytes) -> dict[str, pd.DataFrame | str]:
    sheets = load_excel_file(BytesIO(file_bytes))
    guarantee_sheet, guarantees_df = prepare_guarantees_from_sheets(sheets)
    limits_result = prepare_limits_from_sheets(sheets)
    limits_sheet = "не найден"
    limits_df = None
    if limits_result is not None:
        limits_sheet, limits_df = limits_result

    banks_df = build_banks_from_guarantees(guarantees_df)
    banks_df = merge_bank_directory_with_limits(banks_df, limits_df)
    bank_limits_df = calculate_bank_limits(banks_df, guarantees_df, CONFIG.calculation_date)
    suppliers_df = build_suppliers_from_guarantees(guarantees_df)
    validation_df = validate_guarantees(guarantees_df, CONFIG.calculation_date)
    return {
        "guarantee_sheet": guarantee_sheet,
        "limits_sheet": limits_sheet,
        "guarantees": guarantees_df,
        "bank_limits": bank_limits_df,
        "suppliers": suppliers_df,
        "validation": validation_df,
    }


def process_workbook_with_progress(file_bytes: bytes, source_label: str) -> dict[str, pd.DataFrame | str]:
    """Run workbook processing with a visible progress indicator for non-technical users."""
    progress = st.sidebar.progress(0, text=f"Загружаю {source_label}...")
    try:
        progress.progress(20, text="Читаю Excel-листы...")
        progress.progress(45, text="Нормализую колонки, даты и суммы...")
        data = process_workbook(file_bytes)
        progress.progress(75, text="Считаю лимиты, справочники и проверки...")
        progress.progress(100, text="Готово: данные обработаны")
        st.sidebar.success("Excel-файл загружен и обработан")
        return data
    except Exception as exc:
        progress.empty()
        st.sidebar.error("Не удалось обработать Excel-файл")
        st.sidebar.exception(exc)
        return empty_state()


def empty_state() -> dict[str, pd.DataFrame | str]:
    return {
        "guarantee_sheet": "",
        "limits_sheet": "",
        "guarantees": pd.DataFrame(),
        "bank_limits": pd.DataFrame(),
        "suppliers": pd.DataFrame(),
        "validation": pd.DataFrame(columns=["level", "entity_type", "row_number", "field", "message"]),
    }


def sidebar_data_loader() -> dict[str, pd.DataFrame | str]:
    st.sidebar.title("BG & LIMITS")
    st.sidebar.caption("MVP: импорт Excel → лимиты → дашборд → экспорт")
    uploaded_file = st.sidebar.file_uploader("Загрузите Excel-файл портфеля", type=["xlsx", "xls"])
    use_demo = st.sidebar.checkbox("Использовать демо-данные", value=uploaded_file is None)
    st.sidebar.download_button(
        "Скачать шаблон/демо Excel",
        data=build_demo_workbook(),
        file_name="bg_limits_demo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    if uploaded_file is not None:
        st.sidebar.info(f"Файл выбран: {uploaded_file.name}")
        return process_workbook_with_progress(uploaded_file.getvalue(), uploaded_file.name)
    if use_demo:
        return process_workbook_with_progress(build_demo_workbook(), "демо-шаблон")
    return empty_state()


def render_data_quality(validation_df: pd.DataFrame) -> None:
    if validation_df.empty:
        st.success("Критичных ошибок качества данных не найдено.")
        return
    errors = validation_df[validation_df["level"] == "error"]
    warnings = validation_df[validation_df["level"] == "warning"]
    st.warning(f"Найдено ошибок: {len(errors)}, предупреждений: {len(warnings)}")
    with st.expander("Показать проверки качества данных"):
        st.dataframe(validation_df, use_container_width=True, hide_index=True)


def main() -> None:
    data = sidebar_data_loader()
    guarantees_df = data["guarantees"]
    bank_limits_df = data["bank_limits"]
    suppliers_df = data["suppliers"]
    validation_df = data["validation"]

    st.title("🏦 BG & Limits — анализ банковских гарантий и лимитов")
    st.caption(f"Лист БГ: {data['guarantee_sheet'] or 'не загружен'} · Лист лимитов: {data['limits_sheet'] or 'не загружен'}")
    render_data_quality(validation_df)

    page = st.sidebar.radio(
        "Раздел",
        ["Dashboard", "Bank Limits", "Guarantees", "Suppliers", "Export"],
    )

    if page == "Dashboard":
        render_dashboard(guarantees_df, bank_limits_df, CONFIG.calculation_date)
    elif page == "Bank Limits":
        render_bank_limits(bank_limits_df)
    elif page == "Guarantees":
        render_guarantees(guarantees_df, CONFIG.calculation_date)
    elif page == "Suppliers":
        render_suppliers(suppliers_df)
    elif page == "Export":
        render_export(guarantees_df, bank_limits_df, suppliers_df, validation_df)


if __name__ == "__main__":
    main()
