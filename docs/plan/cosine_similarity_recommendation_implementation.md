# Cosine Similarity Recommendation Implementation

## 1. Purpose

This plan defines how cosine similarity should be integrated into the existing recommendation flow.

The main decision is:

```text
Cosine similarity should power the existing Recommendations experience.
It should not become a separate competing recommendation page.
```

The website should keep one main user-facing recommendation journey:

```text
Recommendations wizard -> backend recommendation endpoint -> ranked game results
```

Cosine similarity becomes the matching engine behind that journey.

---

## 2. Current State

The current website already has:

- a Next.js frontend under `apps/website/`;
- a FastAPI backend under `api/`;
- a `POST /recommendations` endpoint;
- a structured recommendation fallback in `api/app/services/recommendation_service.py`;
- app-ready catalog data in `data/app/app_game_catalog.parquet`;
- teammate-owned hybrid retrieval and similarity/RAG work merged into `dev`;
- active RAG/hybrid retrieval documentation under `docs/project_source_of_truth/`;
- an older SQLite-based cosine recommender in `src/recommender_engine.py`, which should not be the primary website integration path because the final website backend is Parquet-first.

The current recommendation endpoint returns usable ranked recommendations, but it still reports:

```text
structured_fallback_active
```

or:

```text
similarity_artifacts_available_not_integrated
```

when similarity artifacts exist but are not yet wired into the endpoint.

For this implementation, the first cosine-similarity version should not depend on missing predictive parquet artifacts. It should build metadata-based vectors directly from `data/app/app_game_catalog.parquet`.

---

## 3. Target Direction

The target recommendation flow is:

```text
1. User answers recommendation wizard questions.
2. User optionally enters games they played recently.
3. Backend validates the request.
4. Backend applies hard filters such as platform availability.
5. Backend builds a metadata-based user preference profile.
6. Backend uses cosine similarity to compare that profile against metadata-based game profiles.
7. Backend applies ranking adjustments for quality, evidence, hidden-gem preference, visibility, and playtime.
8. Backend returns ranked recommendations with explanations.
```

The final user should not need to know whether the score came from filtering, cosine similarity, or a ranking adjustment. That explanation belongs in Methodology or a technical section.

---

## 4. Why Recent Games Should Be Added

Adding recent games is a strong direction because it provides concrete behavioral evidence.

Questionnaire answers such as genre, theme, and mood are useful, but recent games tell the system what the user has actually played. In the first implementation, recently played games should be interpreted as taste signals for finding similar games.

Recommended wizard question:

```text
Recently played games
Tell us up to 5 games you played recently.
```

Optional later enhancement:

```text
Do you want something similar to these games, or something different?
```

For the first implementation, assume the user wants recommendations similar to the recent games they provide. The "similar versus different" question can be added later if time allows.

---

## 5. Recommendation Request Contract

The current request body already supports several useful fields.

The cosine-similarity version should keep the existing structure and strengthen the role of `favorite_games` or rename it in the UI as recent games.

Recommended request body:

```json
{
  "platforms": ["PC"],
  "genres": ["RPG", "Adventure"],
  "themes": ["Fantasy"],
  "mood_words": ["immersive", "story-rich", "exploration"],
  "favorite_games": ["Baldur's Gate 3", "Disco Elysium"],
  "playstyle_preferences": ["single-player", "turn-based"],
  "discovery_preference": "balanced",
  "rating_quality_importance": "high",
  "desired_playtime": "20-40 hours",
  "release_year_min": 2010,
  "release_year_max": 2024,
  "max_results": 10
}
```

UI wording can call `favorite_games`:

```text
Recent games you played
```

The backend can keep the field name for compatibility unless the API schema is intentionally changed later.

---

## 6. Backend-First Implementation Rule

Cosine similarity should be implemented in the shared backend/service layer first, not directly in Streamlit.

Recommended layering:

```text
metadata-based cosine adapter using app_game_catalog.parquet
        |
        v
api/app/services/recommendation_service.py
        |
        v
api/app/routers/recommendations.py
        |
        v
apps/website/src/app/recommendations/
```

