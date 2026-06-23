# Definitive Project Guideline  
# IGDB Game Discovery & RAG Recommendation System

**Course:** BUSA 649  
**Team:** QUEST ACCEPTED!  
**Project:** IGDB Game Discovery & RAG Recommendation System  
**Core Positioning:** A four-pillar analytics project that combines an IGDB-powered relational database, exploratory analytics, predictive modeling, hybrid recommendation logic, and a RAG chatbot interface to help users discover games through natural-language preferences.

---

## 1. Project Purpose

This project builds a prototype analytics system for video game discovery and recommendation. The system is designed for users who struggle to find games that match their platform, mood, genre preferences, play style, and subjective “vibe.”

The project should demonstrate the full analytics lifecycle:

1. **Data acquisition** from the IGDB API.
2. **Data engineering** through a structured extraction and relational database pipeline.
3. **Descriptive analytics** to understand the game catalog.
4. **Diagnostic analytics** to uncover patterns behind ratings, popularity, genres, themes, and platforms.
5. **Predictive analytics** to classify or score games based on quality and match potential.
6. **Prescriptive analytics** to recommend games to users.
7. **RAG chatbot interface** to let users ask for games in natural language.
8. **Dashboard/application layer** to present findings, model results, recommendations, and chatbot outputs.

The final project should feel like an end-to-end analytics product, not just a notebook or isolated model.

---

## 2. Business Problem

Modern game discovery is difficult because users face a massive number of available titles across many platforms, genres, publishers, and digital storefronts. Existing recommendation systems often rely on simple metadata filtering, raw popularity, or aggregate ratings.

The project addresses three main problems:

### 2.1 Choice Paralysis

Players have too many options and often do not know where to start. A user may not want “the highest-rated game overall”; they may want something specific, such as:

> “A cozy exploration game on Switch with a relaxing atmosphere and good music.”

Traditional filters are too rigid for this kind of request.

### 2.2 Popularity Bias

Highly popular AAA games often dominate rankings. This can make it harder for niche, indie, older, or mid-market games to be discovered, even when those games are highly rated and relevant to a user’s preferences.

The project should intentionally include a **hidden gem** logic so the recommendation engine does not simply return the most popular titles every time.

### 2.3 Natural-Language Preference Gap

Users naturally describe games using language such as “cozy,” “challenging but not stressful,” “dark fantasy,” “story-rich,” “short sessions,” or “similar to Zelda but more relaxing.” These expressions do not map perfectly to rigid database fields.

The RAG chatbot is included to bridge this gap by retrieving relevant game profiles and generating grounded, explainable recommendations.

---

## 3. Target Users

The target users are casual to moderately engaged gamers who want better game recommendations without needing to manually browse large catalogs.

Primary user types:

| User Type | Need | Example Request |
|---|---|---|
| Casual gamer | Find something enjoyable without doing deep research | “Recommend a relaxing game for tonight.” |
| Platform-constrained user | Find games available on a specific platform | “I only have a Nintendo Switch. What should I play?” |
| Mood-based user | Search by vibe, tone, or experience | “I want a cozy game with exploration and no stress.” |
| Hidden-gem seeker | Discover less obvious but high-quality games | “Give me underrated sci-fi games.” |
| Analytical user | Explore patterns in the game market | “Which genres tend to have higher ratings?” |

---

## 4. Project Objectives

The project has four core objectives.

### Objective 1: Extract, Clean, and Store IGDB Data

Build a repeatable data pipeline that extracts game metadata from the IGDB API, handles pagination and rate limits, stores raw responses, cleans the data, and loads it into a normalized relational database.

Key outputs:

- API extraction scripts
- Raw JSON cache
- Cleaned staging tables
- Normalized SQLite database
- Data quality checks
- ERD

### Objective 2: Analyze the Game Catalog

Use descriptive and diagnostic analytics to understand the structure of the game catalog.

Key outputs:

- Genre distribution analysis
- Platform distribution analysis
- Release trend analysis
- Rating and popularity summaries
- Hidden gem identification
- Genre-theme-platform relationships
- Developer/publisher patterns where feasible

### Objective 3: Build Predictive and Prescriptive Logic

Develop a predictive model and recommendation engine.

Key outputs:

- Feature table for modeling
- High-rated game classifier
- Evaluation metrics such as ROC-AUC, precision, recall, and confusion matrix
- Hybrid recommendation scoring function
- Explainable recommendation outputs

### Objective 4: Build a Dashboard and RAG Chatbot Interface

Create an interactive application that allows users to explore insights and ask for game recommendations in natural language.

Key outputs:

- Streamlit or equivalent app
- Dashboard pages
- RAG chatbot page
- Vector database or vector index
- Grounded recommendation responses
- Evaluation prompt test suite

---

## 5. Scope Definition

Clear scope is important because this project can easily become too large. The MVP should focus on a strong analytics pipeline and recommendation prototype rather than trying to become a full commercial recommender system.

### 5.1 In Scope

The following are core commitments:

- IGDB API data extraction.
- Local raw data caching.
- Relational database design using SQLite.
- Normalized tables for games, genres, themes, platforms, companies, and bridge tables.
- Data cleaning and transformation rules.
- Descriptive analytics dashboard.
- Diagnostic analytics dashboard.
- Predictive model for high-rated game classification.
- Hybrid recommendation engine.
- Game profile document generation for embeddings.
- Vector search for semantic retrieval.
- RAG chatbot that only uses retrieved game context.
- Final report and README documentation.

