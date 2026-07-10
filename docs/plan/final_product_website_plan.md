# Final Product Website Plan
## IGDB Game Discovery & RAG Recommendation System

**Project:** IGDB Game Discovery & RAG Recommendation System  
**Team:** QUEST ACCEPTED!  
**Course:** BUSA 649  
**Plan Name:** Final Product Website Plan  
**Status:** Planning document  

---

# 0. Confirmed Decisions

The following decisions are confirmed for the final product direction:

| Decision Area | Confirmed Direction |
|---|---|
| Repository strategy | Build the website inside the same repository |
| Frontend stack | Next.js, React, TypeScript, Tailwind CSS |
| Backend stack | FastAPI, Python, Pydantic response schemas |
| Data source | Existing SQLite, parquet, and JSON artifacts |
| Minimum availability | Must run locally |
| Public deployment | Optional if it can be done for free without delaying the local MVP |
| Visual direction | Cyberpunk / game-menu inspired UI |
| Build strategy | Step-by-step vertical slices |
| Similarity and RAG ownership | Teammate owns core similarity/RAG logic |
| Predictive workflow | Recommendation questionnaire becomes the main predictive/similarity input |
| Streamlit role | Internal analytics workbench and backup demo |
| Website role | Final polished user-facing product |

The plan should prioritize a working foundation before deep UI polish. Detailed visual design should happen after the first website slice proves that routing, backend communication, and catalog data loading work correctly.

---

# 1. Purpose of This Plan

This document defines the project direction for moving from the current Streamlit MVP toward a fully customized final website.

The confirmed product direction is:

```text
Streamlit = MVP, internal analytics workbench, and backup demo
Custom website = final polished user-facing product
```

This direction is valid because Streamlit helped the team validate the data, pages, logic, and demo flow quickly, but the final user experience needs more UI/UX control than Streamlit comfortably provides.

---

# 2. Core Decision

The final product should be a custom website because the project needs:

- Full control over layout, branding, navigation, and page transitions.
- Better game-card design.
- More polished recommendation flows.
- Better chatbot UI.
- More responsive design across screen sizes.
- Cleaner separation between frontend presentation and backend logic.
- A stronger portfolio/demo experience.

Streamlit should not be removed immediately. It should remain useful as:

- An internal analytics dashboard.
- A debugging and validation interface.
- A backup demo if the website is not fully ready.
- A fast way to inspect app-ready artifacts.
- A place to show deeper descriptive/diagnostic tables that may not belong in the polished website.

---

# 3. Product Split

## 3.1 Final Website Role

The website should become the main user-facing product.

It should contain the polished experience for:

- Landing page.
- Game discovery.
- Hidden-gem browsing.
- Structured recommendations.
- Similarity-based match scoring results.
- RAG chatbot.
- Game detail views.
- Methodology summary.
- Final demo flow.

## 3.2 Streamlit Role

Streamlit should remain as the internal project workbench.

It can keep:

- Deep descriptive analytics tables.
- Diagnostic notebook-style charts.
- Data quality summaries.
- Artifact audit views.
- Internal debugging pages.
- Backup demo pages.

## 3.3 Rule for User Experience

The main user journey should not be split across Streamlit and the website.

Bad final flow:

```text
User opens website -> clicks recommendation -> gets redirected to Streamlit
```

Better final flow:

```text
User opens website -> explores games -> gets recommendations -> asks chatbot -> views results
```

Streamlit can still exist, but it should not interrupt the polished user-facing path.

---

# 4. Can Everything Transfer to a Website?

Yes. Everything important can be transferred into a website because the core project assets are not Streamlit-specific.

Reusable project assets include:

- SQLite database.
- App-ready parquet files.
- App-ready JSON files.
- Recommendation service logic.
- Hidden-gem logic.
- Similarity scoring logic.
- RAG retrieval logic.
- Data dictionary.
- Business rules.
- Methodology documentation.
- Findings reports.

The website does not replace the Python/data work. It becomes the polished frontend that consumes the existing assets through a backend API.

---

# 5. Confirmed Architecture