Reasoning:

- The website is the final user-facing product.
- Streamlit should not become the source of truth for recommendation logic.
- Shared backend logic keeps website and Streamlit outputs consistent.
- The recommendation endpoint becomes easier to test.
- RAG can integrate later without rewriting frontend logic.

Streamlit can consume the same backend later if needed, but it should not be the first integration target.

The first website implementation should use metadata-based cosine similarity from `app_game_catalog.parquet`. It should not call the older SQLite-based `ContentBasedRecommender` directly unless the team later decides to refactor that code to be Parquet-native.

---

## 7. Similarity Logic Design

Confirmed implementation decisions:

- Use metadata-based cosine similarity.
- Use `data/app/app_game_catalog.parquet` as the authoritative game profile source.
- Interpret recent games as "games the user played recently" and use them as similar-taste seed signals.
- Match recent-game titles with exact matching first and fuzzy matching second.
- Exclude matched seed games from returned recommendations by default.
- Keep the existing structured fallback if cosine scoring cannot produce reliable results.

## 7.1 Hard Filters

Hard filters should happen before similarity ranking.

Hard filters include:

- platform availability when the user selects a platform;
- release-year range when selected;
- valid catalog games only;
- optionally released/main-game constraints if already encoded in the app catalog.

Hard filters should not be replaced by similarity. If a user asks for PC games, the backend should not recommend a game unless the catalog says it is available on PC.

## 7.2 User Preference Profile

The backend should build a user preference profile from:

- selected platforms;
- selected genres;
- selected themes;
- mood words;
- playstyle preferences;
- desired playtime;
- discovery preference;
- recent/favorite games.

Structured answers and recent-game seeds should be combined into one profile.

The first version should create vectors from available catalog metadata instead of relying on a separate precomputed profile artifact.

Candidate metadata fields:

- platforms;
- genres;
- themes;
- game modes;
- player perspectives;
- keywords if available and lightweight enough;
- developers or publishers only if useful and not too sparse;
- rating-quality bucket or normalized rating as a small numeric feature;
- playtime band when available.

The exact feature set should be limited to fields already present in `app_game_catalog.parquet` so the backend does not depend on SQLite joins during recommendation-time execution.

## 7.3 Recent-Game Seed Matching

For each recent game entered by the user:

1. Normalize the title.
2. Search for the closest matching game in `app_game_catalog.parquet`.
3. Use exact match first.
4. Use fuzzy title matching only if exact match fails.
5. Return unmatched titles in the request summary or caveats.

Rules:

- Do not crash if a recent game cannot be matched.
- Do not recommend the same seed games back by default.
- If multiple recent games are matched, average or otherwise combine their game vectors.
- Recent-game similarity should influence the result, but should not completely override explicit platform or preference constraints.
- Treat the seed-game vector as a similar-taste signal for v1.

## 7.4 Candidate Similarity

Once a user profile vector exists:

```text
similarity_score = cosine(user_profile_vector, game_profile_vector)
```

The similarity score should be normalized to a user-readable `0.0` to `1.0` range.

Implementation note:

```text
No separate `game_similarity_profiles.parquet` artifact is required for v1.
Game vectors can be generated in memory from `app_game_catalog.parquet` and cached by the backend process.
```

## 7.5 Ranking Adjustments

The final ranking should combine similarity with project-specific scoring adjustments.

Recommended conceptual formula:

```text
final_score =
    similarity_weight * cosine_similarity
  + quality_weight * rating_quality_score
  + evidence_weight * rating_evidence_score
  + discovery_weight * hidden_gem_or_visibility_adjustment
  + playtime_weight * playtime_fit_score
```

The exact weights should be tuned after testing. The first implementation can use conservative weights so similarity remains the main ranking factor.

Recommended initial weighting:

```text
cosine similarity: 65%
rating quality:   15%
rating evidence:  10%
discovery fit:     5%
playtime fit:      5%
```

These weights are starting points, not final truth.

