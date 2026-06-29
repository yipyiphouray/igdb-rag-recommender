# Streamlit Page Context

Last updated: 2026-06-29

This document describes the current Streamlit MVP pages for the IGDB Game Discovery & RAG Recommendation System. It is intended to help teammates, evaluators, and future development sessions understand what each page does, what data it uses, and what still needs integration.

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

## Current UI Direction

The current app has completed the second UI polish pass.

The user-facing discovery pages are intentionally cleaner and less technical:

- Home is a cyberpunk game-menu landing page with clickable hover panels.
- Explore Games and Hidden Gems support List View, Grid View, and Detailed View.
- Recommendations is a step-by-step wizard with Back, Next, Reset, and final recommendation actions.
- Insights is the deep "Data nerds only" page for descriptive and diagnostic exports, excluding hidden-gem and coverage-only analysis sections.
- Methodology is a continuous academic/trust page with headings, cards, formulas, caveats, and artifact audits instead of expander sections.

Technical explanations that were previously visible on discovery pages have been moved into Methodology or concise styled rule/caveat boxes.

---

## 1. Main App Home

File:

```text
streamlit_app.py
```

Purpose:

The main Home page introduces the product and acts as a navigation menu for the app.

Primary audience:

- Users landing in the app for the first time.
- Project evaluators who need a quick orientation.

Main data sources:

```text
None loaded on the Home page.
```

Current content:

- Cyberpunk arcade-style title treatment.
- Clickable hover menu panels linking to:
  - Explore Games;
  - Hidden Gems;
  - Recommendations;
  - Insights;
  - Methodology;
  - Chatbot;
  - Predictive Model.
- Page details appear on hover.

Current status:

```text
Implemented and polished for UI V2.
```

Implementation notes:

- The Home page no longer shows featured hidden-gem cards.
- The Home page no longer shows dataset metric cards.
- The Home page no longer shows the technical signal explanation. Those definitions now live in Methodology.
- The full menu panel is clickable through `src/app/components/menu_card.py`.
- Menu cards are rendered through `src/app/components/menu_card.py`.
- Shared CSS is injected through `src/app/components/ui_style.py`.

---

## 2. Home Page in Multipage Navigation

File:

```text
pages/1_Home.py
```

Purpose:

This page mirrors the main Home page inside Streamlit's multipage navigation. It exists because Streamlit treats `streamlit_app.py` and files inside `pages/` differently.

Primary audience:

- Users navigating through the sidebar page list.

Main data sources:

```text
None loaded on the Home page.
```

Current content:

- Same high-level orientation as the main app Home page.
- Clickable cyberpunk menu panels for major app sections.
- Hover details for each page.

Current status:

```text
Implemented and polished for UI V2.
```

Implementation note:

This page is intentionally standalone. It should not import `streamlit_app.py` directly because doing so can create blank-page behavior in Streamlit multipage navigation.

---

## 3. Explore Games

File:

```text
pages/2_Explore_Games.py
```

Purpose:

Allows users to browse the current game catalog through structured search and filters.

Primary audience:

- Users who want to manually explore the catalog.
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
src/app/components/ui_style.py
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
- User-selectable display view:
  - List View;
  - Grid View;
  - Detailed View.
- List and Detailed cards keep useful details inside the card rectangle.
- Game cards can show:
  - cover image;
  - title;
  - release year;
  - platform badges;
  - rating;
  - rating evidence;
  - visibility status or percentile;
  - short summary;
  - genre and theme badges;
  - useful details such as modes, perspectives, cohort, and playtime.

Current status:

```text
Implemented and polished for UI V2.
```

Trust rules:

- Result rows are one row per game.
- Missing ratings are not treated as low ratings.
- Missing PopScore is not treated as low visibility.
- `total_rating_count` is displayed as rating evidence/activity, not popularity.

Known limitations:

- Result display is card-based with a result limit, not full pagination.
- Platform icons are represented as short badges rather than official platform icons.
- No dedicated game detail page exists yet.

---

## 4. Hidden Gems

File:

```text
pages/3_Hidden_Gems.py
```

Purpose:

Surfaces lower-visibility, high-quality games from the curated project sample.

Primary audience:

- Users looking for strong games that may be less obvious.
- Evaluators reviewing the diagnostic hidden-gem logic.

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
src/app/components/ui_style.py
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

- Short user-facing explanation.
- Hidden-gem rule shown directly in a styled rule box.
- Matching candidate count.
- User-selectable List View, Grid View, and Detailed View.
- Game cards with candidate explanations.

Current status:

```text
Implemented and polished for UI V2.
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

## 5. Recommendations

File:

```text
pages/4_Recommendations.py
```

Purpose:

Provides structured, explainable MVP recommendations through guided user preference questions.

Primary audience:

- Users who want ranked suggestions without manually tuning every catalog filter.
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
src/app/components/ui_style.py
```

Current wizard steps:

- Platform.
- Preferred genres.
- Preferred themes / mood.
- Discovery preference:
  - Balanced;
  - Hidden gems;
  - Popular / visible games.
- Desired quality level.
- Desired playtime:
  - Any length;
  - Shorter games;
  - Medium games;
  - Longer games.
- Release-year range.
- Number of recommendations.

MVP scoring components:

```text
Platform eligibility: hard gate when selected
Genre match:          0-30
Theme match:          0-20
Quality score:        0-15
Rating evidence:      0-5
Hidden-gem boost:     0-10 when selected
Visibility bias:      0-5 when popular/visible is selected
Playtime fit:         0-5 when selected and playtime data exists
```

Current output:

- Step-by-step wizard with Back, Next, Reset, and final Show Recommendations controls.
- Current preference loadout summary.
- Ranked recommendation cards.
- Recommendation score.
- Explanation text describing why each game matched.
- Compact scoring caveat shown below the wizard.

Current status:

```text
Implemented and polished for UI V2.
```

Trust rules:

- Platform is treated as a hard gate when selected.
- Recommendations are limited to existing catalog games.
- The page does not predict ratings for imaginary games.
- Explanations are generated from actual scoring/filter components.
- Missing playtime does not penalize a game unless playtime data is needed for a selected fit bonus.

Known limitations:

- The scoring formula is intentionally simple for MVP clarity.
- Game mode, perspective, multiplayer, and natural-language preference scoring can be added later.
- This page should eventually integrate teammate predictive/RAG signals when those artifacts are ready.

---

## 6. Chatbot

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
- The page is intentionally non-blocking so Explore, Hidden Gems, Insights, Methodology, and Recommendations can work before RAG is complete.

---

## 7. Insights

File:

```text
pages/6_Insights.py
```

Purpose:

Summarizes the completed descriptive and diagnostic analytics in a dashboard-style page.

Primary audience:

- Evaluators reviewing the analytics story.
- Analytical users exploring catalog patterns.

Main data sources:

```text
data/app/app_game_catalog.parquet
data/analytics/descriptive/games_by_release_year.csv
data/analytics/descriptive/rating_bands.csv
data/analytics/descriptive/top_genres.csv
data/analytics/descriptive/top_themes.csv
data/analytics/descriptive/top_platforms.csv
data/analytics/descriptive/game_mode_distribution.csv
data/analytics/descriptive/player_perspective_distribution.csv
data/analytics/descriptive/playtime_band_distribution.csv
data/analytics/diagnostic/quality_popscore_correlation.csv
data/analytics/diagnostic/quality_rating_activity_correlation.csv
data/analytics/diagnostic/user_critic_agreement_summary.csv
data/analytics/diagnostic/diagnostic_takeaways.csv
data/analytics/diagnostic/genre_rating_summary.csv
data/analytics/diagnostic/theme_rating_summary.csv
data/analytics/diagnostic/platform_family_rating_summary.csv
data/analytics/diagnostic/cohort_adjusted_association_summary.csv
```

Current tabs:

- Catalog.
- Composition.
- Reception.
- Diagnostic Signals.
- Category Diagnostics.
- Export Browser.

Current content:

- Dataset metric cards.
- Release-year timeline.
- Genre, theme, platform, mode, perspective, developer, and publisher charts.
- Rating-band and playtime-band charts.
- Quality versus PopScore diagnostic metric.
- Quality versus rating activity diagnostic metric.
- User versus critic agreement diagnostic metric.
- Diagnostic takeaway table.
- Category-level diagnostic tables.
- Cohort-adjusted association table.
- Export browser with table previews and CSV downloads.
- Hidden-gem and coverage-only analysis sections are intentionally excluded from this page.

Current status:

```text
Implemented and polished for UI V2.
```

Known limitations:

- Large notebook tables are previewed with download buttons instead of fully rendered at page load.
- Hidden-gem and coverage-only outputs remain available in project files but are intentionally not part of this page.

---

## 8. Predictive Model

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

## 9. Methodology

File:

```text
pages/8_Methodology.py
```

Purpose:

Explains the project methodology, current sample design, metric definitions, hidden-gem definition, recommendation scoring, artifact audit, limitations, and implementation boundaries.

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
src/app/components/metric_cards.py
src/app/components/ui_style.py
```

Current content:

- Top-level methodology metric cards.
- Continuous report-style sections with no expander/toggle blocks.
- Data source and app artifact explanation.
- Curated sample design explanation and caveat.
- Metric definitions:
  - `total_rating`;
  - `total_rating_count`;
  - PopScore interest;
  - missing PopScore interpretation.
- Hidden-gem calculation.
- Recommendation scoring.
- Artifact audit.
- Known limitations.
- Streamlit implementation boundaries.

Current status:

```text
Implemented and polished for UI V2.
```

Key implementation boundary:

Streamlit loads prepared assets. It should not:

- rebuild the database;
- call the live IGDB API;
- retrain models;
- generate embeddings during normal app use.

Known limitations:

- Methodology is app-facing, not a full written methodology chapter.
- More polished report narrative can still be added for final presentation.

---

## 10. Shared App Service Layer

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
src/app/components/menu_card.py
src/app/components/ui_style.py
src/app/components/empty_state.py
src/app/components/loading_state.py
src/app/components/sidebar_filters.py
```

App-ready artifact builder:

```text
src/pipeline/build_app_catalog.py
```

Validation tests:

```text
tests/test_app_data_validation.py
tests/test_fetch_igdb_selection.py
```

---

## 11. Current Implementation Status Summary

```text
Home:                 UI V2 cyberpunk menu
Explore Games:        UI V2 with List/Grid/Detailed views
Hidden Gems:          UI V2 with visible rule box and multiple views
Recommendations:      UI V2 step-by-step wizard
Chatbot:              Placeholder / teammate integration pending
Insights:             UI V2 deep analytics page
Predictive Model:     Placeholder / teammate integration pending
Methodology:          UI V2 continuous trust page
```

Recommended next improvements:

1. Run a manual Streamlit QA pass for the UI polish branch.
2. Fix any visual spacing/card issues found during browser testing.
3. Add better result pagination or "load more" behavior.
4. Add a game detail page or modal-style detail view if time allows.
5. Integrate teammate predictive artifacts when ready.
6. Integrate teammate RAG/vector-store artifacts when ready.
7. Prepare the final Streamlit demo flow for evaluators.
