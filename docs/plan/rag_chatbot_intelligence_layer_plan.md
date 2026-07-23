# RAG Chatbot Intelligence Layer Plan

## Current Superseding Decision: No Free-Form Chat

This intelligence-layer direction has been superseded by the condition-based `Ask the Guide_` design.

The Guide page no longer needs semantic intent matching for arbitrary user text. Users choose predefined guide instructions, and the backend returns deterministic responses based on the selected `route_mode`. This removes the need for open-ended chatbot routing and avoids LLM dependency.

## 1. Purpose

The current Guide page has a working RAG retrieval backend, but testing showed that RAG alone does not feel as strong as the structured `Recommend Me_` page for game recommendations. The new goal is to make the chatbot a deterministic orchestration layer that routes each user message to the right project system.

The updated direction is:

```text
Recommendation request -> cosine-similarity recommendation engine
Project / methodology / data question -> RAG-backed guide response
Catalog-context or explanation question -> RAG retrieval or catalog lookup
Vague request -> clarification
Unsupported request -> scoped fallback
```

This keeps RAG in the project, but gives it a narrower and more defensible role.

This layer should help the chatbot:

- understand broader user wording;
- remember conversation context;
- extract game preferences from natural language;
- ask useful clarification questions;
- explain why games were recommended using recommendation metadata and retrieved project/catalog context;
- support follow-up refinement;
- keep a consistent guide personality;
- avoid using an LLM.

The chatbot should feel intelligent because it behaves contextually and explains itself, not because it generates unrestricted language.

## 2. Core Constraint

The chatbot will not use an LLM.

The system must remain:

- deterministic;
- explainable;
- lightweight enough for free or low-cost hosting;
- based on local project artifacts;
- scoped to game discovery and project explanation.

The deployed RAG path should continue using:

```text
data/app/app_game_catalog.parquet
data/rag/lightweight/game_embeddings.npy
data/rag/lightweight/game_ids.json
data/rag/lightweight/manifest.json
```

The deployment default should remain:

```text
RAG_BACKEND=lightweight
```

## 3. Target Chatbot Experience

The user should feel like they are talking to a project guide that can understand their request, route it to the correct backend, and explain the result clearly. The guide should not compete with `Recommend Me_`; it should provide a conversational entry point into the same recommendation logic.

Expected behavior examples:

### Vague Recommendation

User:

```text
Recommend me something good.
```

Guide:

```text
I can do that, but I need one useful clue first. Do you want something cozy, story-heavy, strategic, fast-paced, or weird?
```

### Preference-Based Recommendation

User:

```text
I want something cozy on Switch.
```

Guide should:

- detect mood: cozy;
- detect platform: Switch;
- call the cosine-similarity recommendation service with the extracted preferences;
- explain the match.

### Seed-Game Recommendation

User:

```text
I played Hades and Dead Cells recently. Recommend similar games.
```

Guide should:

- detect seed games: Hades, Dead Cells;
- exclude those exact games from final results;
- call the cosine-similarity recommendation service using those games as taste anchors;
- explain that the matches are based on action, roguelike, combat, platform, and genre signals when available.

### Follow-Up Refinement

User:

```text
Make them shorter.
```

Guide should:

- use the previous recommendation context;
- preserve prior constraints;
- add short-playtime preference;
- rerun retrieval or rerank results.

### Project Question

User:

```text
How does this guide work?
```

Guide should:

- answer from the project methodology layer;
- not return game recommendations.

## 4. Proposed Architecture

```text
User message
-> Message normalization
-> Intent router
-> Slot extraction
-> Conversation memory update
-> Route decision
   -> Project/methodology answer
   -> Cosine-similarity recommendation service
   -> RAG/project-context retrieval
   -> Recommendation refinement
   -> Clarifying question
   -> Scoped fallback
-> Template-based response
-> Recommendation or retrieved-context explanation
```

## 5. Chat Intent Router

The chatbot should route messages into clear intent categories.

Recommended intent categories:

| Intent | Purpose |
|---|---|
| `greeting` | Respond to hello/hey style messages. |
| `project_identity` | Explain what the guide/project is. |
| `project_methodology` | Explain RAG, retrieval, cosine similarity, data source, or analytics pillars. |
| `game_recommendation` | Route extracted preferences to the cosine-similarity recommendation service. |
| `recommendation_refinement` | Modify prior results based on follow-up instructions. |
| `clarification_needed` | Ask one targeted question when the user request is too vague. |
| `hidden_gem_explanation` | Explain hidden-gem logic. |
| `unsupported` | Keep the guide scoped when the user asks unrelated questions. |
| `personality` | Handle light, quirky, guide-style interactions. |