### 5.2 Out of Scope for MVP

The following should not be treated as required deliverables:

- Live price tracking.
- Price forecasting.
- Steam/Epic marketplace integration.
- User accounts and authentication.
- Persistent personalized user profiles.
- Large-scale collaborative filtering.
- Production-grade cloud architecture.
- Real-time commercial deployment.
- Full recommender retraining based on live user behavior.

### 5.3 Stretch Goals

Only attempt these after the MVP works:

1. **Deployed Web Application**  
   Deploy the app beyond local Streamlit so external users can access it.

2. **User Feedback Loop**  
   Let users rate whether recommendations were relevant, helpful, or poor.

3. **Personalized User Profiles**  
   Store preferred platforms, genres, favorite games, disliked games, and recommendation history.

---

## 6. Guiding Principle: Build the System in Layers

The safest way to complete this project is to build it in layers. Do not start with the chatbot. The chatbot should sit on top of a strong data foundation.

Recommended build order:

1. API extraction works.
2. Raw JSON is stored locally.
3. Core database tables are created.
4. Clean relational data is loaded.
5. Data quality checks pass.
6. Descriptive analytics are completed.
7. Diagnostic analytics are completed.
8. Predictive feature table is created.
9. Predictive model is trained and evaluated.
10. Recommendation scoring function works.
11. Game profile documents are generated.
12. Vector search works.
13. RAG chatbot works.
14. Dashboard integrates all pieces.
15. Final report documents the full system.

---

## 7. Recommended Technical Architecture

```text
IGDB API
   |
   v
Raw JSON Cache
   |
   v
Bronze / Staging Tables
   |
   v
Clean Relational SQLite Database
   |
   +----------------------+
   |                      |
   v                      v
Analytics Tables       Game Profile Documents
   |                      |
   v                      v
Descriptive /          Embeddings + Vector Store
Diagnostic Analysis       |
   |                      v
   v                   RAG Retrieval
Dashboard Pages           |
                          v
Predictive Feature     LLM Response Generation
Table                     |
   |                      v
   v                   Chatbot Interface
ML Model
   |
   v
Recommendation Scoring Engine
   |
   v
Ranked Game Recommendations
```

---

## 8. Data Source: IGDB API

### 8.1 Primary Source

The primary data source is the IGDB API through Twitch Developer authentication.

The API provides game metadata such as:

- Game titles
- Summaries and storylines
- Genres
- Themes
- Platforms
- Release dates
- Ratings
- Rating counts
- Companies
- Involved companies
- Game modes, player perspectives, or keywords if selected

### 8.2 API Extraction Considerations

The extraction pipeline must account for:

- Authentication using client ID and access token.
- Rate limits.
- Pagination.
- Nested JSON structures.
- Many-to-many relationships.
- Missing fields.
- Inconsistent metadata coverage.
- Reproducibility through local caching.

### 8.3 Recommended API Strategy

Do not attempt to extract every IGDB endpoint immediately. Start with the entities needed for the MVP.

Recommended MVP endpoints:

| Endpoint | Purpose | Priority |
|---|---|---|
| games | Core game records | Required |
| genres | Genre lookup table | Required |
| themes | Theme lookup table | Required |
| platforms | Platform lookup table | Required |
| release_dates | Release year/platform availability | Required |
| involved_companies | Link games to companies | Recommended |
| companies | Developer/publisher names | Recommended |
| keywords | More detailed semantic tagging | Optional |
| game_modes | Single-player/multiplayer context | Optional |
| player_perspectives | Useful for recommendation explanation | Optional |

### 8.4 Data Volume Recommendation

For an academic project, extract enough records to support meaningful analysis but not so many that the pipeline becomes unstable.

Recommended target:

- **MVP minimum:** 2,000 to 5,000 games.
- **Better target:** 10,000 to 25,000 games if extraction is stable.
- **Avoid:** attempting to extract the entire IGDB universe before the MVP works.

Prioritize games with enough metadata for analysis and recommendation.

---

## 9. Data Storage Strategy

### 9.1 Raw Layer

Store raw API responses exactly as received.

Recommended folder:

```text
data/raw/igdb/
```

Purpose:

- Reproducibility
- Debugging
- Avoiding repeated API calls
- Recovery if transformation logic changes

Recommended format:

```text
data/raw/igdb/games_batch_001.json
 data/raw/igdb/genres.json
 data/raw/igdb/platforms.json
```

### 9.2 Staging Layer

Convert nested JSON into flatter staging tables.

Recommended folder:

```text
data/interim/
```

Purpose:

- Preserve transformed but not final-clean data.
- Make debugging easier.
- Separate API parsing from final database modeling.

### 9.3 Production Database Layer

Store final normalized relational tables in SQLite.

Recommended path:

```text
data/processed/igdb_games.db
```

Purpose:

- Queryable database for analytics.
- Stable foundation for dashboard, modeling, and RAG profile generation.

### 9.4 Vector Store Layer

Store vector embeddings separately from the relational database.

Recommended path:

```text
data/vector_store/
```

Purpose:

- Semantic search.
- RAG retrieval.
- Natural-language game matching.

---

## 10. Relational Database Design

The database should be normalized because IGDB data contains many-to-many relationships. For example, one game can have multiple genres, and one genre can appear in many games.

