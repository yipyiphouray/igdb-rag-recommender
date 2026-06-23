# Streamlit MVP Architecture Plan
## IGDB Game Discovery & RAG Recommendation System

**Project:** IGDB Game Discovery & RAG Recommendation System  
**Team:** QUEST ACCEPTED!  
**Course:** BUSA 649  
**Product Direction:** User-facing game-discovery product with an evaluator-facing analytics backbone  
**Primary Delivery:** Local Streamlit MVP, with public deployment as an optional stretch goal after the MVP is stable  

---

# 1. Purpose of This Plan

This document defines the architecture for the Streamlit MVP of the IGDB Game Discovery & RAG Recommendation System.

The app should feel like a real game-discovery product for players while also giving evaluators a clear, inspectable view of the project's data engineering, four analytics pillars, recommendation logic, model outputs, RAG approach, and limitations.

The Streamlit app is not the place to rebuild the database, rerun extraction, retrain models, or generate embeddings. Those processes should remain in reproducible scripts and notebooks. Streamlit should load prepared, validated assets and present them through a polished interactive interface.

---

# 2. Product Vision

## 2.1 Core user problem

Players often face choice overload when trying to select a game. Traditional discovery methods rely heavily on broad genres, numeric ratings, or popularity rankings. They do not always reflect what a player actually wants, such as:

- Platform availability
- Mood or theme
- Gameplay style
- Desired playtime
- Multiplayer preferences
- Camera perspective
- Interest in lesser-known but high-quality games

## 2.2 Core user promise

> Help users discover games that fit their preferences, explain why each recommendation fits, and surface strong lower-visibility games without relying only on popularity.

## 2.3 Product positioning

The app should combine:

```text
Structured game exploration
+ explainable recommendation logic
+ hidden-gem discovery
+ predictive support
+ RAG-based conversational discovery
```

## 2.4 Product design principle

> Build a user-facing discovery product first, while making the evidence, methodology, and caveats easy for evaluators to inspect.

---

# 3. MVP Goals

The MVP should support four main user journeys.

## 3.1 Browse

Users can explore the game catalog using filters and search.

Examples:

```text
Show me highly rated games on Nintendo Switch.
Find horror games released after 2020.
Browse co-op games with strong ratings.
Find games with a third-person perspective.
```

## 3.2 Discover

Users can browse lower-visibility, high-quality candidate games.

Examples:

```text
Show hidden gems on PC.
Find lower-visibility RPGs with reliable ratings.
Show hidden-gem candidates released between 2018 and 2024.
```

## 3.3 Recommend

Users can enter structured preferences and receive ranked, explainable recommendations.

Examples:

```text
I want a solo fantasy game on Switch.
I want a highly rated strategy game with a shorter playtime.
I want an action game that is less popular but well received.
```

## 3.4 Ask

Users can eventually describe their needs in natural language through a RAG chatbot.

Examples:

```text
I want a relaxing sci-fi game I can play alone.
Recommend something dark, challenging, and not too long.
I want a cozy game for PC that is not one of the obvious blockbuster titles.
```

---

# 4. Scope Boundaries

## 4.1 In scope

```text
Streamlit application
Catalog explorer
Filters and game cards
Hidden-gem discovery
Rule-based or hybrid recommendation logic
Descriptive and diagnostic insight pages
Predictive-model integration page
RAG chatbot integration page
Methodology and limitation transparency
Local app execution
Public deployment only if time, hosting constraints, and MVP stability allow it
```

## 4.2 Out of scope for the MVP

```text
Custom React/Next.js website
User accounts
Authentication
Saved favorites
Persistent user profiles
Collaborative filtering
Live price tracking
Real-time API extraction
Continuous model retraining
Production microservice architecture
Advanced personalized memory
```

## 4.3 Stretch goals

These should only be considered after the Streamlit MVP is polished and stable.

```text
Custom website frontend
FastAPI backend
Persistent user profiles
Saved recommendation lists
User feedback loop
More advanced hybrid ranking
Live data refreshes
Store-price integration
```

---

# 5. Architecture Principles

## 5.1 Separate data, logic, and presentation

Use the following layered structure:

