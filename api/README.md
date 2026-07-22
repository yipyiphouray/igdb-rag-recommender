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
GET  /insights/summary
GET  /methodology/summary
```

## Recommendation Behavior

`POST /recommendations` uses the metadata-based cosine similarity recommender when the request contains usable preference inputs. The structured scoring recommender remains available as a fallback when cosine similarity cannot produce usable results.