### 10.1 Core Tables

Recommended core tables:

| Table | Grain | Description |
|---|---|---|
| games | One row per game | Main game-level metadata |
| genres | One row per genre | Genre lookup table |
| themes | One row per theme | Theme lookup table |
| platforms | One row per platform | Platform lookup table |
| companies | One row per company | Developer/publisher lookup table |
| release_dates | One row per game-platform-release record | Release information |
| involved_companies | One row per game-company relationship | Developer/publisher relationship |

### 10.2 Bridge Tables

Recommended bridge tables:

| Bridge Table | Purpose |
|---|---|
| game_genres | Connect games to genres |
| game_themes | Connect games to themes |
| game_platforms | Connect games to platforms |
| game_keywords | Connect games to keywords, if used |
| game_modes_bridge | Connect games to game modes, if used |
| game_player_perspectives | Connect games to player perspectives, if used |

### 10.3 Suggested `games` Table Fields

| Field | Description |
|---|---|
| game_id | IGDB game ID; primary key |
| name | Game title |
| slug | URL-friendly game name |
| summary | Short description |
| storyline | Longer narrative description, if available |
| first_release_date | Original timestamp/date |
| release_year | Extracted year |
| total_rating | Combined IGDB rating |
| total_rating_count | Number of ratings |
| rating | IGDB user rating, if available |
| rating_count | Number of user ratings |
| aggregated_rating | Critic rating, if available |
| aggregated_rating_count | Number of critic ratings |
| popularity_score | Derived score if available or calculated |
| cover_url | Optional display asset |
| created_at | Extracted/loaded timestamp |
| updated_at | Extracted/loaded timestamp |

### 10.4 Database Integrity Rules

The database should satisfy these rules:

- Every bridge table row must reference a valid game ID.
- Every bridge table row must reference a valid lookup ID.
- No duplicate rows in bridge tables.
- No duplicate primary keys in entity tables.
- Every included game must have a non-empty title.
- Every included game used in platform-specific recommendation must have at least one platform.
- Every rating-dependent analysis must exclude records with missing rating values.
- Every year-based analysis must exclude records with missing release year.

---

## 11. Data Cleaning and Transformation Rules

### 11.1 Required Cleaning Steps

The pipeline should perform the following transformations:

1. Convert Unix timestamps into readable dates.
2. Extract release year from release date.
3. Standardize column names to snake_case.
4. Remove duplicate game records.
5. Remove duplicate bridge table relationships.
6. Flatten nested arrays into bridge tables.
7. Separate lookup tables from game-level tables.
8. Clean empty strings and invalid nulls.
9. Standardize platform, genre, theme, and company names.
10. Create derived fields for modeling and recommendation.

### 11.2 Missing Value Rules

Not all missing values should be treated the same way.

| Field Type | Rule |
|---|---|
| Game title | Required; exclude if missing |
| Game ID | Required; exclude if missing |
| Platform | Required for platform-aware recommendations |
| Genre/theme | Keep if missing, but mark as unknown |
| Summary/storyline | Keep for analytics, but lower usefulness for RAG |
| Rating | Exclude from rating-dependent analysis if missing |
| Rating count | Use for confidence weighting where available |
| Release year | Exclude from release trend analysis if missing |

### 11.3 Game Inclusion Rules

Recommended inclusion rules for the clean analytical dataset:

A game can be included if it has:

- A valid `game_id`.
- A non-empty `name`.
- At least one usable metadata field beyond the title.

For recommendation and RAG use, a game should ideally have:

- Name
- Summary or storyline
- At least one genre, theme, platform, or keyword

For predictive modeling, a game should have:

- Target variable availability, such as `total_rating`
- Sufficient features for prediction

---

## 12. Analytics Framework: Four Pillars

The project should explicitly organize analysis around the four pillars: descriptive, diagnostic, predictive, and prescriptive analytics.

---

## 13. Descriptive Analytics

### Main Question

> What does the game catalog look like?

### Purpose

Descriptive analytics summarizes the structure of the dataset and helps the audience understand the catalog before deeper analysis.

### Recommended Analyses

1. Number of games collected.
2. Number of platforms represented.
3. Number of genres and themes.
4. Games by release year.
5. Games by platform.
6. Games by genre.
7. Games by theme.
8. Rating distribution.
9. Rating count distribution.
10. Top developers/publishers by number of games.
11. Share of games with missing ratings.
12. Share of games with missing summaries/storylines.

### Recommended Visuals

| Visual | Purpose |
|---|---|
| Bar chart: top genres | Show catalog composition |
| Bar chart: top platforms | Show platform coverage |
| Line chart: games by release year | Show release trends |
| Histogram: ratings | Show rating distribution |
| Histogram: rating counts | Show popularity skew |
| Missingness heatmap/table | Show data quality limitations |

### Suggested Dashboard Page

**Page Name:** Catalog Overview

Components:

- KPI cards: total games, total genres, total platforms, total companies.
- Release trend chart.
- Genre distribution chart.
- Platform distribution chart.
- Rating summary chart.
- Data quality summary.

---

## 14. Diagnostic Analytics

### Main Question

> Why do certain games, genres, platforms, or themes perform better than others?

### Purpose

Diagnostic analytics explores patterns and relationships behind game ratings, popularity, and catalog structure.

### Recommended Analyses

