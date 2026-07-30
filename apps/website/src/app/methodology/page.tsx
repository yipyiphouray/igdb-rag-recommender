import { getMethodologySummary } from "@/lib/api";
import type { MethodologySummary } from "@/types/api";

const METRIC_DEFINITIONS: Record<string, string> = {
  total_games: "Total games available in the project app catalog.",
  release_year_start: "Earliest release year included in the curated app sample.",
  release_year_end: "Latest release year included in the curated app sample.",
  games_per_year: "Target number of games selected for each release year where enough data exists.",
  quality_cohort_count: "Games pulled because they had strong rating evidence or quality signals.",
  lower_rated_cohort_count: "Lower-rated games kept for comparison so the catalog is not only highly rated titles.",
  popularity_cohort_count: "Games selected because they showed stronger visibility or current-interest signals.",
  low_visibility_cohort_count: "Games selected to keep less-visible titles represented in the sample.",
  comparison_cohort_count: "Additional games used to make the catalog broader for exploration and comparison.",
  rating_coverage: "Share of catalog games with a total rating value available.",
  reliable_rating_coverage: "Share of catalog games with enough rating-count evidence to treat ratings as more stable.",
  popscore_coverage: "Share of catalog games with a PopScore/current-interest signal available.",
  summary_coverage: "Share of catalog games with summary text available for browsing and retrieval context.",
  hidden_gem_count: "Games flagged as strong quality candidates with lower visibility.",
  quality_threshold: "Minimum total-rating score used to define the stronger-quality group.",
  min_rating_count: "Minimum number of rating records needed before treating a rating as reliable.",
  hidden_gem_visibility_percentile: "Visibility cutoff used when deciding whether a strong game may count as lower visibility.",
};

const JARGON_TERMS = [
  {
    term: "IGDB",
    definition: "The Internet Game Database source used to collect game metadata for this project.",
  },
  {
    term: "Catalog",
    definition: "The curated set of app-ready games used by the website, not the full IGDB database.",
  },
  {
    term: "Curated sample",
    definition: "A dataset selected with project rules instead of a raw random pull.",
  },
  {
    term: "Metadata",
    definition: "Descriptive game fields such as platform, genre, theme, release year, summary, playtime, and rating.",
  },
  {
    term: "App artifact",
    definition: "A prepared data file used by the website so the app does not rebuild the database at runtime.",
  },
  {
    term: "total_rating",
    definition: "IGDB's combined quality or reception score when available, measured from 0 to 100.",
  },
  {
    term: "total_rating_count",
    definition: "The amount of rating evidence behind total_rating. Higher count means stronger support for the score.",
  },
  {
    term: "Rating coverage",
    definition: "The share of catalog games that have a total_rating value.",
  },
  {
    term: "Reliable rating",
    definition: "A rating treated as more stable because total_rating_count is at least 25.",
  },
  {
    term: "PopScore",
    definition: "IGDB popularity or interest signals used as visibility context when available.",
  },
  {
    term: "custom_interest_score",
    definition: "Project visibility score built from IGDB interest primitives: 0.60 * Want to Play + 0.40 * Playing.",
  },
  {
    term: "custom_interest_percentile",
    definition: "A game's relative visibility position based on custom_interest_score.",
  },
  {
    term: "visibility_percentile_eligible_pool",
    definition: "Within-year visibility percentile among hidden-gem-eligible games. Lower values mean lower relative visibility.",
  },
  {
    term: "Cohort",
    definition: "A selection group used to explain why a game entered the catalog.",
  },
  {
    term: "Quality cohort",
    definition: "Games selected because they had stronger rating quality and enough rating evidence.",
  },
  {
    term: "Lower-rated cohort",
    definition: "Reliable lower-rated games kept for diagnostic contrast.",
  },
  {
    term: "Popularity cohort",
    definition: "Games selected because they had stronger known visibility signals.",
  },
  {
    term: "Low-visibility cohort",
    definition: "Games selected because they had weaker known visibility signals.",
  },
  {
    term: "Comparison cohort",
    definition: "A reproducible baseline sample from remaining eligible games.",
  },
  {
    term: "Hidden gem",
    definition: "A project-defined game with strong quality evidence, enough rating activity, and lower relative visibility.",
  },
  {
    term: "Cosine similarity",
    definition: "A scoring method that measures how close the user preference vector is to a game metadata vector.",
  },
  {
    term: "Preference vector",
    definition: "The user's selected platforms, genres, themes, moods, playstyles, seed titles, and playtime converted into comparable signals.",
  },
  {
    term: "Game metadata vector",
    definition: "A game's metadata converted into comparable recommendation signals.",
  },
  {
    term: "Hard filter",
    definition: "A required condition applied before ranking, such as selected platform or release-year range.",
  },
  {
    term: "Candidate pool",
    definition: "The smaller set of games that remains after hard filters and deployment-safe limits are applied.",
  },
  {
    term: "Seed title",
    definition: "A recent game entered by the user to guide similarity matching.",
  },
  {
    term: "RAG",
    definition: "Retrieval-Augmented Generation: retrieving project context before generating a grounded answer.",
  },
  {
    term: "Tool routing",
    definition: "The chatbot step that chooses whether a question needs a catalog fact, project fact, game lookup, comparison, navigation answer, or project-context answer.",
  },
  {
    term: "Frontend",
    definition: "The Next.js website interface that users interact with.",
  },
  {
    term: "Backend",
    definition: "The FastAPI service that loads artifacts and returns catalog, recommendation, insight, methodology, and chatbot responses.",
  },
  {
    term: "API",
    definition: "The connection layer between the website and backend service.",
  },
];

