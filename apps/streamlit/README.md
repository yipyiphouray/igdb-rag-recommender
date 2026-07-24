# Streamlit App

This folder contains the Streamlit MVP and internal analytics workbench.

Run from this folder so Streamlit picks up the local `.streamlit/config.toml` file:

```bash
cd apps/streamlit
streamlit run streamlit_app.py
```

The Streamlit app imports shared project logic from the repository-level `src/` package through `_path_setup.py`.
