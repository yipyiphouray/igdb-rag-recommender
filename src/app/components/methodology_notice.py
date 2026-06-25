from __future__ import annotations


def render_sample_caveat() -> None:
    import streamlit as st

    st.info(
        "This app uses a curated 15,000-game IGDB analytical sample, not the full IGDB catalog. "
        "Quality and visibility cohorts are intentionally oversampled, so full-sample rating or "
        "visibility shares are not market prevalence estimates."
    )


def render_signal_caveat() -> None:
    import streamlit as st

    st.caption(
        "`total_rating` = quality/reception. `total_rating_count` = rating evidence/activity. "
        "PopScore interest = visibility/current interest. Missing PopScore means unknown visibility, not low visibility."
    )

