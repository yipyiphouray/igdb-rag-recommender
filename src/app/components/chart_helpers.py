from __future__ import annotations

import pandas as pd


def render_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    import streamlit as st

    if df.empty or x not in df or y not in df:
        st.caption(f"No data available for {title}.")
        return
    st.subheader(title)
    st.bar_chart(df.set_index(x)[y])

