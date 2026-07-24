from __future__ import annotations

import streamlit as st

import _path_setup  # noqa: F401
from src.app.rag_service import answer_game_query, rag_status


st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="wide")
st.title("RAG Chatbot")
st.write("Natural-language discovery page backed by the shared RAG service when local vector artifacts are available.")

status = rag_status()
st.subheader("Integration status")
st.json(status)

query = st.text_area(
    "Example prompt",
    value="I want a cozy game for PC that is not one of the obvious blockbuster titles.",
)

if st.button("Ask"):
    response = answer_game_query(query=query, filters=None, top_k=5)
    st.write(response["answer_text"])
    if response["warnings"]:
        st.warning(" ".join(response["warnings"]))

st.subheader("Expected teammate artifacts")
st.code(
    """data/app/app_game_catalog.parquet
data/vector_store/
src/rag_engine.py
src/app/rag_service.py""",
    language="text",
)

