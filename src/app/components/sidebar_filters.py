from __future__ import annotations


def render_multiselect(label: str, options: list[str], max_default: int = 0) -> list[str]:
    import streamlit as st

    default = options[:max_default] if max_default else []
    return st.multiselect(label, options=options, default=default)

