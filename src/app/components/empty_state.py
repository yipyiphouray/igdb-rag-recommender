from __future__ import annotations


def render_empty_state(message: str = "No games matched the current filters.", suggestions: list[str] | None = None) -> None:
    import streamlit as st

    st.warning(message)
    fallback_suggestions = [
        "Broaden the release-year range.",
        "Remove one genre, theme, or platform filter.",
        "Lower the minimum rating threshold.",
    ]
    st.markdown("Try this:")
    for suggestion in suggestions or fallback_suggestions:
        st.markdown(f"- {suggestion}")

