# Final Product Current State

Last updated: July 28, 2026

This document defines the current final product state for the IGDB Game Discovery project. Use it as the high-level source of truth when checking whether planning documents, presentation language, source-of-truth files, or README content still match the working product.

## 1. Final Product Direction

The final user-facing product is the custom Next.js website in:

```text
apps/website
```

The final backend is the FastAPI service in:

```text
api
```

Streamlit remains available as an internal prototype and analytics workbench in:

```text
apps/streamlit
```

Streamlit is not the primary final product, final demo target, or deployment target.

## 2. Deployment State

Current deployment direction:

| Layer | Technology | Hosting target |
|---|---|---|
| Frontend | Next.js / React / TypeScript / Tailwind CSS | Vercel |
| Backend | FastAPI / Python | Render |

The deployed frontend calls the deployed backend through the configured API base URL.

The backend must allow the deployed Vercel URL through CORS.

## 3. Current Website Pages

| Page | Route | Current purpose |
|---|---|---|
| Home | `/` | Project overview and launchpad into the main user flows. |
| Explore Games | `/explore` | Browse, search, filter, and inspect the app catalog. |
| Game Detail | `/explore/[game_id]` | Inspect one catalog game in more detail. |
| Recommend Me | `/recommendations` | Generate metadata cosine-similarity recommendations from structured preferences. |
| Hidden Gems | `/hidden-gems` | Surface project-defined high-quality, lower-visibility games. |
| Insights | `/insights` | Present descriptive and diagnostic analytics findings. |
| Methodology | `/methodology` | Explain data extraction, artifacts, analytics, recommendation logic, RAG role, and limitations. |
| Ask the Guide | `/guide` | Answer scoped project, catalog, methodology, website, and recommendation-logic questions. |

## 4. Data Foundation

The website uses a curated IGDB analytical sample, not the full IGDB database.

Current app-facing catalog:

- 47,835 games;
- release years 2010 through 2024;
- 1,425 quality-cohort games;
- 147 lower-rated-cohort games;
- 9,000 popularity-cohort games;
- 5,329 low-visibility-cohort games;
- 31,934 comparison-cohort games;
- 231 hidden-gem candidates.

Core interpretation rules:

```text
total_rating       = quality / reception signal
total_rating_count = rating evidence / rating activity signal
PopScore           = visibility / current-interest signal when available
```

Important caveats:

- The catalog is curated for product usefulness and analytical contrast.
- Full-sample rating, visibility, and cohort shares are not full-market prevalence estimates.
- Missing PopScore means unknown visibility, not low visibility.
- Missing rating data means quality scoring is limited, not that the game is low quality.
- Diagnostic findings should not be framed as causal claims.

## 5. Data Extraction Logic

The extraction targeted 50,000 selected released main games from IGDB across 2010 through 2024.

The final selected app catalog contains 47,835 games because some release-year and eligibility combinations did not have enough records to fully fill the planned target.

High-level extraction flow:

```text
query IGDB candidates by release year
-> apply local eligibility rules
-> fetch PopScore primitives for eligible candidates
-> select yearly cohorts
-> deduplicate by IGDB game ID
-> fetch full game and relationship records
-> build relational SQLite database
-> export app-ready artifacts
```

Current cohort design:

| Cohort | Meaning |
|---|---|
| Quality | Reliable higher-reception games based on `total_rating >= 75` and `total_rating_count >= 25`. |
| Lower rated | Reliable lower-reception games based on `total_rating <= 60` and `total_rating_count >= 25`. |
| Popularity | High known IGDB visibility games using project-defined interest score or IGDB Visits fallback. |
| Low visibility | Low known IGDB visibility games using project-defined interest score or IGDB Visits fallback. |
| Comparison | Reproducible residual sample from remaining eligible games. |

## 6. Recommendation Engine

`Recommend Me_` is the main ranked recommendation workflow.

It uses metadata-based cosine similarity, not supervised machine learning.

The user provides structured inputs such as:

- recent games;
- platforms;
- genres;
- themes;
- mood words;
- playstyle preferences;
- desired playtime;
- rating-quality preference;
- discovery preference.

Current custom ranking function:

```text
final_score =
  0.65 * cosine_similarity
+ 0.15 * quality_score
+ 0.10 * rating_evidence_score
+ 0.05 * discovery_score
+ 0.05 * playtime_score
```

The backend applies hard filters and candidate limiting before cosine scoring so the hosted Render backend does not process the full catalog for every request.

Recommended hosted environment variable:

```text
RECOMMENDATION_COSINE_CANDIDATE_LIMIT=2500
```

Lower this value if Render returns memory-related failures or timeouts.

## 7. Ask the Guide

`Ask the Guide_` is the scoped project explanation layer.

It is not the primary ranked recommendation engine.

Current behavior:

- accepts typed project and catalog questions;
- uses structured tools for exact facts and catalog-backed answers;
- retrieves project context for broader methodology questions;
- uses Gemini when configured to phrase grounded answers;
- falls back to extractive project-context answers when the LLM is unavailable;
- routes ranked recommendation requests to `Recommend Me_`;
- avoids exposing internal file names, document names, paths, retrieval metadata, or source artifacts.

Available chatbot tool categories:

- project facts;
- catalog counts;
- catalog distributions;
- game lookup;
- game comparison;
- recommendation input help;
- term definitions;
- website navigation;
- recommendation redirect;
- project-context retrieval;
- unsupported-scope refusal.

## 8. Retrieval Boundary

There are two different retrieval concepts in the project.

| Retrieval area | Current role |
|---|---|
| Project-context retrieval | Used by Ask the Guide for project, methodology, and website Q&A. |
| Lightweight hybrid game retrieval | Retained as an internal/development/evaluation stack, not the main final website recommender. |

Chroma is not required for final website deployment.

The lightweight game-retrieval artifacts are optional for the final website unless a specific route explicitly enables that retained retrieval stack.

## 9. Source-of-Truth Priority

When documents conflict, use this priority order:

1. Current working website/backend code.
2. `final_product_current_state.md`.
3. `ask_the_guide_current_state.md`.
4. `website_visual_style_guide.md`.
5. IGDB ERD/business-rule/data-quality source-of-truth documents.
6. Streamlit context documents.
7. Old planning documents and session logs.

Planning documents are historical unless they were explicitly consolidated into a source-of-truth file.

