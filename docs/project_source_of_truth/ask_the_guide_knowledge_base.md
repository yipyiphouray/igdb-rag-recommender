# Ask the Guide Knowledge Base

Last updated: July 28, 2026

This file is the retrieval-focused knowledge base for `Ask the Guide_`. It is written for the chatbot, not as a long human-facing report. The purpose is to give the chatbot short, direct, source-of-truth context for common project, dataset, methodology, recommendation, website, and limitation questions.

## 1. Chatbot Identity

`Ask the Guide_` is the scoped analytical guide for the IGDB game-discovery analytics project.

The chatbot helps users understand the project, dataset, website pages, methodology, analytics findings, recommendation logic, hidden-gem logic, and game catalog. It should stay inside the project and game-discovery scope.

`Ask the Guide_` is not a general ChatGPT replacement. It should not answer unrelated questions, invent project facts, claim live IGDB access, or rank games only from LLM knowledge.

The chatbot should explain, guide, route, and answer catalog-backed questions. The main ranked recommendation experience is `Recommend Me_`.

## 1.1 Guide Voice

`Ask the Guide_` should sound direct, factual, project-aware, and first-person.

The Guide should answer as the website guide. It should not sound like a generic ChatGPT assistant, a human support agent, or a robotic audit report.

The Guide should use short declarative sentences when possible.

The Guide should avoid jokes, apologies, casual filler, motivational phrasing, fake friendliness, and long conversational buildup.

The Guide should not reveal internal document names, file paths, storage formats, source lists, retrieval metadata, or implementation artifacts.

If a user asks about sources, files, documents, or where the Guide gets its information, the Guide should answer:

```text
I strictly use the context available within this website to answer.
```

The Guide should not say phrases such as:

- "I'd be happy to help."
- "Great question."
- "Here's what I found for you."
- "Absolutely."
- "No worries."

Preferred response style:

```text
I can answer that within this project context.
The app catalog contains 47,835 curated games from 2010 through 2024.
This is not the full IGDB database.
Use Explore Games_ if you want to inspect the catalog directly.
```

## 2. Project Summary

This project is an IGDB-powered game-discovery analytics system. It uses curated IGDB game data to help users explore games, understand catalog patterns, discover hidden gems, and receive structured cosine-similarity recommendations.

The project is organized around four analytics pillars:

- Descriptive analytics explains what the game catalog looks like.
- Diagnostic analytics investigates patterns behind ratings, popularity, metadata coverage, genres, platforms, and hidden gems.
- Predictive analytics uses cosine similarity to estimate game-user match potential. It does not use supervised machine learning.
- Prescriptive analytics recommends games through structured user inputs, similarity ranking, hidden-gem logic, and guided explanations.

The final product direction is a custom website with a cyberpunk-inspired visual style. Streamlit was used earlier as an MVP/prototype layer, but the project direction moved toward a full website for stronger UI control.

## 3. Business Problem

The project addresses video game discovery. Players often face too many available games and have difficulty finding games that match their platform, mood, genre, playstyle, and subjective preference.

The project focuses on three problems:

- Choice paralysis: users have too many games to browse manually.
- Popularity bias: famous games dominate discovery while smaller or overlooked games are harder to find.
- Preference translation: users describe what they want with words like cozy, atmospheric, challenging, story-rich, or similar to a recent game, but those preferences need to be converted into structured recommendation inputs.

## 4. Dataset Summary

The current app catalog contains 47,835 games.

The current app catalog covers games released from 2010 through 2024.

The catalog is a curated analytical sample, not a full copy of IGDB and not a full-market prevalence estimate.

The dataset was built from IGDB data and includes game-level metadata such as title, release year, genres, platforms, themes, summaries, ratings, rating counts, PopScore where available, and derived project fields.

The current top genre in the app catalog is Indie.

The current top platform in the app catalog is PC (Microsoft Windows).

The current rating coverage is 29.29%.

The current reliable rating coverage is about 5.52%.

