# Folder Structure Description

Last updated: 2026-07-22

This file describes the active folder layout for the IGDB Game Discovery and Hybrid RAG Recommender project.

```text
Community_Project/
|-- api/
|-- apps/
|   |-- streamlit/
|   `-- website/
|-- archive/
|-- assets/
|-- data/
|   |-- analytics/
|   |   |-- descriptive/
|   |   |-- diagnostic/
|   |   `-- plots/
|   |-- app/
|   |-- database/
|   |-- predictive/
|   |-- processed/
|   |-- raw/
|   |-- recommendations/
|   `-- vector_store/
|-- docs/
|   |-- plan/
|   |-- project_source_of_truth/
|   `-- report/
|-- notebooks/
|-- scripts/
|   `-- manual_checks/
|-- src/
|   |-- app/
|   `-- pipeline/
`-- tests/
```

## `api/`

FastAPI backend for the final website. It exposes catalog browsing, game details, recommendations, insights, methodology, and health endpoints.

## `apps/`

User-facing application layers.

### `apps/streamlit/`

Streamlit MVP and internal analytics workbench.

### `apps/website/`

Next.js final-product website frontend. Generated folders such as `.next/` and `node_modules/` should remain ignored by Git.

## `archive/`

Older reference material that should be preserved for history but should not guide active implementation decisions.

## `assets/`

Shared visual assets such as screenshots, diagrams, logos, and style references.

## `data/`

Project data at different stages of the pipeline.

### `data/raw/`

Raw IGDB API extracts before transformation.

### `data/database/`

Local SQLite database output from the relational database build process. The database file is ignored by Git because it can become too large to push.

### `data/app/`

App-ready Parquet and JSON artifacts used by Streamlit, FastAPI, and the website.

### `data/analytics/`

Notebook-exported descriptive, diagnostic, and plot artifacts.

### `data/predictive/`

Predictive/recommendation-related feature outputs and modeling artifacts when needed.

### `data/vector_store/`

Local vector-store output used by RAG/hybrid retrieval. Generated vector-store files should remain ignored by Git.

## `docs/`

Project documentation, planning notes, source-of-truth docs, reports, and the session log.

### `docs/plan/`

Forward-looking implementation plans, pillar plans, website plans, and UI improvement plans.

### `docs/project_source_of_truth/`

Active source-of-truth documentation that should guide implementation decisions.

### `docs/report/`

Written findings and report-ready summaries for the project pillars.

## `notebooks/`

Exploration and analysis notebooks.

## `scripts/`

Utility scripts that are not part of the main app runtime.

### `scripts/manual_checks/`

Small manual inspection scripts used during development.

## `src/`

Reusable Python source code.

### `src/app/`

Shared app logic used by Streamlit and the FastAPI backend, including data loading, filtering, hidden-gem logic, recommendation logic, RAG helpers, and UI helper functions for Streamlit.

### `src/pipeline/`

Data pipeline scripts for building app-ready artifacts.

## `tests/`

Automated tests for selection logic, app artifacts, services, API recommendation integration, hidden-gem logic, and recommendation behavior.
