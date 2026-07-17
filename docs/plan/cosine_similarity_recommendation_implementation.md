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
- active RAG/hybrid retrieval documentation under `docs/project_source_of_truth/`.

The current recommendation endpoint returns usable ranked recommendations, but it still reports:

```text
structured_fallback_active
```

or:

```text
similarity_artifacts_available_not_integrated
```

when similarity artifacts exist but are not yet wired into the endpoint.

---

## 3. Target Direction

The target recommendation flow is:

```text
1. User answers recommendation wizard questions.
2. User optionally enters recent games they played or enjoyed.
3. Backend validates the request.
4. Backend applies hard filters such as platform availability.
5. Backend builds a user preference profile.
6. Backend uses cosine similarity to compare that profile against game profiles.
7. Backend applies ranking adjustments for quality, evidence, hidden-gem preference, visibility, and playtime.
8. Backend returns ranked recommendations with explanations.
```

The final user should not need to know whether the score came from filtering, cosine similarity, or a ranking adjustment. That explanation belongs in Methodology or a technical section.

---

## 4. Why Recent Games Should Be Added

Adding recent games is a strong direction because it provides concrete behavioral evidence.

Questionnaire answers such as genre, theme, and mood are useful, but recent games tell the system what the user has actually played, liked, or wants something similar to.

Recommended wizard question:

```text
Recently played games
Tell us up to 5 games you recently played, liked, or want something similar to.
```

Optional follow-up:

```text
Do you want something similar to these games, or something different?
```

This is important because a user may say they recently played a difficult game but now want something less stressful.

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
Recent games you played or enjoyed
```

The backend can keep the field name for compatibility unless the API schema is intentionally changed later.

---

## 6. Backend-First Implementation Rule

Cosine similarity should be implemented in the shared backend/service layer first, not directly in Streamlit.

Recommended layering:

```text
src/app/recommendation_service.py or teammate similarity module
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

---

## 7. Similarity Logic Design

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

## 7.4 Candidate Similarity

Once a user profile vector exists:

```text
similarity_score = cosine(user_profile_vector, game_profile_vector)
```

The similarity score should be normalized to a user-readable `0.0` to `1.0` range.

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
  "similarity_status": "cosine_similarity_active",
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
Add up to 5 games you recently played, liked, or want something similar to.
```

Helper text:

```text
These help the recommender understand your taste beyond genre filters.
```

---

## 11. Implementation Phases

## Phase 1: Audit Teammate Similarity Code

Goal:

- Identify the exact callable function or class that produces similarity rankings.

Tasks:

- Review teammate similarity files.
- Identify expected input fields.
- Identify required artifacts.
- Confirm whether vectors are precomputed or generated at runtime.
- Confirm whether the logic supports user-profile vectors, game-to-game vectors, or both.

Deliverable:

```text
Clear function contract for backend integration.
```

## Phase 2: Backend Adapter

Goal:

- Wrap teammate similarity logic inside the FastAPI recommendation service.

Tasks:

- Add a cosine-similarity adapter function.
- Load required artifacts lazily and cache them.
- Convert `RecommendationRequest` into the expected similarity input.
- Match recent/favorite game titles to catalog records.
- Apply platform and year hard filters.
- Return ranked games using the existing `RecommendationResponse` schema.
- Keep structured fallback active when artifacts are missing.

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
- API returns cosine-similarity results when artifacts exist.
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

- `POST /recommendations` can use cosine similarity when artifacts are available.
- `POST /recommendations` still falls back gracefully when artifacts are missing.
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

## 14. Open Questions for Implementation

These questions should be answered before coding the integration:

1. What exact teammate function/class should the backend call for cosine similarity?
2. Which artifact is the authoritative game profile vector source?
3. Are vectors already precomputed for all games in `app_game_catalog.parquet`?
4. Does the teammate logic support user preference vectors, or only game-to-game similarity?
5. How should recent games be matched: exact title only, fuzzy title, or both?
6. Should users be allowed to request games similar to recent games, different from recent games, or both?
7. Should seed games be excluded from recommendations by default?
8. What final weights should be used for similarity, rating quality, rating evidence, hidden-gem preference, and playtime fit?

Recommended default answers if the team needs to move quickly:

- Use fuzzy title matching after exact matching fails.
- Exclude seed games from results by default.
- Start with conservative weights:
  - 65% similarity;
  - 15% rating quality;
  - 10% rating evidence;
  - 5% discovery preference;
  - 5% playtime fit.
- Add "similar vs different" as a later enhancement if time is limited.

---

## 15. Related Documentation

Relevant documents:

- `docs/plan/final_product_website_plan.md`
- `docs/plan/predictive_analytics_pillar_plan.md`
- `docs/project_source_of_truth/hybrid_retrieval_methodology.md`
- `docs/project_source_of_truth/hybrid_search_technical_journey.md`
- `docs/project_source_of_truth/definitive_project_guideline_igdb_rag.md`

