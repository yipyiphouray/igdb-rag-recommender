# Folder Structure Description

Last updated: 2026-07-17

This file describes the high-level folder layout for the IGDB Game Discovery and RAG Recommendation System.

```text
Community_Project/
|-- archive/
|-- data/
|   |-- raw/
|   |-- database/
|   |-- processed/
|   `-- analytics/
|       `-- descriptive/
|-- docs/
|   |-- plan/
|   |-- project_source_of_truth/
|   `-- report/
|-- apps/
|   |-- streamlit/
|   `-- website/
|-- models/
|-- notebooks/
|-- outputs/
|   |-- figures/
|   |-- model_results/
|   `-- tables/
|-- sql/
`-- src/
```

## `archive/`

Stores older reference material or project files that are no longer part of the active workflow.

Current examples include legacy project guidelines and older RAG/SQLite-era documentation that should be preserved for history but should not be treated as the active implementation source of truth.

## `data/`

Stores project data at different stages of the pipeline.

### `data/raw/`

Stores raw IGDB API extracts before transformation.

### `data/database/`

Stores the normalized SQLite database created from the raw IGDB extracts.

### `data/processed/`

Reserved for cleaned or intermediate processed datasets.

### `data/analytics/`

Stores analysis-ready datasets and exported outputs used by notebooks, scripts, dashboards, or later project layers.

### `data/analytics/descriptive/`

Stores exported descriptive analytics tables from the descriptive exploration notebook.

## `docs/`

Stores project documentation, planning notes, schema documentation, session logs, and pillar-specific planning files.

### `docs/plan/`

Stores forward-looking implementation plans, UI improvement plans, page plans, and pillar execution plans.

### `docs/project_source_of_truth/`

Stores active source-of-truth documentation that should guide implementation decisions. This includes the definitive project guideline, ERD/data dictionary documents, website style guide, page context, and current retrieval/RAG methodology documents.

Current retrieval/RAG source-of-truth documents include:

- `hybrid_retrieval_methodology.md`
- `hybrid_search_technical_journey.md`

### `docs/report/`

Stores written findings and report-ready summaries for the analytics pillars.

## `apps/`

Stores user-facing application layers.

### `apps/streamlit/`

Stores the Streamlit MVP/prototype app.

### `apps/website/`

Stores the Next.js final-product website frontend. Generated folders such as `.next/` and `node_modules/` should remain ignored by Git.

## `models/`

Reserved for saved model artifacts created during the predictive analytics layer.

## `notebooks/`

Stores exploration and analysis notebooks.

## `outputs/`

Stores final or presentation-ready outputs.

### `outputs/figures/`

Reserved for exported charts and visual assets.

### `outputs/model_results/`

Reserved for model evaluation outputs and prediction results.

### `outputs/tables/`

Reserved for final tables used in reports, dashboards, or presentations.

## `sql/`

Reserved for reusable SQL queries, views, or database scripts.

## `src/`

Stores reusable Python scripts for API extraction, database creation, quality checks, feature engineering, and other project workflows.
