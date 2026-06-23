from __future__ import annotations

import streamlit as st

from src.app import config
from src.app.components.methodology_notice import render_sample_caveat, render_signal_caveat
from src.app.data_loader import load_json_artifact
from src.app.validation import artifact_audit


st.set_page_config(page_title="Methodology", page_icon="📚", layout="wide")
st.title("Methodology")

render_sample_caveat()
render_signal_caveat()

st.subheader("Current sample design")
st.write(
    "The current database contains 15,000 curated IGDB games: exactly 1,000 released main games per year "
    "from 2010 through 2024. The extraction uses quality, popularity, and comparison cohorts."
)

st.subheader("Hidden-gem definition")
st.code(
    """quality cohort
AND total_rating >= 80
AND total_rating_count >= 25
AND main game
AND PopScore available
AND within-year quality-cohort visibility percentile <= 40%""",
    language="text",
)

st.subheader("Artifact audit")
st.json(artifact_audit())

st.subheader("Methodology metrics")
st.json(load_json_artifact(config.APP_METHODOLOGY_METRICS_PATH))

st.subheader("Implementation boundaries")
st.write(
    "Streamlit loads prepared assets. It should not rebuild the database, call the live IGDB API, retrain models, "
    "or generate embeddings during normal app use."
)
