# Ask the Guide Page Current State

Last updated: July 23, 2026

This document explains the current state of the website chatbot page, now called **Ask the Guide_**. It is intended as a handoff document for improving the page without needing to reverse-engineer the current implementation from scratch.

## 1. Current Product Direction

Ask the Guide_ is no longer designed to behave like ChatGPT. The project previously explored a more open-ended RAG chatbot direction, but that approach became unreliable for the current project scope because user questions could be phrased in many different ways and the system sometimes routed questions incorrectly.

The current page is now a **condition-based project guide**. Users do not freely type questions. Instead, they select one predefined instruction from a dropdown, run that instruction, and receive a controlled answer from the backend.

The page’s current purpose is:

- Explain the project.
- Explain the IGDB dataset and its limitations.
- Explain the recommendation methodology.
- Explain hidden-gem logic.
- Explain the role of RAG in the project.
- Answer selected dataset facts such as game count, year range, and rating coverage.
- Help users navigate to the correct page.
- Direct users to Recommend Me_ when they want actual game recommendations.

The page’s current non-purpose is:

- It is not the main recommendation engine.
- It is not a free-form chatbot.
- It is not an LLM-powered assistant.
- It is not expected to answer every possible user question.
- It does not return game cards or ranked game recommendations.

## 2. Current UX Behavior

The user lands on `/guide`.

The page shows:

- A large terminal-style guide panel on the left.
- A CSS-built futuristic AI face/projection on the right.
- A welcome bubble from the Guide.
- A dropdown of supported instructions.
- A `Run instruction` button.
- A `Clear chat` button.
- A terminal-style transcript area.
- A bottom callout that sends users to Recommend Me_ for ranked recommendations.
- A bottom disclaimer explaining Guide boundaries.

When no instruction has been run yet, the transcript area shows an animated terminal idle message:

```text
terminal idle_
guide@igdb:~$ awaiting selected instruction
```

Once the user runs an instruction, the idle message disappears and the transcript displays the selected instruction and the Guide response.

The chat thread is capped at `8` user selections through:

```ts
const MAX_GUIDE_USER_TURNS = 8;
```

Once the limit is reached, the page prevents more instruction submissions until the user clears the chat.

## 3. Current Visual Direction

The visual style is cyberpunk, black/orange/white, and terminal-inspired.

The current design intentionally avoids the earlier green Matrix-style treatment on this page. The current Ask the Guide-specific CSS uses:

- Black page background.
- White grid/scanline texture.
- Orange accent color `#ff3e00`.
- White/orange AI projection effects.
- A CSS-generated AI face inspired by futuristic AI face references.
- Homepage-inspired glitch slices and flicker effects.

The AI visual is not an imported image. It is built with HTML spans and CSS so that the project avoids licensing issues and remains easy to deploy.

The relevant frontend component is:

```text
apps/website/src/app/guide/page.tsx
```

The relevant styling is in:

```text
apps/website/src/app/globals.css
```

The main CSS class family is:

```text
ask-guide-*
```

Important visual classes include:

- `ask-guide-shell`
- `ask-guide-stage`
- `ask-guide-stage-grid`
- `ask-guide-terminal`
- `ask-guide-transcript`
- `ask-guide-terminal-waiting`
- `ask-guide-avatar`
- `ask-guide-face`
- `ask-guide-face-outline`
- `ask-guide-face-eye`
- `ask-guide-face-glitch`
- `ask-guide-data-rain`
- `ask-guide-lower-callout`
- `ask-guide-disclaimer`

## 4. Current Frontend Structure

The page is implemented as a client component:

```ts
"use client";
```

Main imports:

```ts
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { postChatMessage } from "@/lib/api";
import type { ChatResponse, ChatRouteMode } from "@/types/api";
```

The page sends requests through:

```ts
postChatMessage(...)
```

which is defined in:

```text
apps/website/src/lib/api.ts
```

