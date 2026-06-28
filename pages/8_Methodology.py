from __future__ import annotations

import streamlit as st

from src.app import config
from src.app.components.methodology_notice import render_sample_caveat, render_signal_caveat
from src.app.components.metric_cards import render_metric_row
from src.app.components.ui_style import inject_global_styles
from src.app.constants import HIDDEN_GEM_VISIBILITY_PERCENTILE, MIN_RATING_COUNT, MVP_RECOMMENDATION_WEIGHTS, QUALITY_THRESHOLD
from src.app.data_loader import load_json_artifact
from src.app.validation import artifact_audit


st.set_page_config(page_title="Methodology", page_icon="📚", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Academic / trust layer</div>', unsafe_allow_html=True)
st.title("Methodology")
st.write("The technical source-of-truth page for data sources, sample design, calculations, caveats, and implementation boundaries.")

metrics = load_json_artifact(config.APP_METHODOLOGY_METRICS_PATH)

render_metric_row(
    [
        ("Games", f"{int(metrics.get('total_games', 0)):,}", "Current app catalog"),
        ("Years", f"{metrics.get('release_year_start')}-{metrics.get('release_year_end')}", "Balanced release years"),
        ("Hidden gems", f"{int(metrics.get('hidden_gem_count', 0)):,}", "Balanced rule"),
        ("PopScore coverage", f"{metrics.get('popscore_coverage', 0) * 100:.1f}%", "Known IGDB interest score"),
    ]
)

with st.expander("1. Data source and app artifacts", expanded=True):
    st.write(
        "The project uses IGDB data extracted through the project API pipeline, loaded into a normalized SQLite database, "
        "then converted into app-ready artifacts for Streamlit."
    )
    st.code(
        """Primary database:
data/database/igdb_games.db

App-ready artifacts:
data/app/app_game_catalog.parquet
data/app/app_hidden_gems.parquet
data/app/app_filter_options.json
data/app/app_insight_summary.json
data/app/app_methodology_metrics.json""",
        language="text",
    )

with st.expander("2. Curated sample design", expanded=True):
    render_sample_caveat()
    st.write(
        "The current sample selects exactly 1,000 released main games per year from 2010 through 2024. "
        "The extraction uses quality, popularity, and comparison cohorts to make the sample useful for analytics "
        "and discovery instead of being a raw IGDB pull."
    )
    st.code(
        """Final sample:
15,000 games
2010-2024
1,000 games per year

Cohorts:
quality
popularity
comparison""",
        language="text",
    )

with st.expander("3. Metric definitions", expanded=True):
    render_signal_caveat()
    st.write("These definitions should be preserved throughout the app and reports:")
    st.code(
        """total_rating       = quality / reception signal
total_rating_count = rating evidence / rating activity signal
PopScore interest  = visibility / current-interest signal

Missing PopScore = unknown visibility, not low visibility.""",
        language="text",
    )

with st.expander("4. Hidden-gem calculation", expanded=True):
    st.write("The default Balanced hidden-gem rule comes from the finalized diagnostic analytics notebook.")
    st.code(
        f"""quality cohort
AND total_rating >= {QUALITY_THRESHOLD}
AND total_rating_count >= {MIN_RATING_COUNT}
AND main game
AND PopScore available
AND within-year quality-cohort visibility percentile <= {HIDDEN_GEM_VISIBILITY_PERCENTILE:.0%}""",
        language="text",
    )
    st.write(
        "Conservative and Broad variants are exploratory sensitivity views. They should not replace the Balanced diagnostic definition."
    )

with st.expander("5. Recommendation scoring"):
    st.write(
        "The current recommender is a transparent MVP rule-based scorer. It is intentionally simple so users and evaluators "
        "can inspect why a game was returned."
    )
    st.json(MVP_RECOMMENDATION_WEIGHTS)
    st.code(
        """Current guided recommender:
- platform is a hard gate when selected;
- genre and theme matches add relevance;
- observed total_rating adds quality signal;
- total_rating_count adds rating-evidence signal;
- hidden-gem preference can boost documented hidden-gem candidates;
- popular/visible preference can add a small visibility bias;
- playtime preference can add a small fit bonus when time-to-beat data exists.""",
        language="text",
    )

with st.expander("6. Artifact audit"):
    st.json(artifact_audit())

with st.expander("7. Known limitations", expanded=True):
    st.write(
        "- The project sample is curated and should not be treated as a full-market random sample.\n"
        "- Quality and visibility cohorts are intentionally oversampled.\n"
        "- Missing optional metadata usually means unknown, not negative.\n"
        "- PopScore is availability-dependent.\n"
        "- Diagnostic associations do not establish causality.\n"
        "- Many categories overlap because games can have multiple genres, themes, platforms, and companies.\n"
        "- Predictive and RAG pages are currently integration placeholders."
    )

with st.expander("8. Implementation boundaries"):
    st.write(
        "Streamlit loads prepared assets. It should not rebuild the database, call the live IGDB API, retrain models, "
        "or generate embeddings during normal app use."
    )
