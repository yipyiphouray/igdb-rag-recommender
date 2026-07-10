from __future__ import annotations

import json

import streamlit as st

import _path_setup  # noqa: F401
from src.app.predictive_service import artifact_path, load_predictions, predictive_status


st.set_page_config(page_title="Predictive Model", page_icon="🤖", layout="wide")
st.title("Predictive Model")
st.write("Placeholder and integration page for teammate predictive modeling artifacts.")

status = predictive_status()
st.subheader("Integration status")
st.json(status)

metrics_path = artifact_path("model_metrics")
if metrics_path.exists():
    with metrics_path.open("r", encoding="utf-8") as file:
        st.json(json.load(file))
else:
    st.info("Model metrics are not available yet.")

predictions = load_predictions()
if predictions.empty:
    st.warning("Model predictions are not available yet.")
else:
    st.dataframe(predictions.head(25))

st.subheader("Expected teammate artifacts")
st.code(
    """data/analytics/predictive/model_metrics.json
data/analytics/predictive/feature_importance.csv
data/analytics/predictive/model_predictions.parquet
data/analytics/predictive/confusion_matrix.png
data/analytics/predictive/roc_curve.png""",
    language="text",
)