```text
IGDB extraction pipeline
        ->
Normalized SQLite database
        ->
Analytics notebooks and validated exports
        ->
App-ready datasets and artifacts
        ->
Streamlit service layer
        ->
Reusable UI components
        ->
Streamlit pages
```

## 5.2 Maintain a single source of truth

The core database remains:

```text
data/database/igdb_games.db
```

The Streamlit app should consume prepared assets based on that database.

Recommended authoritative folders:

```text
data/database/
data/analytics/descriptive/
data/analytics/diagnostic/
data/analytics/predictive/
data/recommendations/
data/rag/
data/app/
```

## 5.3 Do not flatten every relationship inside the app

The database is normalized because games can have multiple genres, themes, platforms, companies, keywords, release dates, screenshots, and other relationships.

Do not create one massive direct SQL join during every app interaction.

Instead:

- Preserve the normalized database as the authoritative data model.
- Create app-specific one-row-per-game datasets.
- Use prepared list fields for genres, themes, platforms, and other filterable attributes.
- Keep game-level grain for app browsing and recommendations.

## 5.4 Make every recommendation explainable

A recommendation should never be shown as a black box.

Every result should answer:

```text
Why was this game shown?
Which user preferences did it satisfy?
What rating evidence supports it?
Is it considered a lower-visibility, high-quality candidate?
Which information is unavailable or uncertain?
```

## 5.5 Preserve data caveats throughout the app

The current sample is curated, not market-representative.

The app must preserve these interpretation rules:

```text
total_rating = quality / reception signal
total_rating_count = rating evidence / rating activity signal
PopScore interest = visibility / current-interest signal
```

Important limitations:

```text
Missing PopScore means visibility is unknown, not low.
The full sample intentionally oversamples quality and visibility cohorts.
Unadjusted popularity or rating shares are not market prevalence estimates.
Association findings do not establish causation.
Games can belong to multiple genres, themes, platforms, and companies.
```

---

# 6. Recommended Repository Structure

```text
igdb-rag-recommender/
|
|-- streamlit_app.py
|
|-- pages/
|   |-- 1_Home.py
|   |-- 2_Explore_Games.py
|   |-- 3_Hidden_Gems.py
|   |-- 4_Recommendations.py
|   |-- 5_Chatbot.py
|   |-- 6_Insights.py
|   |-- 7_Predictive_Model.py
|   `-- 8_Methodology.py
|
|-- src/
|   |-- app/
|   |   |-- config.py
|   |   |-- constants.py
|   |   |-- data_loader.py
|   |   |-- database.py
|   |   |-- filters.py
|   |   |-- formatting.py
|   |   |-- recommendation_service.py
|   |   |-- hidden_gem_service.py
|   |   |-- predictive_service.py
|   |   |-- rag_service.py
|   |   |-- validation.py
|   |   |
|   |   `-- components/
|   |       |-- sidebar_filters.py
|   |       |-- game_card.py
|   |       |-- game_detail_panel.py
|   |       |-- metric_cards.py
|   |       |-- chart_helpers.py
|   |       |-- methodology_notice.py
|   |       |-- empty_state.py
|   |       `-- loading_state.py
|   |
|   `-- pipeline/
|       |-- build_app_catalog.py
|       |-- build_recommendation_features.py
|       |-- build_game_profiles.py
|       `-- build_app_insight_assets.py
|
|-- data/
|   |-- database/
|   |   `-- igdb_games.db
|   |
|   |-- analytics/
|   |   |-- descriptive/
|   |   |-- diagnostic/
|   |   `-- predictive/
|   |
|   |-- app/
|   |   |-- app_game_catalog.parquet
|   |   |-- app_hidden_gems.parquet
|   |   |-- app_filter_options.json
|   |   |-- app_insight_summary.json
|   |   `-- app_methodology_metrics.json
|   |
|   |-- recommendations/
|   |   |-- recommendation_feature_table.parquet
|   |   `-- recommendation_explanations.json
|   |
|   `-- rag/
|       |-- game_profiles.parquet
|       |-- retrieval_metadata.parquet
|       `-- vector_store/
|
|-- assets/
|   |-- logo/
|   |-- screenshots/
|   |-- diagrams/
|   `-- styles/
|
|-- tests/
|   |-- test_data_loader.py
|   |-- test_filters.py
|   |-- test_recommendation_service.py
|   `-- test_app_data_validation.py
|
|-- .streamlit/
|   `-- config.toml
|
|-- requirements.txt
|-- README.md
`-- .gitignore
```

Reusable app components should live under `src/app/components/` so Streamlit pages, services, and shared UI helpers import from one app package instead of splitting app code across root-level folders.

---

# 7. App-Ready Data Layer

## 7.0 Phase 0: artifact audit

Before building app-ready datasets, confirm that the source artifacts exist and identify which teammate-owned artifacts are still pending.

Required checks:

```text
Current SQLite database exists:
    data/database/igdb_games.db