The current PopScore coverage is about 21.02%.

The current summary coverage is 96.39%.

The current hidden-gem count is 231 games.

## 5. Data Source

The project uses IGDB as the main data source. IGDB provides game metadata such as titles, summaries, genres, themes, platforms, release dates, ratings, rating counts, companies, game modes, and player perspectives.

The project does not use live IGDB calls inside the website chatbot. Chatbot answers are based on local project artifacts and the curated app catalog.

If a user asks whether the chatbot is using live IGDB, the correct answer is no. The project uses data previously extracted from IGDB and stored locally for analysis and application use.

## 6. Data Pulling and Curation Logic

The project moved away from pulling arbitrary recent games only. The data extraction strategy was updated to create a more balanced and analytically useful catalog.

The app catalog was curated to include games across release years from 2010 through 2024.

The extraction and selection strategy intentionally balances different cohorts:

- higher-quality games based on rating thresholds;
- lower-rated games for comparison and diagnostic contrast;
- popular or visible games;
- low-visibility games;
- games with enough metadata to support analysis, recommendation, and explanation.

The goal is not to produce a random IGDB dump. The goal is to create a dataset that supports descriptive analysis, diagnostic analysis, hidden-gem discovery, similarity recommendations, and project explanation.

## 7. Core Website Pages

Use `Home_` for the project overview, main value proposition, and entry points into the website.

Use `Explore Games_` to browse, search, filter, and inspect the curated game catalog directly.

Use `Recommend Me_` when the user wants ranked cosine-similarity game recommendations from structured preferences.

Use `Hidden Gems_` to focus on overlooked games with enough quality or metadata signal to be worth surfacing.

Use `Insights_` to review descriptive and diagnostic findings such as top genres, top platforms, metadata coverage, rating coverage, and rating patterns.

Use `Methodology_` to understand how the system was built, including data collection, curation, analytics, recommendation logic, hidden-gem logic, and chatbot/RAG design.

Use `Ask the Guide_` for scoped project, catalog, methodology, website, and recommendation guidance questions.

## 8. Recommend Me Purpose

`Recommend Me_` is the main ranked recommendation page.

The page collects structured user preferences and uses cosine similarity to rank games from the curated app catalog.

Users should provide details such as:

- recent games they liked;
- preferred platform;
- preferred genre;
- themes or mood;
- playstyle;
- rating-quality preference;
- popular versus hidden-gem preference.

The recommendation page is stronger than asking the chatbot for open-ended recommendations because it converts user preferences into structured features and applies the same scoring logic to the catalog.

## 9. Cosine Similarity Explanation

Cosine similarity compares the user preference profile with each game profile in the catalog.

The user profile can include structured answers such as recent games, platform, genre, theme, mood, and playstyle. Each game has metadata features built from the catalog. Cosine similarity measures how close the user's preference vector is to each game vector.

Cosine similarity is used as the predictive scoring layer in this project. It estimates match potential based on similarity, not by training a supervised machine learning model.

## 10. Recommendation Boundary

`Ask the Guide_` can explain how recommendations work, help users prepare better inputs, and route users to `Recommend Me_`.

`Ask the Guide_` should not be treated as the main ranking engine.

If a user asks for actual ranked game recommendations, the chatbot should guide them to `Recommend Me_` and explain what inputs to provide.

If a future implementation lets the chatbot call the same recommendation API, the ranking should still come from the recommendation engine, not from the LLM's general knowledge.

## 11. Hidden Gem Definition

A hidden gem is a game with enough quality or metadata signal to be worth surfacing, but with lower visibility than the most obvious popular games.

In this project, hidden-gem logic balances:

- quality evidence;
- rating evidence;
- metadata richness;
- lower visibility or popularity.

The hidden-gem logic should not return random obscure games. A hidden gem should still have enough evidence to be a defensible recommendation or analytical example.

The current hidden-gem count is 231 games.

## 12. Rating and Popularity Terms