The confirmed final architecture is:

```text
Next.js / React frontend
        |
        v
FastAPI backend
        |
        v
SQLite database
Parquet / JSON app artifacts
Python recommendation services
Similarity scoring services
RAG retrieval services
```

## 5.1 Frontend

Confirmed frontend stack:

```text
Next.js
React
TypeScript
Tailwind CSS
```

The frontend owns:

- Layout.
- Visual design.
- Navigation.
- Game cards.
- Recommendation wizard UI.
- Chatbot UI.
- User interactions.
- Loading states.
- Error states.

## 5.2 Backend

Confirmed backend stack:

```text
FastAPI
Python
Pydantic response schemas
```

The backend owns:

- Reading SQLite data.
- Reading parquet/json app artifacts.
- Calling recommendation logic.
- Calling similarity scoring logic.
- Calling RAG retrieval/chatbot logic.
- Returning clean JSON responses to the website.

## 5.3 Data Layer

The data layer should reuse the existing project outputs:

```text
data/database/igdb_games.db
data/app/app_game_catalog.parquet
data/app/app_hidden_gems.parquet
data/app/app_filter_options.json
data/app/app_insight_summary.json
data/app/app_methodology_metrics.json
data/analytics/predictive/
data/rag/
```

The website should not directly rebuild these artifacts. The existing Python scripts and notebooks remain responsible for data generation.

## 5.4 Same-Repository Folder Structure

Because the website will live inside the same repository, the recommended structure is:

```text
Community_Project/
|-- api/
|   |-- main.py
|   |-- requirements-api.txt
|   |-- app/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- schemas/
|   |   |   |-- catalog.py
|   |   |   |-- recommendations.py
|   |   |   |-- similarity.py
|   |   |   `-- chatbot.py
|   |   |-- services/
|   |   |   |-- catalog_service.py
|   |   |   |-- hidden_gem_service.py
|   |   |   |-- recommendation_service.py
|   |   |   |-- similarity_service.py
|   |   |   |-- chatbot_service.py
|   |   |   `-- methodology_service.py
|   |   `-- routers/
|   |       |-- health.py
|   |       |-- catalog.py
|   |       |-- hidden_gems.py
|   |       |-- recommendations.py
|   |       |-- similarity.py
|   |       |-- chatbot.py
|   |       `-- methodology.py
|
|-- apps/
|   |-- streamlit/
|   |   |-- .streamlit/
|   |   |-- pages/
|   |   |-- _path_setup.py
|   |   `-- streamlit_app.py
|   |
|   `-- website/
|       |-- package.json
|       |-- next.config.ts
|       |-- tailwind.config.ts
|       |-- tsconfig.json
|       |-- src/
|       |   |-- app/
|       |   |   |-- page.tsx
|       |   |   |-- explore/
|       |   |   |   `-- page.tsx
|       |   |   |-- games/
|       |   |   |   `-- [gameId]/
|       |   |   |       `-- page.tsx
|       |   |   |-- hidden-gems/
|       |   |   |   `-- page.tsx
|       |   |   |-- recommendations/
|       |   |   |   `-- page.tsx
|       |   |   |-- similarity/
|       |   |   |   `-- page.tsx
|       |   |   |-- chatbot/
|       |   |   |   `-- page.tsx
|       |   |   `-- methodology/
|       |   |       `-- page.tsx
|       |   |-- components/
|       |   |-- lib/
|       |   |-- styles/
|       |   `-- types/
|
|-- data/
|-- docs/
|-- src/
`-- requirements.txt
```

Reasoning:

- `apps/streamlit/` isolates the Streamlit MVP/internal workbench from the repository root.
- `apps/website/` isolates the frontend dependencies from the Python project.
- `api/` isolates the FastAPI layer from the existing pipeline and Streamlit app.
- Existing `src/` logic can still be reused by the API where appropriate.
- Existing `data/` artifacts remain the shared source for Streamlit and the website backend.

## 5.5 Local Development Workflow

Minimum local workflow:

```text
Terminal 1:
cd api
uvicorn main:app --reload --port 8000