The frontend request goes to:

```text
POST /chat
```

with a payload shaped like:

```ts
{
  message: topic.prompt,
  route_mode: topic.id,
  max_results: 5,
  history: []
}
```

Important implementation detail: the frontend currently sends `history: []` every time. The Guide is not using conversational memory. It behaves like selected deterministic commands.

## 5. Current Supported Guide Topics

The supported instructions are defined in `guideTopics` inside:

```text
apps/website/src/app/guide/page.tsx
```

Current topic list:

| Route mode | Dropdown label | Purpose |
|---|---|---|
| `explain_project` | Explain this project | Explains the overall project goal and analytics system. |
| `explain_data` | Explain the data | Explains the IGDB app catalog and metadata fields. |
| `dataset_size` | How many games are in the dataset? | Returns the current game count from project metrics. |
| `dataset_year_range` | What years does the dataset cover? | Returns the release-year range from project metrics. |
| `rating_coverage` | What is rating coverage? | Explains rating coverage using project metrics. |
| `explain_recommendation` | Explain recommendations | Explains the cosine-similarity recommendation workflow. |
| `recommend_me_guidance` | Help me use Recommend Me | Explains how users should use the Recommend Me_ page. |
| `explain_hidden_gems` | Explain hidden gems | Explains hidden-gem logic. |
| `explain_rag` | Explain RAG | Explains RAG as a project grounding concept. |
| `search_catalog` | Where do I browse games? | Points users to Explore Games_. |
| `website_navigation` | Website navigation | Explains what each website page is for. |
| `explain_limitations` | Explain limitations | Explains dataset and methodology limitations. |

## 6. Current Follow-Up Behavior

Backend responses include `follow_up_prompts`.

The frontend renders those prompts as buttons under a Guide response. When clicked, the frontend tries to infer a route mode from the prompt using:

```ts
routeModeForPrompt(prompt)
```

This is a lightweight fallback router on the frontend. It checks whether the follow-up prompt includes keywords such as:

- `how many`
- `dataset size`
- `year`
- `rating coverage`
- `hidden gem`
- `recommend`
- `rag`
- `data`
- `navigation`
- `website`
- `limitation`

Then it submits another controlled request to the backend.

This is not meant to support free-form user typing. It only helps follow-up buttons continue the controlled guide flow.

## 7. Current Backend Behavior

The backend chat logic is implemented in:

```text
api/app/services/chat_service.py
```

The current backend engine identifies itself as:

```text
condition_based_project_guide
```

The backend accepts route modes through:

```py
GUIDED_ROUTE_MODES = {
    "custom_question",
    "dataset_size",
    "dataset_year_range",
    "explain_data",
    "explain_hidden_gems",
    "explain_limitations",
    "explain_project",
    "explain_rag",
    "explain_recommendation",
    "recommend_games",
    "recommend_me_guidance",
    "rating_coverage",
    "search_catalog",
    "website_navigation",
}
```

Important detail: `custom_question` still exists in the schema/backend route list, but the current frontend does not expose free-form typing. If the user somehow sends an unsupported or non-routed request, the backend returns an unsupported-instruction response.

## 8. Backend Response Types

The backend returns a `ChatResponse`.

The frontend expects this TypeScript shape:

```ts
export type ChatResponse = {
  answer: string;
  mode: string;
  status: string;
  route_mode?: ChatRouteMode | null;
  conversation_id?: string | null;
  retrieved_games: ChatRetrievedGame[];
  caveats: string[];
  applied_filters: Record<string, unknown>;
  follow_up_prompts: string[];
  contextual_query?: string | null;
  interpreted_preferences: Record<string, unknown>;
  chat_intent?: string | null;
  intent_confidence?: number | null;
  route_source?: string | null;
  matched_intent_example?: string | null;
};
```

For the current condition-based Guide, most fields are intentionally empty or static:

