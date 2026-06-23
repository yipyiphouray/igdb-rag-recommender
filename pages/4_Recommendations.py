from __future__ import annotations

import streamlit as st

from src.app.components.empty_state import render_empty_state
from src.app.components.game_card import render_game_card
from src.app.components.methodology_notice import render_signal_caveat
from src.app.constants import RATING_LEVELS
from src.app.data_loader import load_app_catalog, load_filter_options
from src.app.recommendation_service import recommend_games


st.set_page_config(page_title="Recommendations", page_icon="🎯", layout="wide")
st.title("Structured Recommendations")
st.write("MVP rule-based recommendations using platform gates, genre/theme fit, quality, rating evidence, and hidden-gem boost.")
render_signal_caveat()

try:
    catalog = load_app_catalog()
    options = load_filter_options()
except FileNotFoundError:
    st.error("App-ready catalog is missing. Run `python src/pipeline/build_app_catalog.py` first.")
    st.stop()

years = options.get("release_years") or sorted(catalog["release_year"].dropna().astype(int).unique().tolist())
min_year, max_year = int(min(years)), int(max(years))

with st.form("recommendation_form"):
    col1, col2 = st.columns(2)
    platform = col1.selectbox("Required platform", [""] + options.get("platforms", []))
    genres = col1.multiselect("Preferred genres", options.get("genres", []))
    themes = col2.multiselect("Preferred themes / mood", options.get("themes", []))
    year_range = col2.slider("Release year", min_year, max_year, (min_year, max_year))
    rating_level = col1.selectbox("Desired quality level", list(RATING_LEVELS.keys()), index=0)
    prefer_hidden_gems = col2.checkbox("Boost hidden-gem candidates")
    top_n = st.slider("Number of recommendations", 3, 25, 10)
    submitted = st.form_submit_button("Generate recommendations")

if submitted:
    results = recommend_games(
        catalog,
        platform=platform or None,
        genres=genres,
        themes=themes,
        release_year_range=year_range,
        rating_level=rating_level,
        prefer_hidden_gems=prefer_hidden_gems,
        top_n=top_n,
    )

    if results.empty:
        render_empty_state("No recommendations matched the required constraints.")
    else:
        st.metric("Recommendations returned", f"{len(results):,}")
        for _, row in results.iterrows():
            render_game_card(row, show_explanation=True)
else:
    st.info("Choose preferences and generate recommendations.")

