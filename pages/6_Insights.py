from __future__ import annotations

import streamlit as st

from src.app import config
from src.app.components.chart_helpers import render_bar_chart
from src.app.components.methodology_notice import render_sample_caveat, render_signal_caveat
from src.app.components.metric_cards import render_metric_row
from src.app.data_loader import load_app_catalog, load_csv_artifact, load_hidden_gems, load_json_artifact


st.set_page_config(page_title="Insights", page_icon="📊", layout="wide")
st.title("Descriptive & Diagnostic Insights")
render_sample_caveat()
render_signal_caveat()

catalog = load_app_catalog()
hidden_gems = load_hidden_gems()
metrics = load_json_artifact(config.APP_METHODOLOGY_METRICS_PATH)

render_metric_row(
    [
        ("Games", f"{len(catalog):,}", None),
        ("Rated games", f"{int(catalog['rating_available_flag'].sum()):,}", None),
        ("Reliable-rated games", f"{int(catalog['rating_reliable_flag'].sum()):,}", "total_rating_count >= 25"),
        ("Hidden gems", f"{len(hidden_gems):,}", "Balanced diagnostic definition"),
    ]
)

tabs = st.tabs(["Catalog Overview", "Reception and Visibility", "Hidden Gems", "Coverage and Limits"])

with tabs[0]:
    top_genres = load_csv_artifact(config.DESCRIPTIVE_DIR / "top_genres.csv").head(10)
    top_platforms = load_csv_artifact(config.DESCRIPTIVE_DIR / "top_platforms.csv").head(10)
    col1, col2 = st.columns(2)
    with col1:
        render_bar_chart(top_genres, "genre_name", "game_count", "Top genres")
    with col2:
        render_bar_chart(top_platforms, "platform_name", "game_count", "Top platforms")

with tabs[1]:
    st.subheader("Quality, rating evidence, and visibility")
    st.write(
        "The diagnostic notebook found a moderate positive association between quality and PopScore visibility, "
        "but visibility and quality are not the same concept."
    )
    st.dataframe(load_csv_artifact(config.DIAGNOSTIC_DIR / "quality_popscore_correlation.csv"))
    st.dataframe(load_csv_artifact(config.DIAGNOSTIC_DIR / "user_critic_agreement_summary.csv"))

with tabs[2]:
    st.subheader("Hidden-gem candidates")
    st.write(
        "Balanced hidden gems are reliable high-rated quality-cohort games with low known visibility within their release year."
    )
    st.dataframe(hidden_gems[["name", "release_year", "total_rating", "total_rating_count", "custom_interest_percentile"]].head(25))

with tabs[3]:
    st.subheader("Coverage and limitations")
    st.json(metrics)
    st.write(
        "Missing optional metadata should usually be read as unknown. Multiplayer details, time-to-beat, and PopScore "
        "coverage are availability-dependent."
    )