- `retrieved_games` is usually `[]`.
- `applied_filters` is usually `{}`.
- `interpreted_preferences` is usually `{}`.
- `contextual_query` is usually `null`.
- `intent_confidence` is usually `1.0`.
- `route_source` is usually `selected_route_mode`.

This is expected because the Guide is not currently performing game retrieval.

## 9. Current Project-Fact Logic

Some Guide instructions route through structured project facts instead of hard-coded text.

This logic lives in:

```text
src/app/project_facts.py
```

The structured fact routes are:

```py
FACT_ROUTE_QUESTIONS = {
    "dataset_size": "How many games does the dataset have?",
    "dataset_year_range": "What years does the dataset cover?",
    "rating_coverage": "What is rating coverage?",
}
```

These pull from structured artifacts such as:

```text
data/app/app_methodology_metrics.json
data/app/app_insight_summary.json
data/rag/lightweight/manifest.json
```

This is the strongest part of the current Guide architecture because factual answers can update when the project artifacts update, instead of being only hard-coded copy.

## 10. Current RAG Role

The current Guide explains RAG but does not behave like a full RAG chatbot.

Current project direction:

- RAG is still part of the project as a concept and supporting methodology.
- The Guide page is currently condition-based for reliability.
- The Guide does not currently retrieve project documents dynamically.
- The Guide does not currently call an LLM.
- The Guide does not currently use vector retrieval to generate natural-language answers.

In short: the current page is a **guided explanation layer**, not a true free-form RAG assistant.

## 11. Current Recommendation Role

Ask the Guide_ is not responsible for recommendations.

The current recommendation workflow lives on:

```text
/recommendations
```

Ask the Guide_ only explains how to use Recommend Me_.

When a response has:

```ts
response.mode === "recommend_me_guidance"
```

or:

```ts
response.chat_intent === "recommend_me_guidance"
```

the frontend shows an extra reminder:

```text
For actual ranked matches, continue on Recommend Me_.
```

The page also has a bottom callout:

```text
Want game recommendations?_
Go to Recommend Me_
Ask the Guide_ explains the project. Recommend Me_ is the page that turns your preferences into ranked game matches.
```

## 12. Current API Status Endpoint

The backend still provides:

```text
GET /chat/status
```

The frontend API helper still has:

```ts
getChatStatus()
```

However, the current Ask the Guide_ page does not display the status panel anymore. It only uses `postChatMessage`.

The status endpoint may still be useful for future debugging or admin-style diagnostics, but it is not part of the current user-facing Guide page.

## 13. Current Error Behavior

If the frontend cannot reach the chat API, the failed turn displays:

```text
Chat API is unavailable. Start the FastAPI backend and try again.
```

If the user reaches the turn limit, the page displays:

```text
This guide thread has reached 8 user selections. Start a new topic to keep the context clean.
```

If the backend receives an unsupported route, it returns:

```text
Ask the Guide_ is now condition-based. Choose one of the predefined guide instructions instead of typing a free-form question.
```

## 14. Current Known Limitations

The current page is reliable, but limited by design.

Known limitations:

- The user cannot freely type a question.
- The Guide cannot answer arbitrary project questions unless they are represented by a predefined route or fact artifact.
- Most answers are still hard-coded in `chat_service.py`.
- Only a few project facts are dynamically grounded in artifacts.
- `custom_question` still exists in the backend schema, but the frontend does not use it.
- `ChatRetrievedGame` types still exist because of the previous RAG/retrieval design, but the current Guide does not render game cards.
- `getChatStatus()` still exists in the frontend API helper but is unused by the current Guide page.
- The Guide is not conversational in the LLM sense. It is command-based.
- Follow-up prompts are clickable, but they are still routed by simple frontend keyword logic.
- If the project expands, the dropdown could become too long and may need grouping.

## 15. Current Strengths

The current implementation has several strengths:

