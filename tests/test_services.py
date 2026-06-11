from __future__ import annotations

from datetime import date
from io import BytesIO

import pandas as pd

from bank_guarantee_tool.src.loaders.excel_loader import load_excel_file, prepare_guarantees_from_sheets, prepare_limits_from_sheets
from bank_guarantee_tool.src.services.bank_service import build_banks_from_guarantees, merge_bank_directory_with_limits
from bank_guarantee_tool.src.services.demo_data import build_demo_workbook
from bank_guarantee_tool.src.services.limit_service import calculate_bank_limits
from bank_guarantee_tool.src.services.normalization_service import normalize_money_value, normalize_rate_value
from bank_guarantee_tool.src.services.supplier_service import build_suppliers_from_guarantees
from bank_guarantee_tool.src.services.validation_service import validate_guarantees


def test_money_and_rate_normalization() -> None:
    assert normalize_money_value("1 250 000,50 ₽") == 1250000.50
    assert normalize_rate_value("8,5%") == 0.085
    assert normalize_rate_value(0.09) == 0.09


def test_demo_workbook_pipeline_calculates_limits() -> None:
    sheets = load_excel_file(BytesIO(build_demo_workbook()))
    _, guarantees = prepare_guarantees_from_sheets(sheets)
    limits_result = prepare_limits_from_sheets(sheets)
    assert limits_result is not None
    _, limits = limits_result

    banks = merge_bank_directory_with_limits(build_banks_from_guarantees(guarantees), limits)
    calculated = calculate_bank_limits(banks, guarantees, date.today())
    suppliers = build_suppliers_from_guarantees(guarantees)
    validation = validate_guarantees(guarantees, date.today())

    assert not calculated.empty
    assert calculated["used_limit"].sum() == 480_000_000
    assert "LOW_AVAILABLE_LIMIT" in ", ".join(calculated["risk_flags"].astype(str))
    assert suppliers["guarantee_count"].sum() == 5
    assert not validation.empty


def test_limit_calculation_handles_zero_total_limit() -> None:
    banks = pd.DataFrame([{"bank_name": "Банк", "legal_entity_name": "ЮЛ", "total_limit": 0, "reserved_limit": 0}])
    guarantees = pd.DataFrame([
        {"bank_name": "Банк", "legal_entity_name": "ЮЛ", "amount": 100, "status": "active", "end_date": pd.Timestamp("2099-01-01")}
    ])
    result = calculate_bank_limits(banks, guarantees, date.today())
    assert result.loc[0, "used_limit"] == 100
    assert pd.isna(result.loc[0, "limit_usage_percent"])
    assert "LIMIT_OVERUSED" in result.loc[0, "risk_flags"]
