from __future__ import annotations

import pandas as pd

from src.app.formatting import compact_text, format_percent, format_rating, format_number


def _field(row: pd.Series, key: str, default: str = "Unknown") -> str:
    value = row.get(key)
    if value is None or pd.isna(value):
        return default
    text = str(value).strip()
    return text if text else default


def render_game_card(row: pd.Series, show_explanation: bool = False) -> None:
    import streamlit as st

    with st.container(border=True):
        cols = st.columns([1, 3])
        cover_url = row.get("cover_url")
        if cover_url and not pd.isna(cover_url):
            cols[0].image(str(cover_url), width=160)
        else:
            cols[0].markdown("No cover")

        title = _field(row, "name")
        release_year = _field(row, "release_year")
        hidden_label = " | Hidden-gem candidate" if int(row.get("hidden_gem_balanced_flag", 0) or 0) == 1 else ""
        cols[1].markdown(f"### {title} ({release_year}){hidden_label}")
        cols[1].caption(
            f"Rating: {format_rating(row.get('total_rating'))} / 100 | "
            f"Rating evidence: {format_number(row.get('total_rating_count'))} | "
            f"Visibility percentile: {format_percent(row.get('custom_interest_percentile'))}"
        )
        cols[1].write(compact_text(row.get("summary"), max_chars=320) or "No summary available.")
        cols[1].caption(f"Genres: {_field(row, 'genres_list')}")
        cols[1].caption(f"Platforms: {_field(row, 'platforms_list')}")

        if show_explanation:
            explanation = row.get("recommendation_explanation") or row.get("candidate_explanation")
            if explanation and not pd.isna(explanation):
                cols[1].success(str(explanation))

        with st.expander("Details"):
            st.write(f"Themes: {_field(row, 'themes_list')}")
            st.write(f"Modes: {_field(row, 'game_modes_list')}")
            st.write(f"Perspectives: {_field(row, 'player_perspectives_list')}")
            st.write(f"Cohort: {_field(row, 'extraction_cohort')}")
            if row.get("normal_playtime_hours") == row.get("normal_playtime_hours"):
                st.write(f"Normal playtime: {format_number(row.get('normal_playtime_hours'), 1)} hours")