## 6. Semantic Intent Matching Without an LLM

Regex rules alone are too brittle. The next improvement should add semantic intent matching using embeddings over curated intent examples.

This is not an LLM. It is lightweight classification.

Example structure:

```json
{
  "intent": "project_methodology",
  "examples": [
    "how does the guide work",
    "how are games retrieved",
    "what is hybrid search",
    "why do you use BM25",
    "how does RAG work here"
  ],
  "response_template": "The guide uses hybrid retrieval..."
}
```

Runtime flow:

```text
Embed user message
-> compare to embedded intent examples
-> choose intent if similarity is above threshold
-> otherwise fall back to regex/keyword routing or clarification
```

Deployment note:

- For free hosting, avoid embedding intent examples on every request.
- Precompute intent-example embeddings during startup or store them in a small JSON/NumPy artifact.
- Keep the intent set small and curated.

## 7. Conversation Memory

The chatbot should maintain lightweight conversation state.

Recommended memory fields:

```json
{
  "last_intent": "game_recommendation",
  "last_query": "Recommend cozy games on Switch",
  "last_results": ["game_id_1", "game_id_2", "game_id_3"],
  "preferred_platforms": ["Nintendo Switch"],
  "preferred_genres": ["RPG"],
  "preferred_themes": ["Fantasy"],
  "preferred_moods": ["cozy"],
  "recent_games": ["Hades", "Dead Cells"],
  "avoid_terms": ["horror"],
  "playtime_preference": "short",
  "discovery_preference": "hidden_gem"
}
```

Deployment note:

- Keep memory in the frontend/browser session.
- Send recent memory/history with each `/chat` request.
- Avoid server-side session storage for the MVP because it complicates free hosting.

## 8. Slot Extraction

The chatbot should extract structured preference slots from user language.

Recommended slots:

| Slot | Examples |
|---|---|
| `platforms` | PC, Switch, PS5, Xbox |
| `genres` | RPG, horror, strategy, puzzle |
| `themes` | fantasy, sci-fi, mystery, cyberpunk |
| `moods` | cozy, relaxing, dark, chaotic, atmospheric |
| `recent_games` | Hades, Stardew Valley, Dead Cells |
| `avoid_terms` | no horror, avoid sports |
| `playtime_preference` | short, long, quick, deep |
| `multiplayer_preference` | co-op, online, offline, single-player |
| `discovery_preference` | hidden gem, popular, highly rated |

Initial implementation can use:

- curated keyword dictionaries;
- platform aliases;
- regex for negative constraints;
- existing seed-game detection;
- exact/fuzzy title matching against the catalog.

## 9. Clarification Strategy

The chatbot should not force retrieval when the user gives too little information.

Clarification should trigger when:

- the user asks for a recommendation with no useful preference;
- extracted slots are empty;
- intent confidence is low;
- the query is off-scope but close to supported project/game topics.

Clarification should ask one focused question.

Good clarification examples:

```text
Do you want something cozy, story-heavy, strategic, fast-paced, or weird?
```

```text
What platform should I focus on: PC, Switch, PlayStation, or Xbox?
```

```text
Should I prioritize popular games, hidden gems, or highly rated games?
```

## 10. Recommendation Explanation Layer

Every recommended game should have a short explanation based on actual matched signals from the recommendation engine, with RAG used to support project/catalog explanation when needed.

Possible explanation signals:

- platform match;
- genre overlap;
- theme overlap;
- seed-game similarity;
- mood keyword match;
- rating strength;
- rating-count reliability;
- hidden-gem flag;
- playtime fit;
- multiplayer fit.

Example explanation:

```text
I picked this because it matches your Switch platform preference, has cozy simulation tags, and appears in the catalog as a hidden-gem candidate.
```

No LLM is required. This can be template-generated from structured metadata.

## 11. Personality Layer

The chatbot can have personality without using free-form generation.

Recommended style:

- concise;
- useful;
- slightly cyberpunk/game-guide themed;
- not overly gimmicky;
- never fake certainty.

Example deterministic phrasing:

```text
Signal locked. Based on your preferences, I would start with these.
```

```text
That request is a little too foggy. Give me one anchor: mood, platform, genre, or a game you liked.
```

