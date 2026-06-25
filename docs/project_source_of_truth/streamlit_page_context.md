# Streamlit Page Context

This document describes the current Streamlit MVP pages for the IGDB Game Discovery & RAG Recommendation System. It is intended to help teammates, evaluators, and future development sessions understand what each page currently does, what data it uses, and what still needs integration.

Main app entry point:

```text
streamlit_app.py
```

Run command:

```text
streamlit run streamlit_app.py
```

Current app-ready data artifacts:

```text
data/app/app_game_catalog.parquet
data/app/app_hidden_gems.parquet
data/app/app_filter_options.json
data/app/app_insight_summary.json
data/app/app_methodology_metrics.json
```

Core interpretation rules used across the app:

```text
total_rating       = quality / reception signal
total_rating_count = rating evidence / rating activity signal
PopScore interest  = visibility / current-interest signal
```

Important caveats:

- The app uses a curated 15,000-game IGDB analytical sample, not the full IGDB catalog.
- The sample includes exactly 1,000 released main games per year from 2010 through 2024.
- Quality and visibility cohorts are intentionally oversampled.
- Missing PopScore means unknown visibility, not low visibility.
- Diagnostic associations should not be interpreted as causal claims.

---

# 1. Main App Home

File:

```text
streamlit_app.py
```

Purpose:

The main app home page introduces the project, shows top-level dataset metrics, provides navigation shortcuts, and highlights a few hidden-gem candidates.

Primary audience:

- Project evaluators who need a quick orientation.
- Users landing in the app for the first time.

Main data sources:

```text
data/app/app_game_catalog.parquet
data/app/app_hidden_gems.parquet
data/app/app_methodology_metrics.json
```

Current content:

- Project title and short caption.
- Metric cards:
  - total games;
  - release-year range;
  - hidden-gem candidate count;
  - reliable-rated share.
- Sample caveat.
- Signal caveat explaining rating, rating count, and PopScore.
- Navigation links to:
  - Explore Games;
  - Hidden Gems;
  - Recommendations;
  - Chatbot.
- Featured hidden-gem candidate cards.

Current status:

```text
Implemented and functional.
```

Known limitations:

- Featured hidden gems currently use the first few rows from the hidden-gem artifact.
- No custom branding or visual design polish has been added yet.

---

# 2. Home Page in Multipage Navigation

File:

```text
pages/1_Home.py
```

Purpose:

This page mirrors the main home page inside Streamlit's multipage navigation. It exists because Streamlit treats `streamlit_app.py` and files inside `pages/` differently.

Primary audience:

- Users navigating through the sidebar page list.

Main data sources:

```text
data/app/app_game_catalog.parquet
data/app/app_hidden_gems.parquet
data/app/app_methodology_metrics.json
```

Current content:

- Same high-level project orientation as the main app page.
- Metric cards.
- Caveat notices.
- Quick action page links.
- Featured hidden-gem candidates.

Current status:

```text
Implemented and functional.
```

Implementation note:

This page is intentionally standalone. It should not import `streamlit_app.py` directly because doing so can create blank-page behavior in Streamlit multipage navigation.

---

# 3. Explore Games

File:

```text
pages/2_Explore_Games.py
```

Purpose:

Allows users to browse the current game catalog through structured search and filters.

Primary audience:

- Users who want to explore the catalog manually.
- Evaluators who want to inspect the current dataset through the app.

Main data sources:

```text
data/app/app_game_catalog.parquet
data/app/app_filter_options.json
```

Service-layer dependencies:

```text
src/app/data_loader.py
src/app/filters.py
src/app/components/game_card.py
```

Current filters:

- Title or summary search.
- Release-year range.
- Platform.
- Genre.
- Theme.
- Game mode.
- Player perspective.
- Extraction cohort.
- Minimum total rating.
- Minimum rating evidence.
- Hidden-gem candidates only.
- Sort option.
- Result limit.

Current sort options:

- Highest rating.
- Most rating evidence.
- Highest visibility.
- Newest release.
- Lowest visibility among reliable high-rated games.

Current output:

- Matching game count.
- Game cards with:
  - cover;
  - title;
  - release year;
  - rating;
  - rating evidence;
  - visibility percentile;
  - summary;
  - genres;
  - platforms;
  - expandable details.

Current status:

```text
Implemented and functional.
```

Trust rules:

- Result rows are one row per game.
- Missing ratings are not treated as low ratings.
- Missing PopScore is not treated as low visibility.
- `total_rating_count` is displayed as rating evidence, not popularity.

Known limitations:

