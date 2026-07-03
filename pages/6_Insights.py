from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.app import config
from src.app.components.chart_helpers import render_bar_chart
from src.app.components.metric_cards import render_metric_row
from src.app.components.ui_style import inject_global_styles
from src.app.data_loader import load_app_catalog, load_csv_artifact


DESCRIPTIVE_EXPORTS = {
    "KPI snapshot": config.DESCRIPTIVE_DIR / "kpi_snapshot.csv",
    "Games by release year": config.DESCRIPTIVE_DIR / "games_by_release_year.csv",
    "Games by release decade": config.DESCRIPTIVE_DIR / "games_by_release_decade.csv",
    "Rating bands": config.DESCRIPTIVE_DIR / "rating_bands.csv",
    "Top genres": config.DESCRIPTIVE_DIR / "top_genres.csv",
    "Top themes": config.DESCRIPTIVE_DIR / "top_themes.csv",
    "Top platforms": config.DESCRIPTIVE_DIR / "top_platforms.csv",
    "Platform families": config.DESCRIPTIVE_DIR / "platform_family_distribution.csv",
    "Platform types": config.DESCRIPTIVE_DIR / "platform_type_distribution.csv",
    "Game modes": config.DESCRIPTIVE_DIR / "game_mode_distribution.csv",
    "Player perspectives": config.DESCRIPTIVE_DIR / "player_perspective_distribution.csv",
    "Playtime bands": config.DESCRIPTIVE_DIR / "playtime_band_distribution.csv",
    "Playtime by game": config.DESCRIPTIVE_DIR / "playtime_by_game.csv",
    "Top developers": config.DESCRIPTIVE_DIR / "top_developers.csv",
    "Top publishers": config.DESCRIPTIVE_DIR / "top_publishers.csv",
    "Top keywords": config.DESCRIPTIVE_DIR / "top_keywords.csv",
}

DIAGNOSTIC_EXPORTS = {
    "Diagnostic takeaways": config.DIAGNOSTIC_DIR / "diagnostic_takeaways.csv",
    "Quality vs visibility correlation": config.DIAGNOSTIC_DIR / "quality_popscore_correlation.csv",
    "Quality vs rating activity correlation": config.DIAGNOSTIC_DIR / "quality_rating_activity_correlation.csv",
    "User critic agreement": config.DIAGNOSTIC_DIR / "user_critic_agreement_summary.csv",
    "Genre rating summary": config.DIAGNOSTIC_DIR / "genre_rating_summary.csv",
    "Theme rating summary": config.DIAGNOSTIC_DIR / "theme_rating_summary.csv",
    "Genre-theme rating summary": config.DIAGNOSTIC_DIR / "genre_theme_rating_summary.csv",
    "Platform family rating summary": config.DIAGNOSTIC_DIR / "platform_family_rating_summary.csv",
    "Platform type rating summary": config.DIAGNOSTIC_DIR / "platform_type_rating_summary.csv",
    "Game mode rating summary": config.DIAGNOSTIC_DIR / "game_mode_rating_summary.csv",
    "Player perspective rating summary": config.DIAGNOSTIC_DIR / "player_perspective_rating_summary.csv",
    "Playtime rating summary": config.DIAGNOSTIC_DIR / "playtime_rating_summary.csv",
    "User critic gap by genre": config.DIAGNOSTIC_DIR / "user_critic_gap_by_genre.csv",
    "User critic gap by theme": config.DIAGNOSTIC_DIR / "user_critic_gap_by_theme.csv",
    "User critic gap by release year": config.DIAGNOSTIC_DIR / "user_critic_gap_by_release_year.csv",
    "Cohort adjusted associations": config.DIAGNOSTIC_DIR / "cohort_adjusted_association_summary.csv",
}


def _first_value(df: pd.DataFrame, column: str, default: object = 0) -> object:
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


def _load(path: Path) -> pd.DataFrame:
    return load_csv_artifact(path)


def _table(df: pd.DataFrame, rows: int = 50) -> None:
    if df.empty:
        st.caption("No data available for this table.")
        return
    st.dataframe(df.head(rows), width="stretch", hide_index=True)


def _line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if df.empty or x not in df or y not in df:
        st.caption(f"No data available for {title}.")
        return
    st.subheader(title)
    st.line_chart(df.set_index(x)[y])


