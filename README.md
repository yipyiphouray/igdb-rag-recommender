# IGDB Game Discovery and Hybrid RAG Recommender

A game discovery project that combines IGDB catalog analytics, metadata-based recommendations, and a custom website interface. Streamlit remains available as the MVP/internal workbench, while the Next.js website is the polished final-product direction.

## Current Architecture

- `apps/website/`
  - Next.js, React, TypeScript, and Tailwind frontend.
  - Final user-facing website.
- `api/`
  - FastAPI backend for catalog, insights, methodology, recommendations, and RAG chat.
- `apps/streamlit/`
  - Streamlit prototype and internal analytics workbench.
- `src/`
  - Shared Python logic for data loading, filtering, recommendation logic, RAG utilities, app services, and data pipelines.
- `data/app/`
  - App-ready Parquet and JSON artifacts used by Streamlit, FastAPI, and the website.
- `data/analytics/descriptive/` and `data/analytics/diagnostic/`
  - Notebook-generated analytics CSV outputs. These are local/generated and are condensed into app-ready JSON for deployment.
- `data/database/`
  - Local SQLite database output from the IGDB relational build pipeline. The database file is intentionally ignored by Git.
- `docs/`
  - Plans, source-of-truth documentation, reports, and session logs.

## Setup

Install the shared Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Install the FastAPI backend dependencies:

```bash
python -m pip install -r api/requirements-api.txt
```

Install the website dependencies:

```bash
cd apps/website
npm install
```

## Run the Final Website Locally

Terminal 1:

```bash
cd api
uvicorn main:app --reload --port 8000
```

Terminal 2:

```bash
cd apps/website
npm run dev
```

Open:

```text
http://localhost:3000
```

API docs:

```text
http://localhost:8000/docs
```

## Run the Streamlit Workbench

```bash
cd apps/streamlit
streamlit run streamlit_app.py
```

## Key Website Pages

- `/`
- `/explore`
- `/explore/[game_id]`
- `/hidden-gems`
- `/guide`
- `/insights`
- `/methodology`
- `/recommendations`

## Useful Validation Commands

Website build:

```bash
cd apps/website
npm run build
```

Focused recommendation tests:

```bash
python -m unittest tests/test_metadata_cosine_recommendation.py tests/test_api_recommendation_service.py tests/test_recommendation_service.py
```

Vector/RAG checks:

```bash
python src/validate_vector_store.py
python src/debug_engine.py
```

RAG chatbot API checks:

```text
GET  http://localhost:8000/chat/status
POST http://localhost:8000/chat
```

## Notes

- Do not commit `.env`, `.DS_Store`, `__pycache__/`, `.next/`, `node_modules/`, local SQLite databases, or generated vector-store files.
- The main app catalog source is `data/app/app_game_catalog.parquet`.
- The deployed Insights page uses `data/app/app_insights_dashboard.json`, which condenses the required descriptive and diagnostic dashboard tables into one app-ready artifact.
- Large raw IGDB endpoint dumps are not required for deployment. Keep `data/raw/extraction_manifest.json` and regenerate raw extracts with `src/fetch_IGDB.py` when needed.
- Generated Chroma/vector-store folders should remain ignored. Lightweight RAG artifacts live in `data/rag/lightweight/` when needed.
- Rebuild retrieval artifacts after refreshing the app catalog:

```bash
python src/build_lightweight_rag_index.py
```