Descriptive exports exist:
    data/analytics/descriptive/

Diagnostic exports exist:
    data/analytics/diagnostic/

Hidden-gem candidate output exists or can be generated from the diagnostic definition.

Predictive artifacts are present, pending, or intentionally stubbed.

RAG artifacts are present, pending, or intentionally stubbed.

All required app columns can be loaded directly or derived from the database and analytics exports.
```

This audit should be treated as the first implementation checkpoint. Do not build pages around assumed fields until their source is confirmed.

## 7.1 Purpose

Create a dedicated app-ready layer so Streamlit can load data quickly, avoid complex repeated joins, and preserve one row per game.

Recommended output folder:

```text
data/app/
```

## 7.2 Primary app dataset

Create:

```text
data/app/app_game_catalog.parquet
```

### Grain

```text
One row per game
```

### Recommended fields

```text
game_id
name
slug
release_year
summary
storyline
cover_url
screenshot_url

total_rating
total_rating_count
rating
rating_count
aggregated_rating
aggregated_rating_count

game_type_name
game_status_name
extraction_cohort

genres_list
themes_list
keywords_list
platforms_list
platform_families_list
platform_types_list
developers_list
publishers_list
game_modes_list
player_perspectives_list

num_platforms
num_genres
num_themes
num_keywords

custom_interest_score
custom_interest_percentile
popscore_available_flag

rating_available_flag
rating_reliable_flag
high_rated_flag
rag_ready_flag

normal_playtime_hours
completionist_playtime_hours

multiplayer_flag
online_coop_flag
offline_coop_flag
split_screen_flag
```

## 7.3 Handling multi-value fields

Recommended storage approach:

```text
Parquet list columns where feasible.
```

If Parquet is used, include `pyarrow` in `requirements.txt`. If deployment size, environment compatibility, or dependency issues become a problem, use CSV plus JSON list fields for smaller app artifacts.

If serialization or compatibility becomes difficult, use a standardized delimiter:

```text
Genre 1 | Genre 2 | Genre 3
```

Then provide shared parsing logic in `formatting.py` or `filters.py`.

Do not use inconsistent delimiters across fields.

## 7.4 Supporting app artifacts

### `app_hidden_gems.parquet`

Contains the final hidden-gem candidate list and explanation fields.

The default Balanced hidden-gem list should be generated from the finalized diagnostic definition and exported as an app artifact. The app should not silently calculate a different default rule than the one documented in the diagnostic notebook and report.

Sensitivity options can create alternate exploratory views, but the default Balanced view should remain the documented diagnostic rule.

Suggested fields:

```text
game_id
name
release_year
cover_url
total_rating
total_rating_count
custom_interest_percentile
hidden_gem_version
hidden_gem_score
genres_list
themes_list
platforms_list
candidate_explanation
```

### `app_filter_options.json`

Contains standardized filter values.

Suggested keys:

```text
release_years
genres
themes
platforms
platform_families
platform_types
game_modes
player_perspectives
rating_bands
cohorts
```

### `app_insight_summary.json`

Contains concise descriptive and diagnostic headline findings for the Insights page.

### `app_methodology_metrics.json`

Contains:

```text
total_games
release_year_start
release_year_end
games_per_year
quality_cohort_count
popularity_cohort_count
comparison_cohort_count
rating_coverage
reliable_rating_coverage
popscore_coverage
summary_coverage
theme_coverage
```

### `recommendation_feature_table.parquet`

Contains standardized and preprocessed scoring features used by the recommendation service.

### `game_profiles.parquet`

Contains RAG-ready text profiles, retrieval metadata, and game identifiers.

---

# 8. Navigation Architecture

Recommended navigation:

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

Navigation should be ordered around the user journey first:

```text
Discover -> Explore -> Recommend -> Ask
```

Analytics and methodology should remain easy to find but should not interrupt the product experience.

---

# 9. Page Specifications

# 9.1 Home

## Purpose

Give users a clear understanding of what the product does and guide them toward discovery actions.

## Main user-facing content

```text
Hero title
Short project value proposition
Quick action buttons
Featured game cards
Featured hidden gems
Short explanation of how the tool works
```

## Recommended content structure

```text
Hero:
    Find your next game without scrolling through thousands of titles.