Terminal 2:
cd apps/website
npm run dev
```

Expected local URLs:

```text
Backend API:      http://localhost:8000
API docs:         http://localhost:8000/docs
Frontend website: http://localhost:3000
```

The frontend should read the backend URL from an environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Do not hard-code local paths to data files inside the frontend. Only the backend should know where SQLite, parquet, and JSON artifacts live.

---

# 6. Page Transfer Strategy

## 6.1 Transfer First

These pages should move to the website first because they are user-facing and benefit most from custom UI.

| Website Page | Reason to Transfer Early |
|---|---|
| Home | First impression and strongest branding opportunity |
| Explore Games | Needs polished cards, filters, and responsive layout |
| Hidden Gems | Strong project differentiator and good visual showcase |
| Recommendations | Needs a guided, polished user journey |
| Chatbot | Needs a custom conversational UI |

## 6.2 Transfer Second

These pages should move after the core user flow works.

| Website Page | Reason |
|---|---|
| Game Detail Page | Useful once Explore and Recommendations are stable |
| Methodology Summary | Important for academic trust but not the first build priority |
| Similarity Scoring Explanation | Useful after teammate similarity artifacts are ready |

## 6.3 Keep Mostly in Streamlit

These sections can remain mostly in Streamlit or be summarized lightly on the website.

| Streamlit/Internal Section | Reason |
|---|---|
| Full descriptive analytics tables | More analytical than user-facing |
| Full diagnostic charts | Useful for evaluator review but not core product UX |
| Data quality checks | Internal validation focus |
| Artifact audits | Internal debugging focus |

---

# 7. Proposed Website Pages

## 7.1 Landing Page

Purpose:

- Explain the product quickly.
- Establish the game-discovery theme.
- Route users into the core flows.

Content:

- Project title.
- Short value proposition.
- Main call-to-action: start recommendation wizard.
- Secondary call-to-action: explore catalog.
- Highlight cards for Hidden Gems, Recommendations, Chatbot, and Methodology.

## 7.2 Explore Games

Purpose:

- Let users browse the curated game catalog.

Features:

- Search by game title.
- Filter by platform.
- Filter by genre.
- Filter by theme.
- Sort by rating, rating count, release year, or visibility.
- Grid/list card layout.
- Game detail modal or page.

## 7.3 Hidden Gems

Purpose:

- Surface high-quality games with lower visibility.

Features:

- Hidden-gem definition summary.
- Hidden-gem cards.
- Filter by platform, genre, theme, and release year.
- Clear caveat that hidden gems are relative to the curated project sample.

## 7.4 Recommendations

Purpose:

- Give users a structured, guided recommendation flow that creates a user preference profile for cosine-similarity scoring.

Predictive/similarity role:

```text
The recommendation wizard asks multiple preference questions.
The answers are combined into a user preference profile.
The profile is converted into a vector.
The vector is compared against game profile vectors using cosine similarity.
The highest-similarity games become recommendation candidates.
```

Recommended UX:

```text
Step 1: Choose platform
Step 2: Choose genre / theme interests
Step 3: Choose mood / vibe words
Step 4: Optionally name favorite reference games
Step 5: Choose popular vs hidden gem preference
Step 6: Choose rating quality importance
Step 7: Review preferences
Step 8: Show recommendations
```

Scoring rule:

```text
Hard filters first:
- platform requirement
- released games
- main games when applicable

Then similarity scoring:
- genre answers
- theme answers
- mood/vibe answers
- favorite-game answers
- playstyle answers

