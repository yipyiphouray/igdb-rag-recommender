from __future__ import annotations


def render_sample_caveat() -> None:
    import streamlit as st

    st.info(
        "This app uses a refreshed curated 47,835-game IGDB analytical sample, not the full IGDB catalog. "
        "Reception and visibility cohorts are intentionally shaped by the extraction design, so full-sample rating or "
        "visibility shares are not market prevalence estimates."
    )


def render_sample_footnote() -> None:
    import streamlit as st

    st.markdown(
        """
        <div class="small-caveat">
        * Uses a refreshed curated 47,835-game IGDB analytical sample, not the full IGDB catalog.
        Reception and visibility cohorts are intentionally shaped by the extraction design, so rating or visibility shares
        are not market prevalence estimates.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_signal_caveat() -> None:
    import streamlit as st

    st.caption(
        "`total_rating` = quality/reception. `total_rating_count` = rating evidence/activity. "
        "PopScore interest = visibility/current interest. Missing PopScore means unknown visibility, not low visibility."
    )

