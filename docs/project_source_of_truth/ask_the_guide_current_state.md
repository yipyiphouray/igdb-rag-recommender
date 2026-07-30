# Ask the Guide Page Current State

Last updated: July 28, 2026

This document explains the current state of the website chatbot page, called **Ask the Guide_**. It is intended as a handoff document for future improvements without needing to reverse-engineer the implementation from scratch.

## 1. Current Product Direction

Ask the Guide_ is now a **scoped RAG + free-LLM project guide**.

The page allows users to type natural questions, but the assistant is intentionally bounded to this project. It should answer questions about:

- the IGDB game-discovery project;
- the app dataset and its limitations;
- descriptive and diagnostic analytics findings;
- website navigation;
- hidden-gem logic;
- recommendation methodology;
- cosine similarity;
- RAG and retrieval;
- game-discovery questions that can be grounded in project context.

The page should not behave like a general ChatGPT replacement. If the user asks unrelated questions, the backend returns a scoped refusal and redirects the user toward supported project topics.

The Guide voice should be direct, factual, scoped, and first-person. It should feel like a project-aware guide inside the website, not a generic assistant and not a robotic report generator. It should avoid casual filler, avoid fake uncertainty, and answer with clear project-grounded statements.

The Guide should not expose internal source documents, file paths, retrieval metadata, storage formats, or implementation artifacts to website users. If users ask what sources or files it uses, the Guide should answer that it strictly uses the context available within the website.

## 2. Current Purpose

The current purpose of Ask the Guide_ is:

- Answer project and game-catalog questions directly and factually.
- Retrieve relevant project context before generating a response.
- Use structured project facts for exact metrics such as dataset size, year range, rating coverage, and RAG index size.
- Use a free external LLM only to phrase grounded answers.
- Hide internal source names, document paths, retrieval metadata, and storage formats from users.
- Route actual ranked recommendations to Recommend Me_.

Ask the Guide_ is the project explanation layer. Recommend Me_ remains the main recommendation engine.

## 3. Current Non-Purpose

Ask the Guide_ is not:

- the main recommendation engine;
- a replacement for Recommend Me_;
- a general-purpose chatbot;
- a live IGDB browser;
- a system that should invent unsupported project metrics;
- a system that should rank games using only LLM knowledge.

When users ask for ranked recommendations, the Guide should explain how to use Recommend Me_ and what inputs improve recommendation quality.

## 4. Current UX Behavior

The user lands on `/guide`.

The page shows:

- a terminal-style guide panel;
- a futuristic AI face/projection visual;
- a welcome message explaining the page scope;
- a typed question box;
- starter prompt cards;
- a scrollable transcript;
- optional next-action buttons;
- a Recommend Me_ callout;
- a scope disclaimer.

When no message has been sent, the transcript shows a terminal idle state similar to:

```text
terminal idle_
guide@igdb:~$ awaiting project question
```

The chat thread is capped at `10` user turns through:

```ts
const MAX_GUIDE_USER_TURNS = 10;
```

This keeps long conversations from degrading retrieval quality or becoming confusing.

## 5. Current Frontend Files

Main page:

```text
apps/website/src/app/guide/page.tsx
```

Shared API helper:

```text
apps/website/src/lib/api.ts
```

Shared API types:

```text
apps/website/src/types/api.ts
```

Styling:

```text
apps/website/src/app/globals.css
```

The main CSS class family is:

```text
ask-guide-*
```

## 6. Current Frontend Request Flow

The frontend sends typed user messages to:

```text
POST /chat
```

Request shape:

```ts
{
  message: cleanedMessage,
  route_mode: "custom_question",
  max_results: 5,
  history: buildHistory()
}
```

The frontend includes recent chat history so the backend can provide limited context to the LLM. The backend still controls scope and retrieval.

## 7. Starter Prompts

The page keeps starter prompts so users know what the Guide is good at.

Current starter prompt topics:

- Explain this project.
- Dataset size.
- Recommend Me logic.
- Hidden gems.
- RAG role.
- Website navigation.

These are not hard route locks anymore. They submit normal natural-language questions through the same chat endpoint.

## 8. Current Backend Files

Main chat service:

```text
api/app/services/chat_service.py
```

Chat schemas:

```text
api/app/schemas/chat.py
```

Project fact layer:

```text
src/app/project_facts.py
```

Project document retrieval layer:

```text
src/app/project_context_retrieval.py
```

LLM provider wrapper:

```text
src/app/llm_provider.py
```

## 9. Current Backend Engine

The backend identifies the current chatbot engine as:

```text
scoped_rag_llm_project_guide
```

The backend now uses a tool-grounded flow:

```text
User message
-> LLM planner chooses an approved tool
-> backend executes the selected project tool
-> exact metrics and catalog counts come from Python/project artifacts
-> explanatory questions use project-context retrieval
-> LLM phrases grounded answers when needed
-> fallback routing still works if the planner or API key is unavailable
```

Approved tools:

