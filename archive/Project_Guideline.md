# Project Guidelines: IGDB Game Discovery & RAG Recommendation System

## 1. Project Overview

Define the project purpose, target users, and high-level value proposition.

Main idea:

> Build a game discovery and recommendation system using IGDB data, four pillars of analytics, and a RAG-based chatbot interface.

---

## 2. Business Problem

Discuss the problem your project is solving.

Major points:

- Game discovery is difficult because users have too many choices.
- Ratings and popularity alone do not capture user preference.
- Users often describe games by “vibe,” mood, platform, genre, or play style.
- The project helps users find better game matches through analytics and natural language.

---

## 3. Project Objectives

Define what the project aims to accomplish.

Major objectives:

- Collect game metadata from the IGDB API.
- Build a structured relational database.
- Analyze the game catalog using the four pillars of analytics.
- Build a recommendation engine.
- Use natural language input to support game discovery.
- Create a RAG chatbot as the user-facing interface.
- Provide explainable recommendations.

---

## 4. Data Source and API Scope

Discuss where the data comes from and what will be collected.

Major topics:

- IGDB API as the primary data source.
- API authentication and rate limits.
- Selected endpoints to extract.
- Raw data storage.
- Data quality considerations.
- API extraction boundaries and limitations.

---

## 5. Data Architecture

Explain how data flows through the project.

Major layers:

- Raw API data
- Bronze/staging layer
- Clean relational database
- Analytics-ready tables
- Machine learning feature tables
- Vector database for RAG
- Dashboard/chatbot application layer

---

## 6. Relational Database Design

Discuss how the IGDB data will be structured.

Major topics:

- Core entities
- Lookup tables
- Bridge tables
- Primary keys and foreign keys
- Many-to-many relationships
- Database normalization
- ERD design
- Data integrity rules

---

## 7. Data Cleaning and Transformation

Discuss how raw API data becomes usable.

Major topics:

- Handling missing values
- Removing duplicates
- Converting timestamps
- Standardizing names and IDs
- Flattening nested fields
- Creating bridge tables
- Filtering irrelevant game records
- Preparing analytics-ready datasets

---

## 8. Four Pillars of Analytics

Organize the project around the four analytics pillars.

### 8.1 Descriptive Analytics

Major topics:

- Game catalog overview
- Genre distribution
- Platform distribution
- Release trends
- Rating summaries
- Popularity summaries
- Company/developer summaries

Main question:

> What does the game catalog look like?

---

### 8.2 Diagnostic Analytics

Major topics:

- Rating differences across genres
- Platform catalog differences
- Popularity versus rating analysis
- Hidden gem identification
- Genre-theme relationships
- Developer/publisher performance patterns
- Factors associated with game quality or popularity

Main question:

> Why do certain games, genres, or platforms perform better than others?

---

### 8.3 Predictive Analytics

Major topics:

- Predicting whether a game is highly rated
- Predicting user-game match score
- Feature engineering
- Model selection
- Model evaluation
- Model interpretation
- Predictive limitations

Main question:

> What games are likely to be high-quality or match the user’s preferences?

---

### 8.4 Prescriptive Analytics

Major topics:

- Game recommendation engine
- Ranked recommendation outputs
- Platform-aware recommendations
- Hidden gem recommendations
- Similar game recommendations
- Recommendation explanations
- User decision support

Main question:

> What game should the user play, explore, or save next?

---

## 9. Recommendation Engine Design

Discuss how recommendations will be generated.

Major topics:

- User preference extraction
- Genre matching
- Theme matching
- Platform filtering
- Rating and popularity scoring
- Semantic similarity
- Hybrid recommendation score
- Ranking logic
- Explanation logic

---

## 10. RAG Chatbot Interface

Discuss how the chatbot supports the system.

Major topics:

- Natural-language user input
- Game profile document creation
- Embedding generation
- Vector database storage
- Retrieval process
- Context grounding
- Response generation
- Recommendation explanation
- Chatbot limitations and guardrails

---

## 11. Dashboard and User Interface

Discuss how users will interact with the project.

Major components:

- Analytics dashboard
- Game catalog exploration page
- Genre/platform analysis page
- Hidden gem analysis page
- Predictive model results page
- Chatbot recommendation page

---

## 12. Business Rules

Define project rules that keep outputs consistent.

Major topics:

- Game inclusion and exclusion rules
- Minimum data quality thresholds
- Platform matching rules
- Rating threshold rules
- Hidden gem scoring rules
- Recommendation ranking rules
- Chatbot grounding rules
- No unsupported claims outside the dataset

---

## 13. Evaluation Plan

Discuss how project quality will be measured.

Major areas:

- Data quality validation
- Database integrity checks
- Model performance evaluation
- Recommendation relevance testing
- Chatbot response evaluation
- User prompt test cases
- Dashboard usability review

---

## 14. Technical Stack

Discuss the tools used.

Major components:

- Python
- IGDB API
- pandas
- SQL database
- scikit-learn
- Vector database
- Embedding model
- RAG framework or custom RAG logic
- Streamlit or dashboard tool
- GitHub

---

## 15. Project Deliverables

List the final outputs.

Major deliverables:

- API extraction pipeline
- Clean relational database
- ERD
- Analytics-ready datasets
- Four-pillar analysis
- Predictive model
- Recommendation engine
- RAG chatbot
- Dashboard or app
- Final report
- README documentation

---

## 16. Project Scope

Clarify what is included and excluded.

Included:

- IGDB-based game discovery
- Four-pillar analytics
- Relational database
- Recommendation engine
- RAG chatbot
- Explainable recommendations

Excluded or future work:

- Live price tracking
- Price forecasting
- User account system
- Real-time production deployment
- Full collaborative filtering
- Large-scale commercial recommender system

---

## 17. Risks and Limitations

Discuss potential challenges.

Major topics:

- IGDB data completeness
- Missing ratings or metadata
- API rate limits
- Recommendation bias toward popular games
- Natural language ambiguity
- Limited user feedback data
- RAG hallucination risk
- Price data not available from IGDB

---

## 18. Future Improvements

Discuss possible extensions.

Major ideas:

- Add Steam or price data
- Add price history and buy-now recommendation
- Add user feedback loop
- Add collaborative filtering
- Add advanced NLP preference parsing
- Add deployment
- Add more personalized recommendations
- Add watchlist functionality

---

## 19. Final Project Positioning

Use this as the clean final framing:

> This project builds a four-pillar analytics system for video game discovery using IGDB data. It combines a relational database, descriptive and diagnostic analysis, predictive match scoring, prescriptive recommendations, and a RAG chatbot interface to help users find games based on natural-language preferences.