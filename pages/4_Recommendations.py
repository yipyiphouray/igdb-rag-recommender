from __future__ import annotations

import streamlit as st

from src.app.components.empty_state import render_empty_state
from src.app.components.game_card import render_game_card
from src.app.components.ui_style import inject_global_styles
from src.app.constants import RATING_LEVELS
from src.app.data_loader import load_app_catalog, load_filter_options
from src.app.recommendation_service import recommend_games


st.set_page_config(page_title="Recommendations", page_icon="🎯", layout="wide")
inject_global_styles()

st.title("Guided Recommendations")
st.write("Answer a few preference questions. The app will apply hard constraints, rank matching games, and explain why each result fits.")

try:
    catalog = load_app_catalog()
    options = load_filter_options()
except FileNotFoundError:
    st.error("App-ready catalog is missing. Run `python src/pipeline/build_app_catalog.py` first.")
    st.stop()

years = options.get("release_years") or sorted(catalog["release_year"].dropna().astype(int).unique().tolist())
min_year, max_year = int(min(years)), int(max(years))

with st.form("guided_recommendation_form"):
    st.markdown('<div class="section-kicker">Preference form</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    platform = col1.selectbox("What platform do you play on?", [""] + options.get("platforms", []))
    genres = col1.multiselect("What kind of game are you in the mood for? Pick genres.", options.get("genres", []))
    themes = col2.multiselect("What themes or vibes sound right?", options.get("themes", []))
    discovery_preference = col2.radio(
        "Do you prefer popular games or hidden gems?",
        ["Balanced", "Hidden gems", "Popular / visible games"],
        horizontal=True,
    )

    rating_level = col1.selectbox("How important is rating quality?", list(RATING_LEVELS.keys()), index=0)
    desired_playtime = col2.selectbox(
        "Do you want shorter or longer games?",
        ["Any length", "Shorter games", "Medium games", "Longer games"],
    )
    year_range = st.slider("Release year range", min_year, max_year, (min_year, max_year))
    top_n = st.slider("How many recommendations do you want?", 3, 25, 10)

    submitted = st.form_submit_button("Show me recommendations")

with st.expander("How scoring works"):
    st.write(
        "Platform is a hard gate when selected. The MVP score then rewards genre match, theme match, observed quality, "
        "rating evidence, optional hidden-gem preference, optional visibility preference, and optional playtime fit."
    )
    st.code(
        """MVP score components:
genre match:          up to 30
theme match:          up to 20
quality score:        up to 15
rating evidence:      up to 5
hidden-gem boost:     up to 10 when selected
popular/visible bias: up to 5 when selected
playtime fit:         up to 5 when selected""",
        language="text",
    )

if submitted:
    results = recommend_games(
        catalog,
        platform=platform or None,
        genres=genres,
        themes=themes,
        release_year_range=year_range,
        rating_level=rating_level,
        prefer_hidden_gems=discovery_preference == "Hidden gems",
        discovery_preference=discovery_preference,
        desired_playtime=desired_playtime,
        top_n=top_n,
    )

    if results.empty:
        render_empty_state("No recommendations matched the required constraints.")
    else:
        st.metric("Recommendations returned", f"{len(results):,}")
        for _, row in results.iterrows():
            render_game_card(row, show_explanation=True)
else:
    st.info("Choose preferences and click `Show me recommendations`.")