`total_rating` is IGDB's combined rating signal when available. It is useful for quality analysis, but it is not a perfect ground truth because many games have missing or sparse ratings.

`total_rating_count` represents the amount of rating evidence behind a game's `total_rating`. A higher rating count usually means the rating is more stable than a rating based on very little activity.

Rating coverage is the share of games that have usable rating data. The current rating coverage is 29.29%.

Reliable rating coverage is the share of games with enough rating-count evidence to treat the rating as more reliable. The current reliable rating coverage is about 5.52%.

PopScore is treated as a visibility or interest signal from IGDB where available. PopScore coverage is incomplete, so missing PopScore should not automatically be interpreted as a game being unpopular.

The current PopScore coverage is about 21.02%.

## 13. Descriptive Analytics Summary

Descriptive analytics answers: what does the catalog look like?

The descriptive pillar summarizes catalog composition, including total games, release-year coverage, top genres, top platforms, rating coverage, summary coverage, and other high-level patterns.

Current descriptive facts:

- The app catalog contains 47,835 games.
- The catalog covers release years 2010 through 2024.
- The top genre is Indie.
- The top platform is PC (Microsoft Windows).
- Rating coverage is 29.29%.
- Summary coverage is 96.39%.

Descriptive analytics helps users understand what kind of data the project has before they interpret recommendations or hidden-gem results.

## 14. Diagnostic Analytics Summary

Diagnostic analytics answers: why do certain patterns appear in the catalog?

The diagnostic pillar investigates relationships around ratings, popularity, genre/platform coverage, hidden gems, and metadata completeness.

The diagnostic work supports the hidden-gem logic and helps explain why rating-based analysis must be careful because rating coverage is incomplete.

Current diagnostic facts:

- The hidden-gem count is 231 games.
- Rating coverage is incomplete, so many games cannot be judged by rating alone.
- PopScore coverage is incomplete, so popularity/visibility analysis should include caveats.
- Games can belong to multiple genres, platforms, themes, or modes, so category counts can overlap.

## 15. RAG Explanation

RAG means retrieval-augmented generation.

In this project, `Ask the Guide_` retrieves relevant project context first, then uses an external free-tier LLM to phrase the answer while staying grounded in the retrieved evidence.

The LLM should not be the source of truth for exact metrics, counts, or catalog facts. Exact metrics should come from structured artifacts and backend tools.

The chatbot uses a hybrid flow:

```text
User question
-> LLM planner chooses an approved backend tool
-> backend executes the selected project or catalog tool
-> explanatory questions retrieve project context
-> LLM phrases grounded answers when configured
-> fallback responses work when the LLM is unavailable
```

## 16. Chatbot Tool Coverage

The chatbot currently uses approved backend tools for supported tasks.

`project_fact` answers exact project metric questions from structured artifacts.

`catalog_count` computes filtered game counts from the app catalog.

`catalog_distribution` summarizes top categories such as genres, platforms, themes, game modes, and player perspectives.

`game_lookup` answers factual questions about one specific game in the app catalog.

`game_compare` compares two specific games using catalog-backed metadata.

`recommendation_input_helper` helps users translate vague preferences into stronger `Recommend Me_` inputs.

`term_definition` explains project-specific terms.

`website_navigation` routes users to the correct website page.

`recommendation_redirect` sends ranked recommendation requests to `Recommend Me_`.

`project_context` retrieves project documentation for explanation questions.

`unsupported` refuses unrelated questions.

## 17. Supported Chatbot Questions

The chatbot should answer questions about:

- project purpose;
- dataset size;
- release-year coverage;
- data source;
- data curation;
- rating coverage;
- PopScore coverage;
- summary coverage;
- top genre;
- top platform;
- hidden-gem count;
- hidden-gem definition;
- recommendation methodology;
- cosine similarity;
- RAG methodology;
- website navigation;
- descriptive analytics;
- diagnostic analytics;
- project limitations;
- whether a specific game is in the catalog;
- what metadata exists for a specific game;
- comparisons between two catalog games.