Subheading:
    Explore games by platform, mood, play style, quality, and visibility.

Quick actions:
    Explore the catalog
    Discover hidden gems
    Get recommendations
    Ask the chatbot

Featured section:
    Trending discovery picks
    Hidden-gem spotlight
    How recommendations work
```

## Evaluator-facing support

Use a short footer or compact information box:

```text
Built from a curated 15,000-game IGDB sample.
Combines descriptive, diagnostic, predictive, and prescriptive analytics.
```

## Completion criteria

```text
Home page loads without errors.
All quick-action links work.
Featured game cards render correctly.
No dense methodology content dominates the page.
```

---

# 9.2 Explore Games

## Purpose

Let users browse the catalog using structured filters and search.

## Sidebar filters

```text
Title / keyword search
Release-year range
Platform
Platform family
Genre
Theme
Game mode
Player perspective
Rating range
Minimum rating evidence
Playtime range
Multiplayer preferences
Optional cohort filter
```

## Main results area

```text
Total result count
Sort selection
Game cards
Expandable game details
Pagination or result limit
```

## Recommended sort options

```text
Highest rating
Most rating evidence
Highest visibility
Newest release
Lowest visibility among reliable high-rated games
Best recommendation score
```

## Required display rules

```text
Do not label unrated games as low rated.
Do not treat missing PopScore as low visibility.
Display total_rating_count as rating evidence.
Show missing data honestly.
Use game-level filtering without duplicate rows.
```

## Completion criteria

```text
All filters work with multi-value genre/theme/platform fields.
Platform filtering returns only eligible games.
Result rows are unique by game_id.
No direct relationship join duplicates appear.
Empty states explain how to broaden filters.
```

---

# 9.3 Hidden Gems

## Purpose

Surface lower-visibility, high-quality candidates in a transparent way.

## Balanced candidate rule

```text
quality cohort
AND total_rating >= 80
AND total_rating_count >= 25
AND main game
AND PopScore available
AND within-year visibility percentile <= 40%
```

## Data source rule

```text
The default Balanced view should load from `data/app/app_hidden_gems.parquet`,
which should be generated from the finalized diagnostic hidden-gem definition.
```

The app may offer Conservative and Broad sensitivity settings, but those should be labeled as exploratory alternate views. They should not replace the documented diagnostic definition.

## User controls

```text
Genre
Theme
Platform
Release-year range
Minimum rating
Minimum rating evidence
Hidden-gem sensitivity setting
```

## Sensitivity options

```text
Conservative:
    Higher rating threshold and lower visibility percentile.

Balanced:
    Current project definition.

Broad:
    Lower rating threshold and wider visibility cutoff.
```

## Candidate card content

```text
Cover
Game title
Release year
Genres and themes
Platforms
Total rating
Rating evidence
Visibility percentile
Why it qualifies
```

## Required caveat

```text
This page identifies lower-visibility, high-quality candidates within the
curated project sample. It does not estimate overlooked games in the full
video game market.
```

## Completion criteria

```text
Candidates use the documented diagnostic rule.
Missing PopScore games are excluded from hidden-gem eligibility.
Sensitivity options are clearly labeled.
Every card explains why it qualifies.
```

---

# 9.4 Recommendations

## Purpose

Provide users with ranked and explainable game recommendations based on structured preferences.

## User input form

Use a guided form, not a large technical filter panel.

MVP inputs:

```text
Required platform
Preferred genres
Preferred themes or mood
Preferred release-year range
Desired quality level
Preference for hidden gems
```

Full target inputs after the MVP recommender works:

```text
Required platform
Preferred genres
Preferred themes or mood
Game mode preference
Perspective preference
Preferred release-year range
Desired quality level
Preference for hidden gems
Preferred playtime range
Multiplayer preferences
```

Optional natural-language preference box:

```text
What are you in the mood for?
```

At first, this text can guide the user to select structured options. Later, it can support RAG routing.

## Output content

Each recommendation should display:

```text
Cover
Title
Release year
Platforms
Genres
Themes
Rating
Rating evidence
Visibility information when available
Final recommendation score
Why it matches
```

## Hard filters

These should remove games from consideration:

```text
Platform availability
Main-game status
Released status when applicable
Cancelled or rumored records excluded
```

## Soft preferences

These should influence ranking:

```text
Genre match
Theme match
Game mode match
Perspective match
Quality score
Rating evidence
Hidden-gem preference
Playtime fit
Multiplayer fit
```

For the first implementation, keep the recommender intentionally simple:

```text
Hard gates:
    Platform, if specified
    Released main games
    Valid core metadata