- Result display is currently card-based with a result limit, not full pagination.
- Some multi-value fields can be visually long.
- No dedicated game detail page exists yet.

---

# 4. Hidden Gems

File:

```text
pages/3_Hidden_Gems.py
```

Purpose:

Surfaces lower-visibility, high-quality games from the curated project sample.

Primary audience:

- Users looking for strong games that may be less obvious.
- Evaluators reviewing the diagnostic/prescriptive logic.

Main data sources:

```text
data/app/app_hidden_gems.parquet
data/app/app_game_catalog.parquet
data/app/app_filter_options.json
```

Service-layer dependencies:

```text
src/app/hidden_gem_service.py
src/app/components/game_card.py
```

Default Balanced hidden-gem rule:

```text
quality cohort
AND total_rating >= 80
AND total_rating_count >= 25
AND main game
AND PopScore available
AND within-year quality-cohort visibility percentile <= 40%
```

Current controls:

- Sensitivity:
  - Balanced;
  - Conservative;
  - Broad.
- Release-year range.
- Platform.
- Genre.
- Theme.
- Minimum rating.
- Minimum rating evidence.
- Number of candidates to show.

Current output:

- Hidden-gem rule explanation.
- Matching candidate count.
- Candidate game cards with explanation text.

Current status:

```text
Implemented and functional.
```

Important implementation rule:

The default Balanced view loads from:

```text
data/app/app_hidden_gems.parquet
```

This artifact is generated from the finalized diagnostic hidden-gem definition. Conservative and Broad settings are exploratory alternate views and should not replace the documented diagnostic rule.

Known limitations:

- Sensitivity variants are rule-based exploratory views.
- Hidden-gem status is relative to the curated sample, not the full video game market.

---

# 5. Recommendations

File:

```text
pages/4_Recommendations.py
```

Purpose:

Provides structured, explainable MVP recommendations using simple preference inputs.

Primary audience:

- Users who want ranked suggestions from structured preferences.
- Evaluators who want to inspect transparent recommendation logic.

Main data sources:

```text
data/app/app_game_catalog.parquet
data/app/app_filter_options.json
```

Service-layer dependencies:

```text
src/app/recommendation_service.py
src/app/filters.py
src/app/components/game_card.py
```

Current user inputs:

- Required platform.
- Preferred genres.
- Preferred themes / mood.
- Release-year range.
- Desired quality level.
- Hidden-gem boost toggle.
- Number of recommendations.

MVP scoring components:

```text
Platform eligibility: required gate
Genre match:          0-30
Theme match:          0-20
Quality score:        0-15
Rating evidence:      0-5
Hidden-gem boost:     0-10
```

Current output:

- Ranked recommendation cards.
- Recommendation score.
- Explanation text describing why each game matched.

Current status:

```text
Implemented as first MVP version.
```

Trust rules:

- Platform is treated as a hard gate when selected.
- Recommendations are limited to existing catalog games.
- The page does not predict ratings for imaginary games.
- Explanations are generated from actual scoring/filter components.

Known limitations:

- Game mode, perspective, playtime, multiplayer, and natural-language preference scoring are planned later.
- The scoring formula is intentionally simple for MVP clarity.
- This page should eventually integrate teammate predictive/RAG signals when those artifacts are ready.

---

# 6. Chatbot

File:

```text
pages/5_Chatbot.py
```

Purpose:

Provides the app shell for future RAG-based natural-language game discovery.

Primary audience:

- Users who will eventually ask for recommendations in natural language.
- Teammates integrating RAG and vector retrieval.

Expected future data/artifacts:

```text
data/rag/game_profiles.parquet
data/rag/retrieval_metadata.parquet
data/rag/vector_store/
```

Service-layer dependency:

```text
src/app/rag_service.py
```

Current content:

- RAG integration status.
- Example prompt text box.
- Safe fallback response when retrieval artifacts are missing.
- Expected teammate artifact list.

Current status:

```text
Placeholder / integration-contract page.
```

Required final behavior:

- Recommend only database-backed retrieved games.
- Do not invent game metadata.
- Explain recommendations using retrieved context.
- Disclose missing data when relevant.
- Ask users to broaden or clarify when no strong match exists.

Known limitations:

- No final vector retrieval is currently wired into the app.
- The page is intentionally non-blocking so Explore, Hidden Gems, Insights, Methodology, and basic Recommendations can work before RAG is complete.

---

# 7. Insights

File:

```text
pages/6_Insights.py
```

Purpose:

Summarizes the completed descriptive and diagnostic analytics in a concise app-facing format.

Primary audience:

- Evaluators reviewing the analytics story.
- Analytical users exploring catalog patterns.

