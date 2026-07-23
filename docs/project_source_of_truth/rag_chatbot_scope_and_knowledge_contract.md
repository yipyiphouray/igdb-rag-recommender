# Ask the Guide Scope and Knowledge Contract

## 1. Current Direction

`Ask the Guide_` is now a condition-based project guide.

The user does not type unrestricted free-form questions. Instead, the user selects from predefined guide instructions. Each instruction maps to a controlled backend route, and the backend returns a deterministic project explanation or exact structured fact.

This direction replaces the earlier open-ended chatbot direction.

## 2. Product Identity

`Ask the Guide_` is not a general chatbot and not the main recommendation engine.

It exists to:

- explain the IGDB game-discovery project;
- explain the dataset and data caveats;
- answer selected exact dataset facts;
- explain the cosine-similarity recommendation logic;
- explain the role of RAG in the project;
- explain hidden-gem logic;
- explain website navigation;
- explain project limitations;
- direct users to `Recommend Me_` for actual ranked game recommendations.

The clearest product split is:

```text
Recommend Me_  -> personalized game recommendation workflow
Ask the Guide_ -> controlled project explanation and navigation guide
```

## 3. Why The Guide Is Condition-Based

The earlier open-ended chatbot approach created too many failure points:

- users can phrase the same question in many ways;
- deterministic intent matching cannot reliably understand every phrasing;
- recommendation questions were sometimes routed incorrectly;
- open-ended chat made the Guide feel weaker than `Recommend Me_`;
- adding more phrase patches created maintenance complexity;
- using an LLM was removed from scope for this implementation.

The condition-based design is more defensible because every supported user path is known, testable, and explainable.

## 4. Supported Guide Instructions

The Guide page should expose predefined buttons for these supported instructions.

| Instruction | Backend route | Purpose |
|---|---|---|
| Explain this project | `explain_project` | Summarize the project goal and analytics system |
| Explain the data | `explain_data` | Explain IGDB source data, catalog fields, and metadata caveats |
| How many games are in the dataset? | `dataset_size` | Return current dataset size from structured metrics |
| What years does the dataset cover? | `dataset_year_range` | Return release-year coverage from structured metrics |
| What is rating coverage? | `rating_coverage` | Explain rating availability from structured metrics |
| Explain recommendations | `explain_recommendation` | Explain cosine similarity and structured preference matching |
| Help me use Recommend Me | `recommend_me_guidance` | Tell users what inputs improve recommendations |
| Explain hidden gems | `explain_hidden_gems` | Explain hidden-gem definition and caveats |
| Explain RAG | `explain_rag` | Explain RAG as a project concept and grounding layer |
| Where do I browse games? | `search_catalog` | Direct users to `Explore Games_` |
| Website navigation | `website_navigation` | Explain what each website page is for |
| Explain limitations | `explain_limitations` | Summarize dataset and recommendation limitations |

## 5. Unsupported Behavior

The Guide should not:

- accept unrestricted typed questions;
- behave like ChatGPT;
- use an LLM provider;
- make live external API calls;
- return ranked game recommendations;
- replace `Recommend Me_`;
- infer unsupported facts;
- invent game metadata;
- use a large vector database for this page.

If an unsupported route reaches the backend, the response should say that the Guide is condition-based and that users should choose one of the predefined instructions.

## 6. Trusted Fact Sources

Exact numeric facts should still come from structured local artifacts.

| Artifact | Purpose |
|---|---|
| `data/app/app_methodology_metrics.json` | Current dataset metrics, coverage, thresholds, and counts |
| `data/app/app_insight_summary.json` | Website-facing descriptive and diagnostic summary facts |
| `data/rag/lightweight/manifest.json` | Lightweight RAG index metadata when RAG artifact facts are needed |

Exact facts should not be hard-coded into the response text when a structured artifact already contains the value.

## 7. Backend Rules

The `/chat` endpoint should behave as a route-mode dispatcher.

Required behavior:

```text
selected route_mode -> deterministic response
```

The backend should not perform natural-language routing for the Guide page.

Recommended priority:

```text
1. If route_mode maps to an exact fact, call src/app/project_facts.py.
2. If route_mode maps to a curated explanation, return the predefined answer.
3. If route_mode is unsupported, return the condition-based fallback.
```

## 8. Frontend Rules

The Guide page should:

- show predefined guide instruction cards;
- remove the free-form text input;
- show a response thread after each selected instruction;
- offer predefined follow-up buttons;
- include a clear `Recommend Me_` callout;
- keep the existing cyberpunk/terminal visual style;
- explain that the Guide is controlled by design.

The page should not invite users to ask anything they want.

## 9. Recommendation Handling

For actual game recommendations, users should go to `Recommend Me_`.

Recommended Guide message:

```text
Use Recommend Me_ when you want actual game matches. The Guide can explain what to enter, but Recommend Me_ is where ranking happens.
```

## 10. RAG Positioning

RAG remains part of the overall project methodology, but the Guide page is no longer implemented as an open-ended RAG chatbot.

The Guide can still explain what RAG means in the project. However, its current website behavior is a controlled explanation interface, not a retrieval-based open chat interface.

## 11. Acceptance Criteria

The condition-based Guide is ready when:

- users can only select predefined guide instructions;
- the free-form text input is removed;
- each supported instruction returns a controlled response;
- exact dataset facts come from structured artifacts;
- recommendation requests are directed to `Recommend Me_`;
- no LLM provider code is required;
- no LLM environment variables are required;
- backend tests pass;
- frontend production build passes;
- documentation clearly states the Guide is condition-based.

## 12. Final Report Wording

Use this wording when describing the Guide:

> `Ask the Guide_` is a condition-based project guide that explains the IGDB dataset, methodology, recommendation logic, hidden-gem rules, RAG concept, limitations, and website navigation through predefined user instructions. Personalized game ranking remains in `Recommend Me_`, where structured user preferences are processed with cosine similarity.
