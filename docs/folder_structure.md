# Folder Structure Description

Last updated: 2026-06-23

This file describes the high-level folder layout for the IGDB Game Discovery and RAG Recommendation System.

```text
Community_Project/
|-- .streamlit/
|-- archive/
|-- assets/
|-- data/
|   |-- raw/
|   |-- database/
|   |-- processed/
|   |-- analytics/
|   |   |-- descriptive/
|   |   |-- diagnostic/
|   |   `-- predictive/
|   |-- app/
|   |-- recommendations/
|   `-- rag/
|-- docs/
|   |-- plan/
|   |-- project_source_of_truth/
|   `-- report/
|-- notebooks/
|-- pages/
|-- src/
|   |-- app/
|   |   `-- components/
|   `-- pipeline/
|-- tests/
|-- streamlit_app.py
|-- requirements.txt
`-- requirement.txt
```

## `.streamlit/`

Stores local Streamlit configuration. Local secrets should use `.streamlit/secrets.toml`, which is ignored by Git.

## `archive/`

Stores older reference material or project files that are no longer part of the active workflow.

## `assets/`

Stores optional visual assets for the app, reports, or presentation layer.

### `assets/logo/`

Reserved for project logos or branding assets.

### `assets/screenshots/`

Reserved for screenshots used in documentation or final presentation materials.

### `assets/diagrams/`

Reserved for architecture diagrams, workflow diagrams, or app screenshots.

### `assets/styles/`

Reserved for styling assets if the Streamlit app needs custom CSS or visual references.

## `data/`

Stores project data at different stages of the pipeline.

### `data/raw/`

Stores raw IGDB API extracts before transformation.

### `data/database/`

Stores the normalized SQLite database created from the raw IGDB extracts.

Current primary database:

```text
data/database/igdb_games.db
```

### `data/processed/`

Reserved for cleaned or intermediate processed datasets.

### `data/analytics/`

Stores analysis-ready datasets and exported outputs used by notebooks, scripts, dashboards, or later project layers.

### `data/analytics/descriptive/`

Stores exported descriptive analytics tables from the descriptive exploration notebook.

### `data/analytics/diagnostic/`

Stores exported diagnostic analytics tables from the diagnostic exploration notebook.

### `data/analytics/predictive/`

Reserved for teammate predictive-model outputs, such as model metrics, feature importance, predictions, and evaluation visuals.

### `data/app/`

Stores app-ready Streamlit artifacts generated from the SQLite database and analytics outputs.

Current generated artifacts:

```text
app_game_catalog.parquet
app_hidden_gems.parquet
app_filter_options.json
app_insight_summary.json
app_methodology_metrics.json
```

### `data/recommendations/`

Reserved for prepared recommendation feature tables or explanation artifacts.

### `data/rag/`

Reserved for RAG game profiles, retrieval metadata, and vector-store artifacts.

## `docs/`

Stores project documentation, planning notes, schema documentation, session logs, and pillar-specific reporting files.

### `docs/project_source_of_truth/`

Stores source-of-truth project guideline and API documentation. Be careful when modifying these files; downstream plans should remain aligned with them.

### `docs/plan/`

Stores planning documents, including the Streamlit MVP architecture plan.

### `docs/report/`

Stores report-style Markdown findings and project narrative outputs.

## `notebooks/`

Stores exploration and analysis notebooks.

Current major notebooks:

```text
01_descriptive_analytics_exploration.ipynb
02_diagnostic_analytics_exploration.ipynb
```

## `pages/`

Stores Streamlit multipage app pages.

Current app pages:

```text
1_Home.py
2_Explore_Games.py
3_Hidden_Gems.py
4_Recommendations.py
5_Chatbot.py
6_Insights.py
7_Predictive_Model.py
8_Methodology.py
```

## `src/`

Stores reusable Python scripts for API extraction, database creation, quality checks, feature engineering, app services, and data-preparation pipelines.

### `src/app/`

Stores Streamlit app service-layer code, including configuration, data loading, filters, validation, recommendation logic, hidden-gem logic, predictive placeholders, and RAG placeholders.

### `src/app/components/`

Stores reusable Streamlit UI components such as game cards, metric rows, caveat notices, chart helpers, and empty/loading states.

### `src/pipeline/`

Stores data-preparation scripts for building app-ready artifacts.

Current app pipeline:

```text
build_app_catalog.py
```

## `tests/`

Stores automated tests for extraction logic, app data validation, filtering, recommendation behavior, and future integration checks.

## `streamlit_app.py`

Main Streamlit entry point.

Run locally with:

```text
streamlit run streamlit_app.py
```

## `requirements.txt`

Standard dependency file for the Streamlit MVP and deployment environments.

## `requirement.txt`

Legacy dependency file from the earlier project setup. Prefer `requirements.txt` for the Streamlit MVP going forward.
