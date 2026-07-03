# IGDB Game Discovery & RAG Recommendation System

This project builds a Streamlit-based game discovery and recommendation MVP using IGDB data. It combines a normalized SQLite database, descriptive analytics, diagnostic analytics, hidden-gem logic, structured recommendation rules, and placeholder integration pages for predictive modeling and RAG chatbot work.

The current project direction is:

```text
Local Streamlit MVP first.
Public deployment and custom website later only if the MVP is stable.
```

## Current Status

Completed:

- IGDB extraction pipeline.
- Curated 15,000-game analytical sample.
- Normalized SQLite database.
- Descriptive analytics notebook and findings report.
- Diagnostic analytics notebook and findings report.
- Streamlit MVP foundation.
- Streamlit UI polish V3.
- App-ready data layer.
- Explore Games page.
- Hidden Gems page.
- Guided structured Recommendations page.
- Insights page.
- Methodology page.
- Predictive and RAG placeholder pages.

Pending / teammate-owned:

- Predictive model artifact integration.
- RAG/vector-store integration.
- Final chatbot behavior.
- Final demo flow and presentation polish.

## Current Dataset

Primary database:

```text
data/database/igdb_games.db
```

Current analytical sample:

```text
Total games:       15,000
Release years:     2010-2024
Games per year:    1,000
Quality cohort:    1,418
Popularity cohort: 3,000
Comparison cohort: 10,582
```

Important interpretation rules:

```text
total_rating       = quality / reception signal
total_rating_count = rating evidence / rating activity signal
PopScore interest  = visibility / current-interest signal
```

Important caveats:

- The dataset is a curated project sample, not the full IGDB catalog.
- Quality and visibility cohorts are intentionally oversampled.
- Full-sample high-rating or popularity shares should not be interpreted as market prevalence.
- Missing PopScore means unknown visibility, not low visibility.
- Diagnostic associations are not causal claims.

## Streamlit App

Main entry point:

```text
streamlit_app.py
```

Run locally:

```bash
streamlit run streamlit_app.py
```

Current pages:

```text
Home
Explore Games
Hidden Gems
Recommendations
Chatbot
Insights
Predictive Model
Methodology
```

Current UI direction:

- Home is a cyberpunk game-menu landing page with a 3-column clickable hover-panel grid.
- Explore Games and Hidden Gems support Grid View and Detailed View.
- Recommendations uses a minimal step-by-step wizard with quick-start personas and review/confirm.
- Insights is split into clear Descriptive and Diagnostic sections.
- Methodology is a continuous trust page with definitions, formulas, caveats, and artifact audits.

Current app-ready artifacts:

```text
data/app/app_game_catalog.parquet
data/app/app_hidden_gems.parquet
data/app/app_filter_options.json
data/app/app_insight_summary.json
data/app/app_methodology_metrics.json
```

Rebuild app-ready artifacts:

```bash
python src/pipeline/build_app_catalog.py
```

## Setup

Recommended Python environment:

```text
Python 3.10+
```

Install Streamlit MVP dependencies:

```bash
pip install -r requirements.txt
```

The older `requirement.txt` file is retained for legacy pipeline dependencies. Prefer `requirements.txt` for the Streamlit MVP.

## Environment Variables

Create a `.env` file only if you need to run IGDB extraction or future API-backed RAG features.

Example:

```text
IGDB_CLIENT_ID=your_twitch_client_id
IGDB_CLIENT_SECRET=your_twitch_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit secrets.

Local Streamlit secrets should go in:

```text
.streamlit/secrets.toml
```

That file is ignored by Git.

## Project Structure

```text
Community_Project/
|-- .streamlit/
|-- assets/
|-- data/
|   |-- raw/
|   |-- database/
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

More detail:

```text
docs/folder_structure.md
```

## Key Documentation

Project source of truth:

```text
docs/project_source_of_truth/definitive_project_guideline_igdb_rag.md
docs/project_source_of_truth/streamlit_page_context.md
docs/project_source_of_truth/IGDB_API_Documentation.md
```

Plans:

```text
docs/plan/descriptive_analytics_pillar_plan.md
docs/plan/diagnostic_analytics_pillar_plan.md
docs/plan/streamlit_mvp_architecture_plan.md
docs/plan/streamlit_manual_qa_test_cases.md
docs/plan/streamlit_ui_polish_plan_v1.md
```

Findings reports:

```text
docs/report/descriptive_pillar_findings.md
docs/report/diagnostic_pillar_findings.md
```

Session log:

```text
docs/session_log.md
```

## Notebooks

```text
notebooks/01_descriptive_analytics_exploration.ipynb
notebooks/02_diagnostic_analytics_exploration.ipynb
```

The notebooks generate exported analytics tables under:

```text
data/analytics/descriptive/
data/analytics/diagnostic/
```

## Tests

Run the full project unit test suite:

```bash
python -m unittest tests/test_app_data_validation.py tests/test_fetch_igdb_selection.py tests/test_app_filters.py tests/test_recommendation_service.py tests/test_hidden_gem_service.py tests/test_app_artifact_schema.py
```

Focused app/service tests:

```bash
python -m unittest tests/test_app_filters.py
python -m unittest tests/test_recommendation_service.py
python -m unittest tests/test_hidden_gem_service.py
python -m unittest tests/test_app_artifact_schema.py
```

Run Python compile checks manually if needed:

```bash
python -m compileall streamlit_app.py pages src/app src/pipeline
```

Manual Streamlit QA checklist:

```text
docs/plan/streamlit_manual_qa_test_cases.md
```

## Current Hidden-Gem Definition

The default Balanced hidden-gem rule is:

```text
quality cohort
AND total_rating >= 80
AND total_rating_count >= 25
AND main game
AND PopScore available
AND within-year quality-cohort visibility percentile <= 40%
```

The app's Hidden Gems page uses:

```text
data/app/app_hidden_gems.parquet
```

This artifact is generated from the finalized diagnostic hidden-gem definition.

## Teammate Integration Contracts

Predictive model expected artifacts:

```text
data/analytics/predictive/model_metrics.json
data/analytics/predictive/feature_importance.csv
data/analytics/predictive/model_predictions.parquet
data/analytics/predictive/confusion_matrix.png
data/analytics/predictive/roc_curve.png
```

RAG expected artifacts:

```text
data/rag/game_profiles.parquet
data/rag/retrieval_metadata.parquet
data/rag/vector_store/
```

The current Predictive Model and Chatbot pages are designed to load safely even when these artifacts are not yet available.

## Typical Development Flow

```text
1. Rebuild app artifacts if database or analytics exports changed.
2. Run validation tests.
3. Run Streamlit locally.
4. Complete manual QA checklist.
5. Fix page-specific issues.
6. Integrate teammate predictive/RAG artifacts when ready.
7. Polish final demo flow.
```

Commands:

```bash
python src/pipeline/build_app_catalog.py
python -m unittest tests/test_app_data_validation.py
streamlit run streamlit_app.py
```

