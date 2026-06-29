from __future__ import annotations

import streamlit as st

from src.app.components.empty_state import render_empty_state
from src.app.components.game_card import VIEW_MODES, render_game_results
from src.app.components.ui_style import inject_global_styles
from src.app.data_loader import load_app_catalog, load_filter_options, load_hidden_gems
from src.app.formatting import html_escape
from src.app.hidden_gem_service import filter_hidden_gems, hidden_gem_rule_text


st.set_page_config(page_title="Hidden Gems", page_icon="💎", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Low-visibility discovery</div>', unsafe_allow_html=True)
st.title("Hidden Gems")
st.write(
    "Hidden gems are reliable high-rated quality-cohort games with known lower visibility inside their release year. "
    "This is a within-sample discovery signal, not a claim about the full video game market."
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
    st.header("Hidden-gem controls")
    sensitivity = st.radio("Sensitivity", ["Balanced", "Conservative", "Broad"])
    year_range = st.slider("Release year", min_year, max_year, (min_year, max_year))
    platforms = st.multiselect("Platforms", options.get("platforms", []))
    genres = st.multiselect("Genres", options.get("genres", []))
    themes = st.multiselect("Themes", options.get("themes", []))
    min_rating = st.slider("Minimum total rating", 75, 100, 80)
    min_rating_count = st.slider("Minimum rating evidence", 25, 500, 25)
    result_limit = st.slider("Candidates to show", 5, 100, 25)

st.markdown(
    f"""
    <div class="rule-box">
      <div class="rule-box-title">Current hidden-gem rule</div>
      <div class="rule-box-body">{html_escape(hidden_gem_rule_text(sensitivity))}</div>
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
    render_empty_state("No hidden-gem candidates matched the current controls.")
else:
    render_game_results(filtered.head(result_limit), view_mode=view_mode, show_explanation=True)
