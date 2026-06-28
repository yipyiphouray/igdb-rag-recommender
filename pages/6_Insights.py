from __future__ import annotations

import pandas as pd
import streamlit as st

from src.app import config
from src.app.components.chart_helpers import render_bar_chart
from src.app.components.methodology_notice import render_sample_caveat
from src.app.components.metric_cards import render_metric_row
from src.app.components.ui_style import inject_global_styles
from src.app.data_loader import load_app_catalog, load_csv_artifact, load_hidden_gems, load_json_artifact


def _first_value(df: pd.DataFrame, column: str, default: object = "N/A") -> object:
    if df.empty or column not in df:
        return default
    return df.iloc[0][column]


def _filter_equal(df: pd.DataFrame, **filters: str) -> pd.DataFrame:
    if df.empty:
        return df
    mask = pd.Series(True, index=df.index)
    for column, expected in filters.items():
        if column not in df:
            return df.iloc[0:0]
        mask = mask & (df[column] == expected)
    return df[mask]


st.set_page_config(page_title="Insights", page_icon="📊", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Data nerds only</div>', unsafe_allow_html=True)
st.title("Descriptive & Diagnostic Insights")
st.write("This page summarizes the notebook findings behind the product experience.")

catalog = load_app_catalog()
hidden_gems = load_hidden_gems()
metrics = load_json_artifact(config.APP_METHODOLOGY_METRICS_PATH)

rating_coverage = load_csv_artifact(config.DESCRIPTIVE_DIR / "rating_coverage.csv")
relationship_coverage = load_csv_artifact(config.DESCRIPTIVE_DIR / "relationship_coverage.csv")
top_genres = load_csv_artifact(config.DESCRIPTIVE_DIR / "top_genres.csv")
top_platforms = load_csv_artifact(config.DESCRIPTIVE_DIR / "top_platforms.csv")
quality_popscore = load_csv_artifact(config.DIAGNOSTIC_DIR / "quality_popscore_correlation.csv")
user_critic = load_csv_artifact(config.DIAGNOSTIC_DIR / "user_critic_agreement_summary.csv")
hidden_sensitivity = load_csv_artifact(config.DIAGNOSTIC_DIR / "hidden_gem_sensitivity_analysis.csv")
diagnostic_takeaways = load_csv_artifact(config.DIAGNOSTIC_DIR / "diagnostic_takeaways.csv")

render_metric_row(
    [
        ("Games", f"{len(catalog):,}", "Curated analytical sample"),
        ("Rated games", f"{int(catalog['rating_available_flag'].sum()):,}", "total_rating available"),
        ("Reliable-rated games", f"{int(catalog['rating_reliable_flag'].sum()):,}", "total_rating_count >= 25"),
        ("Hidden gems", f"{len(hidden_gems):,}", "Balanced diagnostic definition"),
    ]
)

tabs = st.tabs(["Descriptive Snapshot", "Diagnostic Signals", "Hidden-Gem Lab", "Coverage & Caveats"])

with tabs[0]:
    st.subheader("What does the catalog look like?")
    st.write(
        "The descriptive layer summarizes what exists in the current project sample: genres, platforms, rating coverage, "
        "metadata coverage, companies, media, and optional gameplay fields."
    )
    col1, col2 = st.columns(2)
    with col1:
        render_bar_chart(top_genres.head(10), "genre_name", "game_count", "Top genres")
    with col2:
        render_bar_chart(top_platforms.head(10), "platform_name", "game_count", "Top platforms")

    if not rating_coverage.empty:
        row = rating_coverage.iloc[0]
        render_metric_row(
            [
                ("Total rating coverage", f"{int(row['games_with_total_rating']):,}", "Games with total_rating"),
                ("User rating coverage", f"{int(row['games_with_user_rating']):,}", "Games with IGDB user rating"),
                ("Critic rating coverage", f"{int(row['games_with_critic_rating']):,}", "Games with critic rating"),
            ]
        )

with tabs[1]:
    st.subheader("What relationships explain the catalog better?")
    st.write(
        "Diagnostic analytics keeps quality, rating activity, and visibility separate. The strongest user/critic result "
        "is agreement between user and critic ratings; PopScore has a positive but moderate relationship with quality."
    )
    spearman = _filter_equal(quality_popscore, scope_type="overall", method="spearman")
    user_spearman = _filter_equal(user_critic, metric="user_critic_spearman_correlation")
    render_metric_row(
        [
            (
                "Quality vs visibility",
                f"{float(_first_value(spearman, 'coefficient', 0)):.3f}",
                "Spearman rho: total_rating vs PopScore interest",
            ),
            (
                "User vs critic agreement",
                f"{float(_first_value(user_spearman, 'value', 0)):.3f}",
                "Spearman rho",
            ),
            ("Diagnostic takeaways", f"{len(diagnostic_takeaways):,}", "Notebook-level finding summaries"),
        ]
    )
    st.dataframe(diagnostic_takeaways, width="stretch", hide_index=True)

with tabs[2]:
    st.subheader("Hidden-gem lab")
    st.write(
        "The default Balanced list is the finalized diagnostic artifact. Conservative and Broad variants are useful for "
        "sensitivity checks, not replacements for the documented definition."
    )
    st.dataframe(hidden_sensitivity, width="stretch", hide_index=True)
    st.dataframe(
        hidden_gems[
            [
                "name",
                "release_year",
                "total_rating",
                "total_rating_count",
                "visibility_percentile_eligible_pool",
                "genres",
                "platforms",
            ]
        ].head(25),
        width="stretch",
        hide_index=True,
    )

with tabs[3]:
    st.subheader("Coverage and caveats")
    render_sample_caveat()
    st.write(
        "Optional fields are availability-dependent. Missing multiplayer detail, playtime, or PopScore should usually be "
        "read as unknown, not as a negative game attribute."
    )
    if not relationship_coverage.empty:
        render_bar_chart(relationship_coverage.head(12), "relationship", "coverage_rate", "Relationship coverage rate")
    with st.expander("Methodology metrics JSON"):
        st.json(metrics)