MVP scoring:
    Genre match
    Theme match
    Quality score
    Rating evidence
    Hidden-gem boost
```

Add game mode, perspective, playtime, and multiplayer scoring only after the first recommendation flow works end to end.

## MVP scoring design

```text
Platform eligibility: required gate
Genre match:          0-30
Theme match:          0-20
Quality score:        0-15
Rating evidence:      0-5
Hidden-gem boost:     0-10
```

Store MVP weights centrally:

```python
MVP_RECOMMENDATION_WEIGHTS = {
    "genre": 30,
    "theme": 20,
    "quality": 15,
    "rating_evidence": 5,
    "hidden_gem": 10,
}
```

Full target scoring can later add:

```text
Game mode match:      0-10
Perspective match:    0-10
Playtime fit:         0-10
Multiplayer fit:      0-10
```

## Explanation template

```text
Recommended because it is available on [platform], matches your preferred
[genres/themes], supports [mode/perspective], and has a [rating] total rating
based on [rating count] ratings. [Optional hidden-gem note.]
```

## Completion criteria

```text
All recommended games satisfy hard platform constraints.
Each recommendation includes a readable explanation.
Score components are retained for debugging and evaluation.
Changing preferences changes the ranking logically.
No unavailable or invalid games are recommended.
```

---

# 9.5 Chatbot

## Purpose

Allow natural-language game discovery through RAG.

## Initial placeholder design

Before full RAG integration, build:

```text
Chat interface shell
Example prompts
Explanation of how the chatbot will work
Fallback status message when retrieval is unavailable
```

## Final RAG flow

```text
User prompt
    ->
Preference and intent extraction
    ->
Metadata filters where applicable
    ->
Vector retrieval from game profiles
    ->
Hybrid ranking with recommendation logic
    ->
Grounded answer and game cards
```

## Required chatbot behavior

```text
Recommend only database-backed retrieved games.
Do not invent game facts.
State uncertainty when metadata is missing.
Explain why each recommendation fits.
Use concise recommendation cards.
Allow users to open recommended games in the explorer.
```

## Teammate integration contract

Recommended artifacts:

```text
data/rag/game_profiles.parquet
data/rag/retrieval_metadata.parquet
data/rag/vector_store/
src/app/rag_service.py
```

Recommended service interface:

```python
def answer_game_query(
    query: str,
    filters: dict | None = None,
    top_k: int = 5
) -> dict:
    ...