---

## 8. Response Contract

The existing response shape should be preserved as much as possible.

Recommended response:

```json
{
  "mode": "cosine_similarity",
  "similarity_status": "metadata_cosine_similarity_active",
  "request_summary": {
    "hard_filters": ["PC"],
    "profile_terms": ["RPG", "Adventure", "Fantasy", "story-rich"],
    "favorite_games": ["Baldur's Gate 3", "Disco Elysium"],
    "matched_seed_games": ["Baldur's Gate 3", "Disco Elysium"],
    "unmatched_seed_games": [],
    "ranking_adjustments": [
      "cosine_similarity",
      "rating_quality",
      "rating_evidence",
      "discovery_preference",
      "playtime_fit"
    ]
  },
  "items": [
    {
      "rank": 1,
      "game_id": 123,
      "name": "Example Game",
      "match_score": 0.89,
      "similarity_score": 0.84,
      "rating_score": 0.81,
      "hidden_gem_boost": 0.03,
      "explanation": "Matched your fantasy RPG preference and similarity to your recent games.",
      "caveats": []
    }
  ]
}
```

Fallback response should remain supported:

```text
mode = structured_fallback
similarity_status = structured_fallback_active
```

Recommended active-mode labels:

| Situation | `mode` | `similarity_status` |
|---|---|---|
| Metadata cosine succeeds | `cosine_similarity` | `metadata_cosine_similarity_active` |
| Not enough usable preference input | `structured_fallback` | `structured_fallback_active` |
| Required catalog columns unavailable | `structured_fallback` | `metadata_cosine_unavailable_fallback_active` |

---

## 9. Explanation Rules

Each recommendation should explain why it appeared.

Good explanation:

```text
Matched your RPG, fantasy, and story-rich preferences, and is similar to Baldur's Gate 3 through genre/theme overlap.
```

Bad explanation:

```text
Recommended because cosine similarity was 0.84291.
```

Explanations should mention:

- matched genres;
- matched themes;
- matched mood/playstyle terms;
- recent-game similarity when applicable;
- platform fit;
- hidden-gem or discovery adjustment if relevant;
- rating caveats when the rating evidence is weak.

---

## 10. UI Changes Needed

The website Recommendations page should add a recent-games step.

Recommended wizard steps:

```text
1. Platform and availability
2. Genres and themes
3. Mood and playstyle
4. Recent games / reference games
5. Discovery preference
6. Results
```

Recent-games UI requirements:

- allow up to 5 game titles;
- support comma-separated entry or individual input chips;
- explain that these games guide the match;
- show clear messaging if a typed game cannot be matched;
- avoid recommending the same seed games back unless explicitly allowed later.

Recommended copy:

```text
Recent games
Add up to 5 games you played recently.
```

Helper text:

```text
These help the recommender understand your taste beyond genre filters.
```

---

## 11. Implementation Phases

## Phase 1: Confirm Metadata Feature Inputs

Goal:

- Confirm which `app_game_catalog.parquet` columns should be used for metadata-based cosine similarity.

Tasks:

- Inspect available app catalog columns.
- Choose stable vector fields for platforms, genres, themes, game modes, perspectives, and playtime.
- Avoid columns that are too sparse or expensive for the first implementation.
- Confirm seed games can be resolved from the catalog title field.
- Confirm the older SQLite-based recommender is not required for v1.

Deliverable:

```text
Confirmed metadata vector feature list.
```

## Phase 2: Backend Adapter

Goal:

- Add metadata-based cosine similarity inside the FastAPI recommendation service.

Tasks:

- Add a cosine-similarity adapter function.
- Load the app catalog lazily and cache metadata vectors in memory.
- Convert `RecommendationRequest` into a metadata-based user vector.
- Match recent/favorite game titles to catalog records.
- Apply platform and year hard filters.
- Exclude matched seed games from returned recommendations by default.
- Return ranked games using the existing `RecommendationResponse` schema.
- Keep structured fallback active when cosine scoring has insufficient input or required catalog columns are unavailable.

