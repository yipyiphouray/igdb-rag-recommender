from __future__ import annotations

import streamlit as st

import _path_setup  # noqa: F401
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
    "Review",
]


PERSONAS = {
    "Cozy Switch": {
        "platform": "Nintendo Switch",
        "genres": ["Puzzle", "Adventure"],
        "themes": ["Kids", "Fantasy"],
        "discovery": "Balanced",
        "rating": "Good or better (70+)",
        "playtime": "Shorter games",
    },
    "Long fantasy RPG": {
        "platform": "PC (Microsoft Windows)",
        "genres": ["Role-playing (RPG)"],
        "themes": ["Fantasy", "Open world"],
        "discovery": "Balanced",
        "rating": "Highly rated (80+)",
        "playtime": "Longer games",
    },
    "Hidden indie gem": {
        "platform": "No platform preference",
        "genres": ["Indie", "Adventure"],
        "themes": ["Mystery"],
        "discovery": "Hidden gems",
        "rating": "Good or better (70+)",
        "playtime": "Any length",
    },
    "Popular action": {
        "platform": "PlayStation 5",
        "genres": ["Shooter", "Adventure"],
        "themes": ["Action"],
        "discovery": "Popular / visible games",
        "rating": "Good or better (70+)",
        "playtime": "Medium games",
    },
}


def _valid_values(options: dict[str, object], key: str, values: list[str]) -> list[str]:
    available = set(options.get(key, []))
    return [value for value in values if value in available]


def _valid_platform(options: dict[str, object], platform: str) -> str:
    if platform == "No platform preference":
        return platform
    return platform if platform in set(options.get("platforms", [])) else "No platform preference"


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
        "rec_confirmed": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _reset_wizard(min_year: int, max_year: int) -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("rec_") or key == "recommendation_step":
            del st.session_state[key]
    _init_state(min_year, max_year)
    st.rerun()


def _apply_persona(name: str, options: dict[str, object], min_year: int, max_year: int) -> None:
    persona = PERSONAS[name]
    st.session_state.rec_platform = _valid_platform(options, persona["platform"])
    st.session_state.rec_genres = _valid_values(options, "genres", persona["genres"])
    st.session_state.rec_themes = _valid_values(options, "themes", persona["themes"])
    st.session_state.rec_discovery = persona["discovery"]
    st.session_state.rec_rating = persona["rating"]
    st.session_state.rec_playtime = persona["playtime"]
    st.session_state.rec_year_range = (min_year, max_year)
    st.session_state.rec_top_n = 10
    st.session_state.recommendation_step = len(STEP_LABELS) - 1
    st.session_state.rec_confirmed = False
    st.rerun()


def _preference_summary_html() -> str:
    platform = st.session_state.rec_platform
    platform_label = "Any platform" if platform == "No platform preference" else platform
    genres = ", ".join(st.session_state.rec_genres) or "Any"
    themes = ", ".join(st.session_state.rec_themes) or "Any"
    return f"""
    <div class="insight-panel compact-summary">
      <div class="method-section-title">Review your picks</div>
      <div class="method-section-body">
        Platform: {html_escape(platform_label)}<br>
        Genres: {html_escape(genres)}<br>
        Themes: {html_escape(themes)}<br>
        Discovery: {html_escape(st.session_state.rec_discovery)}<br>
        Quality: {html_escape(st.session_state.rec_rating)}<br>
        Playtime: {html_escape(st.session_state.rec_playtime)}<br>
        Years: {html_escape(st.session_state.rec_year_range[0])}-{html_escape(st.session_state.rec_year_range[1])}<br>
        Results: {html_escape(st.session_state.rec_top_n)}
      </div>
    </div>
    """


def _render_personas(options: dict[str, object], min_year: int, max_year: int) -> None:
    st.markdown('<div class="section-kicker">Quick starts</div>', unsafe_allow_html=True)
    columns = st.columns(4)
    for index, name in enumerate(PERSONAS):
        with columns[index]:
            if st.button(name):
                _apply_persona(name, options, min_year, max_year)


def _render_current_step(options: dict[str, object], min_year: int, max_year: int) -> None:
    step = int(st.session_state.recommendation_step)
    label = STEP_LABELS[step]
    st.progress((step + 1) / len(STEP_LABELS), text=f"Step {step + 1} of {len(STEP_LABELS)}")

    _, center, _ = st.columns([1, 2.2, 1])
    with center:
        st.markdown(
            f"""
            <div class="wizard-panel question-card">
              <div class="wizard-step-label">{html_escape(label)}</div>
              <div class="method-section-body">Make one choice, then continue.</div>
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
                "What discovery style do you want?",
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
        elif step == 7:
            st.markdown(_preference_summary_html(), unsafe_allow_html=True)


def _navigation_buttons(min_year: int, max_year: int) -> bool:
    step = int(st.session_state.recommendation_step)
    final_step = len(STEP_LABELS) - 1

    _, center, _ = st.columns([1, 2.2, 1])
    with center:
        back_col, next_col, reset_col = st.columns([1, 1.4, 1])
        with back_col:
            if st.button("Back", disabled=step == 0):
                st.session_state.recommendation_step = max(step - 1, 0)
                st.session_state.rec_confirmed = False
                st.rerun()
        with next_col:
            if step < final_step:
                if st.button("Next"):
                    st.session_state.recommendation_step = min(step + 1, final_step)
                    st.session_state.rec_confirmed = False
                    st.rerun()
            elif st.button("Confirm picks"):
                st.session_state.rec_confirmed = True
        with reset_col:
            if st.button("Reset"):
                _reset_wizard(min_year, max_year)

    return bool(st.session_state.get("rec_confirmed", False))


st.set_page_config(page_title="Recommendations", page_icon="🎯", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Recommendation wizard</div>', unsafe_allow_html=True)
st.title("Guided Recommendations")
st.write("Start from a persona or answer one question at a time. Review your picks before results appear.")

try:
    catalog = load_app_catalog()
    options = load_filter_options()
except FileNotFoundError:
    st.error("App-ready catalog is missing. Run `python src/pipeline/build_app_catalog.py` first.")
    st.stop()

years = options.get("release_years") or sorted(catalog["release_year"].dropna().astype(int).unique().tolist())
min_year, max_year = int(min(years)), int(max(years))
_init_state(min_year, max_year)

_render_personas(options, min_year, max_year)
st.divider()
_render_current_step(options, min_year, max_year)
ready = _navigation_buttons(min_year, max_year)

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
        render_empty_state(
            "No recommendations matched your picks.",
            [
                "Go back and choose Any rating.",
                "Remove one genre or theme.",
                "Choose No platform preference.",
                "Expand the release-year range.",
            ],
        )
    else:
        st.metric("Recommendations returned", f"{len(results):,}")
        render_game_results(results, view_mode="Grid View", show_explanation=True)
else:
    st.info("Confirm your picks on the Review step to generate recommendations.")