const FEATURE_LOGIC = [
  {
    feature: "Catalog extraction",
    purpose: "Build the shared app catalog used by every website page.",
    logic: [
      "Target 50,000 released main games from 2010-2024.",
      "Keep games with name, release date, genre, and platform.",
      "Remove cancelled, rumored, unreleased, version-parent, and metadata-incomplete records.",
      "Select year-by-year to avoid a catalog dominated by only recent, popular, or highly rated games.",
    ],
    formula:
      "IGDB API -> eligibility rules -> cohort selection -> relational database -> app-ready artifacts",
  },
  {
    feature: "Cohort selection",
    purpose: "Keep the catalog analytically balanced instead of only popularity-driven.",
    logic: [
      "Quality: high total_rating with enough total_rating_count evidence.",
      "Lower-rated: low total_rating with enough total_rating_count evidence.",
      "Popularity: stronger IGDB visibility signal.",
      "Low visibility: weaker IGDB visibility signal.",
      "Comparison: reproducible baseline from remaining eligible games.",
    ],
  },
  {
    feature: "Explore Games",
    purpose: "Let users browse and narrow the catalog directly.",
    logic: [
      "Search checks game names and summaries.",
      "Filters use release year, platform, genre, theme, minimum rating, minimum reviews, and hidden-gem status.",
      "Sorting can prioritize rating, rating evidence, visibility, release year, or name.",
    ],
  },
  {
    feature: "Recommend Me",
    purpose: "Rank games from structured user preferences.",
    logic: [
      "Apply hard filters first.",
      "Build a deployment-safe candidate pool.",
      "Convert user answers into a preference vector.",
      "Compare against game metadata vectors with cosine similarity.",
      "Adjust ranking with quality, rating evidence, discovery preference, and playtime fit.",
    ],
    formula:
      "final_score = 0.65*cosine_similarity + 0.15*quality_score + 0.10*rating_evidence_score + 0.05*discovery_score + 0.05*playtime_score",
  },
  {
    feature: "Recommendation components",
    purpose: "Explain what the ranking formula rewards.",
    logic: [
      "cosine_similarity = closeness between user preference vector and game metadata vector.",
      "quality_score = normalized total_rating / 100.",
      "rating_evidence_score = normalized log-scaled total_rating_count.",
      "discovery_score = hidden-gem signal or visibility signal depending on user preference.",
      "playtime_score = whether the game fits the selected playtime band.",
    ],
  },
  {
    feature: "Hidden Gems",
    purpose: "Surface high-quality games with lower relative visibility.",
    logic: [
      "Require strong quality evidence.",
      "Require enough rating activity to trust the quality signal.",
      "Require known visibility data.",
      "Compare visibility within the same release year eligible pool.",
      "Treat missing visibility as unknown, not low visibility.",
    ],
    formula:
      "hidden_gem = total_rating >= 80 AND total_rating_count >= 25 AND visibility_percentile_eligible_pool <= 0.40",
  },
  {
    feature: "Hidden-gem ranking",
    purpose: "Order hidden-gem candidates after they satisfy the rule.",
    logic: [
      "Higher quality improves the hidden-gem score.",
      "Lower relative visibility improves the hidden-gem score.",
    ],
    formula:
      "hidden_gem_score = 0.65*(total_rating/100) + 0.35*(1 - visibility_percentile_eligible_pool)",
  },
  {
    feature: "Insights",
    purpose: "Turn descriptive and diagnostic analytics into dashboard evidence.",
    logic: [
      "Descriptive analytics summarizes what is in the catalog.",
      "Diagnostic analytics compares quality, rating activity, visibility, genre, theme, platform, and cohort patterns.",
      "Findings are treated as associations, not causal claims.",
    ],
  },
  {
    feature: "Ask the Guide",
    purpose: "Answer project, catalog, methodology, and website questions without replacing Recommend Me.",
    logic: [
      "Plan the question route.",
      "Use structured tools for exact project facts, catalog counts, game lookup, game comparison, term definitions, and navigation.",
      "Retrieve project context for broader methodology questions.",
      "Use Gemini API only as the grounded answer phrasing layer when available.",
      "Redirect ranked recommendation requests to Recommend Me.",
    ],
    formula:
      "user question -> tool planning -> facts or project-context retrieval -> grounded answer -> next action",
  },
];