```text
Neon clue accepted. I will look for atmospheric sci-fi matches.
```

## 12. Fallback Rules

The chatbot should have clear fallback behavior.

| Situation | Behavior |
|---|---|
| Vague recommendation | Ask a clarification question. |
| Unsupported non-game topic | Explain scope and suggest supported prompts. |
| No retrieval results | Ask the user to broaden constraints. |
| Low confidence intent | Ask whether they mean project explanation or game recommendation. |
| Missing artifacts | Return an environment/setup warning. |

## 13. Implementation Phases

### Phase 1: Deterministic Memory and Slot Extraction

- Add a shared slot extractor.
- Extract platform, mood, genre, theme, recent games, avoid terms, playtime, and multiplayer preferences.
- Add structured memory object to the chat request/response flow.
- Keep memory stored on the frontend side.

### Phase 2: Better Routing

- Add an intent router module.
- Move current regex/predefined logic into a cleaner routing layer.
- Add confidence thresholds.
- Add clarification routing before game retrieval.

### Phase 3: Semantic Intent Matching

- Define curated intent examples.
- Precompute example embeddings or build them once on startup.
- Route flexible user phrasing through semantic intent similarity.
- Keep thresholds conservative so game retrieval is not triggered incorrectly.

### Phase 4: Explanation Templates

- Add result-level explanation generation.
- Add response-level summaries such as:
  - why these games were selected;
  - what constraints were applied;
  - what the user can refine next.

### Phase 5: UX Integration

- Show active interpreted preferences in the Guide page.
- Let users remove or adjust remembered preferences.
- Add quick-reply chips for clarification answers.
- Keep the chat transcript scrollable.

## 14. Success Criteria

The chatbot intelligence layer is successful when:

- vague prompts trigger useful clarification instead of random retrieval;
- project/methodology questions do not return game cards;
- follow-up prompts preserve prior context;
- seed games are not repeated as recommendations;
- recommendation requests use the cosine-similarity service rather than RAG-only retrieval;
- recommendations include understandable explanations;
- users can tell what the guide understood from their message;
- the deployment backend remains lightweight enough for free hosting.

## 15. Recommended Next Step

Start with Phase 1.

The first implementation should create a reusable module such as:

```text
src/app/chat_intelligence.py
```

This module should contain:

- message normalization;
- slot extraction;
- confidence scoring;
- clarification decision logic;
- recommendation context object;
- explanation helper functions.

After Phase 1, the existing `/chat` endpoint can pass richer structured context into either the recommendation service or the lightweight RAG backend without changing the website architecture too heavily.

## 16. Implementation Status

### Completed: Phase 1 Backend Intelligence Layer

Implemented the first deterministic chatbot intelligence layer in:

```text
src/app/chat_intelligence.py
```

The implemented layer now supports:

- message normalization;
- tokenization;
- deterministic semantic intent routing with curated examples and cosine scoring;
- platform, genre, theme, mood, recent-game, avoid-term, playtime, multiplayer, discovery, and rating preference extraction;
- catalog-title matching so known game names can be detected without writing a separate prompt pattern for every sentence structure;
- vague recommendation clarification before retrieval;
- filter overrides from detected platform and multiplayer preferences;
- interpreted preference payloads in `/chat` responses;
- match explanations added to retrieved games;
- enhanced answer text that summarizes what the guide understood and why the top games fit.
- seed-game exclusion so games the user explicitly mentioned playing are not displayed as recommendations when they appear in retrieved results.
- routing safeguards based on intent categories rather than one-off sentence patches.

The `/chat` service now uses this layer before calling the lightweight RAG backend, which means specific prompts such as:

```text
Recommend cozy RPGs on Switch.
```

can be interpreted as a recommendation request even when older keyword routing would have been too brittle.

Added validation coverage in:

```text
tests/test_chat_intelligence.py
tests/test_chat_service_intelligence.py
```

Current validation result:

```text
python -m unittest tests/test_chat_intelligence.py tests/test_chat_service_intelligence.py
17 tests passed
```

### Completed: Phase 2 Initial Semantic Routing

The `/chat` endpoint now uses the intelligence layer as the primary routing source. The older phrase-specific service checks are no longer responsible for deciding whether a message should go to RAG retrieval.

The older dead service-level routing helpers for vague recommendation detection and game-discovery detection were removed after the semantic router took over that responsibility.

