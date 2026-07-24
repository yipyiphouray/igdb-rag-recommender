# Scoped RAG + Free LLM Chatbot Direction Plan

## 1. Purpose of This Plan

This plan defines the new direction for the website chatbot page.

The chatbot should no longer be treated as a purely deterministic dropdown guide, but it also should not become a general ChatGPT-style assistant. The new target is a **scoped RAG-powered AI guide** that lets users type natural questions while keeping the assistant grounded in project and game-related context.

The goal is to make the chatbot feel conversational without allowing it to drift away from the project.

## 2. New Chatbot Purpose

The chatbot page should act as a scoped AI guide for the IGDB game-discovery project.

Its purpose is to help users:

- Understand the project.
- Understand the IGDB dataset.
- Understand the website pages.
- Understand descriptive and diagnostic findings.
- Understand the recommendation methodology.
- Understand hidden-gem logic.
- Understand the role of RAG.
- Ask game-discovery questions that can be grounded in the project catalog.
- Get directed toward `Recommend Me_` when they need actual ranked recommendations.

The chatbot should feel like users are talking to an intelligent guide, but its answers should remain bounded by retrieved project context and catalog data.

## 3. What the Chatbot Is Not

The chatbot should not be:

- A general-purpose chatbot.
- A replacement for ChatGPT.
- The main recommendation engine.
- A place for unsupported topics outside games, IGDB, the project, or the website.
- A system that invents facts when retrieval does not provide enough context.
- A system that recommends games purely from the LLM’s general knowledge.

If a user asks something outside the project/game scope, the chatbot should politely refuse and redirect them to supported topics.

## 4. Product Identity

The chatbot identity should be:

> A scoped AI project guide that explains the game-discovery system, answers project and game-catalog questions, and helps users move to the correct website tool.

Short version:

> Ask the Guide_ is the conversational explanation layer for the project.

The chatbot should be useful, conversational, and project-aware, but not unrestricted.

## 5. Recommended Architecture

The recommended architecture is a hybrid RAG + LLM flow.

```text
User message
→ scope and intent check
→ retrieve project/game context
→ build grounded prompt
→ free LLM generates answer
→ response includes guardrails, caveats, and page routing
```

The system should use retrieval to keep the LLM grounded and prevent it from inventing unsupported project facts.

### Tool-Grounded Update

The chatbot should use a tool-grounded RAG + LLM flow rather than relying on keyword patches.

```text
User message
-> LLM planner classifies the request into an approved project tool
-> Python/backend executes the selected tool against project artifacts
-> RAG retrieves project context when the request is explanatory
-> LLM phrases the final grounded answer when needed
-> response includes guardrails, caveats, sources, and page routing
```

The LLM should not be the source of truth for facts or calculations. It should act as a planner and answer writer. Python/backend tools remain responsible for counts, metrics, routing, and retrieval.

Approved backend tools:

- `project_fact`: exact project metrics from structured artifacts.
- `catalog_count`: filtered game counts from the app catalog.
- `catalog_distribution`: top genres, platforms, themes, modes, or perspectives from the app catalog.
- `game_lookup`: factual lookup for one specific game in the app catalog, including title, release year, genre, platform, rating, hidden-gem flag, summary, and link to the game detail page.
- `game_compare`: factual comparison of two specific games in the app catalog, including release year, genres, platforms, themes, ratings, rating counts, and hidden-gem flags.
- `recommendation_input_helper`: translates vague user preference language into stronger inputs for `Recommend Me_`, without replacing the recommender engine.
- `term_definition`: explains project-specific terms such as PopScore, hidden gem, total_rating_count, rating coverage, RAG, and cosine similarity.
- `website_navigation`: routes users to the correct website page for browsing games, getting recommendations, reviewing hidden gems, reading insights, checking methodology, or using the Guide.
- `recommendation_redirect`: recommendation requests are routed to `Recommend Me_`.
- `project_context`: RAG-backed explanatory questions.
- `unsupported`: unrelated questions outside the project/game-discovery scope.

## 6. High-Level Flow

### Step 1: User asks a natural question

Example:

```text
How many games are in the dataset?
```

or:

```text
Why does Recommend Me ask for recent games?
```

or:

```text
Can you explain what makes something a hidden gem?
```

### Step 2: Scope checker classifies the question

The backend should classify whether the question is:

- project-related;
- dataset-related;
- methodology-related;
- recommendation-related;
- game-discovery-related;
- website-navigation-related;
- out of scope.

### Step 3: Retrieve relevant context

If the question is in scope, the backend retrieves relevant context from project artifacts.

Potential retrieval sources:

- chatbot knowledge base;
- methodology summaries;
- descriptive findings;
- diagnostic findings;
- data dictionary;
- business rules;
- website page context;
- current app methodology metrics;
- current insight summary;
- game catalog summaries;
- recommendation methodology documentation.

### Step 4: Build grounded LLM prompt

The backend should send the LLM:

- the user question;
- retrieved context;
- strict answer rules;
- project scope boundaries;
- instruction to avoid unsupported claims;
- instruction to redirect recommendations to `Recommend Me_` when appropriate.

### Step 5: LLM answers with guardrails

The LLM should answer in a conversational way, but only using the retrieved context.

If context is insufficient, it should say that the project data does not provide enough evidence.

### Step 6: UI displays the response

The frontend should show:

- user message;
- Guide response;
- optional source/context note;
- optional recommended next action;
- optional button to `Recommend Me_`, `Explore Games_`, `Insights_`, or `Methodology_`.

## 7. Deployment Constraints

The architecture must support free or low-cost deployment.

Important constraints:

- Do not self-host an LLM.
- Do not rely on GPU infrastructure.
- Do not use a heavy vector database that is difficult to deploy for free.
- Prefer lightweight retrieval artifacts.
- Keep secrets in environment variables.
- Expect free hosted services to have rate limits.
- Expect backend cold starts if deployed on free services.

Recommended deployment approach:

- Website frontend: Vercel free tier.
- Backend API: Render free web service or Vercel serverless functions.
- LLM: external free-tier API.
- Retrieval: local lightweight JSON/NumPy/parquet artifacts or small indexed text files.

## 8. Free LLM Provider Options

Potential provider options:

### Option A: Gemini API Free Tier

Pros:

- Official developer API.
- Free tier exists for selected models.
- Good enough for project-answering and lightweight chatbot use.

Cons:

- Rate limits can change.
- Requires API key.
- Free-tier behavior may vary by account and region.

### Option B: OpenRouter Free Models

Pros:

- OpenAI-compatible API shape.
- Provides access to free model variants.
- Easy to swap models.

Cons:

- Free tier has strict rate limits.
- Free models may be inconsistent.
- Some router options can charge if misconfigured, so only explicit free models should be used.

### Option C: Hugging Face Inference Providers

Pros:

- Many models available.
- Good ecosystem for open-source models.

Cons:

- Free monthly credits are limited.
- Availability and latency can vary.

## 9. Recommended Provider Choice

The recommended first implementation should use:

```text
Gemini API free tier
```

Reason:

- It is practical for a student project.
- It avoids self-hosting.
- It is likely strong enough for project explanation.
- It should be easier than maintaining a local model.

The code should still be provider-abstracted so the project can later switch to OpenRouter if needed.

## 10. Retrieval Design

The retrieval layer should be lightweight.

Recommended retrieval sources should be transformed into concise text chunks.

Example chunk sources:

- `docs/project_source_of_truth/ask_the_guide_knowledge_base.md`
- `docs/project_source_of_truth/ask_the_guide_current_state.md`
- `docs/project_source_of_truth/IGDB_ERD_BusinessRules.md`
- `docs/project_source_of_truth/IGDB_ERD_Data_Dictionary.md`
- `docs/report/descriptive_pillar_findings.md`
- `docs/report/diagnostic_pillar_findings.md`
- `docs/project_source_of_truth/website_visual_style_guide.md`
- `data/app/app_methodology_metrics.json`
- `data/app/app_insight_summary.json`

The retrieval system should return a small number of highly relevant chunks, not the entire project context.

Recommended retrieval behavior:

- retrieve top 3 to 6 chunks;
- prefer project facts over generic documentation when answering exact metric questions;
- include source labels;
- do not include excessive raw text;
- keep the final prompt small enough for free-tier API limits.

## 11. Scope Guardrails

The chatbot should answer only if the question falls into supported scope.

Supported topics:

- the project;
- IGDB data;
- game metadata;
- game discovery;
- recommendations;
- cosine similarity;
- hidden gems;
- RAG methodology;
- descriptive analytics;
- diagnostic analytics;
- website navigation;
- project limitations.

Unsupported topics:

- unrelated general trivia;
- coding help unrelated to the project;
- medical, legal, political, or financial advice;
- personal questions unrelated to the project;
- requests to invent data;
- requests for facts not supported by project artifacts.

Unsupported response style:

```text
I can only help with this IGDB game-discovery project, the game catalog, methodology, recommendations, hidden gems, and website navigation. Try asking about the dataset, the recommendation system, or how to use the site.
```

## 12. Recommendation Boundary

The chatbot can discuss recommendations, but it should not replace `Recommend Me_`.

Allowed:

- Explain how recommendations work.
- Explain what inputs improve recommendations.
- Explain why recent games help.
- Explain why a recommendation may be weak.
- Suggest that the user go to `Recommend Me_`.

Not preferred:

- Generating ranked game recommendations directly from the LLM.
- Letting the LLM invent games from its general training data.
- Returning recommendations that bypass the cosine-similarity workflow.

If the user asks:

```text
Can you recommend games like Baldur's Gate 3?
```

The chatbot should respond with guidance and a next action:

```text
I can help you prepare a stronger recommendation request. For actual ranked matches, use Recommend Me_ and enter Baldur's Gate 3 as a recent game, then add platform, genre, mood, and playstyle preferences.
```

Optional future enhancement:

- The chatbot may call the same recommendation API used by `Recommend Me_`, but it should not rely only on the LLM for ranking.

## 13. Prompting Rules for the LLM

The LLM system prompt should enforce:

- Stay within the IGDB game-discovery project scope.
- Use only retrieved context and known project artifacts.
- Do not invent dataset counts, metrics, or methodology details.
- If context is insufficient, say so.
- Redirect actual ranked recommendations to `Recommend Me_`.
- Keep answers concise and helpful.
- Mention limitations when relevant.
- Do not claim to browse live IGDB unless the backend actually does so.

## 14. Frontend UX Direction

The chatbot page should feel conversational again.

Recommended frontend behavior:

- Restore a text input for the user.
- Keep suggested starter prompts.
- Keep the terminal/cyberpunk visual style.
- Keep the AI face/projection visual.
- Keep the chat transcript scrollable.
- Add source/context badges for grounded answers.
- Add next-action buttons when appropriate.

Recommended quick action buttons:

- Explain the project.
- How many games are in the dataset?
- How does Recommend Me work?
- What is a hidden gem?
- What does RAG do here?
- Where should I go for recommendations?

## 15. Backend API Direction

The `/chat` endpoint should support natural user messages again.

Recommended request shape:

```json
{
  "message": "How does Recommend Me work?",
  "conversation_id": "optional-session-id",
  "history": [],
  "max_results": 5
}
```

Recommended response additions:

```json
{
  "answer": "...",
  "status": "success",
  "mode": "rag_project_guide",
  "sources": [
    {
      "title": "Ask the Guide Knowledge Base",
      "path": "docs/project_source_of_truth/ask_the_guide_knowledge_base.md"
    }
  ],
  "next_actions": [
    {
      "label": "Open Recommend Me",
      "href": "/recommendations"
    }
  ]
}
```

The current schema may need extension for:

- retrieved source chunks;
- source labels;
- next actions;
- refusal reason;
- LLM provider metadata.

## 16. Implementation Phases

### Phase 1: Planning and contract update

- Confirm chatbot scope.
- Confirm LLM provider.
- Confirm retrieval sources.
- Define API request/response contract.
- Decide what source metadata the frontend should display.

### Phase 2: Retrieval artifact preparation

- Build a lightweight project-document index.
- Chunk source-of-truth markdown files.
- Add source labels.
- Add exact fact extraction for metrics where possible.
- Validate retrieval manually with known questions.

### Phase 3: LLM provider integration

- Add environment variable for API key.
- Add provider abstraction.
- Implement Gemini API first.
- Add timeout handling.
- Add rate-limit handling.
- Add fallback response if provider is unavailable.

### Phase 4: RAG answer generation

- Add scope detection.
- Retrieve relevant context.
- Build grounded prompt.
- Call LLM.
- Return answer with sources and next actions.

### Phase 5: Frontend chatbot update

- Restore typed user input.
- Keep suggested prompts.
- Display assistant responses.
- Display source/context badges.
- Display next-action buttons.
- Keep terminal visual style.

### Phase 6: Testing and validation

- Test supported project questions.
- Test dataset fact questions.
- Test recommendation guidance questions.
- Test hidden-gem questions.
- Test out-of-scope questions.
- Test missing API key behavior.
- Test deployed environment behavior.

## 17. Acceptance Criteria

The new chatbot direction is successful if:

- Users can type natural project/game questions.
- The chatbot answers project and game-catalog questions in a conversational way.
- The chatbot refuses unsupported topics.
- Answers are grounded in retrieved project context.
- The chatbot does not invent project metrics.
- Recommendation requests are redirected to `Recommend Me_` unless intentionally routed through the recommendation API.
- The system can run locally.
- The system can be deployed to free hosting with environment variables.
- The project does not require self-hosted LLM infrastructure.

## 18. Main Risks

### Risk 1: Free LLM limits

Free APIs have rate limits and may become unavailable.

Mitigation:

- Add fallback responses.
- Keep deterministic answers for exact metric questions.
- Keep provider abstraction.

### Risk 2: LLM hallucination

The model may answer beyond retrieved context.

Mitigation:

- Strict system prompt.
- Small grounded context.
- Refusal behavior when context is insufficient.
- Source display.

### Risk 3: Deployment complexity

Secrets and backend hosting may complicate deployment.

Mitigation:

- Use environment variables.
- Keep retrieval lightweight.
- Avoid Chroma or heavy local services.

### Risk 4: Chatbot overlaps with Recommend Me_

Users may expect the chatbot to produce ranked recommendations.

Mitigation:

- Keep the chatbot as a guide.
- Route recommendation intent to `Recommend Me_`.
- Clearly explain the boundary.

## 19. Recommended Final Position

The best final position is:

> Ask the Guide_ is a scoped RAG-powered AI guide. It uses a free external LLM only after retrieving project context, answers questions about the game-discovery project and catalog, and redirects users to Recommend Me_ for actual ranked recommendations.

This keeps the chatbot useful and conversational while preserving the project’s core structure.
