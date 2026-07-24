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


VIEW_MODES = ["Grid View", "Detailed View"]


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _field(row: pd.Series, key: str, default: str = "Unknown") -> str:
    value = row.get(key)
    if _is_missing(value):
        return default
    text = str(value).strip()
    return text if text else default


def _has_value(row: pd.Series, key: str) -> bool:
    return not _is_missing(row.get(key))


def _visibility_text(row: pd.Series) -> str:
    if int(row.get("popscore_available_flag", 0) or 0) != 1 and _is_missing(row.get("custom_interest_percentile")):
        return "Visibility unknown"
    return f"Visibility {format_percent(row.get('custom_interest_percentile'), decimals=0)}"


def _rating_text(row: pd.Series) -> str:
    if _is_missing(row.get("total_rating")):
        return "Rating unknown"
    return f"Rating {format_rating(row.get('total_rating'))}/100"


def _evidence_text(row: pd.Series) -> str:
    if _is_missing(row.get("total_rating_count")):
        return "Evidence unknown"
    return f"Evidence {format_number(row.get('total_rating_count'))}"


def _playtime_text(row: pd.Series) -> str:
    if not _has_value(row, "normal_playtime_hours"):
        return "Unknown"
    return f"{format_number(row.get('normal_playtime_hours'), 1)} hours"


def _cover_html(row: pd.Series) -> str:
    cover_url = row.get("cover_url")
    if not _is_missing(cover_url):
        return f'<img class="game-cover" src="{html_escape(_high_res_cover_url(str(cover_url)))}" alt="Game cover" />'
    return '<div class="game-cover-placeholder">No cover</div>'


def _high_res_cover_url(cover_url: str) -> str:
    return (
        cover_url.replace("/t_thumb/", "/t_cover_big/")
        .replace("/t_cover_small/", "/t_cover_big/")
        .replace("/t_720p/", "/t_cover_big/")
    )


def _platform_badges(row: pd.Series, max_items: int = 7) -> str:
    return badge_html(
        split_list(row.get("platforms_list")),
        css_class="platform-badge",
        max_items=max_items,
        shorten_platforms=True,
    )


def _tag_badges(row: pd.Series, detailed: bool = False) -> str:
    genre_limit = 8 if detailed else 4
    theme_limit = 6 if detailed else 3
    genre_badges = badge_html(split_list(row.get("genres_list")), css_class="tag-badge", max_items=genre_limit)
    theme_badges = badge_html(split_list(row.get("themes_list")), css_class="tag-badge", max_items=theme_limit)
    return genre_badges + theme_badges


def _metric_badges(row: pd.Series) -> str:
    badges = [
        _rating_text(row),
        _evidence_text(row),
        _visibility_text(row),
    ]
    if _has_value(row, "recommendation_score"):
        badges.append(f"Match {format_number(row.get('recommendation_score'), 1)}")
    return "".join(f'<span class="metric-badge">{html_escape(badge)}</span>' for badge in badges)


def _detail_item(label: str, value: object) -> str:
    return (
        '<div class="detail-item">'
        f"<span>{html_escape(label)}</span>"
        f"<strong>{html_escape(value)}</strong>"
        "</div>"
    )


def _details_html(row: pd.Series, detailed: bool = False) -> str:
    items = [
        ("Platforms", _field(row, "platforms_list")),
        ("Genres", _field(row, "genres_list")),
        ("Themes", _field(row, "themes_list")),
        ("Modes", _field(row, "game_modes_list")),
        ("Perspective", _field(row, "player_perspectives_list")),
        ("Cohort", _field(row, "extraction_cohort")),
        ("Playtime", _playtime_text(row)),
    ]
    if detailed:
        items.extend(
            [
                ("Release year", _field(row, "release_year")),
                ("Rating", _rating_text(row)),
                ("Rating evidence", _evidence_text(row)),
                ("Visibility", _visibility_text(row)),
            ]
        )
    return '<div class="detail-grid">' + "".join(_detail_item(label, value) for label, value in items) + "</div>"


def _explanation_html(row: pd.Series, show_explanation: bool) -> str:
    if not show_explanation:
        return ""
    explanation = row.get("recommendation_explanation") or row.get("candidate_explanation")
    if _is_missing(explanation):
        return ""
    return f'<div class="card-explanation">{html_escape(explanation)}</div>'


def render_game_card(row: pd.Series, show_explanation: bool = False, view_mode: str = "Grid View") -> None:
    import streamlit as st

    view_mode = view_mode if view_mode in VIEW_MODES else "Grid View"
    title = _field(row, "name")
    release_year = _field(row, "release_year")
    hidden_flag = int(row.get("hidden_gem_balanced_flag", 0) or 0) == 1
    hidden_badge = '<span class="hidden-badge">Hidden gem</span>' if hidden_flag else ""

    if view_mode == "Grid View":
        st.markdown(
            f"""
            <div class="game-grid-card">
              {_cover_html(row)}
              <div class="game-grid-title">{html_escape(title)}</div>
              <div class="game-subtitle">{html_escape(release_year)} - {html_escape(_rating_text(row))}</div>
              <div class="badge-row">{hidden_badge}</div>
              {_explanation_html(row, show_explanation)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    detailed = view_mode == "Detailed View"
    summary_length = 420 if detailed else 210
    summary = compact_text(row.get("summary"), max_chars=summary_length) or "No summary available."
    card_class = "game-card detailed" if detailed else "game-card list"

    st.markdown(
        f"""
        <div class="{card_class}">
          <div>{_cover_html(row)}</div>
          <div>
            <div class="game-title">{html_escape(title)} <span class="game-subtitle">({html_escape(release_year)})</span></div>
            <div class="badge-row">{_platform_badges(row, max_items=10 if detailed else 7)}{hidden_badge}</div>
            <div class="badge-row">{_metric_badges(row)}</div>
            <div class="game-summary">{html_escape(summary)}</div>
            <div class="badge-row">{_tag_badges(row, detailed=detailed)}</div>
            {_details_html(row, detailed=detailed)}
            {_explanation_html(row, show_explanation)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_game_results(
    games: pd.DataFrame,
    view_mode: str = "Grid View",
    show_explanation: bool = False,
    grid_columns: int = 4,
) -> None:
    import streamlit as st

    view_mode = view_mode if view_mode in VIEW_MODES else "Grid View"

    if view_mode == "Grid View":
        columns = st.columns(grid_columns)
        for index, (_, row) in enumerate(games.iterrows()):
            with columns[index % grid_columns]:
                render_game_card(row, show_explanation=show_explanation, view_mode=view_mode)
        return

    for _, row in games.iterrows():
        render_game_card(row, show_explanation=show_explanation, view_mode=view_mode)
