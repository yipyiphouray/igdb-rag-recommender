from __future__ import annotations

import streamlit as st

from src.app.components.home_menu import render_home_menu
from src.app.components.ui_style import inject_global_styles


MENU_ITEMS = [
    (
        "Explore Games",
        "Browse the curated catalog with filters, sorting, and visual result layouts.",
        "pages/2_Explore_Games.py",
        "Enter catalog",
    ),
    (
        "Hidden Gems",
        "Find strong games that may be easier to miss in the broader catalog.",
        "pages/3_Hidden_Gems.py",
        "Enter gems",
    ),
    (
        "Recommendations",
        "Answer a few guided questions and get explainable game suggestions.",
        "pages/4_Recommendations.py",
        "Start wizard",
    ),
    (
        "Insights",
        "Open the deep descriptive and diagnostic analytics room.",
        "pages/6_Insights.py",
        "Open data room",
    ),
    (
        "Methodology",
        "Review sources, formulas, caveats, and implementation boundaries.",
        "pages/8_Methodology.py",
        "Open trust layer",
    ),
    (
        "Chatbot",
        "Placeholder page for teammate RAG integration and natural-language discovery.",
        "pages/5_Chatbot.py",
        "Open shell",
    ),
    (
        "Predictive Model",
        "Placeholder page for teammate model outputs and interpretation.",
        "pages/7_Predictive_Model.py",
        "Open model shell",
    ),
]


st.set_page_config(
    page_title="IGDB Game Discovery",
    page_icon="🎮",
    layout="wide",
)
inject_global_styles()

st.markdown(
    """
    <div class="cyber-hero">
      <div class="cyber-title">IGDB Arcade</div>
      <div class="cyber-subtitle">Hover to preview. Click any panel to enter.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_home_menu(MENU_ITEMS, columns_per_row=3)