Then ranking adjustments:
- rating quality
- hidden-gem boost
- popularity/rating-count confidence
```

Output:

- Ranked recommendations.
- Match explanation.
- Rating and rating evidence.
- Platform availability.
- Genre/theme tags.
- Caveats where data is missing.

## 7.5 Predictive / Similarity Scoring

Purpose:

- Present questionnaire-driven cosine-similarity match scoring in a user-understandable way.

This page should not look like a machine learning classifier dashboard.

It should show:

- Similarity objective.
- Profile fields used.
- Recommendation questions used to build the user preference profile.
- Example reference-game or preference-profile query.
- Top-k similar games.
- Relevance evaluation summary.
- Limitations.

Expected artifacts:

```text
data/analytics/predictive/similarity_config.json
data/analytics/predictive/game_similarity_profiles.parquet
data/analytics/predictive/similarity_neighbors.parquet
data/analytics/predictive/persona_similarity_results.parquet
data/analytics/predictive/similarity_evaluation.json
```

## 7.6 RAG Chatbot

Purpose:

- Let users ask for game recommendations in natural language.

The chatbot should:

- Use retrieved project game profiles.
- Avoid unsupported claims.
- Explain why games were recommended.
- Mention missing data when relevant.
- Ask users to clarify when the query is too broad or no match exists.

## 7.7 Methodology

Purpose:

- Build trust with evaluators and users.

Website methodology should be shorter than the full documentation.

Include:

- Data source.
- Curated sample logic.
- Quality and visibility signals.
- Hidden-gem definition.
- Recommendation scoring summary.
- Similarity scoring summary.
- RAG grounding rule.
- Known limitations.

## 7.8 Frontend Component Plan

The website should use reusable components instead of rebuilding page-specific UI repeatedly.

Recommended component groups:

```text
components/
|-- layout/
|   |-- AppShell.tsx
|   |-- SiteHeader.tsx
|   |-- SiteNav.tsx
|   `-- PageSection.tsx
|
|-- game/
|   |-- GameCard.tsx
|   |-- GameCardGrid.tsx
|   |-- GameDetailPanel.tsx
|   |-- RatingBadge.tsx
|   |-- PlatformBadgeList.tsx
|   `-- TagList.tsx
|
|-- filters/
|   |-- SearchBox.tsx
|   |-- PlatformFilter.tsx
|   |-- GenreFilter.tsx
|   |-- ThemeFilter.tsx
|   `-- SortSelect.tsx
|
|-- recommendations/
|   |-- RecommendationWizard.tsx
|   |-- WizardStep.tsx
|   |-- PreferenceSummary.tsx
|   |-- RecommendationResultCard.tsx
|   `-- MatchExplanation.tsx
|
|-- chatbot/
|   |-- ChatWindow.tsx
|   |-- ChatMessage.tsx
|   |-- RetrievedEvidence.tsx
|   `-- PromptExamples.tsx
|
`-- common/
    |-- LoadingState.tsx
    |-- ErrorState.tsx
    |-- EmptyState.tsx
    `-- StatusBadge.tsx
```

## 7.9 Cyberpunk Design Direction

The visual direction should stay cyberpunk/game-menu inspired, but detailed UI polish should happen after the website foundation works.

High-level design rules:

- Dark background.
- Neon accent colors.
- Game-menu style navigation.
- Strong card hover states.
- Clear visual hierarchy.
- Avoid cluttered dashboards on user-facing pages.
- Keep methodology and caveats visible but not visually overwhelming.

Recommended initial design tokens:

```text
background: near-black / dark navy
primary accent: electric cyan
secondary accent: neon magenta or violet
success accent: green
warning accent: amber
text: off-white
muted text: gray-blue
card background: translucent dark panel
border: subtle neon glow or thin glass border
```

Do not overbuild animations in the foundation phase. Add animation only after the data flow and pages are stable.

---

# 8. Backend API Design

The website should communicate with a backend API instead of reading local data files directly.

Recommended API endpoints:

```text
GET  /health
GET  /catalog/games
GET  /catalog/games/{game_id}
GET  /catalog/filter-options
GET  /hidden-gems
POST /recommendations
GET  /similarity/games/{game_id}
POST /similarity/query
POST /chat
GET  /methodology/summary
```

## 8.1 Endpoint Responsibilities