def _category_rating_table(df: pd.DataFrame, label_column: str, rows: int = 15) -> pd.DataFrame:
    columns = [
        label_column,
        "game_count",
        "median_total_rating",
        "median_total_rating_count",
        "high_rated_share",
        "odds_ratio",
        "adjusted_p_value",
        "fdr_significant",
    ]
    available = [column for column in columns if column in df.columns]
    if not available:
        return pd.DataFrame()
    sort_column = "median_total_rating" if "median_total_rating" in df.columns else available[0]
    return df[available].sort_values(sort_column, ascending=False, na_position="last").head(rows)


def _downloadable_table(label: str, df: pd.DataFrame, source_path: Path) -> None:
    st.subheader(label)
    _table(df, rows=200)
    if not df.empty:
        st.download_button(
            "Download full CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=source_path.name,
            mime="text/csv",
        )


st.set_page_config(page_title="Insights", page_icon="📊", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Data nerds only</div>', unsafe_allow_html=True)
st.title("Descriptive & Diagnostic Insights")
st.write(
    "This page exposes the descriptive and diagnostic notebook outputs in a deeper app-facing format. "
    "Hidden-gem and coverage-only analyses are intentionally excluded from this page."
)

catalog = load_app_catalog()

games_by_year = _load(config.DESCRIPTIVE_DIR / "games_by_release_year.csv")
rating_bands = _load(config.DESCRIPTIVE_DIR / "rating_bands.csv")
top_genres = _load(config.DESCRIPTIVE_DIR / "top_genres.csv")
top_themes = _load(config.DESCRIPTIVE_DIR / "top_themes.csv")
top_platforms = _load(config.DESCRIPTIVE_DIR / "top_platforms.csv")
platform_families = _load(config.DESCRIPTIVE_DIR / "platform_family_distribution.csv")
game_modes = _load(config.DESCRIPTIVE_DIR / "game_mode_distribution.csv")
perspectives = _load(config.DESCRIPTIVE_DIR / "player_perspective_distribution.csv")
playtime_bands = _load(config.DESCRIPTIVE_DIR / "playtime_band_distribution.csv")
top_developers = _load(config.DESCRIPTIVE_DIR / "top_developers.csv")
top_publishers = _load(config.DESCRIPTIVE_DIR / "top_publishers.csv")

quality_popscore = _load(config.DIAGNOSTIC_DIR / "quality_popscore_correlation.csv")
quality_activity = _load(config.DIAGNOSTIC_DIR / "quality_rating_activity_correlation.csv")
user_critic = _load(config.DIAGNOSTIC_DIR / "user_critic_agreement_summary.csv")
diagnostic_takeaways = _load(config.DIAGNOSTIC_DIR / "diagnostic_takeaways.csv")
genre_rating = _load(config.DIAGNOSTIC_DIR / "genre_rating_summary.csv")
theme_rating = _load(config.DIAGNOSTIC_DIR / "theme_rating_summary.csv")
platform_rating = _load(config.DIAGNOSTIC_DIR / "platform_family_rating_summary.csv")
playtime_rating = _load(config.DIAGNOSTIC_DIR / "playtime_rating_summary.csv")
associations = _load(config.DIAGNOSTIC_DIR / "cohort_adjusted_association_summary.csv")

render_metric_row(
    [
        ("Games", f"{len(catalog):,}", "Curated analytical sample"),
        ("Rated games", f"{int(catalog['rating_available_flag'].sum()):,}", "total_rating available"),
        ("Reliable-rated", f"{int(catalog['rating_reliable_flag'].sum()):,}", "total_rating_count >= 25"),
        ("PopScore known", f"{int(catalog['popscore_available_flag'].sum()):,}", "Known visibility/current-interest signal"),
    ]
)

tabs = st.tabs(["Descriptive Insights", "Diagnostic Insights", "Export Browser"])

with tabs[0]:
    st.header("Descriptive Insights")
    st.write("Descriptive analytics explains what is in the current project catalog: release timing, genres, themes, platforms, modes, playtime, and major companies.")

    st.subheader("Catalog timeline")
    st.write("The current app sample is balanced by release year, which makes time-based comparisons easier to read.")
    _line_chart(games_by_year, "release_year", "game_count", "Games by release year")

    col1, col2 = st.columns(2)
    with col1:
        render_bar_chart(platform_families.head(12), "platform_family", "game_count", "Platform families")
    with col2:
        render_bar_chart(rating_bands, "rating_band", "game_count", "Rating bands")

    st.subheader("Catalog composition")
    st.write("These charts describe the major content surfaces in the curated IGDB sample.")
    col1, col2 = st.columns(2)
    with col1:
        render_bar_chart(top_genres.head(15), "genre_name", "game_count", "Top genres")
        render_bar_chart(game_modes.head(12), "game_mode", "game_count", "Game modes")
        render_bar_chart(top_developers.head(12), "developer_name", "game_count", "Top developers")
    with col2:
        render_bar_chart(top_themes.head(15), "theme_name", "game_count", "Top themes")
        render_bar_chart(perspectives.head(12), "player_perspective", "game_count", "Player perspectives")
        render_bar_chart(top_publishers.head(12), "publisher_name", "game_count", "Top publishers")

    st.subheader("Reception and playtime")
    st.write("This section focuses on observed reception and experience signals, not recommendation logic.")
    col1, col2 = st.columns(2)
    with col1:
        render_bar_chart(rating_bands, "rating_band", "game_count", "Observed total-rating bands")
    with col2:
        render_bar_chart(playtime_bands, "playtime_band", "game_count", "Playtime bands")
    st.subheader("Playtime summary")
    _table(playtime_bands, rows=20)

with tabs[1]:
    st.header("Diagnostic Insights")
    st.write("Diagnostic analytics explains relationships in the sample. These are useful signals, not causal claims.")

    st.subheader("Diagnostic signal strength")
    st.write(
        "Diagnostic analytics keeps quality, rating activity, and visibility separate. "
        "These are associations inside the curated project sample, not causal effects."
    )
    spearman_visibility = _filter_equal(quality_popscore, scope_type="overall", method="spearman")
    spearman_activity = _filter_equal(quality_activity, scope_type="overall", method="spearman")
    user_spearman = _filter_equal(user_critic, metric="user_critic_spearman_correlation")
    render_metric_row(
        [
            (
                "Quality vs visibility",
                f"{float(_first_value(spearman_visibility, 'coefficient', 0)):.3f}",
                "Spearman rho: total_rating vs PopScore interest",
            ),
            (
                "Quality vs activity",
                f"{float(_first_value(spearman_activity, 'coefficient', 0)):.3f}",
                "Spearman rho: total_rating vs total_rating_count",
            ),
            (
                "User vs critic",
                f"{float(_first_value(user_spearman, 'value', 0)):.3f}",
                "Spearman rho",
            ),
        ]
    )
    st.subheader("Notebook takeaways")
    _table(diagnostic_takeaways, rows=50)

    st.subheader("Category-level diagnostics")
    st.write(
        "These tables summarize rating and enrichment patterns by category. Odds ratios are cohort-adjusted association "
        "signals, not proof that a category causes higher quality."
    )
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Genres")
        _table(_category_rating_table(genre_rating, "genre_name"), rows=15)
        st.markdown("#### Platform families")
        _table(_category_rating_table(platform_rating, "platform_family"), rows=15)
    with col2:
        st.markdown("#### Themes")
        _table(_category_rating_table(theme_rating, "theme_name"), rows=15)
        st.markdown("#### Playtime by cohort")
        playtime_columns = [
            column
            for column in [
                "playtime_band",
                "extraction_cohort",
                "game_count",
                "median_normally_hours",
                "rated_reliable_games",
                "median_total_rating",
                "median_total_rating_count",
                "high_rated_share",
            ]
            if column in playtime_rating.columns
        ]
        _table(playtime_rating[playtime_columns].head(30), rows=30)

    st.markdown("#### Strongest cohort-adjusted category associations")
    association_columns = [
        column
        for column in [
            "category_type",
            "category_name",
            "estimand",
            "category_game_count",
            "odds_ratio",
            "odds_ratio_ci_low",
            "odds_ratio_ci_high",
            "adjusted_p_value",
            "fdr_significant",
        ]
        if column in associations.columns
    ]
    if association_columns:
        assoc_preview = associations[association_columns].sort_values("odds_ratio", ascending=False, na_position="last")
        _table(assoc_preview, rows=50)

with tabs[2]:
    st.subheader("Notebook export browser")
    st.write(
        "Use this browser to inspect notebook exports without forcing every large table to render at page load. "
        "Hidden-gem and coverage-only outputs are excluded from this page by design."
    )
    export_group = st.radio("Export group", ["Descriptive", "Diagnostic"], horizontal=True)
    export_map = DESCRIPTIVE_EXPORTS if export_group == "Descriptive" else DIAGNOSTIC_EXPORTS
    export_label = st.selectbox("Export table", list(export_map.keys()))
    export_path = export_map[export_label]
    export_df = _load(export_path)
    _downloadable_table(export_label, export_df, export_path)