1. Average rating by genre.
2. Average rating by theme.
3. Average rating by platform.
4. Rating versus rating count.
5. Popularity bias analysis.
6. Hidden gem identification.
7. Genre-theme combinations associated with higher ratings.
8. Platform catalog differences.
9. Company/developer performance patterns where data quality supports it.
10. Missing metadata patterns by genre, platform, or release year.

### Hidden Gem Definition

A practical hidden gem definition should balance quality and low visibility.

Recommended MVP rule:

A game is a hidden gem if:

- `total_rating >= 80`
- `total_rating_count` is below a selected popularity threshold
- The game has enough metadata to be recommended

Possible threshold options:

| Threshold Type | Example |
|---|---|
| Fixed count threshold | total_rating_count < 500 |
| Percentile threshold | total_rating_count below 40th percentile |
| Hybrid threshold | rating >= 80 and rating_count between minimum confidence and low-popularity ceiling |

Recommended final approach:

Use a **percentile-based popularity threshold**, because rating count distributions are usually highly skewed.

Example:

```text
hidden_gem = total_rating >= 80 AND total_rating_count >= minimum_confidence_count AND total_rating_count <= 40th percentile
```

This avoids calling a game a hidden gem if only one person rated it.

### Recommended Visuals

| Visual | Purpose |
|---|---|
| Scatter plot: rating vs rating count | Show quality vs popularity |
| Boxplot: rating by genre | Compare genre performance |
| Bar chart: hidden gems by genre | Surface niche areas |
| Heatmap: genre-theme average rating | Show interaction patterns |
| Table: top hidden gems | Provide actionable examples |

### Suggested Dashboard Page

**Page Name:** Hidden Gems & Rating Drivers

Components:

- Hidden gem filter controls.
- Rating vs popularity scatter plot.
- Top hidden gems table.
- Genre/theme performance summary.
- Explanatory notes about data limitations.

---

## 15. Predictive Analytics

### Main Question

> Can we predict whether a game is likely to be highly rated or relevant to a user’s preferences?

### Purpose

Predictive analytics should show that the project can move beyond describing the catalog and estimate game quality or match potential using structured metadata.

### 15.1 Target Variable

Recommended target:

```text
high_rated = 1 if total_rating >= 80 else 0
```

Only include games with valid `total_rating` in the supervised model.

### 15.2 Feature Engineering

Recommended features:

| Feature Type | Examples |
|---|---|
| Release features | release_year, game_age |
| Platform features | number_of_platforms, platform flags |
| Genre features | one-hot encoded genres |
| Theme features | one-hot encoded themes |
| Company features | developer/publisher indicators if reliable |
| Popularity features | rating_count, log_rating_count |
| Text features | summary length, storyline availability, optional embeddings |
| Metadata completeness | has_summary, has_storyline, num_genres, num_themes |

### 15.3 Model Choices

Use simple, explainable models first.

Recommended baseline models:

1. Logistic Regression
2. Random Forest
3. Gradient Boosting / XGBoost if time allows

Recommended final model selection criteria:

- Strong enough performance.
- Easy to explain.
- Compatible with available time.
- Does not dominate the whole project.

### 15.4 Train/Test Strategy

Recommended split:

- 70% training
- 15% validation
- 15% test

Alternative:

- 80% training
- 20% test with cross-validation

Important considerations:

- Use stratified split because the target may be imbalanced.
- Do not evaluate only with accuracy.
- Compare against a simple baseline.

### 15.5 Evaluation Metrics

Recommended metrics:

| Metric | Why It Matters |
|---|---|
| ROC-AUC | Measures ranking ability across thresholds |
| Precision | Important when recommending high-rated games |
| Recall | Measures ability to capture high-rated games |
| F1-score | Balances precision and recall |
| Confusion matrix | Easy to explain to non-technical audience |
| Feature importance | Helps interpret drivers |

Target:

```text
ROC-AUC >= 0.70
```

This is a reasonable academic target, but if the data does not support it, document why.

### 15.6 Model Interpretation

Include interpretation such as:

- Which genres are associated with higher predicted quality?
- Does platform coverage matter?
- Does metadata completeness influence prediction?
- Does rating count correlate with predicted high-rating probability?

### 15.7 Predictive Limitations

Document clearly:

- Ratings are not perfect measures of quality.
- IGDB data may have missing or biased ratings.
- Popular games may have more complete metadata.
- The model predicts historical rating patterns, not personal enjoyment.
- The classifier should support recommendation, not replace user preference matching.

---

## 16. Prescriptive Analytics and Recommendation Engine

### Main Question

> What game should the user play, explore, or save next?

### Purpose

Prescriptive analytics turns analysis into action by recommending games based on user preferences.

### 16.1 Recommendation Engine Design

The engine should combine:

1. **Hard filters**  
   Requirements that must be satisfied.

2. **Soft scores**  
   Preferences that improve ranking but do not necessarily exclude a game.

3. **Semantic similarity**  
   Natural-language match between user prompt and game profile.

4. **Quality score**  
   Rating-based or model-based quality signal.

5. **Hidden gem adjustment**  
   Boosts relevant, high-quality, lower-popularity games.

### 16.2 Hard Filters

Examples:

- Platform must match if user specifies platform.
- Exclude games with insufficient metadata for chatbot explanation.
- Exclude games below a minimum rating if user asks for “highly rated.”
- Exclude games outside a release year range if user specifies one.

### 16.3 Soft Matching Signals

