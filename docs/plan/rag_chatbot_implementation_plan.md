# RAG Chatbot Implementation on Website Plan

## Current Superseding Decision: Condition-Based Guide

The open-ended chatbot direction has been superseded.

`Ask the Guide_` should now be implemented as a condition-based project guide. Users select predefined guide instructions instead of typing unrestricted questions. The backend maps each selected `route_mode` to a deterministic response or an exact structured fact from project artifacts.

No LLM provider is used for this page. Personalized game ranking remains in `Recommend Me_`.

## 1. Purpose

This plan defines how the `Ask the Guide_` chatbot should be integrated into the final website.

The goal is to turn `ASK THE GUIDE_` into a real website page where users can understand the project, data, methodology, recommendation logic, RAG role, hidden-gem logic, and how to use the website.

The updated product direction is:

```text
Recommend Me_ -> primary game recommendation experience
Ask the Guide_ -> project explanation and recommendation guidance
Project / methodology / data questions -> predefined or RAG-backed project context
Recommendation questions -> explain what details to enter on Recommend Me_
```

The chatbot should not be a separate disconnected experiment, a general-purpose AI assistant, or a weaker duplicate of the `Recommend Me_` page. It should reuse the project's current website architecture:

```text
Next.js website -> FastAPI backend -> chat intent router -> recommendation service or RAG service -> app catalog/artifacts
```

---

## 2. Current State

The project already has the main pieces needed for a first website integration.

### Website

Current website structure:

```text
apps/website/
```

Current active pages:

- Home
- Explore Games
- Hidden Gems
- Recommend Me
- Insights
- Methodology

The Home page and top navigation still treat the chatbot as pending:

```text
ASK THE GUIDE_
```

This should become the user-facing RAG chatbot entry point.

### Backend

Current backend structure:

```text
api/
```

Current active API areas:

- health
- catalog
- recommendations
- methodology
- insights

There is no website-facing RAG endpoint yet.

### RAG / Retrieval Code

Current RAG-related code exists in:

```text
src/rag_engine.py
src/app/rag_service.py
src/initialize_vector_db.py
src/validate_vector_store.py
src/debug_engine.py
```

The important distinction is:

- `src/rag_engine.py` contains the real hybrid retrieval engine.
- `src/app/rag_service.py` is still mostly a placeholder adapter.

The implementation should wire the website/API into the real retrieval engine through a clean service layer.

---

## 3. Core Implementation Decision

Use this product/API split:

```text
Website page: /guide
Backend endpoint: POST /chat
Status endpoint: GET /chat/status
```

Reasoning:

- `/guide` matches the website language: `ASK THE GUIDE_`.
- `/chat` is simple and already appears in the final product website planning language.
- The user does not need to see the technical term `RAG` in the main navigation.
- The Methodology page can explain that the guide is powered by RAG/hybrid retrieval.

---

## 4. What The Guide Should Do

The guide should allow users to ask questions such as:

```text
What is this project?
What data does the website use?
How does Recommend Me work?
What does RAG do in this project?
What does hidden gem mean here?
What details should I enter for better recommendations?
```

For recommendation-seeking prompts, the guide should usually explain that `Recommend Me_` is the main recommendation experience and help the user understand what preference details to enter there.

For project, methodology, dataset, catalog-context, or explanation prompts, the response should come from the RAG/project-context layer.

The response should include:

- a short natural-language answer;
- relevant project, data, methodology, or recommendation-logic context;
- guidance for using `Recommend Me_` when the user wants actual recommendations;
- caveats when metadata is incomplete;
- safe fallback messaging if recommendation or RAG artifacts are unavailable.

The guide must not invent games, platforms, ratings, genres, or claims that are not supported by the project data.

---

## 5. Active Data Contract

The active retrieval stack should use the current Parquet-first project architecture.

Authoritative catalog:

```text
data/app/app_game_catalog.parquet
```

Active vector store:

```text
data/vector_store/
```

Active retrieval engine:

```text
src/rag_engine.py
```

Important cleanup note:

Some older documentation and placeholder code still reference:

```text
data/rag/vector_store/
data/rag/game_profiles.parquet
data/rag/retrieval_metadata.parquet
```