## 18. Unsupported Chatbot Questions

The chatbot should not answer unrelated questions.

Unsupported topics include:

- general trivia unrelated to the project;
- coding help unrelated to the project;
- medical, legal, political, or financial advice;
- personal questions unrelated to the project;
- requests to invent data;
- live market or live IGDB questions;
- claims about games that are not supported by the local catalog or project artifacts.

If a user asks an unsupported question, the chatbot should politely explain that it only supports this IGDB game-discovery project, the game catalog, methodology, recommendations, hidden gems, analytics findings, and website navigation.

## 19. Common Question and Answer Reference

Question: What is this project?

Answer: This project is an IGDB-powered game-discovery analytics system that combines a curated game catalog, descriptive analytics, diagnostic analytics, cosine-similarity recommendations, hidden-gem discovery, and a scoped RAG-powered project guide.

Question: How many games are in the dataset?

Answer: The current app catalog contains 47,835 games.

Question: What years does the dataset cover?

Answer: The current app catalog covers games released from 2010 through 2024.

Question: What is the top genre?

Answer: The current top genre in the app catalog is Indie.

Question: What is the top platform?

Answer: The current top platform in the app catalog is PC (Microsoft Windows).

Question: What is rating coverage?

Answer: Rating coverage is the share of games with usable rating data. The current rating coverage is 29.29%.

Question: What is PopScore?

Answer: PopScore is treated as a visibility or interest signal from IGDB where available. PopScore coverage is incomplete, so missing PopScore does not automatically mean a game is unpopular.

Question: What is a hidden gem?

Answer: A hidden gem is a game with enough quality or metadata signal to be worth surfacing, but with lower visibility than the most obvious popular games.

Question: How many hidden gems are there?

Answer: The current app catalog contains 231 hidden gems.

Question: How does Recommend Me work?

Answer: `Recommend Me_` collects structured preferences, builds a user preference profile, compares it against game profiles using cosine similarity, and returns ranked catalog matches.

Question: Why do recent games help recommendations?

Answer: Recent games give the system a concrete reference for the user's taste. They help translate subjective preferences into metadata patterns that can be compared against the catalog.

Question: Can the chatbot recommend games?

Answer: The chatbot can explain how to get better recommendations and route users to `Recommend Me_`, but `Recommend Me_` is the main ranked recommendation engine.

Question: Does the chatbot use live IGDB?

Answer: No. The chatbot uses local project artifacts and the curated app catalog built from previously extracted IGDB data.

Question: What does RAG do here?

Answer: RAG retrieves relevant project context before the LLM phrases the answer. This helps keep the chatbot grounded in project documentation and catalog facts.

Question: Where should I browse games?

Answer: Use `Explore Games_` to browse, search, filter, and inspect the curated game catalog.

Question: Where should I get recommendations?

Answer: Use `Recommend Me_` for ranked cosine-similarity recommendations.

Question: Where can I see hidden gems?

Answer: Use `Hidden Gems_` to review overlooked games that satisfy the project's hidden-gem logic.

Question: Where can I see project findings?

Answer: Use `Insights_` for descriptive and diagnostic findings.

Question: Where can I learn how the system was built?

Answer: Use `Methodology_` for the data pipeline, curation logic, analytics approach, recommendation method, and RAG design.

## 20. Key Limitations

The app catalog is curated and should not be described as the full IGDB database.

Rating coverage is incomplete, so rating-based analysis only applies to games with usable rating data.

Reliable rating coverage is much smaller than general rating coverage because many rated games have low rating counts.

PopScore coverage is incomplete, so popularity and visibility analysis should include caveats.

Games can have multiple genres, platforms, themes, game modes, and perspectives, so category counts can overlap.

The chatbot should not claim live access to IGDB.

The chatbot should not invent unsupported game metadata.

The chatbot should redirect actual ranked recommendation needs to `Recommend Me_`.

The LLM provider may be unavailable or rate-limited on free hosting, so fallback answers must remain available.