```

Suggested returned object:

```text
answer_text
retrieved_game_ids
retrieved_games
applied_filters
retrieval_scores
warnings
```

## Completion criteria

```text
The chatbot handles unavailable vector-store artifacts safely.
All recommended games exist in app_game_catalog.
Answers are grounded in retrieved metadata.
No unsupported claims are made.
```

---

# 9.6 Insights

## Purpose

Translate completed descriptive and diagnostic analysis into a concise, polished product story.

## Recommended tabs

```text
Catalog Overview
Reception and Visibility
Hidden-Gem Patterns
Data Coverage and Limitations
```

## Recommended visual set

Keep only high-value visuals:

```text
Catalog composition by genre
Theme distribution
Platform coverage
Rating coverage
Quality versus PopScore relationship
User versus critic agreement
Hidden-gem distribution
Metadata coverage summary
```

## Content rules

```text
Do not rebuild every notebook chart.
Do not overload the page with CSV exports.
Use short takeaway statements.
Make cohort and sampling caveats visible.
Keep detailed analysis in notebooks and reports.
```

## Completion criteria

```text
Each visual has a clear question and interpretation.
Charts use correct game-level or relationship-level counting.
Caveats are visible where needed.
The page supports the app story rather than feeling like a raw dashboard dump.
```

---

# 9.7 Predictive Model

## Purpose

Demonstrate the predictive analytics pillar and integrate your teammate's work.

## Initial placeholder

```text
Model objective
Target definition
Feature groups
Evaluation metric placeholders
Model status
```

## Final page content

```text
Model objective
High-rated target definition
Training and test approach
Performance metrics
Confusion matrix
ROC curve
Feature importance
Prediction examples on catalog games
Model limitations
```

## Recommended integration artifacts

```text
data/analytics/predictive/model_metrics.json
data/analytics/predictive/feature_importance.csv
data/analytics/predictive/model_predictions.parquet
data/analytics/predictive/confusion_matrix.png
data/analytics/predictive/roc_curve.png
docs/predictive_model_methodology.md
```

## Important product rule

Do not let users type arbitrary imaginary game concepts and receive a fake predicted rating.

Use predictions only for existing catalog games:

```text
Model-estimated likelihood of being highly rated
```

Treat prediction as a supporting signal, not a replacement for observed ratings.

## Completion criteria

```text
The page loads even when artifacts are missing.
Model metrics are clearly labeled.
Prediction outputs are tied to existing games.
Limitations are shown.
```

---

# 9.8 Methodology

## Purpose

Provide transparent evidence for evaluators and interested users.

## Sections

```text
Project overview
Data source
Curated extraction design
Database architecture
Four-pillar framework
Descriptive and diagnostic methods
Predictive method
Recommendation logic
RAG approach
Data quality checks
Known limitations
```

## Mandatory caveats

```text
The dataset is a curated sample, not the full IGDB catalog.
Quality and popularity cohorts are intentionally oversampled.
Rating coverage is incomplete.
Missing PopScore means unknown visibility.
Correlation does not establish causality.
Many category memberships overlap.
```

## Completion criteria

```text
Methodology is clear and readable.
It explains the sample design accurately.
It does not overclaim causal or market-level findings.
It links users back to relevant Insights pages where appropriate.
```

---

# 10. Core Service Layer

## 10.1 `data_loader.py`

Responsibilities:

```text
Load app-ready Parquet and JSON artifacts.
Cache repeated reads.
Validate required columns.
Return clean DataFrames.
```

Recommended pattern:

```python
@st.cache_data
def load_app_catalog():
    return pd.read_parquet(APP_CATALOG_PATH)