- It is simple and predictable.
- It is easier to test than a free-form chatbot.
- It avoids LLM API costs.
- It is compatible with free deployment goals.
- It avoids user frustration from unsupported natural-language routing.
- It clearly separates explanation from recommendation.
- It uses structured project artifacts for selected factual answers.
- It visually matches the cyberpunk website direction.
- It avoids copyrighted image assets by using CSS-generated AI visuals.

## 16. Suggested Improvement Directions

If improving this page, the most useful improvements are not more random intent patches. The better path is to make the Guide more structured and more artifact-driven.

Recommended next improvements:

### 16.1 Expand project-fact coverage

Move more answers from hard-coded backend strings into structured project artifacts.

Examples:

- Total games.
- Release-year range.
- Games per year.
- Hidden-gem count.
- Top genre.
- Top platform.
- Rating coverage.
- PopScore coverage.
- Summary coverage.
- Recommendation formula summary.
- Dataset caveats.
- Extraction logic.

### 16.2 Create grouped instruction categories

Instead of one long dropdown, split instructions into groups:

- Project overview.
- Dataset facts.
- Recommendation methodology.
- RAG and technical architecture.
- Website navigation.
- Limitations.

This would make the page easier to use as the number of supported instructions grows.

### 16.3 Add a source/citation area for fact answers

Current fact answers include source artifacts in `caveats`.

The frontend could show a small `Source` section for answers that are grounded in artifacts.

Example:

```text
Source: data/app/app_methodology_metrics.json
```

### 16.4 Replace frontend follow-up keyword routing with explicit route metadata

Current follow-up prompts are strings, and the frontend guesses the route from the prompt text.

A cleaner approach would be for the backend to return follow-up objects:

```ts
{
  label: "What is rating coverage?",
  route_mode: "rating_coverage"
}
```

This would remove fragile frontend keyword routing.

### 16.5 Decide whether `custom_question` should stay

If the page is strictly condition-based, `custom_question` may be misleading.

Options:

- Keep it only for backend compatibility.
- Remove it from the schema if no longer used.
- Reserve it for a future project-document search mode.

### 16.6 Add tests for every route mode

Each route mode should have a backend test verifying:

- status is expected.
- answer is non-empty.
- follow-up prompts are returned.
- route mode is preserved.
- factual routes use artifacts when available.

### 16.7 Improve the UI copy

The Guide currently explains its own limitations clearly, but some copy could be made more user-centered.

Potential direction:

- Less emphasis on what the Guide cannot do.
- More emphasis on which project topic the user can quickly learn.

Example:

```text
Choose what you want explained. The Guide will return a focused project answer.
```

## 17. Files Most Relevant for Teammate

Frontend:

```text
apps/website/src/app/guide/page.tsx
apps/website/src/app/globals.css
apps/website/src/lib/api.ts
apps/website/src/types/api.ts
```

Backend:

```text
api/app/services/chat_service.py
api/app/schemas/chat.py
api/main.py
```

Project fact layer:

```text
src/app/project_facts.py
```

Current planning docs:

```text
docs/plan/rag_chatbot_implementation_plan.md
docs/plan/rag_chatbot_intelligence_layer_plan.md
docs/project_source_of_truth/rag_chatbot_predefined_responses_reference.md
docs/project_source_of_truth/rag_chatbot_scope_and_knowledge_contract.md
docs/plan/UI_Improvement_Plans/AskTheGuide_Page/
```

## 18. Practical Summary for Teammate

Ask the Guide_ is currently a controlled project-explanation interface, not a natural-language chatbot. The frontend presents predefined guide instructions through a dropdown and sends the selected `route_mode` to the FastAPI backend. The backend returns deterministic responses from `chat_service.py`, with selected factual answers grounded in project artifacts through `src/app/project_facts.py`. The current page is visually styled as a cyberpunk terminal with a CSS-generated AI face, and actual game recommendations are intentionally routed to the separate Recommend Me_ page.