Those references should not drive the website implementation unless the team intentionally restores that artifact layout. The current source-of-truth retrieval path is:

```text
data/vector_store/
```

---

## 6. Backend API Contract

### 6.1 `GET /chat/status`

Purpose:

- Let the website check whether the chatbot backend is available.
- Prevent the page from crashing when vector artifacts are missing.
- Provide clear evaluator-facing status.

Recommended response:

```json
{
  "status": "ready",
  "catalog_available": true,
  "vector_store_available": true,
  "collection_available": true,
  "engine": "hybrid_vector_bm25",
  "warnings": []
}
```

Possible status values:

| Status | Meaning |
|---|---|
| `ready` | RAG retrieval can run. |
| `degraded` | Some optional dependency or artifact is missing, but fallback behavior may still work. |
| `unavailable` | The chatbot should show a safe unavailable message. |

### 6.2 `POST /chat`

Purpose:

- Accept a curated guide topic or custom guide message.
- Classify the topic/question intent.
- Route project, methodology, data-source, catalog-context, RAG, and recommendation-explanation questions to predefined or RAG/project context.
- Return `Recommend Me_` guidance when the user asks for personalized recommendations.
- Return grounded answer text, source/context notes, and caveats when relevant.

Recommended request body:

```json
{
  "message": "How does Recommend Me use recent games?",
  "route_mode": "explain_recommendation",
  "conversation_id": "optional-local-session-id",
  "max_results": 5
}
```

Recommended response body:

```json
{
  "answer": "Recommend Me uses recent games as taste anchors. It compares your selected platforms, genres, themes, moods, playstyle, and recent-game signals against catalog metadata using cosine similarity.",
  "mode": "guide_explanation",
  "status": "success",
  "conversation_id": "optional-local-session-id",
  "retrieved_games": [],
  "caveats": [
    "Recommendation quality depends on the metadata available in the local IGDB catalog."
  ],
  "follow_up_prompts": [
    "What details should I enter into Recommend Me?",
    "Explain cosine similarity",
    "Explain the data source"
  ]
}
```

### 6.3 Response Rules

The API should always return a controlled response shape.

If the message is a recommendation request that should be redirected to the main flow:

```text
mode = recommend_me_guidance
status = success
```

If RAG is available:

```text
mode = rag_hybrid_retrieval
status = success
```

If RAG artifacts are missing:

```text
mode = rag_unavailable
status = unavailable
```

If retrieval runs but returns no strong candidates:

```text
mode = rag_hybrid_retrieval
status = no_results
```

The frontend should never receive raw Python trace logs as the main response.

---

## 7. Backend Implementation Plan

### Phase 1: Add Chat Schemas

Create:

```text
api/app/schemas/chat.py
```

Recommended schema classes:

- `ChatFilters`
- `ChatRequest`
- `ChatRetrievedGame`
- `ChatResponse`
- `ChatStatusResponse`

Implementation notes:

- Keep `max_results` bounded, likely `1` to `10` for the first UI version.
- Keep filters optional.
- Reuse the same user-facing fields as `GameSummary` where possible.

### Phase 2: Add Chat Service

Create:

```text
api/app/services/chat_service.py
```

Responsibilities:

- Lazily initialize the RAG engine.
- Avoid importing or initializing heavy vector dependencies during API startup if possible.
- Catch missing vector-store or dependency errors.
- Call the RAG engine with the user query.
- Map raw retrieval results into API-safe response objects.
- Enrich results from `app_game_catalog.parquet` when the retrieval engine does not return fields needed by website cards.
- Build a short answer from retrieved games.
- Return caveats and status cleanly.

Recommended structure:

```text
get_chat_status()
get_rag_agent()
answer_chat_request(request)
map_rag_result_to_chat_game(...)
build_grounded_answer(...)
```

Important engineering rule:

Do not initialize `RAGAgent()` at module import time. Use lazy loading so `/health`, `/catalog`, and `/recommendations` keep working even if the vector store has a problem.

### Phase 3: Wire Existing RAG Service

Update:

```text
src/app/rag_service.py
```

Purpose:

- Replace the placeholder logic with a real adapter to `src/rag_engine.py`.
- Align artifact paths with the active vector-store location.
- Keep Streamlit and FastAPI able to call the same shared RAG service if needed.

Recommended adapter behavior:

```text
answer_game_query(query, filters=None, top_k=5)
    -> checks catalog/vector-store status
    -> initializes RAGAgent lazily
    -> calls RAGAgent.search(...)
    -> returns normalized answer/retrieval dictionary
```

### Phase 4: Add Chat Router

Create:

```text
api/app/routers/chat.py
```

Add routes:

```text
GET /chat/status
POST /chat
```

Update:

```text
api/main.py
```

Add:

```python
from app.routers import chat
app.include_router(chat.router)
```

### Phase 5: Dependency Alignment

The API runtime will need the dependencies required by `src/rag_engine.py`.

Check and update:

```text
api/requirements-api.txt
requirements.txt
```

Likely required dependencies:

- `chromadb`
- `numpy`
- `pandas`
- `pyarrow`
- `sentence-transformers`
- `rank-bm25` as an optional quality dependency

`rank-bm25` is optional because the project has an in-repo `SimpleBM25` fallback. `sentence-transformers` is not optional if the Chroma embedding function needs it at runtime.

---

## 8. Frontend Implementation Plan

### Phase 1: Add API Types

Update:

```text
apps/website/src/types/api.ts
```

Add:

- `ChatFilters`
- `ChatRequest`
- `ChatRetrievedGame`
- `ChatResponse`
- `ChatStatusResponse`

### Phase 2: Add API Client Functions

Update:

```text
apps/website/src/lib/api.ts
```

Add:

```text
getChatStatus()
postChatMessage(payload)
```

### Phase 3: Add Website Page

Create:

```text
apps/website/src/app/guide/page.tsx
```

Page title:

```text
Ask the Guide_
```

Page purpose:

```text
Ask natural-language questions and get catalog-grounded game suggestions.
```

Recommended page sections:

1. Hero/header box.
2. RAG status strip.
3. Prompt examples.
4. Chat input area.
5. Answer panel.
6. Retrieved game cards.
7. Caveats/methodology note.

The visual style should match the existing cyberpunk website:

- black background;
- white bordered panels;
- red accent line;
- uppercase mono labels;
- compact technical status labels;
- consistent max-width alignment with other pages.

### Phase 4: Reuse Game Card Patterns

Retrieved games should visually align with the Explore Games and Recommend Me cards.

Recommended approach:

- Use the existing `GameCard` component if the retrieved result can satisfy `GameSummary`.
- If RAG-specific score/evidence fields need to be shown, place a small evidence panel beside or below each `GameCard`.

Do not create a completely new unrelated card design.

### Phase 5: Activate Navigation

Update:

```text
apps/website/src/components/SiteHeader.tsx
apps/website/src/app/page.tsx
```

Changes:

- Move `ASK THE GUIDE_` from pending to active.
- Link it to `/guide`.
- Update the Home page feature card description.
- Convert the disabled `ASK GUIDE` CTA into an active link.

---

## 9. Chatbot UX Requirements

The first version should feel useful but controlled.

### 9.1 Prompt Input

The input should support:

- one natural-language question;
- submit button;
- reset/clear button;
- Enter-to-submit if practical;
- loading state while the backend responds.

### 9.2 Suggested Prompts

Include starter prompts such as:

```text
Recommend story-rich RPGs on PC.
Find hidden gems with exploration and fantasy themes.
What are good co-op games with strong ratings?
Suggest games similar to Stardew Valley but less obvious.
Find shorter games with atmospheric worlds.
```

### 9.3 Response Display

The response should show:

- answer text first;
- retrieved games below;
- evidence text per game;
- caveats at the bottom;
- a small methodology note explaining that answers are grounded in retrieved catalog records.

### 9.4 Failure States

The page should handle:

- backend unavailable;
- vector store unavailable;
- empty question;
- no retrieval results;
- partial metadata;
- slow response.

Failure states should be user-readable, not raw stack traces.

---

## 10. Answer Generation Strategy

The safest version should be routed, grounded, and deterministic.

Recommended behavior:

```text
User selects a curated guide topic
-> Optional custom follow-up is typed
-> Chat router validates the topic/question
-> Project/methodology/catalog-context questions use predefined or RAG/project context
-> Recommendation-seeking questions receive Recommend Me_ guidance by default
-> Backend builds concise template-based answer text
-> Frontend displays answer, source/context notes, caveats, and next-step prompts
```

This produces a reliable guide-like experience without requiring an LLM and without forcing RAG to act as the main recommender.

The conversational version should preserve recent turns only for short follow-up explanation questions:

```text
User sends message
-> Frontend sends bounded recent chat history
-> Backend detects whether the message is a follow-up
-> Backend keeps the answer scoped to the selected topic
-> Backend returns deterministic answer text and follow-up prompts
```

This allows back-and-forth behavior such as "show me more like the first one" or "make these shorter to play" while keeping the final answer grounded in retrieved project data.

The guide should also support a small rule-based response layer before retrieval:

```text
Greeting/help/methodology/thanks question
-> Return predefined guide response and suggested next prompts

Game-discovery question or valid follow-up
-> Run cosine-similarity recommendation service

Project, methodology, data, or explanation question
-> Run RAG/project-context retrieval

Unsupported/off-topic question
-> Return scoped default response explaining what the guide can answer
```

This keeps the page feeling conversational without pretending to be an open-ended LLM assistant.

Recommended or retrieved games should appear as compact title rows in the chat response. Hovering over a title should reveal the full game card, and clicking the preview card should open that game's detail page in a new tab.

If the team has an LLM generation layer ready, it can be added later behind the same `/chat` endpoint.

LLM rule if added:

```text
The LLM may only answer using retrieved game context and must disclose missing metadata.
```

Do not let the LLM recommend games that were not returned by retrieval.

---

## 11. Relationship With Recommend Me Page

The `Recommend Me_` page and `Ask the Guide_` page should serve different user intents.

| Page | Purpose |
|---|---|
| Recommend Me | Structured guided recommendation wizard using preference fields and cosine similarity. |
| Ask the Guide | Conversational router that calls the recommendation engine for game requests and RAG for project/context/explanation requests. |

They should not compete.

Recommended distinction:

- Use `Recommend Me_` when the user wants a guided step-by-step recommendation flow.
- Use `Ask the Guide_` when the user wants to type a natural-language question or ask how the project works.

Both can return catalog-backed game cards, but they should share the same recommendation backend whenever the user is asking what to play.

---

## 12. Testing Plan

### Backend Checks

Recommended commands:

```text
python -m py_compile src/app/rag_service.py
python -m py_compile api/main.py
python src/validate_vector_store.py
python src/debug_engine.py
```

Manual API checks:

```text
GET http://localhost:8000/chat/status
POST http://localhost:8000/chat
```

Sample request:

```json
{
  "message": "Recommend story-rich RPGs on PC.",
  "max_results": 5
}
```

### Frontend Checks

Recommended commands:

```text
cd apps/website
npm run build
npm run dev
```

Manual website checks:

- `/guide` loads.
- Header menu links to `/guide`.
- Home page `ASK THE GUIDE_` card links to `/guide`.
- Empty prompt is blocked.
- Valid prompt returns answer and game cards.
- API unavailable state is readable.
- Retrieved game cards open the existing game detail pages.

---

## 13. Acceptance Criteria

The RAG chatbot website integration is complete when:

- `GET /chat/status` returns controlled runtime status.
- `POST /chat` accepts a supported guide question or curated prompt selection.
- `POST /chat` prioritizes project, methodology, data-source, RAG, hidden-gem, and recommendation-logic explanations.
- `POST /chat` helps users understand what details to provide on `Recommend Me_` when they ask for recommendations.
- `POST /chat` only routes to the recommendation service when the intentionally supported conversational recommendation path is enabled and enough preference detail exists.
- The response includes a grounded answer, source/context notes, and caveats when relevant.
- The website has an active `/guide` page.
- The top navigation links to `ASK THE GUIDE_`.
- The Home page no longer marks `ASK THE GUIDE_` as pending.
- Missing vector-store or backend failures do not crash the website.
- If any game examples are shown, they use the same visual language as Explore Games and Recommend Me.
- The Methodology or source-of-truth docs explain the RAG/hybrid retrieval method.