Main data sources:

```text
data/app/app_game_catalog.parquet
data/app/app_hidden_gems.parquet
data/app/app_methodology_metrics.json
data/analytics/descriptive/top_genres.csv
data/analytics/descriptive/top_platforms.csv
data/analytics/diagnostic/quality_popscore_correlation.csv
data/analytics/diagnostic/user_critic_agreement_summary.csv
```

Current tabs:

- Catalog Overview.
- Reception and Visibility.
- Hidden Gems.
- Coverage and Limits.

Current content:

- Metric cards.
- Top genre chart.
- Top platform chart.
- Quality versus PopScore diagnostic table.
- User versus critic agreement diagnostic table.
- Hidden-gem sample table.
- Methodology metrics and caveats.

Current status:

```text
Implemented as first MVP version.
```

Known limitations:

- Visual polish is minimal.
- The page intentionally does not reproduce every notebook chart.
- Some diagnostic tables may need more narrative interpretation before final presentation.

---

# 8. Predictive Model

File:

```text
pages/7_Predictive_Model.py
```

Purpose:

Provides the app shell for teammate predictive-model integration.

Primary audience:

- Teammate building the predictive pillar.
- Evaluators reviewing model results once available.

Expected future artifacts:

```text
data/analytics/predictive/model_metrics.json
data/analytics/predictive/feature_importance.csv
data/analytics/predictive/model_predictions.parquet
data/analytics/predictive/confusion_matrix.png
data/analytics/predictive/roc_curve.png
```

Service-layer dependency:

```text
src/app/predictive_service.py
```

Current content:

- Predictive artifact status.
- Model metrics display if available.
- Model predictions preview if available.
- Expected teammate artifact list.

Current status:

```text
Placeholder / integration-contract page.
```

Required final behavior:

- Show model objective.
- Show target definition.
- Show train/test approach.
- Show performance metrics.
- Show feature importance.
- Show limitations.
- Attach predictions only to existing catalog games.

Known limitations:

- Predictive artifacts are not currently integrated.
- This page should remain non-blocking until teammate outputs are ready.

---

# 9. Methodology

File:

```text
pages/8_Methodology.py
```

Purpose:

Explains the project methodology, current sample design, hidden-gem definition, artifact audit, and implementation boundaries.

Primary audience:

- Evaluators.
- Teammates.
- Future development sessions.

Main data sources:

```text
data/app/app_methodology_metrics.json
```

Service-layer dependencies:

```text
src/app/validation.py
src/app/data_loader.py
```

Current content:

- Sample caveat.
- Signal caveat.
- Current sample design explanation.
- Hidden-gem definition.
- Artifact audit status.
- Methodology metrics JSON.
- Implementation boundaries.

Current status:

```text
Implemented and functional.
```

Key implementation boundary:

Streamlit loads prepared assets. It should not:

- rebuild the database;
- call the live IGDB API;
- retrain models;
- generate embeddings during normal app use.

Known limitations:

- Methodology is currently concise.
- More polished narrative can be added for final presentation.

---

# 10. Shared App Service Layer

The pages rely on the following shared service modules:

```text
src/app/config.py
src/app/constants.py
src/app/data_loader.py
src/app/filters.py
src/app/formatting.py
src/app/hidden_gem_service.py
src/app/recommendation_service.py
src/app/predictive_service.py
src/app/rag_service.py
src/app/validation.py
```

Reusable UI components:

```text
src/app/components/game_card.py
src/app/components/game_detail_panel.py
src/app/components/metric_cards.py
src/app/components/chart_helpers.py
src/app/components/methodology_notice.py
src/app/components/empty_state.py
src/app/components/loading_state.py
src/app/components/sidebar_filters.py
```

App-ready artifact builder:

```text
src/pipeline/build_app_catalog.py
```

Validation test:

```text
tests/test_app_data_validation.py
```

---

# 11. Current Implementation Status Summary

```text
Home:                 Implemented
Explore Games:        Implemented
Hidden Gems:          Implemented
Recommendations:      MVP implemented
Chatbot:              Placeholder / teammate integration pending
Insights:             MVP implemented
Predictive Model:     Placeholder / teammate integration pending
Methodology:          Implemented
```

Recommended next improvements:

1. Polish game-card layout and reduce overly long tag text.
2. Add better result pagination or "load more" behavior.
3. Improve Insights narrative and chart formatting.
4. Add game detail modal/page behavior.
5. Integrate teammate predictive artifacts.
6. Integrate teammate RAG/vector-store artifacts.
7. Prepare final Streamlit demo flow for evaluators.

