# QUEST ACCEPTED: IGDB Game Discovery Website

An end-to-end game discovery website built from IGDB catalog data. The project combines descriptive analytics, diagnostic analytics, hidden-gem discovery, metadata-based cosine similarity recommendations, and a scoped RAG/LLM project guide inside a custom Next.js website.

The final user-facing product is:

```text
Next.js website in apps/website + FastAPI backend in api
```

Streamlit remains available only as an internal prototype and analytics workbench.

## Project Story

Game discovery is difficult because popularity, quality, visibility, and personal taste do not always point to the same games. Popular games are easy to find, but lower-visibility games with strong reception can be missed. This project builds a curated game catalog from IGDB data and turns it into a practical discovery interface.

The website is designed to answer five user needs:

- Browse the game catalog with useful filters.
- Understand broad catalog patterns through analytics.
- Discover lower-visibility, high-quality hidden-gem candidates.
- Receive structured game recommendations from metadata-based cosine similarity.
- Ask project-scoped questions through Ask the Guide.

The system does not claim to represent the full IGDB market. It uses a curated analytical sample and documents the assumptions, limitations, and validation checks behind the app.

## Live Deployment

Frontend:

```text
https://quest-accepted-game-recommender.vercel.app/
```

Backend:

```text
https://igdb-rag-recommender.onrender.com
```

Backend API documentation:

```text
https://igdb-rag-recommender.onrender.com/docs
```

## Main Features

| Area | Website page | Purpose |
|---|---|---|
| Home | `/` | Introduces the project and routes users to the main tools. |
| Explore Games | `/explore` | Search and filter the app-ready game catalog. |
| Game Details | `/explore/[game_id]` | Inspect individual catalog records. |
| Recommend Me | `/recommendations` | Generate cosine-similarity recommendations from structured user preferences. |
| Hidden Gems | `/hidden-gems` | Surface high-quality, lower-visibility candidates from diagnostic analytics. |
| Insights | `/insights` | Present descriptive and diagnostic findings through dashboard cards and charts. |
| Methodology | `/methodology` | Explain the data pipeline, assumptions, and analytical logic. |
| Ask the Guide | `/guide` | Answer project-scoped questions using retrieved project context and a grounded LLM response layer. |

## Repository Structure

```text
Community_Project/
|-- api/                  FastAPI backend
|-- apps/
|   |-- website/          Next.js final website
|   `-- streamlit/        Streamlit prototype/workbench
|-- data/
|   |-- app/              Runtime-ready app artifacts
|   |-- raw/              Raw extraction manifest only
|   |-- rag/              Lightweight retrieval artifacts when needed
|   `-- analytics/        Generated analysis outputs
|-- docs/
|   |-- project_source_of_truth/
|   `-- report/
|-- notebooks/            Descriptive and diagnostic analysis notebooks
|-- src/                  Shared Python logic and data pipelines
|-- tests/                Automated tests
`-- README.md
```

See `docs/folder_structure.md` for the detailed folder description.

## Architecture

```text
IGDB API extraction
        |
        v
Raw/local data artifacts
        |
        v
Relational + analytical processing
        |
        v
App-ready artifacts in data/app/
        |
        v
FastAPI backend
        |
        v
Next.js website
```

The frontend does not read local files directly. It calls the FastAPI backend, and the backend reads app-ready Parquet/JSON artifacts.

## Runtime Data Artifacts

The deployed app depends mainly on these files:

```text
data/app/app_game_catalog.parquet
data/app/app_filter_options.json
data/app/app_hidden_gems.parquet
data/app/app_insight_summary.json
data/app/app_insights_dashboard.json
data/app/app_methodology_metrics.json
```

The optional lightweight game-retrieval artifacts are retained for internal retrieval evaluation and historical RAG experiments:

```text
data/rag/lightweight/game_embeddings.npy
data/rag/lightweight/game_ids.json
data/rag/lightweight/manifest.json
```

They are not required for the main Explore, Recommend Me, Hidden Gems, Insights, or Methodology pages.

Large raw IGDB endpoint dumps are intentionally excluded from the final GitHub story. The retained extraction manifest is:

```text
data/raw/extraction_manifest.json
```

## Environment Variables

Copy the example environment file:

```bash
copy .env.example .env
```

Common backend variables:

```text
FRONTEND_ORIGIN=http://localhost:3000
CORS_ALLOWED_ORIGINS=
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
RAG_BACKEND=lightweight
RECOMMENDATION_COSINE_CANDIDATE_LIMIT=2500
```

Website local environment:

```bash
cd apps/website
copy .env.local.example .env.local
```

Expected local value:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

For Vercel deployment, set `NEXT_PUBLIC_API_BASE_URL` to the deployed Render backend URL.