```

## 10.2 `filters.py`

Responsibilities:

```text
Apply structured filters.
Handle list-like multi-value fields.
Preserve one row per game.
Return filtered results and counts.
```

## 10.3 `recommendation_service.py`

Responsibilities:

```text
Accept preference inputs.
Apply hard filters.
Calculate scoring components.
Rank candidate games.
Generate explanation text.
Return top N results.
```

## 10.4 `hidden_gem_service.py`

Responsibilities:

```text
Load hidden-gem candidates.
Apply page filters.
Support sensitivity settings.
Generate candidate explanations.
```

## 10.5 `predictive_service.py`

Responsibilities:

```text
Load predictive artifacts.
Attach model probabilities to existing catalog games.
Provide metrics and visual paths.
Return graceful fallback output when files do not exist.
```

## 10.6 `rag_service.py`

Responsibilities:

```text
Accept user query.
Call retrieval service.
Apply metadata filters where possible.
Return answer text, retrieved game IDs, scores, warnings, and metadata.
```

## 10.7 `validation.py`

Responsibilities:

```text
Check expected artifact existence.
Check required columns.
Check duplicate game IDs.
Check rating ranges.
Check hidden-gem candidate requirements.
Check model and RAG integration readiness.
```

---

# 11. Reusable Interface Components

## 11.1 Game card

Use one consistent game-card component across Explore, Hidden Gems, Recommendations, and Chatbot pages.

Recommended content:

```text
Cover
Title and release year
Rating and rating evidence
Platforms
Genres
Themes
Short summary
Why it matches
Optional hidden-gem label
Expand for details
```

## 11.2 Game detail panel

Recommended detail content:

```text
Summary
Storyline
Developer and publisher
Genres
Themes
Keywords
Platforms
Modes
Multiplayer support
Playtime
Rating details
Visibility details
External links
```

## 11.3 Methodology notice

Use small reusable notices for caveats.

Examples:

```text
Visibility unavailable for this game.
Rating based on limited evidence.
Hidden-gem classification is relative to the curated project sample.
Multiplayer metadata is unavailable and should not be interpreted as no support.
```

## 11.4 Empty state

Examples:

```text
No games matched all selected filters.
Try removing one theme, broadening the year range, or lowering the minimum rating threshold.
```

## 11.5 Loading state

Use consistent loading messages for:

```text
Loading the catalog
Applying filters
Generating recommendations
Retrieving game profiles
Loading predictive artifacts
```

---

# 12. Visual and Product Design System

## 12.1 Product tone

The app should feel:

```text
Curated
Modern
Playful but credible
Insightful
Not overly technical
```

## 12.2 Design consistency requirements

Define and reuse:

```text
Primary accent color
Secondary accent color
Background color
Card styling
Tag styling
Chart formatting
Button behavior
Heading hierarchy
Spacing system
Image aspect ratios
```

## 12.3 Recommended UI behavior

```text
Use wide layout.
Keep sidebar filters collapsible where possible.
Use game covers as visual anchors.
Use tags sparingly.
Avoid dense tables in discovery pages.
Use expandable sections for technical details.
Use charts only when they answer a decision-relevant question.
```

## 12.4 Required visual distinction

Use different visual labels for:

```text
Observed rating
Rating evidence
Visibility signal
Hidden-gem candidate
Model prediction
RAG recommendation
```

These are different concepts and should not be visually conflated.

---

# 13. Testing Plan

## 13.1 Data tests

```text
App dataset contains one row per game.
Required columns exist.
No duplicate game IDs.
Ratings remain in valid range.
Platform lists are present for eligible games.
Hidden-gem output satisfies the documented rule.
```

## 13.2 Functional tests

```text
Platform filtering excludes unavailable games.
Genre filtering works for multi-genre games.
Recommendation results satisfy hard filters.
Missing PopScore is never treated as low visibility.
Predictive page handles missing artifacts.
Chatbot page handles unavailable retrieval service.
```

## 13.3 Recommendation tests

```text
A requested platform is always enforced.
A genre preference increases relevant games in ranking.
Hidden-gem preference changes ranking without overriding platform eligibility.
Explanations match actual scoring components.
```

## 13.4 User-experience tests

Ask several users to complete:

```text
Find a highly rated Switch game.
Find a lower-visibility game in a preferred genre.
Get recommendations for a mood and platform.
Understand why a recommendation was returned.
Locate the project limitations.
```

Observe:

```text
Where they hesitate.
Which filters they misunderstand.
Whether game-card content is sufficient.
Whether explanations feel useful.
Whether charts add value or distract.
```

---

# 14. Local Execution and Optional Deployment

## 14.1 Stage 1: Local execution

Before considering any deployment, verify:

```text
The app runs from a clean environment.
Relative paths work.
All pages load.
Data artifacts are available.
Missing predictive and RAG artifacts fail gracefully.
No secrets are committed.
```

## 14.2 Stage 2: Optional public Streamlit deployment

Public deployment is optional for the MVP. It should only be attempted after the local Streamlit app is stable and should not delay the core analytics, recommendation, predictive, or RAG deliverables.

Recommended first hosting option:

```text
Streamlit Community Cloud
```

Requirements:

```text
GitHub repository
requirements.txt
public-safe data assets
Streamlit configuration
secret management
reasonable application size
```

## 14.3 Secret-management rules

Never commit:

```text
Twitch client secret
Embedding API keys
LLM API keys
Database credentials
Private tokens
```

Use:

```text
.streamlit/secrets.toml locally
Streamlit Cloud secrets in deployment
.gitignore for local secret files
```

## 14.4 Stage 3: Custom website stretch goal

Only consider after the Streamlit MVP is polished.

Potential future architecture:

```text
Frontend: Next.js or React
Backend: FastAPI
Database: PostgreSQL
RAG service: separate API
Hosting: Vercel plus Render, Railway, or cloud provider
```

This is not part of the required MVP.

---

# 15. Data Contracts With Teammate

## 15.1 Predictive analytics contract

Your teammate should provide:

```text
model_metrics.json
feature_importance.csv
model_predictions.parquet
confusion_matrix.png
roc_curve.png
predictive_model_methodology.md
```

Recommended minimum fields for `model_predictions.parquet`:

```text
game_id
predicted_high_rated_probability
predicted_high_rated_class
model_version
prediction_available_flag
```

## 15.2 RAG contract

Your teammate should provide:

```text
game_profiles.parquet
retrieval_metadata.parquet
vector_store/
rag_service.py or documented callable interface
```

Recommended minimum fields for `game_profiles.parquet`:

```text
game_id
profile_text
embedding_status
metadata_version
```

## 15.3 Integration behavior

The app should safely support three states:

```text
Not integrated:
    Page displays roadmap and placeholder.

