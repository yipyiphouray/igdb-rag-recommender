# FastAPI Backend

This folder contains the first backend slice for the final website.

The API reads app-ready artifacts from:

```text
data/app/app_game_catalog.parquet
data/app/app_filter_options.json
data/app/app_methodology_metrics.json
data/app/app_insight_summary.json
```

## Setup

```text
cd api
python -m pip install -r requirements-api.txt
```

## Run locally

```text
cd api
uvicorn main:app --reload --port 8000
```

Local API docs:

```text
http://localhost:8000/docs
```

Implemented first-slice endpoints:

```text
GET  /health
GET  /catalog/filter-options
GET  /catalog/games
GET  /catalog/games/{game_id}
POST /recommendations
GET  /methodology/summary
```

`POST /recommendations` currently uses the existing structured fallback scoring
so the website flow works before teammate cosine-similarity artifacts are wired
into the API.
