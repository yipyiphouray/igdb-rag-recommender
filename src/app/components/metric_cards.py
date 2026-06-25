from __future__ import annotations


def render_metric_row(metrics: list[tuple[str, object, str | None]]) -> None:
    import streamlit as st

    if not metrics:
        return
    cols = st.columns(len(metrics))
    for col, (label, value, help_text) in zip(cols, metrics):
        col.metric(label=label, value=value, help=help_text)