| Endpoint | Responsibility |
|---|---|
| `/health` | Verify backend is running |
| `/catalog/games` | Return paginated/filterable catalog records |
| `/catalog/games/{game_id}` | Return one game detail record |
| `/catalog/filter-options` | Return platform/genre/theme options |
| `/hidden-gems` | Return hidden-gem records |
| `/recommendations` | Return ranked structured recommendations |
| `/similarity/games/{game_id}` | Return similar games for a reference game |
| `/similarity/query` | Return similarity results for a preference profile |
| `/chat` | Return grounded RAG chatbot response |
| `/methodology/summary` | Return methodology metrics and caveats |

## 8.2 API Contract Details

### `GET /health`

Purpose:

- Confirm that the backend is running.

Example response:

```json
{
  "status": "ok",
  "service": "igdb-website-api",
  "version": "0.1.0"
}
```

### `GET /catalog/games`

Purpose:

- Return paginated, filterable game records for Explore Games.

Recommended query parameters:

```text
search
platform
genre
theme
release_year_min
release_year_max
sort
page
page_size
```

Example response shape:

```json
{
  "items": [
    {
      "game_id": 123,
      "name": "Example Game",
      "release_year": 2021,
      "total_rating": 84.2,
      "total_rating_count": 156,
      "popscore": 21.4,
      "genres": ["Adventure"],
      "themes": ["Sci-Fi"],
      "platforms": ["PC", "Nintendo Switch"],
      "summary": "Short summary text."
    }
  ],
  "page": 1,
  "page_size": 24,
  "total_items": 500,
  "total_pages": 21
}
```

### `GET /catalog/games/{game_id}`

Purpose:

- Return detailed data for one game.

Response should include:

```text
game_id
name
release_year
rating fields
visibility fields
genres
themes
keywords
platforms
companies
summary
storyline
hidden_gem flags if available
data caveats if applicable
```

### `GET /catalog/filter-options`

Purpose:

- Return all filter values needed by Explore, Hidden Gems, and Recommendations.

Example response shape:

```json
{
  "platforms": ["PC", "Nintendo Switch", "PlayStation 5"],
  "genres": ["Adventure", "RPG", "Shooter"],
  "themes": ["Fantasy", "Sci-Fi", "Horror"],
  "release_year_min": 2010,
  "release_year_max": 2024
}
```

### `POST /recommendations`

Purpose:

- Accept the recommendation questionnaire answers and return ranked games.

This endpoint is the main website-facing predictive/similarity workflow.

Recommended request body:

```json
{
  "platforms": ["PC"],
  "genres": ["RPG", "Adventure"],
  "themes": ["Fantasy"],
  "mood_words": ["immersive", "story-rich", "exploration"],
  "favorite_games": ["Baldur's Gate 3"],
  "playstyle_preferences": ["single-player", "turn-based"],
  "discovery_preference": "balanced",
  "rating_quality_importance": "high",
  "max_results": 10
}
```

Recommended response body:

```json
{
  "request_summary": {
    "hard_filters": ["PC"],
    "profile_terms": ["RPG", "Adventure", "Fantasy", "immersive", "story-rich"],
    "ranking_adjustments": ["rating_quality_high", "discovery_balanced"]
  },
  "items": [
    {
      "rank": 1,
      "game_id": 123,
      "name": "Example Game",
      "match_score": 0.87,
      "similarity_score": 0.81,
      "rating_score": 0.84,
      "hidden_gem_boost": 0.04,
      "platforms": ["PC"],
      "genres": ["RPG"],
      "themes": ["Fantasy"],
      "explanation": "Matched your RPG, fantasy, and story-rich preferences.",
      "caveats": []
    }
  ]
}
```

Rules:

- Platform requirements should be applied as hard filters.
- Questionnaire answers should be combined into a user preference profile.
- The user profile should be compared against game profile vectors using cosine similarity when teammate artifacts are available.
- Before teammate artifacts are available, the endpoint may return a placeholder or use the existing structured recommendation logic.
- The response should never claim a game is available on a platform unless the project data supports it.

### `GET /similarity/games/{game_id}`

Purpose:

- Return games similar to an existing catalog game.

Owner:

- Teammate-owned logic.

Initial behavior:

- Return a graceful placeholder if similarity artifacts are missing.

### `POST /similarity/query`

Purpose:

- Return similarity results for a preference-profile query.

Owner:

- Teammate-owned logic.

This endpoint can share request structure with `/recommendations`, but it should focus on similarity output rather than full recommendation ranking.

### `POST /chat`

Purpose:

- Return grounded RAG chatbot responses.

Owner:

- Teammate-owned RAG logic.

Recommended request body:

```json
{
  "message": "Recommend a cozy exploration game on Switch.",
  "conversation_id": "optional-session-id"
}
```

Recommended response body:

```json
{
  "answer": "Based on the project dataset, you may like ...",
  "retrieved_games": [
    {
      "game_id": 123,
      "name": "Example Game",
      "evidence": "Adventure genre, relaxing theme, available on Switch."
    }
  ],
  "caveats": ["Platform availability depends on IGDB metadata completeness."]
}
```

Rules:

- The chatbot must only recommend games retrieved from project data.
- Unsupported metadata should not be invented.
- Missing data should be disclosed when relevant.

## 8.3 Teammate-Owned Integration Contracts

Similarity scoring and RAG remain teammate-owned. The website/backend should still define stable contracts so integration is easier later.

Minimum similarity artifacts expected:

```text
data/analytics/predictive/similarity_config.json
data/analytics/predictive/game_similarity_profiles.parquet
data/analytics/predictive/similarity_neighbors.parquet
data/analytics/predictive/persona_similarity_results.parquet
data/analytics/predictive/similarity_evaluation.json
```

Minimum RAG artifacts expected:

```text
data/rag/game_profiles.parquet
data/rag/retrieval_metadata.parquet
data/rag/vector_store/
```

Until those artifacts are ready:

- Similarity pages should show pending status.
- Chatbot page should show placeholder status.
- Recommendation endpoint can use structured scoring fallback.
- Missing artifacts should not crash the website.

---

# 9. Implementation Phases

## 9.0 Build Strategy

Build the website in vertical slices.

Do not start by designing every page. Start by proving that the frontend can call the backend and render real project data.

Recommended order:

```text
Slice 1: Foundation
Backend health endpoint -> Next.js shell -> cyberpunk landing page -> API connection check

Slice 2: Catalog browsing
Catalog endpoint -> Explore Games page -> GameCard component -> pagination/filter basics

Slice 3: Game detail
Game detail endpoint -> Game detail page/modal -> related metadata display

Slice 4: Hidden gems
Hidden-gem endpoint -> Hidden Gems page -> caveats and sample definition

Slice 5: Recommendations
Questionnaire UI -> POST /recommendations -> ranked result cards -> explanations

Slice 6: Similarity placeholders/integration
Similarity endpoints -> pending status -> integrate teammate artifacts when ready

Slice 7: RAG placeholders/integration
Chatbot UI -> pending status -> integrate teammate RAG artifacts when ready

Slice 8: Methodology and polish
Methodology summary -> final cyberpunk visual polish -> demo script
```

Detailed visual design should start after Slice 1 and Slice 2 are working.

## Phase 1: Planning and Architecture

Goal:

- Define the website stack and API contract.

Tasks:

- Confirm frontend stack.
- Confirm backend stack.
- Create frontend folder inside the same repository.
- Create FastAPI backend skeleton.
- Define response schemas.
- Decide local development workflow.

Deliverable:

```text
Website architecture document and initial project skeleton.
```

Acceptance criteria:

```text
api/ folder exists.
apps/website/ folder exists.
Backend can start locally.
Frontend can start locally.
Frontend can call GET /health.
No production deployment required yet.
```

## Phase 2: Backend Data API

Goal:

- Expose existing project assets through API endpoints.

Tasks:

- Add `/health`.
- Add catalog loading service.
- Add filter-options endpoint.
- Add hidden-gems endpoint.
- Add recommendation endpoint using existing recommendation logic.
- Add methodology summary endpoint.

Deliverable:

```text
Backend can serve catalog, hidden-gem, recommendation, and methodology data as JSON.
```

Acceptance criteria:

```text
GET /health works.
GET /catalog/filter-options works.
GET /catalog/games returns paginated data.
GET /catalog/games/{game_id} returns one valid game.
GET /hidden-gems returns valid hidden-gem records.
POST /recommendations returns either fallback recommendations or a clear pending status.
Missing similarity/RAG artifacts do not crash the API.
```

## Phase 3: Website Foundation

Goal:

- Build the frontend shell and basic navigation.

Tasks:

- Create landing page.
- Create reusable layout.
- Create navigation.
- Create loading/error components.
- Create shared game-card component.
- Connect frontend to backend `/health`.

Deliverable:

```text
Website shell loads and can communicate with backend.
```

Acceptance criteria:

```text
Landing page loads at localhost.
Shared layout exists.
Cyberpunk visual direction is present at a basic level.
API health status can be displayed or verified.
Loading, empty, and error states exist.
No detailed UI polish is required yet.
```

## Phase 4: Core User Pages

Goal:

- Transfer the core user-facing Streamlit flows to the website.

Tasks:

- Build Explore Games.
- Build Hidden Gems.
- Build Recommendations wizard.
- Build game detail modal/page.
- Add responsive layout.

Deliverable:

```text
Website supports the main game discovery and recommendation journey.
```

Acceptance criteria:

```text
Explore Games renders real catalog records.
Users can search or filter at least by one field.
Game cards show useful fields only.
Game detail view loads from backend data.
Hidden Gems page renders hidden-gem records.
Recommendations wizard collects answers and returns ranked output or clear placeholder response.
```

## Phase 5: Similarity and RAG Integration

Goal:

- Integrate teammate similarity and RAG artifacts.

Tasks:

- Add similarity endpoints.
- Add similarity page or similarity section.
- Add chatbot endpoint.
- Add chatbot UI.
- Add retrieved evidence display.
- Add no-match and missing-data behavior.

Deliverable:

```text
Website supports similarity scoring and grounded chatbot recommendations.
```

Acceptance criteria:

```text
Similarity page clearly shows artifact status.
Similarity endpoint handles missing teammate artifacts gracefully.
Chatbot page clearly shows artifact status.
Chat endpoint handles missing teammate artifacts gracefully.
When artifacts are available, outputs only reference existing catalog games.
```

## Phase 6: Polish and Final Demo

Goal:

- Make the website demo-ready.

Tasks:

- Improve visual design.
- Add animations only if they do not distract.
- Tighten copy.
- Add final methodology page.
- Add clear limitations.
- Test core flows.
- Prepare demo script.

Deliverable:

```text
Polished final website ready for presentation.
```

Acceptance criteria:

```text
Main user journey does not require Streamlit.
Cyberpunk theme is visually consistent.
Core pages have clear loading/error/empty states.
Recommendation explanations are understandable.
Methodology and limitations are visible.
Local demo flow is stable.
Public deployment is attempted only if it is free and does not destabilize the local demo.
```

---

# 10. What Not to Do Too Early

Avoid these until the core website works:

- User login.
- Persistent user profiles.
- Live IGDB API calls from the website.
- Rebuilding data artifacts from the website.
- Complex deployment before local website flow is stable.
- Replacing all Streamlit pages before the website has page parity.
- Building advanced animations before the recommendation and chatbot flows work.

---

# 11. Evaluation and QA

## 11.1 Website QA Checklist

The final website should pass these checks:

- Landing page loads.
- Explore page loads catalog data.
- Filters work.
- Hidden Gems page loads hidden-gem records.
- Recommendation wizard returns ranked results.
- Recommendation explanations are understandable.
- Similarity page only uses existing catalog games.
- Chatbot responses are grounded in retrieved context.
- Missing artifacts fail gracefully.
- Backend API errors are handled cleanly in the UI.
- Main pages work on laptop-sized screens.
- No page depends on Streamlit to complete the main user journey.

## 11.2 Backend QA Checklist

The backend should pass these checks:

- `/health` returns success.
- Catalog endpoint returns expected fields.
- Filter-options endpoint returns non-empty options.
- Recommendation endpoint validates request inputs.
- Hidden-gems endpoint returns only valid hidden-gem records.
- Similarity endpoint returns valid existing `game_id` values.
- Chat endpoint does not return unsupported metadata.
- API responses have stable schemas.

