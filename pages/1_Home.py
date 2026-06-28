from __future__ import annotations

import streamlit as st

from src.app import config
from src.app.components.menu_card import render_menu_card
from src.app.components.methodology_notice import render_sample_footnote
from src.app.components.metric_cards import render_metric_row
from src.app.components.ui_style import inject_global_styles
from src.app.data_loader import load_app_catalog, load_hidden_gems, load_json_artifact


st.set_page_config(
    page_title="Home | IGDB Game Discovery",
    page_icon="🎮",
    layout="wide",
)
inject_global_styles()

st.markdown('<div class="section-kicker">Game discovery menu</div>', unsafe_allow_html=True)
st.title("IGDB Game Discovery")
st.caption("Choose the path that matches what you want to do next.")

try:
    catalog = load_app_catalog()
    hidden_gems = load_hidden_gems()
    metrics = load_json_artifact(config.APP_METHODOLOGY_METRICS_PATH)
except FileNotFoundError:
    st.error("App-ready data artifacts are missing.")
    st.code("python src/pipeline/build_app_catalog.py", language="bash")
    st.stop()

render_metric_row(
    [
        ("Games", f"{int(metrics.get('total_games', len(catalog))):,}", "Curated IGDB project sample"),
        (
            "Release years",
            f"{metrics.get('release_year_start')}-{metrics.get('release_year_end')}",
            "Balanced yearly sample",
        ),
        ("Hidden gems", f"{len(hidden_gems):,}", "Balanced diagnostic hidden-gem candidates"),
        (
            "Reliable-rated share",
            f"{metrics.get('reliable_rating_coverage', 0) * 100:.1f}%",
            "total_rating_count >= 25",
        ),
    ]
)

st.divider()

row1 = st.columns(3)
with row1[0]:
    render_menu_card(
        "Explore Games",
        "Browse the catalog with platform, genre, theme, rating, and release-year controls.",
        "pages/2_Explore_Games.py",
        "Open Explore Games",
    )
with row1[1]:
    render_menu_card(
        "Hidden Gems",
        "Find reliable high-rated games with lower known visibility inside the project sample.",
        "pages/3_Hidden_Gems.py",
        "Open Hidden Gems",
    )
with row1[2]:
    render_menu_card(
        "Recommendations",
        "Answer guided preference questions and get ranked, explainable suggestions.",
        "pages/4_Recommendations.py",
        "Open Recommendations",
    )

row2 = st.columns(4)
with row2[0]:
    render_menu_card("Insights", "For the data nerds: descriptive and diagnostic findings.", "pages/6_Insights.py", "Open Insights")
with row2[1]:
    render_menu_card("Methodology", "Sources, formulas, caveats, and calculation logic.", "pages/8_Methodology.py", "Open Methodology")
with row2[2]:
    render_menu_card("Chatbot", "Placeholder for teammate RAG integration.", "pages/5_Chatbot.py", "Open Chatbot")
with row2[3]:
    render_menu_card("Predictive Model", "Placeholder for teammate predictive artifacts.", "pages/7_Predictive_Model.py", "Open Predictive Model")

render_sample_footnote()
