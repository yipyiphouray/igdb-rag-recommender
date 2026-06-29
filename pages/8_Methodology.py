from __future__ import annotations

import pandas as pd
import streamlit as st

from src.app import config
from src.app.components.metric_cards import render_metric_row
from src.app.components.ui_style import inject_global_styles
from src.app.constants import HIDDEN_GEM_VISIBILITY_PERCENTILE, MIN_RATING_COUNT, MVP_RECOMMENDATION_WEIGHTS, QUALITY_THRESHOLD
from src.app.data_loader import load_json_artifact
from src.app.validation import artifact_audit


def _section(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="method-section">
          <div class="method-section-title">{title}</div>
          <div class="method-section-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Methodology", page_icon="📚", layout="wide")
inject_global_styles()

st.markdown('<div class="section-kicker">Trust layer</div>', unsafe_allow_html=True)
st.title("Methodology")
st.write("A continuous reference page for source data, sample design, definitions, formulas, caveats, and app boundaries.")

metrics = load_json_artifact(config.APP_METHODOLOGY_METRICS_PATH)

render_metric_row(
    [
        ("Games", f"{int(metrics.get('total_games', 0)):,}", "Current app catalog"),
        ("Years", f"{metrics.get('release_year_start')}-{metrics.get('release_year_end')}", "Balanced release years"),
        ("Hidden gems", f"{int(metrics.get('hidden_gem_count', 0)):,}", "Balanced rule"),
        ("PopScore coverage", f"{metrics.get('popscore_coverage', 0) * 100:.1f}%", "Known IGDB interest score"),
    ]
)

_section(
    "1. Data source and app artifacts",
    "The project uses IGDB data extracted through the project API pipeline, loaded into a normalized SQLite database, "
    "then converted into app-ready artifacts for Streamlit. Streamlit reads prepared artifacts instead of rebuilding the "
    "database during normal app use.",
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

_section(
    "2. Curated sample design",
    "The current sample selects exactly 1,000 released main games per year from 2010 through 2024. "
    "The extraction uses quality, popularity, and comparison cohorts to make the sample useful for analytics and "
    "discovery instead of being a raw IGDB pull.",
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

st.markdown(
    """
    <div class="small-caveat">
      The app uses a curated analytical sample, not the full IGDB catalog. Quality and visibility cohorts are
      intentionally oversampled, so full-sample rating or visibility shares are not market prevalence estimates.
    </div>
    """,
    unsafe_allow_html=True,
)

_section(
    "3. Metric definitions",
    "The app keeps quality, rating activity, and visibility separate. This prevents rating count from being mislabeled "
    "as popularity and prevents missing PopScore from being treated as low visibility.",
)
st.code(
    """total_rating       = quality / reception signal
total_rating_count = rating evidence / rating activity signal
PopScore interest  = visibility / current-interest signal

Missing PopScore = unknown visibility, not low visibility.""",
    language="text",
)

_section(
    "4. Hidden-gem calculation",
    "The default Balanced hidden-gem rule comes from the finalized diagnostic analytics notebook. Conservative and Broad "
    "views are sensitivity variants for exploration, not replacements for the Balanced definition.",
)
st.code(
    f"""quality cohort
AND total_rating >= {QUALITY_THRESHOLD}
AND total_rating_count >= {MIN_RATING_COUNT}
AND main game
AND PopScore available
AND within-year quality-cohort visibility percentile <= {HIDDEN_GEM_VISIBILITY_PERCENTILE:.0%}""",
    language="text",
)

_section(
    "5. Recommendation scoring",
    "The current recommender is a transparent MVP rule-based scorer. Platform is a hard gate when selected. "
    "The remaining components add relevance and fit signals from observed catalog fields.",
)
weights = pd.DataFrame(
    [{"component": component, "max_points": points} for component, points in MVP_RECOMMENDATION_WEIGHTS.items()]
)
st.dataframe(weights, width="stretch", hide_index=True)
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

_section(
    "6. Artifact audit",
    "This audit confirms whether the major project directories and app artifacts exist in the local workspace.",
)
audit_df = pd.DataFrame(
    [{"artifact_check": key, "available": value} for key, value in artifact_audit().items()]
)
st.dataframe(audit_df, width="stretch", hide_index=True)

_section(
    "7. Known limitations",
    "The project sample is curated and should not be treated as a full-market random sample. Missing optional metadata "
    "usually means unknown, not negative. PopScore is availability-dependent. Diagnostic associations do not establish "
    "causality. Games can belong to multiple genres, themes, platforms, and companies, so category analysis contains "
    "overlapping groups. Predictive and RAG pages are currently integration placeholders.",
)

_section(
    "8. Implementation boundaries",
    "Streamlit loads prepared assets. It should not rebuild the database, call the live IGDB API, retrain models, "
    "or generate embeddings during normal app use. Those steps belong in offline pipeline scripts or teammate-owned "
    "integration workflows.",
)
