from __future__ import annotations

import streamlit as st

import _path_setup  # noqa: F401
from src.app.components.empty_state import render_empty_state
from src.app.components.game_card import VIEW_MODES, render_game_results
from src.app.components.ui_style import inject_global_styles
from src.app.data_loader import load_app_catalog, load_filter_options, load_hidden_gems
from src.app.formatting import html_escape
from src.app.hidden_gem_service import filter_hidden_gems


DISCOVERY_MODES = {
    "Balanced discovery": {
        "sensitivity": "Balanced",
        "rating": 80,
        "rating_count": 25,
        "copy": "Good default. Shows strong games with enough rating activity and lower known visibility.",
    },
    "Strict hidden gems": {
        "sensitivity": "Conservative",
        "rating": 85,
        "rating_count": 25,
        "copy": "Narrower list. Prioritizes very highly rated games with especially low known visibility.",
    },
    "More discoveries": {
        "sensitivity": "Broad",
        "rating": 75,
        "rating_count": 25,
        "copy": "Broader list. Good when you want more options and are comfortable exploring beyond the strictest picks.",
    },
}


st.set_page_config(page_title="Hidden Gems", page_icon="💎", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Low-visibility discovery</div>', unsafe_allow_html=True)
st.title("Hidden Gems")
st.write(
    "Find well-received games that may be easier to miss. Start with a discovery style, then narrow by year, platform, genre, or theme."
)

try:
    catalog = load_app_catalog()
    hidden_gems = load_hidden_gems()
    options = load_filter_options()
except FileNotFoundError:
    st.error("Hidden-gem app artifact is missing. Run `python src/pipeline/build_app_catalog.py` first.")
    st.stop()

years = options.get("release_years") or sorted(catalog["release_year"].dropna().astype(int).unique().tolist())
min_year, max_year = int(min(years)), int(max(years))

with st.sidebar:
    st.header("Display")
    view_mode = st.radio("View type", VIEW_MODES, index=0)
    st.divider()
    st.header("Discovery style")
    mode_label = st.radio("How adventurous should the search be?", list(DISCOVERY_MODES.keys()))
    mode = DISCOVERY_MODES[mode_label]
    sensitivity = mode["sensitivity"]
    st.divider()
    st.header("Tune results")
    year_range = st.slider("Release year", min_year, max_year, (min_year, max_year))
    platforms = st.multiselect("Platforms", options.get("platforms", []))
    genres = st.multiselect("Genres", options.get("genres", []))
    themes = st.multiselect("Themes", options.get("themes", []))
    min_rating = st.slider("Minimum rating score", 75, 100, mode["rating"])
    min_rating_count = st.slider("Minimum rating activity", 25, 500, mode["rating_count"])
    result_limit = st.slider("Candidates to show", 5, 100, 25)

st.markdown(
    f"""
    <div class="rule-box">
      <div class="rule-box-title">How this page picks games</div>
      <div class="rule-box-body">{html_escape(mode["copy"])} The exact formula and caveats live in Methodology.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

filtered = filter_hidden_gems(
    hidden_gems,
    catalog=catalog,
    sensitivity=sensitivity,
    release_year_range=year_range,
    platforms=platforms,
    genres=genres,
    themes=themes,
    min_rating=min_rating,
    min_rating_count=min_rating_count,
)

st.metric("Matching hidden-gem candidates", f"{len(filtered):,}")

if filtered.empty:
    render_empty_state(
        "No hidden-gem candidates matched this setup.",
        [
            "Switch to More discoveries.",
            "Lower the minimum rating score or rating activity.",
            "Remove one platform, genre, or theme filter.",
            "Expand the release-year range.",
        ],
    )
else:
    render_game_results(filtered.head(result_limit), view_mode=view_mode, show_explanation=True)
