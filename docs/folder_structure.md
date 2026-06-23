# Folder Structure Description

Last updated: 2026-06-16

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

### `docs/project_source_of_truth`

Stores all markdown files containing the source of truth of the project. Becareful before modifying. Making sure it always align and if something changes, make sure every other source of truth is followed

### `docs/plan`

Stores all plan markdown file. 

### `docs/report`

Stores all reports type of markdown or narrative. 

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

## tests

Stores all test scripts. 