function labelFor(key: string) {
  const specialLabels: Record<string, string> = {
    popscore_coverage: "PopScore coverage",
    min_rating_count: "Minimum rating count",
  };

  if (specialLabels[key]) return specialLabels[key];

  return key
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function definitionFor(key: string) {
  return (
    METRIC_DEFINITIONS[key] ??
    "Project methodology field used to explain how the catalog and app signals were prepared."
  );
}

function formatMetricValue(key: string, value: unknown) {
  if (typeof value === "number") {
    if (key.includes("year")) return String(Math.round(value));
    if (value > 0 && value < 1) return `${(value * 100).toFixed(1)}%`;
    return value.toLocaleString();
  }

  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value ?? "Unknown");
}

function MetricLabel({ metricKey }: { metricKey: string }) {
  const label = labelFor(metricKey);
  const definition = definitionFor(metricKey);

  return (
    <div className="flex items-center gap-2">
      <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
        {label}
      </p>
      <span className="group relative inline-flex">
        <span
          tabIndex={0}
          aria-label={`${label} definition`}
          className="grid h-5 w-5 cursor-help place-items-center border border-white/40 font-mono text-[0.68rem] font-black text-white outline-none transition hover:border-[#FF3E00] hover:text-[#FF3E00] focus:border-[#FF3E00] focus:text-[#FF3E00]"
        >
          ?
        </span>
        <span className="pointer-events-none absolute left-1/2 top-7 z-20 w-72 -translate-x-1/2 border border-white bg-black p-3 text-left text-xs normal-case leading-5 tracking-normal text-white opacity-0 shadow-[0_0_0_1px_#000] transition group-hover:opacity-100 group-focus-within:opacity-100">
          {definition}
        </span>
      </span>
    </div>
  );
}

function MetricCard({
  metricKey,
  value,
}: {
  metricKey: string;
  value: unknown;
}) {
  return (
    <article className="border border-white bg-black p-5 text-white">
      <MetricLabel metricKey={metricKey} />
      <p className="mt-4 font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase tracking-[-0.05em] text-white">
        {formatMetricValue(metricKey, value)}
      </p>
    </article>
  );
}

function MethodologyUnavailable({ message }: { message: string }) {
  return (
    <div className="methodology-v1-shell">
      <div className="methodology-v1-content">
        <section className="border border-white bg-black p-8 text-white">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
            METHOD_ // OFFLINE
          </p>
          <h1 className="mt-4 font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.9] tracking-[-0.06em] text-white">
            Methodology unavailable_
          </h1>
          <p className="mt-5 max-w-3xl leading-8 text-white/72">{message}</p>
        </section>
      </div>
    </div>
  );
}

