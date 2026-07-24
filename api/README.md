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

The Ask the Guide chatbot layer uses:

```text
project context retrieval
Gemini, when GEMINI_API_KEY is configured
safe deterministic fallback answers
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

## Deployment CORS

The backend allows local frontend origins by default:

```text
http://localhost:3000
http://127.0.0.1:3000
```

For deployment, set one of these backend environment variables on the hosting service:

```text
FRONTEND_ORIGIN=https://your-vercel-site.vercel.app
```

or, for multiple frontend URLs:

```text
CORS_ALLOWED_ORIGINS=https://site-one.vercel.app,https://site-two.vercel.app
```

Do not use `*` while credentials are enabled. Use exact deployed frontend origins.

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

`POST /chat` accepts project-scoped questions about the website, dataset, methodology, analytics findings, recommendation logic, and game catalog. The Guide uses internal website context and does not expose source files, document names, paths, or storage formats. `GET /chat/status` reports whether the required chatbot context and runtime dependencies appear available.

The chat endpoint fails gracefully when chatbot context or dependencies are missing; the rest of the API should still start and serve non-chat pages.

## Render Deployment Settings

Recommended backend deployment target: Render Web Service.

```text
Root directory: repo root
Build command: pip install -r api/requirements-api.txt
Start command: cd api && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```text
FRONTEND_ORIGIN=https://your-vercel-site.vercel.app
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
RAG_BACKEND=lightweight
```
