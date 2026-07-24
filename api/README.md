# FastAPI Backend

This folder contains the backend API used by the final website.

The API reads app-ready artifacts from:

```text
data/app/app_game_catalog.parquet
data/app/app_filter_options.json
data/app/app_hidden_gems.parquet
data/app/app_methodology_metrics.json
data/app/app_insight_summary.json
```

It also reads notebook-exported analytics summaries from:

```text
data/analytics/descriptive/
data/analytics/diagnostic/
```

The RAG chatbot layer uses:

```text
data/app/app_game_catalog.parquet
data/vector_store/
src/rag_engine.py
src/app/rag_service.py
```

## Setup

```bash
python -m pip install -r api/requirements-api.txt
```

## Run locally

```bash
cd api
uvicorn main:app --reload --port 8000
```

Local API docs:

```text
http://localhost:8000/docs
```

## Current Endpoints

```text
GET  /health
GET  /catalog/filter-options
GET  /catalog/games
GET  /catalog/games/{game_id}
POST /recommendations
GET  /chat/status
POST /chat
GET  /insights/summary
GET  /methodology/summary
```

## Recommendation Behavior

`POST /recommendations` uses the metadata-based cosine similarity recommender when the request contains usable preference inputs. The structured scoring recommender remains available as a fallback when cosine similarity cannot produce usable results.

## RAG Chatbot Behavior

`POST /chat` accepts a natural-language game discovery question and returns catalog-backed retrieved games from the hybrid RAG stack. `GET /chat/status` reports whether the catalog, vector store, and runtime dependencies appear available.

The chat endpoint fails gracefully when RAG artifacts or dependencies are missing; the rest of the API should still start and serve non-RAG pages.
