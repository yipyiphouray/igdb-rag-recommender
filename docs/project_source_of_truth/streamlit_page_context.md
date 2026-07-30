# Streamlit Page Context

Last updated: 2026-07-28

This document describes the retained Streamlit MVP and internal analytics workbench. It is no longer the final user-facing product source of truth.

Current product boundary:

- Final user-facing product: Next.js website in `apps/website`.
- Final backend API: FastAPI in `api`.
- Retained internal prototype/workbench: Streamlit in `apps/streamlit`.

Use this document only when maintaining or running the Streamlit workbench. Use the website source-of-truth documents for final product behavior, presentation, and deployment.

Main app entry point:

```text
apps/streamlit/streamlit_app.py
```

Run command:

```text
cd apps/streamlit
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

- The app uses a refreshed curated 47,835-game IGDB analytical sample, not the full IGDB catalog.
- The extraction targeted 50,000 released main games from 2010 through 2024 and selected 47,835 because the earliest years had fewer eligible records than the configured yearly target.
- Quality and visibility cohorts are intentionally oversampled.
- Missing PopScore means unknown visibility, not low visibility.
- Diagnostic associations should not be interpreted as causal claims.

---

## Current Streamlit UI Direction

The Streamlit app completed an earlier UI polish pass and remains useful for internal review. The final visual direction is now defined by the custom website and `website_visual_style_guide.md`.

The user-facing discovery pages are intentionally cleaner and less technical:

- Home is a cyberpunk game-menu landing page with a 3-column clickable hover-panel grid.
- Explore Games and Hidden Gems support Grid View and Detailed View.
- Recommendations is a minimal step-by-step wizard with quick-start personas, Back, Next, Reset, and a Review/Confirm step.
- Insights is split into clear Descriptive and Diagnostic sections plus an export browser.
- Methodology is a continuous academic/trust page with headings, cards, formulas, caveats, and artifact audits instead of expander sections.

Technical explanations that were previously visible on discovery pages have been moved into Methodology or concise styled rule/caveat boxes.

---

## 1. Main App Home

File:

```text
apps/streamlit/streamlit_app.py
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

- Cyberpunk arcade-style title treatment without the old "cyberpunk game menu" label.
- Clickable hover menu panels linking to:
  - Explore Games;
  - Hidden Gems;
  - Recommendations;
  - Insights;
  - Methodology;
  - Chatbot;
  - Predictive / Similarity Scoring.
- Page details appear on hover.
- Panels are arranged in a 3-column menu grid.

Current status:

```text
Implemented and polished for UI V3.
```

Implementation notes:

- The Home page no longer shows featured hidden-gem cards.
- The Home page no longer shows dataset metric cards.
- The Home page no longer shows the technical signal explanation. Those definitions now live in Methodology.
- The full menu panel is clickable through `src/app/components/menu_card.py`.
- The 3-column menu layout is rendered through `src/app/components/home_menu.py`.
- Menu cards are rendered through `src/app/components/menu_card.py`.
- Shared CSS is injected through `src/app/components/ui_style.py`.

---

## 2. Home Page in Multipage Navigation

File:

```text
apps/streamlit/pages/1_Home.py
```

Purpose:

This page mirrors the main Home page inside Streamlit's multipage navigation. It exists because Streamlit treats `apps/streamlit/streamlit_app.py` and files inside `apps/streamlit/pages/` differently.

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
- 3-column menu grid.

Current status:

```text
Implemented and polished for UI V3.
```

Implementation note:

This page is intentionally standalone. It should not import `apps/streamlit/streamlit_app.py` directly because doing so can create blank-page behavior in Streamlit multipage navigation.

---

## 3. Explore Games

File:

```text
apps/streamlit/pages/2_Explore_Games.py
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
  - Grid View;
  - Detailed View.
- Detailed cards keep useful details inside the card rectangle.
- Grid cards use larger cover images where available.
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
Implemented and polished for UI V3.
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
apps/streamlit/pages/3_Hidden_Gems.py
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

- Discovery mode:
  - Balanced discovery;
  - Strict hidden gems;
  - More discoveries.
- Release-year range.
- Platform.
- Genre.
- Theme.
- Minimum rating score.
- Minimum rating activity.
- Number of candidates to show.

Current output:

- Short user-facing explanation.
- User-friendly hidden-gem explanation shown directly in a styled rule box.
- Matching candidate count.
- User-selectable Grid View and Detailed View.
- Game cards with candidate explanations.

Current status:

```text
Implemented and polished for UI V3.
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
apps/streamlit/pages/4_Recommendations.py
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

- Quick-start persona buttons.
- Centered step-by-step wizard with Back, Next, Reset, and final Review/Confirm controls.
- Final preference review before results are generated.
- Ranked recommendation cards.
- Recommendation score.
- Explanation text describing why each game matched.
- Technical scoring details are kept out of the main wizard flow and documented in Methodology.

Current status:

```text
Implemented and polished for UI V3.
```

Trust rules:

- Platform is treated as a hard gate when selected.
- Recommendations are limited to existing catalog games.
- The page does not predict ratings for imaginary games.
- Explanations are generated from actual scoring/filter components.
- Missing playtime does not penalize a game unless playtime data is needed for a selected fit bonus.

Known limitations:

- The scoring formula is intentionally simple for MVP clarity.
- This Streamlit page is retained as an internal workbench mirror.
- The final user-facing recommendation experience now lives in the website Recommend Me page and FastAPI recommendation endpoint.

---

## 6. Chatbot

File:

```text
apps/streamlit/pages/5_Chatbot.py
```

Purpose:

Provides the Streamlit workbench shell for testing guide-style project and catalog Q&A behavior through the shared backend service.

Primary audience:

- Developers validating backend guide behavior.
- Evaluators reviewing fallback behavior in the internal prototype.

Expected data/artifacts:

```text
data/app/app_game_catalog.parquet
docs/project_source_of_truth/ask_the_guide_knowledge_base.md
src/app/project_context_retrieval.py
api/
```

Service-layer dependency:

```text
src/app/rag_service.py
```

Current content:

- Guide integration status.
- Example prompt text box.
- Safe fallback response when backend guide behavior is unavailable.
- Expected active context and service checks.

Current status:

```text
Shared-service RAG page with graceful fallback behavior.
```

Required final behavior:

- Keep answers scoped to the project and catalog.
- Use structured backend tools for exact catalog facts where possible.
- Route ranked game recommendations to the dedicated Recommend Me flow.
- Avoid exposing internal source documents, file paths, retrieval metadata, or implementation artifacts.
- Give direct, factual answers when context is available and a scoped fallback when it is not.

Known limitations:

- The page is still visually simple compared with the final website `/guide` experience.
- The page depends on local backend and project-context artifacts being available.
- The page remains non-blocking so Explore, Hidden Gems, Insights, Methodology, and Recommendations can work even when the guide service is unavailable.

---

## 7. Insights

File:

```text
apps/streamlit/pages/6_Insights.py
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

- Descriptive Insights.
- Diagnostic Insights.
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
- Export browser does not display local file-system paths.
- Hidden-gem and coverage-only analysis sections are intentionally excluded from this page.

Current status:

```text
Implemented and polished for UI V3.
```

Known limitations:

- Large notebook tables are previewed with download buttons instead of fully rendered at page load.
- Hidden-gem and coverage-only outputs remain available in project files but are intentionally not part of this page.

---

## 8. Predictive / Similarity Scoring

File:

```text
apps/streamlit/pages/7_Predictive_Model.py
```

Purpose:

Provides the internal Streamlit shell for reviewing similarity-scoring outputs when needed.

Primary audience:

- Developers reviewing recommendation-scoring artifacts.
- Evaluators comparing the internal prototype against the final website implementation.

Optional internal artifacts:

```text
data/analytics/predictive/similarity_config.json
data/analytics/predictive/game_similarity_profiles.parquet
data/analytics/predictive/similarity_neighbors.parquet
data/analytics/predictive/persona_similarity_results.parquet
data/analytics/predictive/similarity_evaluation.json
```

Service-layer dependency:

```text
src/app/predictive_service.py
```

Current content:

- Predictive/similarity artifact status.
- Similarity configuration display if available.
- Similarity results preview if available.
- Optional artifact list for internal validation.

Current status:

```text
Internal workbench page; final user-facing flow lives in the website Recommend Me page.
```

Required final behavior:

- Show similarity objective.
- Show profile fields used for scoring.
- Show cosine similarity method.
- Show top-k relevance results.
- Show persona/manual evaluation results.
- Show limitations.
- Attach similarity outputs only to existing catalog games.

Known limitations:

- This page is not the primary final-product recommendation UI.
- This page should remain non-blocking even if optional internal artifacts are unavailable.

---

## 9. Methodology

File:

```text
apps/streamlit/pages/8_Methodology.py
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
- recompute similarity profiles;
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
src/app/components/home_menu.py
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
tests/test_app_filters.py
tests/test_recommendation_service.py
tests/test_hidden_gem_service.py
tests/test_app_artifact_schema.py
```

---

## 11. Current Streamlit Implementation Status Summary

```text
Home:                 UI V3 cyberpunk 3-column menu
Explore Games:        UI V3 with Grid/Detailed views
Hidden Gems:          UI V3 simplified discovery modes
Recommendations:      UI V3 minimal wizard with personas
Chatbot:              Internal workbench page; final chatbot lives on website /guide
Insights:             UI V3 descriptive/diagnostic split
Predictive/Similarity: Internal placeholder/workbench; final recommendation flow lives on website /recommendations
Methodology:          UI V2 continuous trust page
```

Recommended next improvements, if Streamlit is maintained:

1. Keep Streamlit non-blocking when optional RAG or similarity artifacts are unavailable.
2. Avoid adding new final-product-only logic to Streamlit unless it is also shared through `src/app`.
3. Use Streamlit for internal sanity checks, not as the final demo target.
4. Keep Streamlit documentation clearly separate from deployed website documentation.