Examples:

- Genre match
- Theme match
- Keyword match
- Similarity to user prompt
- Rating score
- Predicted high-rated probability
- Hidden gem boost
- Popularity confidence

### 16.4 Suggested Scoring Formula

A simple MVP scoring formula:

```text
final_score =
    0.40 * semantic_similarity
  + 0.20 * genre_theme_match_score
  + 0.15 * normalized_rating_score
  + 0.10 * predicted_quality_score
  + 0.10 * platform_match_score
  + 0.05 * hidden_gem_boost
```

This formula can be adjusted after testing.

### 16.5 Score Components

| Component | Description |
|---|---|
| semantic_similarity | Similarity between user prompt and game profile embedding |
| genre_theme_match_score | Structured match on extracted genres/themes |
| normalized_rating_score | Rating scaled from 0 to 1 |
| predicted_quality_score | Model probability that game is high-rated |
| platform_match_score | 1 if matched, 0 if not, or filtered out if required |
| hidden_gem_boost | Small boost for high-quality lower-popularity games |

### 16.6 Recommendation Output Format

Each recommendation should include:

- Game title
- Rank
- Match score
- Available platform(s), if available
- Genre(s)
- Theme(s)
- Rating and rating count, if available
- Short explanation
- Reason it matched the user prompt
- Caveat if data is missing

Example format:

```text
1. Outer Wilds
   Why it matches: Strong semantic match for exploration, mystery, and sci-fi themes.
   Evidence: Adventure genre, sci-fi theme, strong rating profile.
   Caveat: Platform availability depends on IGDB metadata completeness.
```

---

## 17. RAG Chatbot Design

### 17.1 Purpose

The chatbot allows users to describe their preferences in natural language and receive grounded recommendations based on retrieved IGDB game profiles.

The chatbot should not act as a general gaming encyclopedia. It should only answer based on the project dataset and retrieved context.

### 17.2 Game Profile Document Creation

Each game should be converted into a text profile for embedding.

Recommended format:

```text
Title: [game name]
Genres: [genres]
Themes: [themes]
Platforms: [platforms]
Release Year: [year]
Rating: [total_rating]
Rating Count: [total_rating_count]
Developer/Publisher: [companies if available]
Summary: [summary]
Storyline: [storyline if available]
```

### 17.3 Embedding Strategy

Recommended MVP:

- Use open-source sentence-transformers for embeddings.
- Store embeddings in a local vector database or FAISS/Chroma index.

Potential alternative:

- Use Gemini embeddings if needed and feasible.

### 17.4 Retrieval Strategy

When a user submits a prompt:

1. Parse the prompt.
2. Apply hard filters if obvious, such as platform.
3. Embed the prompt.
4. Retrieve top-k similar game profiles.
5. Apply hybrid recommendation scoring.
6. Pass the top results as context to the LLM.
7. Generate grounded recommendations.

Recommended top-k:

```text
Retrieve top 20 candidates → rerank → send top 5 to 8 to chatbot context
```

### 17.5 RAG Guardrails

The chatbot must follow these rules:

- Only recommend games included in retrieved context.
- Do not invent platforms, ratings, developers, or summaries.
- If metadata is missing, say it is missing.
- If no good match is found, say so and suggest how the user can broaden the request.
- Explain recommendations using available game metadata.
- Avoid claiming that a game is available on a platform unless the dataset supports it.

### 17.6 Example Chatbot System Rule

```text
You are a game recommendation assistant. You must answer only using the retrieved game profiles provided in the context. Do not invent game titles, platforms, ratings, developers, or story details. If the context does not contain enough evidence to answer, say that the dataset does not contain a strong match and ask the user to broaden or clarify their request. For every recommendation, explain why it matches the user's request using only the supplied metadata.
```

### 17.7 Chatbot Evaluation

Create a test suite of at least 50 prompts covering different scenarios:

| Prompt Type | Example |
|---|---|
| Platform-specific | “Recommend a good RPG on Nintendo Switch.” |
| Vibe-based | “I want a cozy game with exploration.” |
| Genre-specific | “Give me a tactical strategy game.” |
| Hidden gem | “Find me an underrated indie game.” |
| Constraint-heavy | “I want a short, relaxing sci-fi game on PC.” |
| Ambiguous | “I want something fun.” |
| No-match | “Find me a racing game for a platform not in the data.” |
| Similarity-based | “Something like Hollow Knight but less stressful.” |

Evaluate:

- Is the answer grounded?
- Are all recommended games from retrieved context?
- Are platforms correct?
- Are ratings correct?
- Is the explanation relevant?
- Did the chatbot avoid hallucination?

---

## 18. Dashboard and User Interface

### 18.1 MVP Interface

Streamlit is recommended for the MVP because it is fast to build and suitable for analytics projects. A custom deployed website can be a stretch goal, but it should not delay the core analytics deliverables.

### 18.2 Recommended App Pages

| Page | Purpose |
|---|---|
| Home | Explain project, data source, and system flow |
| Catalog Overview | Descriptive analytics |
| Hidden Gems & Diagnostics | Diagnostic analytics |
| Predictive Model | Model performance and interpretation |
| Recommendation Engine | Structured recommendation filters and ranked results |
| RAG Chatbot | Natural-language game discovery |
| Data Quality | Missingness, coverage, limitations |

### 18.3 Home Page Content

Include:

- Project title
- One-sentence value proposition
- Architecture diagram or pipeline summary
- Dataset size
- Key features
- Navigation instructions

### 18.4 Catalog Overview Page

Include:

- Total games
- Total platforms
- Total genres
- Total themes
- Games by year
- Top platforms
- Top genres
- Rating distribution

### 18.5 Hidden Gems Page

Include:

- Hidden gem definition
- Adjustable rating threshold
- Adjustable popularity threshold
- Hidden gem table
- Rating vs rating count scatter plot
- Genre/theme breakdown

### 18.6 Predictive Model Page

Include:

- Target definition
- Model selected
- ROC-AUC
- Precision/recall/F1
- Confusion matrix
- Feature importance
- Interpretation
- Limitations

### 18.7 Recommendation Page

Include:

- Platform selector
- Genre selector
- Theme selector
- Rating preference
- Hidden gem toggle
- Top-N slider
- Ranked recommendation output

### 18.8 RAG Chatbot Page

Include:

- Text input box
- Example prompts
- Chatbot response
- Retrieved game evidence if possible
- Disclaimer that responses are grounded in project dataset

---

## 19. Business Rules

Business rules keep the project consistent and defensible.

### 19.1 Game Inclusion Rules

- Include only records with valid game ID and name.
- Exclude games from analysis if the required field for that analysis is missing.
- Keep missing metadata visible rather than silently pretending it exists.

### 19.2 Rating Rules

- Use `total_rating` as the primary quality rating when available.
- Define high-rated games as `total_rating >= 80`.
- Exclude missing ratings from supervised rating classification.
- Use rating count to represent confidence or popularity.

### 19.3 Hidden Gem Rules

A hidden gem must satisfy:

- High rating.
- Sufficient rating count to avoid unreliable one-off ratings.
- Lower popularity relative to the dataset.
- Enough metadata to explain the recommendation.

### 19.4 Platform Matching Rules

- If a user specifies a platform, recommendations must be available on that platform according to the dataset.
- If platform metadata is missing, do not claim platform availability.
- If no platform match exists, return no strong match rather than inventing results.

### 19.5 Recommendation Rules

- Recommendations must be ranked by a documented scoring formula.
- Every recommendation should include a reason.
- Hidden gem boost should not override basic relevance.
- Very popular games can still be recommended if they strongly match the user request.
- Recommendations should balance quality, relevance, and discovery.

### 19.6 Chatbot Rules

- The chatbot must only use retrieved context.
- The chatbot must not fabricate unsupported metadata.
- The chatbot should disclose missing data when relevant.
- The chatbot should ask users to broaden or clarify when no good match exists.

---

## 20. Evaluation Plan

Evaluation should cover the full system, not only the machine learning model.

### 20.1 Data Quality Evaluation

Checks:

- Primary key uniqueness.
- Foreign key integrity.
- Duplicate bridge rows.
- Missing required fields.
- Number of records by table.
- Missingness by important field.
- Valid rating ranges.
- Valid release years.

Deliverable:

```text
notebooks/01_data_quality_checks.ipynb
```

or

```text
src/validation/data_quality_checks.py
```

### 20.2 Database Evaluation

Checks:

- Every `game_genres.game_id` exists in `games`.
- Every `game_genres.genre_id` exists in `genres`.
- Same for platforms, themes, companies, and release dates.
- ERD accurately reflects implemented tables.

### 20.3 Predictive Model Evaluation

Report:

- Baseline performance.
- Final model performance.
- ROC-AUC.
- Precision, recall, F1.
- Confusion matrix.
- Feature importance.
- Model limitations.

### 20.4 Recommendation Engine Evaluation

Use manually designed test cases.

Evaluate:

- Does the result match the platform constraint?
- Does the result match genre/theme intent?
- Are hidden gems actually surfaced when requested?
- Are recommendations explainable?
- Are recommendations too popularity-biased?

### 20.5 RAG Chatbot Evaluation

Use a 50-prompt test suite.

Track:

| Metric | Target |
|---|---|
| Grounded responses | At least 90% |
| Unsupported metadata errors | As low as possible; all documented |
| Retrieved-context recommendation rate | 100% |
| Clear no-match handling | 100% for no-match prompts |
| Explanation relevance | Qualitative rating |

### 20.6 Dashboard Evaluation

Assess:

- Are pages easy to navigate?
- Are charts readable?
- Are definitions clear?
- Are limitations visible?
- Can users understand how recommendations are generated?

---

## 21. Success Metrics

| Metric | Definition | Target | Measurement |
|---|---|---|---|
| Data Quality & Integrity | Valid schema, no orphaned relationships, required fields respected | 100% relationship integrity | SQL assertion scripts |
| Predictive Model Performance | Ability to classify high-rated games | ROC-AUC >= 0.70 | Holdout test or cross-validation |
| Recommendation Speed | Time to retrieve and rank recommendations | < 2 seconds excluding LLM response | Execution logs |
| Chatbot Grounding Accuracy | Responses do not include unsupported metadata | >= 90% grounded responses | Manual 50-prompt evaluation |
| Dashboard Completeness | All four pillars represented | 100% required pages completed | Final review checklist |
| Documentation Quality | README and report explain reproducibility | Complete setup and usage instructions | Reviewer can run project locally |

---

## 22. Technical Stack

### 22.1 Core Stack