Deliverable:

```text
POST /recommendations can return cosine-similarity-backed results.
```

## Phase 3: Website Wizard Update

Goal:

- Let the user provide recent games.

Tasks:

- Add a recent-games step to the Recommendations page.
- Store recent game entries in frontend state.
- Send recent games through the existing `favorite_games` field or an agreed renamed field.
- Display matched and unmatched seed games in the result summary if provided by the backend.

Deliverable:

```text
Website recommendation flow collects recent-game signals.
```

## Phase 4: Explanation and Result Polish

Goal:

- Make cosine-backed recommendations understandable.

Tasks:

- Show match score and explanation.
- Show why recent games influenced the result.
- Show caveats for missing ratings or unmatched seed games.
- Avoid overexposing technical scoring math in the main results UI.

Deliverable:

```text
Results feel useful to users and defensible to evaluators.
```

## Phase 5: Testing and Validation

Goal:

- Confirm the recommendation system is stable and relevant.

Required checks:

- API returns fallback results when similarity artifacts are missing.
- API returns metadata cosine-similarity results using `app_game_catalog.parquet`.
- Platform hard filters are respected.
- Recent game seed titles are matched correctly.
- Unmatched seed titles are reported cleanly.
- The system does not recommend seed games back by default.
- Results only contain valid catalog `game_id` values.
- Results include explanations and caveats.

Recommended test cases:

```text
1. PC + RPG + Baldur's Gate 3
2. Switch + cozy + Stardew Valley
3. Horror + short playtime + Resident Evil
4. Hidden gems + puzzle + low visibility preference
5. Unknown recent game title
6. Conflicting request with no strict platform matches
```

---

## 12. Acceptance Criteria

The implementation is complete when:

- `POST /recommendations` uses metadata-based cosine similarity from `app_game_catalog.parquet`.
- `POST /recommendations` still falls back gracefully when cosine scoring cannot run.
- The website wizard asks for recent games.
- Recent games are sent to the backend.
- Matched recent games influence ranking.
- Unmatched recent games are visible as caveats or request-summary notes.
- Platform hard filters are still respected.
- Recommendation results include clear explanations.
- The user sees one unified Recommendations page, not separate competing recommendation pages.

---

## 13. What Not To Do

Do not:

- build cosine similarity only inside Streamlit first;
- create a second user-facing recommendation page that competes with Recommendations;
- expose raw similarity math as the main result experience;
- allow recent-game seeds to override hard platform constraints;
- recommend games that are not in the app catalog;
- hide unmatched recent-game titles from the user;
- claim the system understands personal preferences beyond the provided answers and project data.

---

## 14. Confirmed Decisions and Remaining Engineering Checks

These questions have been answered for the first implementation:

| Question | Confirmed Decision |
|---|---|
| Similarity approach | Use metadata-based cosine similarity |
| Authoritative source | `data/app/app_game_catalog.parquet` |
| Recent games meaning | Games the user played recently |
| Similar or different | Similar taste signal for v1 |
| Title matching | Exact match first, fuzzy match second |
| Seed games in results | Exclude by default |
| Missing/unmatched seeds | Report in request summary or caveats |
| Older SQLite recommender | Do not use directly for v1 |

Remaining engineering decisions:

- Confirm exact metadata columns available in `app_game_catalog.parquet`.
- Confirm fuzzy-match threshold after testing real game titles.
- Start with conservative weights:
  - 65% similarity;
  - 15% rating quality;
  - 10% rating evidence;
  - 5% discovery preference;
  - 5% playtime fit.
- Add "similar versus different" as a later enhancement if time allows.

---

## 15. Related Documentation

Relevant documents:

- `docs/plan/final_product_website_plan.md`
- `docs/plan/predictive_analytics_pillar_plan.md`
- `docs/project_source_of_truth/hybrid_retrieval_methodology.md`
- `docs/project_source_of_truth/hybrid_search_technical_journey.md`
- `docs/project_source_of_truth/ask_the_guide_knowledge_base.md`
