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