export default async function MethodologyPage() {
  let summary: MethodologySummary | null = null;
  let error = "";

  try {
    summary = await getMethodologySummary();
  } catch {
    error = "The methodology API is unavailable. Start the FastAPI backend and refresh this page.";
  }

  if (error || !summary) {
    return (
      <MethodologyUnavailable
        message={
          error ||
          "The methodology summary did not return data. Start the FastAPI backend and refresh this page."
        }
      />
    );
  }

  const importantNotes = [
    ...summary.caveats,
    ...summary.implementation_notes,
  ];

  return (
    <div className="methodology-v1-shell">
      <div className="methodology-v1-content">
        <section className="border border-white bg-black p-8 text-white sm:p-10">
          <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#FF3E00]">
            METHOD_ // CHECK THE SIGNALS
          </p>
          <h1 className="mt-4 max-w-5xl font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.88] tracking-[-0.07em] text-white sm:text-7xl">
            Understand the data before trusting the results_
          </h1>
          <p className="mt-6 max-w-4xl text-lg leading-8 text-white/74">
            This page explains what the catalog numbers mean, how the app data is prepared,
            and what limits to keep in mind before trusting a score or recommendation.
          </p>
        </section>

        <section>
          <div className="mb-4">
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
              Methodology labels_
            </p>
            <h2 className="mt-2 font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase tracking-[-0.05em] text-white">
              What the numbers mean
            </h2>
          </div>

          <div className="grid gap-px border border-white bg-black md:grid-cols-2 xl:grid-cols-3">
            {Object.entries(summary.metrics).map(([key, value]) => (
              <MetricCard key={key} metricKey={key} value={value} />
            ))}
          </div>
        </section>

        <section className="border border-white bg-black p-6 text-white sm:p-8">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
            Project glossary_
          </p>
          <h2 className="mt-3 font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase tracking-[-0.05em] text-white">
            Jargon used across the website
          </h2>
          <p className="mt-4 max-w-4xl leading-8 text-white/72">
            These definitions explain the technical terms used in the catalog,
            recommendation engine, hidden-gem logic, insights, and Ask the Guide.
          </p>

          <div className="mt-6 grid gap-px border border-white bg-white md:grid-cols-2 xl:grid-cols-3">
            {JARGON_TERMS.map((item) => (
              <article key={item.term} className="bg-black p-5">
                <h3 className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
                  {item.term}
                </h3>
                <p className="mt-3 text-sm leading-6 text-white/74">
                  {item.definition}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section className="border border-white bg-black p-6 text-white sm:p-8">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
            Feature logic_
          </p>
          <h2 className="mt-3 font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase tracking-[-0.05em] text-white">
            How each major feature works
          </h2>
          <p className="mt-4 max-w-4xl leading-8 text-white/72">
            This section documents the logic behind the main website features so
            users can inspect the rules behind the results.
          </p>

          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            {FEATURE_LOGIC.map((item) => (
              <article key={item.feature} className="border border-white bg-black p-5">
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
                  {item.feature}
                </p>
                <p className="mt-3 text-sm font-black uppercase tracking-[-0.02em] text-white">
                  {item.purpose}
                </p>
                <ul className="mt-4 space-y-2 text-sm leading-6 text-white/74">
                  {item.logic.map((line) => (
                    <li key={line} className="flex gap-2">
                      <span className="font-mono text-[#FF3E00]">-&gt;</span>
                      <span>{line}</span>
                    </li>
                  ))}
                </ul>
                {item.formula ? (
                  <div className="mt-5 border border-white/24 bg-white/[0.03] p-4">
                    <p className="font-mono text-[0.65rem] uppercase tracking-[0.22em] text-[#FF3E00]">
                      Formula / flow
                    </p>
                    <p className="mt-3 break-words font-mono text-xs leading-6 text-white/82">
                      {item.formula}
                    </p>
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        </section>

        <section className="border border-white bg-black p-6 text-white sm:p-8">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
            Important note_
          </p>
          <h2 className="mt-3 font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase tracking-[-0.05em] text-white">
            Read this before interpreting the app
          </h2>
          <p className="mt-4 max-w-4xl leading-8 text-white/72">
            These points are shown because they affect how users should interpret ratings,
            visibility, recommendations, and RAG answers.
          </p>

          <ul className="mt-6 grid gap-px border border-white bg-white lg:grid-cols-2">
            {importantNotes.map((note) => (
              <li key={note} className="bg-black p-5 leading-7 text-white/76">
                <span className="mr-3 font-mono text-[#FF3E00]">NOTE_</span>
                {note}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