| Component | Tool |
|---|---|
| Programming language | Python |
| API extraction | requests / httpx |
| Data manipulation | pandas, numpy |
| Database | SQLite |
| SQL querying | sqlite3 / SQLAlchemy |
| Visualization | matplotlib, plotly, Streamlit charts |
| Machine learning | scikit-learn |
| Embeddings | sentence-transformers or Gemini embeddings |
| Vector store | FAISS or Chroma |
| Chatbot/RAG | Custom retrieval + LLM call |
| App | Streamlit MVP |
| Version control | GitHub |
| Documentation | Markdown README and final report |

### 22.2 Recommended Environment Files

Include:

```text
requirements.txt
.env.example
README.md
```

Do not commit real API keys.

---

## 23. Recommended Repository Structure

```text
igdb-game-discovery-rag/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── data/
│   ├── raw/
│   │   └── igdb/
│   ├── interim/
│   ├── processed/
│   │   └── igdb_games.db
│   └── vector_store/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_quality_checks.ipynb
│   ├── 03_descriptive_diagnostic_analysis.ipynb
│   ├── 04_predictive_modeling.ipynb
│   └── 05_recommendation_testing.ipynb
│
├── src/
│   ├── config.py
│   ├── api/
│   │   ├── igdb_client.py
│   │   └── extract_igdb.py
│   ├── database/
│   │   ├── create_schema.py
│   │   ├── load_database.py
│   │   └── queries.py
│   ├── transformation/
│   │   ├── clean_games.py
│   │   ├── normalize_entities.py
│   │   └── build_feature_tables.py
│   ├── validation/
│   │   └── data_quality_checks.py
│   ├── analytics/
│   │   ├── descriptive.py
│   │   └── diagnostic.py
│   ├── modeling/
│   │   ├── train_model.py
│   │   ├── evaluate_model.py
│   │   └── predict_quality.py
│   ├── recommender/
│   │   ├── scoring.py
│   │   ├── recommend.py
│   │   └── explanations.py
│   ├── rag/
│   │   ├── build_profiles.py
│   │   ├── build_embeddings.py
│   │   ├── retrieve.py
│   │   └── chatbot.py
│   └── app/
│       ├── streamlit_app.py
│       └── pages/
│           ├── 1_catalog_overview.py
│           ├── 2_hidden_gems.py
│           ├── 3_predictive_model.py
│           ├── 4_recommendations.py
│           └── 5_rag_chatbot.py
│
├── reports/
│   ├── figures/
│   ├── final_report.md
│   └── final_report.pdf
│
├── docs/
│   ├── project_guideline.md
│   ├── data_dictionary.md
│   ├── erd.png
│   ├── business_rules.md
│   └── evaluation_plan.md
│
└── tests/
    ├── test_data_quality.py
    ├── test_recommender.py
    └── test_rag_grounding.py
```

---

## 24. Team Roles and Ownership

Because this is a two-person team, each person should own a primary domain and be backup for the other.

| Team Member | Primary Ownership | Backup Ownership |
|---|---|---|
| Calvin | Data engineering, API pipeline, database, RAG/NLP | Analytics, modeling, dashboard |
| Faye | Analytics, modeling, dashboard, UX | Data engineering, RAG/NLP |

### 24.1 Practical Work Split

Recommended division:

#### Calvin

- IGDB API connection.
- Rate-limit-safe extraction.
- Raw JSON caching.
- SQLite database schema.
- Database loading.
- RAG profile generation.
- Vector search setup.
- Chatbot guardrails.

#### Faye

- Descriptive analysis.
- Diagnostic analysis.
- Hidden gem logic.
- Predictive modeling.
- Model evaluation visuals.
- Streamlit dashboard layout.
- Recommendation result presentation.

#### Shared

- Business rules.
- Recommendation scoring formula.
- Final report.
- README.
- Testing.
- Final presentation/demo.

---

## 25. Timeline and Milestones

The proposal uses an 8-week plan. The following version adds more specific milestones.

| Week | Main Focus | Expected Output |
|---|---|---|
| Week 1 | Define scope, finalize endpoints, set up GitHub | Final scope, repo, `.env.example`, endpoint list |
| Week 2 | API extraction and raw data caching | Working IGDB extraction script, raw JSON saved |
| Week 3 | Database schema, cleaning, normalization | SQLite database, normalized tables, ERD draft |
| Week 4 | Descriptive and diagnostic analytics | Catalog dashboard visuals, hidden gem logic |
| Week 5 | Predictive model and feature table | Trained model, evaluation metrics, feature importance |
| Week 6 | Recommendation engine and vector store | Hybrid scoring, embeddings, retrieval working |
| Week 7 | RAG chatbot and dashboard integration | Streamlit app with chatbot and analytics pages |
| Week 8 | Testing, validation, report, demo polish | Final report, README, test results, final demo |

---

## 26. Risk Management

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Missing IGDB fields | Medium | Medium | Use documented inclusion rules and show missingness analysis |
| API rate limits | Medium | Low/Medium | Add rate limiting, backoff, and raw JSON caching |
| Ratings are sparse or biased | High | Medium | Filter rating-based analysis and document limitations |
| Popularity bias | High | Medium | Add hidden gem boost and percentile-based popularity logic |
| RAG hallucination | Medium | High | Use strict context-only prompt and manual grounding evaluation |
| Scope creep | High | High | Treat deployment, profiles, and feedback as stretch goals only |
| Predictive model underperforms | Medium | Medium | Include baseline, explain limitations, emphasize full analytics system |
| Dashboard integration delays | Medium | Medium | Build simple pages early; polish after core logic works |
| Team bottlenecks | Medium | Medium | Use clear ownership and weekly integration checkpoints |

