from __future__ import annotations


def loading_message(message: str):
    import streamlit as st

    return st.spinner(message)

