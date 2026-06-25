from __future__ import annotations

import streamlit as st

from src.app.rag_service import answer_game_query, rag_status


st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="wide")
st.title("RAG Chatbot")
st.write("Natural-language discovery page. This is ready for teammate RAG/vector-store integration.")

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
    """data/rag/game_profiles.parquet
data/rag/retrieval_metadata.parquet
data/rag/vector_store/
src/app/rag_service.py callable integration""",
    language="text",
)

