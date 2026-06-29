from __future__ import annotations

import streamlit as st

from src.app.components.menu_card import render_menu_card
from src.app.components.ui_style import inject_global_styles


st.set_page_config(
    page_title="Home | IGDB Game Discovery",
    page_icon="🎮",
    layout="wide",
)
inject_global_styles()

st.markdown(
    """
    <div class="cyber-hero">
      <div class="section-kicker">Cyberpunk game menu</div>
      <div class="cyber-title">IGDB Arcade</div>
      <div class="cyber-subtitle">Select a mode. Hover to preview. Click anywhere on a panel to enter.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

row1 = st.columns(3)
with row1[0]:
    render_menu_card(
        "Explore Games",
        "Browse the curated catalog with platform, genre, theme, rating, release-year, cohort, and hidden-gem controls.",
        "pages/2_Explore_Games.py",
        "Enter catalog",
    )
with row1[1]:
    render_menu_card(
        "Hidden Gems",
        "Find reliable high-rated games with lower known visibility inside the project sample.",
        "pages/3_Hidden_Gems.py",
        "Enter gems",
    )
with row1[2]:
    render_menu_card(
        "Recommendations",
        "Use a step-by-step preference wizard to get ranked and explainable game suggestions.",
        "pages/4_Recommendations.py",
        "Start wizard",
    )

row2 = st.columns(4)
with row2[0]:
    render_menu_card("Insights", "Deep descriptive and diagnostic analytics.", "pages/6_Insights.py", "Open data room")
with row2[1]:
    render_menu_card("Methodology", "Source data, formulas, caveats, and limits.", "pages/8_Methodology.py", "Open trust layer")
with row2[2]:
    render_menu_card("Chatbot", "Placeholder for teammate RAG integration.", "pages/5_Chatbot.py", "Open shell")
with row2[3]:
    render_menu_card("Predictive Model", "Placeholder for teammate predictive artifacts.", "pages/7_Predictive_Model.py", "Open model shell")