The semantic router currently supports these high-level intent categories:

- `vague_recommendation`
- `game_recommendation`
- `seed_game_recommendation`
- `recommendation_follow_up`
- `project_question`
- `unsupported`

The router uses lightweight local cosine scoring over curated intent examples, which keeps the design deterministic and deployment-friendly while reducing the need to patch every possible way a user can ask the same thing.

### Completed: Multi-Objective RAG Reranking

The RAG retrieval layer now uses a production-style two-stage search pattern:

```text
Stage 1: retrieve a candidate pool with hybrid semantic + keyword search
Stage 2: rerank the candidate pool with relevance, popularity, quality, and metadata-confidence signals
```

This change addresses the issue where the Guide could return technically relevant but obscure games too often. The system now treats retrieval relevance as the most important signal, but it no longer ranks only by retrieval similarity.

The default ranking profile is:

```text
default_quality_popularity
```

The default profile blends:

- semantic and BM25 retrieval relevance;
- catalog interest / popularity percentile;
- rating-count reliability;
- total rating quality;
- metadata completeness;
- extraction cohort strength;
- a small penalty for hidden-gem candidates unless the user explicitly asks for hidden gems.

The hidden-gem ranking profile is:

```text
hidden_gem
```

The hidden-gem profile is only activated when the user asks for wording such as hidden gems, underrated games, overlooked games, niche games, or lesser-known games. In that mode, popularity still matters, but it is intentionally reduced so that strong hidden-gem candidates can surface.

Implemented in:

```text
src/app/rag_ranking.py
src/lightweight_rag_engine.py
src/rag_engine.py
src/app/rag_service.py
src/app/chat_intelligence.py
```

Added validation coverage in:

```text
tests/test_rag_ranking.py
```

Current validation result:

```text
python -m unittest tests/test_chat_intelligence.py tests/test_chat_service_intelligence.py tests/test_rag_ranking.py
22 tests passed
```

### Completed: Phase 5 Initial UX Guardrails

The Guide page now intentionally behaves like a guided catalog-search assistant rather than an unlimited general chatbot.

Implemented frontend guardrails:

- visible scope message explaining that Ask the Guide is for catalog-backed game discovery and project explanation;
- maximum of 8 user messages per Guide thread;
- warning when the thread reaches 6 user messages;
- Start New Search reset actions;
- shorter chat history window sent to the backend so old context is less likely to pollute retrieval;
- current search context panel showing interpreted preferences from the latest response;
- prompt starters designed around supported use cases;
- button-driven follow-up refinement with a Start New Search option.

This design keeps the chatbot aligned with the final project goal: conversational search over the local IGDB catalog, not a ChatGPT replacement.

### New Direction Before Next Implementation

The next implementation should change `/chat` from a RAG-first endpoint into an intent-router endpoint.

Target routing:

```text
game_recommendation / seed_game_recommendation / recommendation_follow_up
-> call the same recommendation backend used by Recommend Me_

project_question / rag_methodology / data_source / hidden_gem_explanation
-> use RAG or predefined project-context responses

catalog_lookup / explanation_request
-> use RAG or catalog service depending on the query
```

Future work:

- Add editable frontend-side memory chips.
- Improve follow-up refinement so prior constraints are stored as structured state instead of relying mainly on transcript history.
- Make `/chat` call the cosine-similarity recommendation service for recommendation requests.
- Keep RAG focused on project explanation, methodology, catalog context, and recommendation reasoning.
- Optionally replace the lightweight local intent vectors with precomputed sentence-transformer intent embeddings if route quality needs to improve further.

### Completed: Recommendation Requests Routed to Cosine Similarity

The `/chat` backend now routes recommendation-style guide prompts to the same recommendation service used by `Recommend Me_`.

Implemented behavior:

```text
game_recommendation
seed_game_recommendation
recommendation_follow_up
-> RecommendationRequest
-> recommend_from_request(...)
-> cosine-similarity or structured fallback recommendation response
-> chat-compatible guide response
```

This means prompts such as:

```text
Recommend cozy RPGs on Switch.
I played Hades recently. Recommend similar games.
Make these shorter.
```

now use the recommendation backend instead of calling RAG retrieval directly.

Implemented in:

```text
api/app/services/chat_service.py
src/app/chat_intelligence.py
apps/website/src/app/guide/page.tsx
```

Validation result:

```text
python -m unittest discover tests
52 tests passed

npm.cmd run build
Next.js production build passed
```

