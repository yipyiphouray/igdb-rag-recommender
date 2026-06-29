from __future__ import annotations

import streamlit as st

from src.app.components.empty_state import render_empty_state
from src.app.components.game_card import render_game_results
from src.app.components.ui_style import inject_global_styles
from src.app.constants import RATING_LEVELS
from src.app.data_loader import load_app_catalog, load_filter_options
from src.app.formatting import html_escape
from src.app.recommendation_service import recommend_games


STEP_LABELS = [
    "Platform",
    "Genres",
    "Themes",
    "Discovery style",
    "Quality",
    "Playtime",
    "Release window",
]


def _init_state(min_year: int, max_year: int) -> None:
    defaults = {
        "recommendation_step": 0,
        "rec_platform": "No platform preference",
        "rec_genres": [],
        "rec_themes": [],
        "rec_discovery": "Balanced",
        "rec_rating": "Any rating",
        "rec_playtime": "Any length",
        "rec_year_range": (min_year, max_year),
        "rec_top_n": 10,
        "rec_ready": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _reset_wizard(min_year: int, max_year: int) -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("rec_") or key == "recommendation_step":
            del st.session_state[key]
    _init_state(min_year, max_year)
    st.rerun()


def _step_buttons(min_year: int, max_year: int) -> bool:
    step = int(st.session_state.recommendation_step)
    final_step = len(STEP_LABELS) - 1
    back_col, next_col, reset_col = st.columns([1, 1, 4])

    with back_col:
        if st.button("Back", disabled=step == 0):
            st.session_state.recommendation_step = max(step - 1, 0)
            st.session_state.rec_ready = False
            st.rerun()

    show_results = False
    with next_col:
        if step < final_step:
            if st.button("Next"):
                st.session_state.recommendation_step = min(step + 1, final_step)
                st.session_state.rec_ready = False
                st.rerun()
        elif st.button("Show recommendations"):
            st.session_state.rec_ready = True
            show_results = True

    with reset_col:
        if st.button("Reset wizard"):
            _reset_wizard(min_year, max_year)

    return show_results or bool(st.session_state.get("rec_ready", False))


def _render_current_step(options: dict[str, object], min_year: int, max_year: int) -> None:
    step = int(st.session_state.recommendation_step)
    label = STEP_LABELS[step]
    st.progress((step + 1) / len(STEP_LABELS), text=f"Step {step + 1} of {len(STEP_LABELS)}: {label}")

    st.markdown(
        f"""
        <div class="wizard-panel">
          <div class="wizard-step-label">{label}</div>
          <div class="method-section-body">Answer this question, then move to the next step.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if step == 0:
        st.selectbox(
            "What platform do you play on?",
            ["No platform preference"] + list(options.get("platforms", [])),
            key="rec_platform",
        )
    elif step == 1:
        st.multiselect(
            "What kind of game are you in the mood for?",
            list(options.get("genres", [])),
            key="rec_genres",
        )
    elif step == 2:
        st.multiselect(
            "What themes or vibes sound right?",
            list(options.get("themes", [])),
            key="rec_themes",
        )
    elif step == 3:
        st.radio(
            "Do you prefer popular games or hidden gems?",
            ["Balanced", "Hidden gems", "Popular / visible games"],
            horizontal=True,
            key="rec_discovery",
        )
    elif step == 4:
        st.selectbox("How important is rating quality?", list(RATING_LEVELS.keys()), key="rec_rating")
    elif step == 5:
        st.selectbox(
            "Do you want shorter or longer games?",
            ["Any length", "Shorter games", "Medium games", "Longer games"],
            key="rec_playtime",
        )
    elif step == 6:
        st.slider("Release year range", min_year, max_year, key="rec_year_range")
        st.slider("How many recommendations do you want?", 3, 25, key="rec_top_n")


def _render_summary() -> None:
    platform = st.session_state.rec_platform
    platform_label = "Any platform" if platform == "No platform preference" else platform
    genres = ", ".join(st.session_state.rec_genres) or "Any"
    themes = ", ".join(st.session_state.rec_themes) or "Any"
    st.markdown(
        f"""
        <div class="insight-panel">
          <div class="method-section-title">Current preference loadout</div>
          <div class="method-section-body">
            Platform: {html_escape(platform_label)}<br>
            Genres: {html_escape(genres)}<br>
            Themes: {html_escape(themes)}<br>
            Discovery: {html_escape(st.session_state.rec_discovery)}<br>
            Quality: {html_escape(st.session_state.rec_rating)}<br>
            Playtime: {html_escape(st.session_state.rec_playtime)}<br>
            Years: {html_escape(st.session_state.rec_year_range[0])}-{html_escape(st.session_state.rec_year_range[1])}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Recommendations", page_icon="🎯", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Recommendation wizard</div>', unsafe_allow_html=True)
st.title("Guided Recommendations")
st.write("Answer one preference question at a time. The app ranks matching catalog games and explains the result.")

try:
    catalog = load_app_catalog()
    options = load_filter_options()
except FileNotFoundError:
    st.error("App-ready catalog is missing. Run `python src/pipeline/build_app_catalog.py` first.")
    st.stop()

years = options.get("release_years") or sorted(catalog["release_year"].dropna().astype(int).unique().tolist())
min_year, max_year = int(min(years)), int(max(years))
_init_state(min_year, max_year)

_render_current_step(options, min_year, max_year)
ready = _step_buttons(min_year, max_year)
_render_summary()

st.markdown(
    """
    <div class="small-caveat">
      Scoring uses platform gating, genre/theme fit, observed rating, rating evidence, optional hidden-gem preference,
      optional visibility preference, and optional playtime fit. It does not invent games outside the catalog.
    </div>
    """,
    unsafe_allow_html=True,
)

if ready:
    selected_platform = st.session_state.rec_platform
    platform = None if selected_platform == "No platform preference" else selected_platform
    results = recommend_games(
        catalog,
        platform=platform,
        genres=st.session_state.rec_genres,
        themes=st.session_state.rec_themes,
        release_year_range=st.session_state.rec_year_range,
        rating_level=st.session_state.rec_rating,
        prefer_hidden_gems=st.session_state.rec_discovery == "Hidden gems",
        discovery_preference=st.session_state.rec_discovery,
        desired_playtime=st.session_state.rec_playtime,
        top_n=st.session_state.rec_top_n,
    )

    if results.empty:
        render_empty_state("No recommendations matched the selected preferences.")
    else:
        st.metric("Recommendations returned", f"{len(results):,}")
        render_game_results(results, view_mode="List View", show_explanation=True)
else:
    st.info("Use Next to move through the wizard. Recommendations appear on the final step.")
