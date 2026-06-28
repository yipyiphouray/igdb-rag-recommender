from __future__ import annotations

import pandas as pd

from src.app.formatting import (
    badge_html,
    compact_text,
    format_number,
    format_percent,
    format_rating,
    html_escape,
    split_list,
)


def _field(row: pd.Series, key: str, default: str = "Unknown") -> str:
    value = row.get(key)
    if value is None or pd.isna(value):
        return default
    text = str(value).strip()
    return text if text else default


def _visibility_text(row: pd.Series) -> str:
    if int(row.get("popscore_available_flag", 0) or 0) != 1 and pd.isna(row.get("custom_interest_percentile")):
        return "Visibility: unknown"
    return f"Visibility: {format_percent(row.get('custom_interest_percentile'), decimals=0)}"


def _cover_html(row: pd.Series) -> str:
    cover_url = row.get("cover_url")
    if cover_url and not pd.isna(cover_url):
        return f'<img class="game-cover" src="{html_escape(cover_url)}" alt="Game cover" />'
    return '<div class="game-cover-placeholder">No cover</div>'


def render_game_card(row: pd.Series, show_explanation: bool = False) -> None:
    import streamlit as st

    title = _field(row, "name")
    release_year = _field(row, "release_year")
    hidden_flag = int(row.get("hidden_gem_balanced_flag", 0) or 0) == 1
    summary = compact_text(row.get("summary"), max_chars=210) or "No summary available."

    platform_badges = badge_html(
        split_list(row.get("platforms_list")),
        css_class="platform-badge",
        max_items=7,
        shorten_platforms=True,
    )
    genre_badges = badge_html(split_list(row.get("genres_list")), css_class="tag-badge", max_items=4)
    theme_badges = badge_html(split_list(row.get("themes_list")), css_class="tag-badge", max_items=3)
    hidden_badge = '<span class="hidden-badge">Hidden gem</span>' if hidden_flag else ""

    metric_badges = "".join(
        [
            f'<span class="metric-badge">Rating {html_escape(format_rating(row.get("total_rating")))}/100</span>',
            f'<span class="metric-badge">Evidence {html_escape(format_number(row.get("total_rating_count")))}</span>',
            f'<span class="metric-badge">{html_escape(_visibility_text(row))}</span>',
        ]
    )

    st.markdown(
        f"""
        <div class="game-card">
          <div>{_cover_html(row)}</div>
          <div>
            <div class="game-title">{html_escape(title)} <span class="game-subtitle">({html_escape(release_year)})</span></div>
            <div class="badge-row">{platform_badges}{hidden_badge}</div>
            <div class="badge-row">{metric_badges}</div>
            <div class="game-summary">{html_escape(summary)}</div>
            <div class="badge-row">{genre_badges}{theme_badges}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if show_explanation:
        explanation = row.get("recommendation_explanation") or row.get("candidate_explanation")
        if explanation and not pd.isna(explanation):
            st.success(str(explanation))

    with st.expander(f"Details for {title}"):
        col1, col2 = st.columns(2)
        col1.write(f"**Full platforms:** {_field(row, 'platforms_list')}")
        col1.write(f"**Genres:** {_field(row, 'genres_list')}")
        col1.write(f"**Themes:** {_field(row, 'themes_list')}")
        col2.write(f"**Modes:** {_field(row, 'game_modes_list')}")
        col2.write(f"**Perspectives:** {_field(row, 'player_perspectives_list')}")
        col2.write(f"**Cohort:** {_field(row, 'extraction_cohort')}")
        if row.get("normal_playtime_hours") == row.get("normal_playtime_hours"):
            st.write(f"**Normal playtime:** {format_number(row.get('normal_playtime_hours'), 1)} hours")