- `project_fact`: answers exact project metric questions from structured artifacts.
- `catalog_count`: computes filtered game counts from `app_game_catalog.parquet`.
- `catalog_distribution`: summarizes top genres, platforms, themes, game modes, or perspectives.
- `game_lookup`: answers factual questions about one specific game in `app_game_catalog.parquet` and links to that game's Explore Games_ detail page.
- `game_compare`: compares two specific games in `app_game_catalog.parquet` using catalog-backed metadata such as release year, genres, platforms, themes, ratings, rating counts, and hidden-gem flags.
- `recommendation_input_helper`: helps users translate vague preference language into stronger `Recommend Me_` inputs, such as recent games, platform, genre, theme, playstyle, and discovery preference.
- `term_definition`: explains project-specific terms including PopScore, hidden gem, total_rating_count, rating coverage, RAG, RAG-ready, and cosine similarity.
- `website_navigation`: gives deterministic page-routing guidance for Home_, Explore Games_, Recommend Me_, Hidden Gems_, Insights_, Methodology_, and Ask the Guide_.
- `recommendation_redirect`: sends ranked recommendation requests to Recommend Me_.
- `project_context`: retrieves relevant project context and uses the LLM for grounded explanation.
- `unsupported`: refuses unrelated questions.

## 10. Structured Fact Layer

Exact metric questions are answered before the LLM is used.

This logic lives in:

```text
src/app/project_facts.py
```

It can answer questions such as:

- How many games are in the dataset?
- What years does the dataset cover?
- How many hidden gems are there?
- What is rating coverage?
- What is reliable rating coverage?
- What is PopScore coverage?
- How many games have summaries?
- What is the top genre?
- What is the top platform?
- How many embeddings are in the RAG index?

This is intentional. Exact project metrics should come from structured artifacts, not from the LLM.

## 11. Project Context Retrieval Layer

The project-document retrieval layer lives in:

```text
src/app/project_context_retrieval.py
```

It loads and chunks selected project documents and structured JSON artifacts.

Current retrieval sources include:

- `docs/project_source_of_truth/ask_the_guide_knowledge_base.md`
- `docs/project_source_of_truth/ask_the_guide_current_state.md`
- `docs/project_source_of_truth/IGDB_ERD_BusinessRules.md`
- `docs/project_source_of_truth/IGDB_ERD_Data_Dictionary.md`
- `docs/project_source_of_truth/website_visual_style_guide.md`
- `docs/report/descriptive_pillar_findings.md`
- `docs/report/diagnostic_pillar_findings.md`
- `data/app/app_methodology_metrics.json`
- `data/app/app_insight_summary.json`

The retriever is lightweight and lexical. It does not require Chroma, a hosted vector database, or GPU infrastructure.

## 12. LLM Provider Layer

The LLM wrapper lives in:

```text
src/app/llm_provider.py
```

The current provider direction is Gemini through environment variables:

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

If `GEMINI_API_KEY` is missing or the provider fails, the chatbot still returns an extractive fallback answer from retrieved project context.

## 13. Response Shape

The backend returns the existing `ChatResponse` fields plus operational fields for status, prompts, caveats, next actions, route mode, provider, and model.

```ts
next_actions: {
  label: string;
  href: string;
}[];

llm_provider?: string | null;
llm_model?: string | null;
```

The backend response shape still contains a `sources` field for schema compatibility, but the service intentionally returns it as an empty list. The website should not show internal source names or file paths to users.

The frontend renders:

- the Guide answer;
- status;
- caveats;
- follow-up prompt buttons;
- next-action links.

## 14. Recommendation Boundary

Ask the Guide_ can explain recommendations, but it should not replace Recommend Me_.

If a user asks for game recommendations, the backend redirects them toward Recommend Me_ and explains what inputs to provide.

This keeps the project architecture clean:

- Ask the Guide_ = explanation and grounded project Q&A.
- Recommend Me_ = ranked cosine-similarity recommendations.

## 15. Current API Status Endpoint

The backend provides:

```text
GET /chat/status
```

The status response includes:

- catalog availability;
- lightweight retrieval artifact availability;
- project-context availability;
- project-context chunk count;
- LLM provider;
- LLM model;
- whether the LLM API key is available;
- warnings.

## 16. Deployment Notes

The current design supports free or low-cost deployment because:

- the website can run on Vercel;
- the backend can run on a free hosted API service;
- the project-document retriever is local and lightweight;
- the chatbot does not require Chroma for project Q&A;
- the chatbot does not self-host an LLM;
- secrets are environment variables;
- missing LLM keys degrade gracefully.

## 17. Current Limitations

Known limitations:

- Gemini availability depends on a valid `GEMINI_API_KEY`.
- Free LLM providers can have rate limits and cold-start latency.
- The project-document retriever is lexical, not semantic.
- Exact metric quality depends on the structured project artifacts being current.
- The chatbot should still avoid producing ranked recommendations directly.
- Internal source labels and file paths are intentionally not exposed in the user-facing answer.

## 18. Practical Summary

Ask the Guide_ is now a scoped RAG + free-LLM project guide. It accepts typed project and catalog questions, retrieves relevant project context, uses structured fact artifacts for exact metrics, calls Gemini when configured, falls back safely when no LLM key is available, avoids exposing internal files or retrieval metadata, and routes ranked recommendation needs to Recommend Me_.