### Superseded: Guided Mode Routing UX

This was the first refinement direction after open-ended chat testing. It has been superseded by the newer curated project-guide direction below, where `Ask the Guide_` focuses on explanation and `Recommend Me_` remains the main recommendation experience.

Testing showed that fully open-ended chat still creates avoidable ambiguity. Users can phrase the same intent many different ways, and a deterministic no-LLM router cannot reliably infer every sentence.

The next refinement should make the Guide page mode-based while still allowing natural-language typing.

Target user flow:

```text
Choose a route mode
-> Type a natural sentence inside that mode
-> Extract structured preferences or question context
-> Show what the guide understood
-> Run the selected backend only when enough detail exists
```

Recommended route modes:

| Mode | User Intent | Backend Route |
|---|---|---|
| `recommend_games` | User wants game recommendations | Cosine-similarity recommendation service |
| `explain_project` | User asks about project, data, RAG, cosine similarity, or methodology | Predefined guide response or RAG/project context |
| `explain_recommendation` | User asks why a game or result was recommended | Recommendation metadata plus project/catalog context |
| `search_catalog` | User wants to browse or search catalog records without personalization | Catalog search or RAG/catalog retrieval |

The mode should be selected through visible buttons above the input. The user should still type naturally, but the selected mode becomes the primary routing signal.

### Superseded: Recommendation Confirmation Step

For the earlier recommendation-mode direction, the Guide would have shown a compact confirmation panel before running the backend when useful. Under the current direction, this behavior belongs more naturally in the `Recommend Me_` flow.

Example confirmation:

```text
I understood:
Mode: Recommend games
Platform: PC
Recent game: Hades
Mood: Fast-paced

[Get recommendations] [Edit details]
```

If the user gives too little detail, the Guide should ask for one missing signal instead of guessing.

Minimum useful recommendation signals:

- platform;
- genre;
- mood;
- recent game;
- playtime preference;
- hidden-gem or popularity preference;
- rating-quality preference.

If none are present, do not call the recommendation service. Ask the user to choose or type one useful clue.

### Planned Backend Contract Update

The `/chat` request should support an optional explicit route mode:

```json
{
  "message": "I recently played Hades and want something fast-paced on PC.",
  "route_mode": "recommend_games",
  "max_results": 5,
  "history": []
}
```

Backend behavior:

- If `route_mode` is present, trust it as the primary routing signal.
- If `route_mode` is missing, use the existing semantic router as fallback.
- If mode and sentence conflict, return a clarification instead of guessing.
- If recommendation mode lacks useful preference detail, return `needs_clarification`.
- If project/explanation mode is selected, avoid returning game results unless the user explicitly asks for them.

### New Direction: Curated Project Guide Instead of Recommendation Chatbot

After additional testing, the strongest product direction is to reduce the Guide's responsibility even further.

The `Recommend Me_` page should remain the main recommendation experience because it collects structured inputs and produces cleaner cosine-similarity matches. The Guide should not try to compete with that page or act like a general-purpose AI chatbot.

Updated Guide identity:

```text
Ask the Guide is a project-aware explanation and navigation assistant.
It explains the project, data, methodology, RAG role, recommendation logic,
hidden-gem logic, and how users should use Recommend Me_.
```

Primary interaction should be curated buttons, not open-ended typing.

Recommended primary actions:

| Action | Purpose |
|---|---|
| Explain this project | Summarize the project purpose and website flow. |
| Explain the data | Explain IGDB, catalog fields, missingness, and limitations. |
| Explain recommendations | Explain cosine similarity and why structured inputs matter. |
| Explain RAG | Explain the guide's retrieval/grounding role. |
| Explain hidden gems | Explain the hidden-gem concept and caveats. |
| Help me use Recommend Me | Help the user turn preferences into better structured inputs. |

Free-text input can remain, but it should be secondary and clearly labeled as a custom project/methodology/recommendation-logic question. If the user asks for actual recommendations, the preferred behavior is to explain which fields to enter on `Recommend Me_` and provide a link or call-to-action to that page.

Updated routing priority:

```text
Curated prompt/topic selection
-> predefined or RAG-backed project explanation
-> optional custom typed follow-up
-> scoped fallback when unsupported
-> recommendation-service route only if deliberately enabled and enough preference signal exists
```

This direction keeps the project compliant with the RAG requirement while making the user experience more reliable and easier to defend.
