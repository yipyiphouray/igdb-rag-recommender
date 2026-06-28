from __future__ import annotations


def render_menu_card(title: str, copy: str, target_page: str, button_label: str) -> None:
    import streamlit as st

    with st.container():
        st.markdown(
            f"""
            <div class="menu-card">
              <div class="menu-card-title">{title}</div>
              <div class="menu-card-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(target_page, label=button_label)
