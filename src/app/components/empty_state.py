from __future__ import annotations


def render_empty_state(message: str = "No games matched the current filters.") -> None:
    import streamlit as st

    st.warning(message)
    st.caption("Try broadening the year range, removing a genre/theme, or lowering the minimum rating threshold.")