Current implementation update:

- Recommendation prompts in `/chat` now call the cosine-similarity recommendation service.
- Project/methodology/predefined guide prompts remain handled by the guide layer.
- Guide result wording was adjusted from retrieval-only language to matched-title language.
- The implementation passed the full Python unit test suite and website production build.

Next refinement: guide-first interaction model.

Testing showed that a no-LLM chatbot feels weak when users expect open-ended ChatGPT-style conversation. The Guide page should therefore become a curated project assistant rather than a second recommendation interface.

Recommended primary actions:

```text
Explain this project
Explain the data
Explain recommendations
Explain RAG
Explain hidden gems
Help me use Recommend Me
```

Recommended UI flow:

```text
Curated topic buttons
-> User selects a supported question
-> Optional custom typed follow-up
-> Guide answers from project/RAG context
-> If the user wants recommendations, guide them to Recommend Me_
```

Recommended `POST /chat` request extension if topic/mode routing is retained:

```json
{
  "message": "How does Recommend Me use recent games?",
  "route_mode": "explain_recommendation",
  "conversation_id": "optional-session-id",
  "max_results": 5
}
```

Route behavior:

- `explain_project` should use predefined/RAG project-context responses.
- `explain_recommendation` should explain cosine similarity, user preference signals, score interpretation, and recommendation caveats.
- `explain_data` or equivalent topic should explain IGDB, pulled fields, missingness, and catalog limitations.
- `explain_rag` should explain what retrieval does and what it does not do.
- `recommendation_guidance` should help users prepare inputs for `Recommend Me_`.
- `recommend_games` should be secondary, not the main Guide path.
- Missing mode can still fall back to semantic routing, but the UI should encourage choosing a curated topic first.

---

## 14. What Not To Do

Do not:

- build the chatbot only inside Streamlit;
- create a second unrelated backend outside the current FastAPI app;
- hard-code fake chatbot answers;
- position the Guide as the main recommendation experience;
- optimize the Guide for unrestricted open-ended chat;
- allow raw RAG traces to appear as user-facing responses;
- recommend games outside `data/app/app_game_catalog.parquet`;
- make the chatbot invent unsupported metadata;
- block the whole API from starting if the vector store is missing;
- use stale `data/rag/vector_store/` paths unless the team intentionally migrates back to that folder layout.

---

## 15. Documentation Updates Needed

After implementation, update:

```text
docs/session_log.md
docs/project_source_of_truth/website_visual_style_guide.md
docs/project_source_of_truth/streamlit_page_context.md
docs/plan/final_product_website_plan.md
README.md
api/README.md
apps/website/README.md
```

Documentation cleanup should include:

- `ASK THE GUIDE_` is now active.
- The website route is `/guide`.
- The API endpoint is `POST /chat`.
- The status endpoint is `GET /chat/status`.
- The active vector-store path is `data/vector_store/`.
- `src/rag_engine.py` is the active hybrid retrieval engine.
- `src/app/rag_service.py` is the shared adapter layer.

---

## 16. Suggested Implementation Order

Recommended order:

```text
1. Update RAG service adapter and path checks.
2. Add chat schemas.
3. Add chat service.
4. Add chat router.
5. Register router in api/main.py.
6. Add frontend chat API types.
7. Add frontend chat API functions.
8. Create /guide page.
9. Activate navigation and Home page links.
10. Run compile/build checks.
11. Update documentation and session log.
```

This order keeps the backend contract stable before spending time on UI polish.

---

## 17. Open Decisions Before Implementation

These decisions should be confirmed before coding:

| Decision | Recommendation |
|---|---|
| User-facing route | Use `/guide`. |
| Backend route | Use `POST /chat` and `GET /chat/status`. |
| First answer style | Use deterministic retrieval-grounded answer text. |
| LLM generation | Add later only if the teammate's LLM layer is ready. |
| Result count | Default to `5`; cap at `10`. |
| Card design | Reuse existing `GameCard` and add small evidence panels. |
| Vector path | Use `data/vector_store/`. |
| Source catalog | Use `data/app/app_game_catalog.parquet`. |

Once these are accepted, implementation can begin.
