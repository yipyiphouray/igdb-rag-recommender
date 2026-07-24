# Folder Structure Description

Last updated: 2026-07-24

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
|   |-- predictive/
|   |-- rag/
|   `-- raw/
|-- docs/
|   |-- plan/
|   |   `-- UI_Improvement_Plans/
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

Local-only UI iteration drafts can live under `archive/ui_iteration_plans/`. That folder is ignored by Git so the final repository stays focused on current implementation and final documentation.

## `assets/`

Shared visual assets such as screenshots, diagrams, logos, and style references.

## `data/`

Project data at different stages of the pipeline.

### `data/raw/`

Raw extraction documentation. Large raw IGDB endpoint dumps are ignored because they are not required to run the app and would make the repository harder to clone/deploy. The retained extraction manifest explains how to regenerate raw extracts.

### `data/app/`

App-ready Parquet and JSON artifacts used by Streamlit, FastAPI, and the website. This is the runtime data layer for deployment. It includes the game catalog, filter options, hidden gems, methodology metrics, insights summary, and the consolidated Insights dashboard artifact.

### `data/analytics/`

Notebook-exported descriptive, diagnostic, and plot artifacts. Most CSV outputs are treated as generated analysis outputs. The deployed Insights page consumes the consolidated `data/app/app_insights_dashboard.json` artifact instead of reading many CSV files directly.

### `data/predictive/`

Predictive/recommendation-related feature outputs and modeling artifacts when needed.

### `data/rag/`

RAG/retrieval artifacts. Generated Chroma/vector-store folders should remain ignored. Lightweight deployment-aware retrieval artifacts live under `data/rag/lightweight/` when needed.

## `docs/`

Project documentation, planning notes, source-of-truth docs, reports, and the session log.

### `docs/plan/`

Forward-looking implementation plans, pillar plans, website plans, and final consolidated UI improvement plans. Old version-by-version UI drafts should not stay here.

### `docs/plan/UI_Improvement_Plans/`

One consolidated design summary per major website page. This keeps the final product story readable while preserving page-level design decisions.

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
