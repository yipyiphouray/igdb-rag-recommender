from __future__ import annotations

from src.app.formatting import html_escape


PAGE_URLS = {
    "pages/1_Home.py": "/Home",
    "pages/2_Explore_Games.py": "/Explore_Games",
    "pages/3_Hidden_Gems.py": "/Hidden_Gems",
    "pages/4_Recommendations.py": "/Recommendations",
    "pages/5_Chatbot.py": "/Chatbot",
    "pages/6_Insights.py": "/Insights",
    "pages/7_Predictive_Model.py": "/Predictive_Model",
    "pages/8_Methodology.py": "/Methodology",
}


def _page_url(target_page: str) -> str:
    if target_page.startswith("/"):
        return target_page
    return PAGE_URLS.get(target_page, target_page)


def render_menu_card(title: str, copy: str, target_page: str, button_label: str = "Press start") -> None:
    import streamlit as st

    st.markdown(
        f"""
        <a class="menu-card-link" href="{html_escape(_page_url(target_page))}" target="_self">
          <div class="menu-card-title">{html_escape(title)}</div>
          <div class="menu-card-copy">{html_escape(copy)}</div>
          <div class="menu-card-cta">{html_escape(button_label)}</div>
        </a>
        """,
        unsafe_allow_html=True,
    )
