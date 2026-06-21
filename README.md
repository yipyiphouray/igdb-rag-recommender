# IGDB Game Discovery and Recommender (WIP)
An advanced video game discovery and recommendation platform. This system integrates a cleaned relational database of IGDB (Internet Game Database) metadata, a four-pillar analytics pipeline, and a Retrieval-Augmented Generation (RAG) conversational chatbot to help players find games matching their unique "vibe," platform, and playstyle.

## 🚀 Key Features

Data Normalization: Automates extraction from the IGDB API into a fully normalized, local SQLite database.

Four Pillars of Analytics:

- Descriptive: Visualizes the gaming landscape (genres, platform share, developer networks).

- Diagnostic: Explores game quality metrics and isolates "hidden gems" (highly-rated, low-popularity titles).

- Predictive: Classifies whether games are likely to be highly-rated based on metadata features.

- Prescriptive: Leverages a hybrid recommendation engine combining strict metadata filters with semantic similarity.

Conversational RAG Chatbot: Utilizes vector embeddings to parse natural language queries (e.g., "I want a cozy, low-stress sci-fi game on Nintendo Switch") and returns grounded, explainable game suggestions.

Interactive Dashboard: A multi-page Streamlit UI hosting the analytics, model evaluation metrics, and the chatbot interface.

## 🛠️ Technical Stack

- Language: Python 3.9+

- Data & Storage: pandas, SQLite, ChromaDB / FAISS (Vector Database)

- Modeling & RAG: scikit-learn, Gemini 2.5 API (or open-source sentence-transformers)

- Front-End: Streamlit

- Source API: Twitch Developer / IGDB API

## 📁 Project Structure

├── archive/
│   └── Project_Guideline.md       # Original guidelines archive
├── data/
│   └── raw/                       # Raw JSON metadata schemas from IGDB API
│       ├── companies.json
│       ├── covers.json
│       ├── external_games.json
│       ├── game_modes.json
│       ├── games.json
│       ├── genres.json
│       ├── involved_companies.json
│       ├── keywords.json
│       ├── platforms.json
│       ├── player_perspectives.json
│       ├── release_dates.json
│       ├── screenshots.json
│       └── themes.json
├── docs/                          # Project contextual design documentations
│   ├── definitive_project_guideline_igdb_rag.md
│   ├── folder_structure.md
│   └── IGDB_context.md
├── src/                           # Source scripts directory
│   ├── API_Connection_Test.py     # Connection testing module for credentials
│   ├── config.py                  # API config and credential loader
│   ├── fetch_IGDB.py              # Main raw endpoint retrieval pipeline
│   └── query_test.py              # Local testing suite for parsing metadata
├── .env.example                   # Dummy environment credential keys configuration
├── .gitignore                     # Git configuration ignore file
├── LICENSE                        # Project licensing terms
├── README.md                      # Primary project documentation hub
└── requirement.txt                # Python installation dependency packages


## ⚙️ Getting Started

1. Prerequisites

Get an IGDB API Client ID and Secret by registering an application on the Twitch Developer Portal.

2. Installation

# Clone the repository
git clone [https://github.com/your-username/pixelrag-analytics.git](https://github.com/your-username/pixelrag-analytics.git)
cd pixelrag-analytics

# Install dependencies
pip install -r requirement.txt


3. Setup Environment Variables

Create a .env file in the root directory:

IGDB_CLIENT_ID=your_twitch_client_id
IGDB_CLIENT_SECRET=your_twitch_client_secret
GEMINI_API_KEY=your_gemini_api_key


4. Run the Pipeline & App

# 1. Fetch, clean, and populate the database
python src/fetch_IGDB.py

# 2. Run the connection testing script
python src/API_Connection_Test.py