## Local Setup

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install -r api/requirements-api.txt
```

Install website dependencies:

```bash
cd apps/website
npm install
```

If `node_modules/` was removed during cleanup, run `npm install` again before starting the website.

## Run Locally

Terminal 1: start the backend.

```bash
cd api
uvicorn main:app --reload --port 8000
```

Terminal 2: start the website.

```bash
cd apps/website
npm run dev
```

Open:

```text
http://localhost:3000
```

Backend API docs:

```text
http://localhost:8000/docs
```

## Run the Streamlit Workbench

```bash
cd apps/streamlit
streamlit run streamlit_app.py
```

Use Streamlit for internal review and prototype checks. Use the Next.js website as the final user-facing product.

## Rebuild App Artifacts

If the source data changes, rebuild app-ready artifacts before running the website.

Build the main app catalog:

```bash
python src/pipeline/build_app_catalog.py
```

Build the consolidated Insights dashboard artifact:

```bash
python src/pipeline/build_insights_dashboard_artifact.py
```

Rebuild lightweight retrieval artifacts:

```bash
python src/build_lightweight_rag_index.py
```

The IGDB extraction script requires IGDB/Twitch credentials in `.env`:

```bash
python src/fetch_IGDB.py
```

## Backend Endpoints

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

## Recommendation Logic

Recommend Me uses metadata-based cosine similarity. User inputs such as recent games, platforms, genres, themes, mood words, playstyle preferences, desired playtime, rating preference, and discovery preference are converted into a preference profile. That profile is compared against catalog games, then adjusted with quality, rating-evidence, discovery, and playtime signals.

For hosted deployment, the candidate pool is limited to reduce memory pressure:

```text
RECOMMENDATION_COSINE_CANDIDATE_LIMIT=2500
```

Use `2500` for Render free tier. Lower it to `1000` if `POST /recommendations` returns `502` or times out. Raise it only after the endpoint is stable.

## Ask the Guide Logic

Ask the Guide is not meant to replace Recommend Me. Its purpose is to explain the project, dataset, methodology, analytics findings, hidden-gem definition, recommendation logic, RAG design, and website navigation.

The Guide uses structured backend tools for exact facts, retrieves project context for broader methodology questions, and uses Gemini when `GEMINI_API_KEY` is configured. It is scoped so it does not reveal internal file names, paths, source documents, or implementation metadata to website users.

## Validation

Run backend/service checks:

```bash
python -m unittest tests/test_metadata_cosine_recommendation.py tests/test_api_recommendation_service.py tests/test_recommendation_service.py
```

Run broader artifact and service checks:

```bash
python -m unittest tests/test_app_artifact_schema.py tests/test_app_data_validation.py tests/test_app_filters.py tests/test_catalog_facts.py tests/test_project_facts.py tests/test_project_terms.py tests/test_rag_ranking.py
```

Build the website:

```bash
cd apps/website
npm run build
```

Manual usability testing is documented in:

```text
docs/report/usability_testing_protocol.md
```

Hidden-gems ranking validation is documented in:

```text
docs/report/hidden_gems_ranking_validation.md
```

## Key Documentation

```text
docs/report/descriptive_pillar_findings.md
docs/report/diagnostic_pillar_findings.md
docs/report/hidden_gems_ranking_validation.md
docs/report/rag_retrieval_quality_findings.md
docs/report/usability_testing_protocol.md
docs/project_source_of_truth/ask_the_guide_current_state.md
docs/project_source_of_truth/ask_the_guide_knowledge_base.md
docs/project_source_of_truth/website_visual_style_guide.md
```

## Deployment Notes

Backend deployment target: Render Web Service.

```text
Root directory: repo root
Build command: pip install -r api/requirements-api.txt
Start command: cd api && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Frontend deployment target: Vercel.

```text
Root directory: apps/website
Build command: npm run build
Output: Next.js default
```

Set the backend CORS origin to the Vercel URL:

```text
FRONTEND_ORIGIN=https://quest-accepted-game-recommender.vercel.app
```

Set the frontend API base URL:

```text
NEXT_PUBLIC_API_BASE_URL=https://igdb-rag-recommender.onrender.com
```

## Reproducibility Notes

- `.env`, local databases, `.next/`, `node_modules/`, `__pycache__/`, TypeScript build info, and raw endpoint dumps should not be committed.
- The final app should be reproducible from tracked source code plus the app-ready artifacts in `data/app/`.
- The local SQLite database is intentionally excluded because it is large and can be regenerated.
- Raw IGDB extraction can be rerun with valid credentials.
- App-ready artifacts should be regenerated after any major data refresh.

## Cleanup Notes

The repo intentionally excludes obsolete supervised-modeling outputs, local build caches, raw endpoint dumps, and generated dependency folders. The current recommendation system is the metadata cosine-similarity recommender in:

```text
src/app/metadata_cosine_recommendation.py
api/app/services/recommendation_service.py
```

## Limitations

- The catalog is a curated analytical sample, not the full IGDB catalog.
- IGDB metadata coverage varies by game.
- Ratings are treated as reception signals, not objective quality truth.
- Rating counts are treated as evidence/activity, not direct popularity.
- PopScore and visibility signals may be missing for some games.
- Diagnostic findings show associations, not causal claims.
- Recommendation quality depends on the specificity of user inputs.
