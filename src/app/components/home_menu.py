from __future__ import annotations

from collections.abc import Sequence

from src.app.components.menu_card import render_menu_card


MenuItem = tuple[str, str, str, str]


def render_home_menu(menu_items: Sequence[MenuItem], columns_per_row: int = 3) -> None:
    import streamlit as st

    for start in range(0, len(menu_items), columns_per_row):
        row_items = list(menu_items[start : start + columns_per_row])
        columns = st.columns(columns_per_row)
        for index, column in enumerate(columns):
            with column:
                if index < len(row_items):
                    title, copy, target_page, button_label = row_items[index]
                    render_menu_card(title, copy, target_page, button_label)
                else:
                    st.markdown('<div class="menu-card-empty"></div>', unsafe_allow_html=True)
