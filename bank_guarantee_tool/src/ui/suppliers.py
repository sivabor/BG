from __future__ import annotations

import pandas as pd
import streamlit as st

from bank_guarantee_tool.src.ui.formatting import display_dataframe


def render_suppliers(suppliers_df: pd.DataFrame) -> None:
    st.header("Поставщики")
    if suppliers_df.empty:
        st.info("Нет данных по поставщикам.")
        return
    st.dataframe(display_dataframe(suppliers_df), use_container_width=True, hide_index=True)
