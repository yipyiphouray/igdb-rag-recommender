# RAG Chatbot Intelligence Layer Plan

## 1. Purpose

The current Guide page has a working RAG retrieval backend, but the user experience should feel more like speaking with an intelligent AI game recommender. The goal of this plan is to add a deterministic chatbot intelligence layer on top of the existing lightweight RAG backend.

This layer should help the chatbot:

- understand broader user wording;
- remember conversation context;
- extract game preferences from natural language;
- ask useful clarification questions;
- explain why games were recommended;
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

The user should feel like they are talking to an AI guide that can recommend games intelligently.

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
- retrieve catalog-backed games;
- explain the match.

### Seed-Game Recommendation

User:

```text
I played Hades and Dead Cells recently. Recommend similar games.
```

Guide should:

- detect seed games: Hades, Dead Cells;
- exclude those exact games from final results;
- retrieve alternatives;
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
   -> Game discovery retrieval
   -> Recommendation refinement
   -> Clarifying question
   -> Scoped fallback
-> Template-based response
-> Retrieved game explanation
```

## 5. Chat Intent Router

The chatbot should route messages into clear intent categories.

Recommended intent categories:

| Intent | Purpose |
|---|---|
| `greeting` | Respond to hello/hey style messages. |
| `project_identity` | Explain what the guide/project is. |
| `project_methodology` | Explain RAG, retrieval, cosine similarity, data source, or analytics pillars. |
| `game_recommendation` | Retrieve games from the catalog. |
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

Every retrieved game should have a short explanation based on actual matched signals.

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

After Phase 1, the existing `/chat` endpoint can pass richer structured context into the lightweight RAG backend without changing the website architecture too heavily.

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

### Still Future Work

- Add editable frontend-side memory chips.
- Improve follow-up refinement so prior constraints are stored as structured state instead of relying mainly on transcript history.
- Optionally replace the lightweight local intent vectors with precomputed sentence-transformer intent embeddings if route quality needs to improve further.
