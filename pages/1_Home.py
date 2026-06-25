from __future__ import annotations

import streamlit as st

from src.app import config
from src.app.components.game_card import render_game_card
from src.app.components.methodology_notice import render_sample_caveat, render_signal_caveat
from src.app.components.metric_cards import render_metric_row
from src.app.data_loader import load_app_catalog, load_hidden_gems, load_json_artifact


st.set_page_config(
    page_title="Home | IGDB Game Discovery",
    page_icon="🎮",
    layout="wide",
)

st.title("IGDB Game Discovery & RAG Recommendation System")
st.caption(
    "A Streamlit MVP for catalog exploration, hidden-gem discovery, structured recommendations, "
    "and teammate predictive/RAG integration."
)

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
            f"{metrics.get('release_year_start')}–{metrics.get('release_year_end')}",
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

render_sample_caveat()
render_signal_caveat()

st.subheader("Start here")

cols = st.columns(4)
cols[0].page_link("pages/2_Explore_Games.py", label="Explore games", icon="🔎")
cols[1].page_link("pages/3_Hidden_Gems.py", label="Find hidden gems", icon="💎")
cols[2].page_link("pages/4_Recommendations.py", label="Get recommendations", icon="🎯")
cols[3].page_link("pages/5_Chatbot.py", label="Ask chatbot", icon="💬")

st.subheader("Featured hidden-gem candidates")

if hidden_gems.empty:
    st.info("No hidden-gem artifact available yet.")
else:
    for _, row in hidden_gems.head(3).iterrows():
        render_game_card(row, show_explanation=True)