---

# 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Website scope becomes too large | Delays final project | Transfer pages in phases and keep Streamlit as backup |
| Backend/API work takes longer than expected | Website cannot consume data | Start with read-only JSON endpoints first |
| Teammate similarity/RAG artifacts are delayed | Similarity/chatbot pages remain incomplete | Keep placeholders and integrate when artifacts are ready |
| UI polish takes time away from analytics | Weakens academic substance | Keep methodology, caveats, and evaluation visible |
| Deployment creates technical issues | Demo risk | Keep local website and Streamlit backup demo |
| Website and Streamlit wording diverge | Confusing documentation | Keep source-of-truth docs updated after major changes |

---

# 13. Recommended Next Step

The next concrete step is not to immediately rebuild the entire app or design every page.

Recommended next step:

```text
Create the apps/website and api skeletons inside the same repo, then build the smallest working slice:

Backend health endpoint -> Next.js shell -> cyberpunk landing page -> backend connection check
```

After that works, build:

```text
Explore Games -> Game Detail -> Hidden Gems -> Recommendations wizard
```

Then integrate Similarity Scoring and RAG Chatbot when teammate artifacts are ready.

---

# 14. Deployment Strategy

## 14.1 Minimum Requirement

The minimum requirement is a stable local website:

```text
FastAPI backend running locally
Next.js frontend running locally
Website can load project data through the backend
Main demo flow works without Streamlit
```

This local version is enough for the project if public deployment becomes too expensive, unstable, or time-consuming.

## 14.2 Optional Free Public Deployment

Public deployment is optional and should only be attempted after the local website is stable.

Possible free deployment approach:

```text
Frontend: Vercel free tier
Backend: Render free tier / Railway trial / Hugging Face Spaces / other free Python host
Data: committed app-ready artifacts or hosted small static artifacts if size allows
```

Deployment risks:

- Free backend services may sleep after inactivity.
- SQLite/parquet file paths may need adjustment.
- Large data artifacts may exceed free hosting limits.
- API cold starts may slow the demo.
- Environment variables must be configured carefully.

Deployment rule:

```text
Do not let public deployment block the local final demo.
```

## 14.3 Deployment Acceptance Criteria

Only consider public deployment successful if:

- Frontend loads publicly.
- Backend API loads publicly.
- Frontend can call backend successfully.
- Main catalog page loads real records.
- Recommendation flow works or clearly shows pending teammate integration.
- No secrets are exposed.
- The local version still works as backup.

---

# 15. Testing Strategy

## 15.1 Frontend Testing

Recommended checks:

- Page routes render.
- Shared layout renders.
- Game cards handle missing fields.
- Filters update query state.
- Recommendation wizard validates required questions.
- Loading, error, and empty states appear correctly.

## 15.2 Backend Testing

Recommended checks:

- Health endpoint returns `status = ok`.
- Catalog endpoints return valid schemas.
- Pagination works.
- Filter options are non-empty.
- Recommendation request validation works.
- Missing similarity/RAG artifacts return graceful responses.

## 15.3 Manual Demo Testing

Before presentation, manually test:

```text
1. Open landing page.
2. Navigate to Explore Games.
3. Search/filter games.
4. Open a game detail page.
5. Navigate to Hidden Gems.
6. Complete the Recommendations wizard.
7. Review ranked recommendation output.
8. Open Similarity page and verify status/results.
9. Open Chatbot page and verify status/results.
10. Open Methodology and verify caveats are visible.
```

---

# 16. Final Positioning

The project should be positioned this way:

> The team first built a Streamlit MVP to validate the analytics pipeline, recommendation logic, page structure, and data artifacts. After confirming the core product direction, the final user-facing product will move toward a custom website so the team can fully control the interface, interaction design, recommendation journey, and chatbot experience. Streamlit remains useful as an internal analytics workbench and backup demo, while the custom website becomes the polished final product experience.