---

## 27. Final Deliverables

The final submission should include:

| Deliverable | Description | Format |
|---|---|---|
| API ingestion pipeline | Scripts to extract and cache IGDB data | `.py` |
| Clean database | Normalized SQLite database | `.db` |
| ERD | Database entity relationship diagram | `.png` or `.pdf` |
| Data dictionary | Explanation of tables and fields | `.md` |
| Descriptive analytics | Catalog overview and summary visuals | Dashboard / notebook |
| Diagnostic analytics | Hidden gems and rating relationship analysis | Dashboard / notebook |
| Predictive model | High-rated game classifier | `.py`, notebook, model file |
| Recommendation engine | Hybrid scoring and ranked outputs | `.py` |
| RAG chatbot | Natural-language grounded recommender | Streamlit page / `.py` |
| Dashboard/app | Integrated user interface | Streamlit app |
| Evaluation test suite | Data, model, recommendation, and RAG validation | `.md`, `.py`, notebook |
| Final report | Full methodology, findings, limitations, future work | `.md` / `.pdf` |
| README | Reproducibility and usage instructions | `.md` |

---

## 28. Final Report Structure

Recommended final report outline:

```text
1. Executive Summary
2. Business Problem
3. Project Objectives and Scope
4. Data Source and Data Collection
5. Data Architecture and Relational Database Design
6. Data Cleaning and Business Rules
7. Descriptive Analytics
8. Diagnostic Analytics
9. Predictive Analytics
10. Prescriptive Recommendation Engine
11. RAG Chatbot Design
12. Dashboard / Application Design
13. Evaluation and Validation
14. Risks, Limitations, and Ethical Considerations
15. Future Improvements
16. Conclusion
17. Appendix
```

---

## 29. README Structure

The README should allow someone else to understand and run the project.

Recommended README outline:

```text
# IGDB Game Discovery & RAG Recommendation System

## Project Overview
## Business Problem
## Features
## Architecture
## Data Source
## Setup Instructions
## Environment Variables
## How to Run the Pipeline
## How to Build the Database
## How to Train the Model
## How to Run the Streamlit App
## Project Structure
## Evaluation Summary
## Known Limitations
## Team Members
```

---

## 30. MVP Acceptance Checklist

Use this checklist to know whether the project is complete enough.

### Data Engineering

- [ ] IGDB API extraction works.
- [ ] API keys are stored safely in `.env`.
- [ ] Raw JSON is cached locally.
- [ ] Data is cleaned and normalized.
- [ ] SQLite database is created.
- [ ] ERD is completed.
- [ ] Data quality checks are documented.

### Analytics

- [ ] Descriptive analytics answer “What does the catalog look like?”
- [ ] Diagnostic analytics answer “Why do patterns exist?”
- [ ] Hidden gem logic is defined and implemented.
- [ ] Visualizations are clear and interpretable.

### Predictive Modeling

- [ ] Target variable is defined.
- [ ] Feature table is built.
- [ ] Baseline model is included.
- [ ] Final model is evaluated.
- [ ] ROC-AUC, precision, recall, and F1 are reported.
- [ ] Limitations are documented.

### Recommendation Engine

- [ ] Hard filters work.
- [ ] Hybrid score is implemented.
- [ ] Ranking logic is documented.
- [ ] Recommendation explanations are generated.
- [ ] Hidden gem boost does not overpower relevance.

### RAG Chatbot

- [ ] Game profiles are generated.
- [ ] Embeddings are created.
- [ ] Vector retrieval works.
- [ ] Chatbot uses retrieved context only.
- [ ] No-match behavior is implemented.
- [ ] 50-prompt evaluation is completed.

### Dashboard

- [ ] Home page exists.
- [ ] Catalog overview page exists.
- [ ] Hidden gems/diagnostic page exists.
- [ ] Predictive model page exists.
- [ ] Recommendation page exists.
- [ ] RAG chatbot page exists.

### Documentation

- [ ] README is complete.
- [ ] Final report is complete.
- [ ] Data dictionary is complete.
- [ ] Business rules are documented.
- [ ] Evaluation results are documented.
- [ ] Risks and limitations are documented.

---

## 31. Final Positioning Statement

Use this as the clean final framing for the project:

> This project builds a four-pillar analytics system for video game discovery using IGDB data. It combines a relational database, descriptive and diagnostic analysis, predictive quality modeling, prescriptive hybrid recommendations, and a RAG chatbot interface to help users find games based on natural-language preferences. The system is designed to reduce choice paralysis, surface hidden gems, and provide explainable, dataset-grounded recommendations.

---

## 32. Final Advice for Execution

The strongest version of this project is not the one with the most features. It is the one where the full pipeline works clearly from beginning to end.

Prioritize this order:

1. Working data pipeline.
2. Clean database.
3. Clear analytics.
4. Simple but defensible model.
5. Transparent recommendation logic.
6. Grounded chatbot.
7. Clean dashboard.
8. Strong documentation.

Avoid spending too much time on deployment, advanced UI, or user profiles before the MVP is complete. Those are good portfolio extensions, but they should not compromise the core academic project.