Partially integrated:
    Page loads artifacts and provides limited output.

Fully integrated:
    Page provides final predictive or RAG interactions.
```

## 15.4 Initial integration priority

The first Streamlit implementation should include Predictive Model and Chatbot pages as placeholder/integration-contract pages. These pages should clearly show what artifacts are expected from the teammate and should fail gracefully when those artifacts are missing.

Predictive and RAG availability should not block:

```text
Explore Games
Hidden Gems
Insights
Methodology
Basic structured Recommendations
```

---

# 16. MVP Acceptance Criteria

The MVP is complete when all of the following are true.

## Product

```text
Users can browse the catalog.
Users can filter by platform, genre, theme, and year.
Users can view game cards and details.
Users can explore hidden-gem candidates.
Users can receive explainable recommendations.
```

## Analytics

```text
Insights page communicates key descriptive and diagnostic findings.
Methodology accurately explains the curated sample and caveats.
Predictive model page can display teammate outputs.
```

## Technical

```text
The app runs locally from a clean environment.
Prepared data artifacts are loaded efficiently.
No duplicate game records appear in main results.
Caching is used for repeated data loads.
Missing artifacts fail gracefully.
Secrets are not committed.
```

## Trustworthiness

```text
Missing PopScore is not treated as low visibility.
Rating evidence is distinguished from visibility.
Hidden gems are described as within-sample candidates.
No causal claims are made from diagnostic associations.
Recommendation explanations reflect actual filters and scores.
```

## Deployment

```text
The app is structured so it can be deployed later if time and hosting constraints permit.
Public deployment is optional and should not delay the local MVP.
```

---

# 17. Recommended Build Order

Do not treat this as a weekly schedule. It is the preferred dependency order.

```text
0. Confirm source artifacts and required app fields.
1. Create app-ready datasets and validation checks.
2. Build shared data loader and formatting utilities.
3. Build reusable game-card and detail-panel components.
4. Build Explore Games.
5. Build Hidden Gems using the finalized diagnostic definition.
6. Build Methodology page so caveats are available early.
7. Build Insights using selected analytics outputs.
8. Build a basic Recommendations page with transparent MVP scoring.
9. Build Home page around the completed discovery features.
10. Add Predictive Model placeholder and integration contract.
11. Add Chatbot placeholder and integration contract.
12. Integrate teammate artifacts after their interfaces are stable.
13. Run functional, UX, and local execution testing.
14. Attempt public deployment only if the local MVP is stable and time permits.
```

---

# 18. Immediate Next Steps

The most important immediate work is the app-ready data layer.

```text
0. Run the artifact audit:
   - confirm `data/database/igdb_games.db`;
   - confirm descriptive exports;
   - confirm diagnostic exports;
   - identify pending predictive and RAG artifacts.
1. Build `app_game_catalog.parquet`.
2. Build `app_hidden_gems.parquet` from the finalized diagnostic hidden-gem rule.
3. Build `app_filter_options.json`.
4. Write `data_loader.py`.
5. Write validation checks for app artifacts.
6. Build a reusable game card.
7. Start with the Explore Games page.
```

Once Explore Games is stable, Hidden Gems and Recommendations should reuse the same data, components, and filtering logic.
