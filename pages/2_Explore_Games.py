from __future__ import annotations

import streamlit as st

from src.app.components.empty_state import render_empty_state
from src.app.components.game_card import render_game_card
from src.app.components.methodology_notice import render_sample_caveat, render_signal_caveat
from src.app.data_loader import load_app_catalog, load_filter_options
from src.app.filters import apply_catalog_filters, sort_catalog


st.set_page_config(page_title="Explore Games", page_icon="🔎", layout="wide")
st.title("Explore Games")
render_signal_caveat()

try:
    catalog = load_app_catalog()
    options = load_filter_options()
except FileNotFoundError:
    st.error("App-ready catalog is missing. Run `python src/pipeline/build_app_catalog.py` first.")
    st.stop()

years = options.get("release_years") or sorted(catalog["release_year"].dropna().astype(int).unique().tolist())
min_year, max_year = int(min(years)), int(max(years))

with st.sidebar:
    st.header("Filters")
    search_text = st.text_input("Title or summary search")
    year_range = st.slider("Release year", min_year, max_year, (min_year, max_year))
    platforms = st.multiselect("Platforms", options.get("platforms", []))
    genres = st.multiselect("Genres", options.get("genres", []))
    themes = st.multiselect("Themes", options.get("themes", []))
    game_modes = st.multiselect("Game modes", options.get("game_modes", []))
    perspectives = st.multiselect("Perspectives", options.get("player_perspectives", []))
    cohorts = st.multiselect("Extraction cohorts", options.get("cohorts", []))
    min_rating = st.slider("Minimum total rating", 0, 100, 0)
    min_rating_count = st.slider("Minimum rating evidence", 0, 500, 0)
    hidden_only = st.checkbox("Hidden-gem candidates only")
    sort_option = st.selectbox(
        "Sort by",
        [
            "Highest rating",
            "Most rating evidence",
            "Highest visibility",
            "Newest release",
            "Lowest visibility among reliable high-rated games",
        ],
    )
    result_limit = st.slider("Results to show", 5, 100, 25)

filtered = apply_catalog_filters(
    catalog,
    search_text=search_text,
    release_year_range=year_range,
    platforms=platforms,
    genres=genres,
    themes=themes,
    game_modes=game_modes,
    perspectives=perspectives,
    cohorts=cohorts,
    min_rating=min_rating if min_rating else None,
    min_rating_count=min_rating_count if min_rating_count else None,
    hidden_gems_only=hidden_only,
)
filtered = sort_catalog(filtered, sort_option)

st.metric("Matching games", f"{len(filtered):,}")
render_sample_caveat()

if filtered.empty:
    render_empty_state()
else:
    for _, row in filtered.head(result_limit).iterrows():
        render_game_card(row)

