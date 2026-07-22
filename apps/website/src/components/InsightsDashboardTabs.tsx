"use client";

import {
  useMemo,
  useState,
  type FocusEvent,
  type MouseEvent,
  type ReactNode,
} from "react";

import type { DashboardRow, InsightsSummary } from "@/types/api";

type TabKey = "descriptive" | "diagnostic";
type DashboardValue = DashboardRow[string];

type TableColumn = {
  key: string;
  label: string;
  definition?: string;
  format?: (value: DashboardValue, row: DashboardRow) => string;
};

type TooltipPosition = {
  left: number;
  top: number;
  width: number;
};

const definitions = {
  cohort:
    "A group of games selected through the same extraction rule, such as quality, popularity, low visibility, or lower-rated comparison.",
  curatedSample:
    "The project dataset built from selected IGDB extraction rules. It is not the full IGDB market.",
  hiddenGem:
    "A project-defined game with strong rating quality signals and lower visibility within its release-year comparison group.",
  median:
    "The middle value after sorting results. It is less affected by extreme outliers than the average.",
  metadataRichness:
    "How many relationship links a game has, such as genres, themes, keywords, platforms, companies, media, and related metadata.",
  percentile:
    "A relative position from 0 to 100. A higher percentile means the value is higher than more games in the comparison group.",
  percentOfGames:
    "The share of all games in the current project sample represented by this metric.",
  popscore:
    "An IGDB popularity-style signal used here as a visibility/current-interest indicator when available.",
  ratingBand:
    "A grouped quality bucket based on total rating, such as Excellent, Good, Mixed, or Unrated.",
  ratingCoverage:
    "The share of games that have total rating data available.",
  ratingEvidence:
    "The amount and reliability of rating information behind a game, usually represented through rating counts and reliability flags.",
  reliableRating:
    "A game with enough rating evidence to support a stronger quality interpretation.",
  releaseSpan:
    "The release-year range covered by the curated project sample.",
  sampleSize:
    "The number of games or records used to calculate a metric.",
  spearman:
    "A rank-based correlation. It shows whether two measures generally move in the same direction without assuming a linear relationship.",
  visibility:
    "How visible or currently interesting a game appears in the project data, mainly through PopScore and related popularity signals.",
};

const tabCopy: Record<
  TabKey,
  {
    eyebrow: string;
    title: string;
    description: string;
  }
> = {
  descriptive: {
    eyebrow: "Descriptive_",
    title: "Descriptive",
    description:
      "A direct summary of catalog size, coverage, genres, platforms, ratings, and metadata depth.",
  },
  diagnostic: {
    eyebrow: "Diagnostic_",
    title: "Diagnostic",
    description:
      "A direct summary of relationship checks, hidden-gem logic, rating evidence, and visibility signals.",
  },
};

const tabTerms: Record<TabKey, Array<{ label: string; definition: string }>> = {
  descriptive: [
    { label: "Curated sample", definition: definitions.curatedSample },
    { label: "Rating coverage", definition: definitions.ratingCoverage },
    { label: "Rating band", definition: definitions.ratingBand },
    { label: "Metadata richness", definition: definitions.metadataRichness },
    { label: "Median", definition: definitions.median },
  ],
  diagnostic: [
    { label: "Hidden gem", definition: definitions.hiddenGem },
    { label: "Reliable rating", definition: definitions.reliableRating },
    { label: "PopScore", definition: definitions.popscore },
    { label: "Visibility", definition: definitions.visibility },
    { label: "Spearman rho", definition: definitions.spearman },
    { label: "Cohort", definition: definitions.cohort },
  ],
};

function rowsFor(summary: InsightsSummary, tab: TabKey, key: string): DashboardRow[] {
  return summary.dashboard?.[tab]?.[key] ?? [];
}

function toNumber(value: DashboardValue | unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function formatNumber(value: DashboardValue | unknown, maximumFractionDigits = 1) {
  const number = toNumber(value);
  if (number === null) return String(value ?? "Unknown");

  return number.toLocaleString(undefined, {
    maximumFractionDigits,
  });
}

function formatPercent(value: DashboardValue | unknown) {
  const number = toNumber(value);
  if (number === null) return "Unknown";

  const percent = Math.abs(number) <= 1 ? number * 100 : number;
  return `${percent.toLocaleString(undefined, { maximumFractionDigits: 1 })}%`;
}

function formatMetricLabel(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function summaryValue(
  summary: InsightsSummary,
  group: "dataset" | "descriptive" | "diagnostic",
  key: string,
) {
  return summary[group]?.[key];
}

function metricFromRows(rows: DashboardRow[], key: string): DashboardValue | undefined {
  return rows.find((row) => row.metric === key)?.value;
}

function InfoTooltip({
  definition,
  variant = "default",
}: {
  definition?: string;
  variant?: "default" | "table";
}) {
  const [position, setPosition] = useState<TooltipPosition | null>(null);

  if (!definition) return null;

  function showTooltip(event: MouseEvent<HTMLElement> | FocusEvent<HTMLElement>) {
    if (typeof window === "undefined") return;

    const rect = event.currentTarget.getBoundingClientRect();
    const width = Math.min(320, window.innerWidth - 32);
    const left = Math.min(
      Math.max(rect.left + rect.width / 2 - width / 2, 16),
      window.innerWidth - width - 16,
    );
    const estimatedHeight = 144;
    const belowTop = rect.bottom + 10;
    const top =
      belowTop + estimatedHeight > window.innerHeight
        ? Math.max(16, rect.top - estimatedHeight - 10)
        : belowTop;

    setPosition({ left, top, width });
  }

  return (
    <span className="relative inline-flex align-middle" onMouseLeave={() => setPosition(null)}>
      <span
        tabIndex={0}
        onMouseEnter={showTooltip}
        onFocus={showTooltip}
        onBlur={() => setPosition(null)}
        className={`grid h-5 w-5 cursor-help place-items-center border font-mono text-[0.68rem] font-black leading-none outline-none transition ${
          variant === "table"
            ? "border-black/55 bg-white text-black hover:border-black hover:bg-black hover:text-white focus:border-black focus:bg-black focus:text-white"
            : "border-white/40 bg-black text-white hover:border-[#FF3E00] hover:text-[#FF3E00] focus:border-[#FF3E00] focus:text-[#FF3E00]"
        }`}
        aria-label={definition}
      >
        ?
      </span>
      {position && (
        <span
          role="tooltip"
          className="pointer-events-none fixed z-[100] max-h-44 overflow-y-auto border border-white bg-black p-3 text-left font-sans text-xs normal-case leading-5 tracking-normal text-white shadow-[0_0_0_1px_#000]"
          style={{
            left: position.left,
            top: position.top,
            width: position.width,
          }}
        >
          {definition}
        </span>
      )}
    </span>
  );
}

function LabelWithTooltip({
  children,
  definition,
  tooltipVariant = "default",
}: {
  children: ReactNode;
  definition?: string;
  tooltipVariant?: "default" | "table";
}) {
  return (
    <span className="inline-flex items-center gap-2">
      <span>{children}</span>
      <InfoTooltip definition={definition} variant={tooltipVariant} />
    </span>
  );
}

function TerminologyPanel({ activeTab }: { activeTab: TabKey }) {
  return (
    <section className="border border-white bg-black p-5 text-white">
      <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
        Project terminology_
      </p>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {tabTerms[activeTab].map((term) => (
          <p
            key={term.label}
            className="border border-white/20 bg-black p-3 text-sm leading-6 text-white/70"
          >
            <span className="font-mono text-xs uppercase tracking-[0.16em] text-white">
              {term.label}:{" "}
            </span>
            {term.definition}
          </p>
        ))}
      </div>
    </section>
  );
}

function MetricTile({
  label,
  value,
  note,
  definition,
}: {
  label: string;
  value: DashboardValue | unknown;
  note?: string;
  definition?: string;
}) {
  return (
    <article className="border border-white bg-black p-5 text-white">
      <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#FF3E00]">
        <LabelWithTooltip definition={definition}>{label}</LabelWithTooltip>
      </p>
      <p className="mt-4 font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase leading-none tracking-[-0.05em] text-white">
        {String(value ?? "Unknown")}
      </p>
      {note && <p className="mt-3 text-sm leading-6 text-white/58">{note}</p>}
    </article>
  );
}

function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
        {eyebrow}
      </p>
      <h2 className="mt-2 font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase leading-none tracking-[-0.05em] text-white">
        {title}
      </h2>
      {description && <p className="mt-3 max-w-3xl leading-7 text-white/64">{description}</p>}
    </div>
  );
}

function RankedBars({
  title,
  eyebrow,
  rows,
  labelKey,
  valueKey,
  valueLabel,
  format = formatNumber,
}: {
  title: string;
  eyebrow: string;
  rows: DashboardRow[];
  labelKey: string;
  valueKey: string;
  valueLabel: string;
  format?: (value: DashboardValue | unknown) => string;
}) {
  const max = Math.max(...rows.map((row) => toNumber(row[valueKey]) ?? 0), 1);

  return (
    <section className="border border-white bg-black p-5 text-white">
      <SectionHeader eyebrow={eyebrow} title={title} />
      <div className="mt-6 grid gap-4">
        {rows.map((row, index) => {
          const value = toNumber(row[valueKey]) ?? 0;
          const width = `${Math.max((value / max) * 100, 2)}%`;

          return (
            <div key={`${String(row[labelKey])}-${index}`}>
              <div className="flex items-end justify-between gap-4">
                <p className="font-black uppercase tracking-[-0.03em] text-white">
                  {String(row[labelKey] ?? "Unknown")}
                </p>
                <p className="font-mono text-sm font-semibold uppercase tracking-[0.12em] text-white/68">
                  {format(row[valueKey])} {valueLabel}
                </p>
              </div>
              <div className="mt-2 h-3 border border-white/28 bg-white/5">
                <div className="h-full bg-[#FF3E00]" style={{ width }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function DataTable({
  eyebrow,
  title,
  description,
  rows,
  columns,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  rows: DashboardRow[];
  columns: TableColumn[];
}) {
  return (
    <section className="overflow-hidden border border-white bg-black text-white">
      <div className="p-5">
        <SectionHeader eyebrow={eyebrow} title={title} description={description} />
      </div>
      <div className="border-t border-white">
        <table className="w-full table-fixed border-collapse text-left">
          <thead>
            <tr className="border-b border-white bg-white text-black">
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="px-4 py-4 align-top font-mono text-xs uppercase tracking-[0.12em]"
                >
                  <LabelWithTooltip definition={column.definition} tooltipVariant="table">
                    {column.label}
                  </LabelWithTooltip>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="border-b border-white/18 last:border-b-0">
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className="break-words px-4 py-3 align-top text-sm leading-6 text-white/72"
                  >
                    {column.format
                      ? column.format(row[column.key], row)
                      : String(row[column.key] ?? "Unknown")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function TakeawayCards({ rows }: { rows: DashboardRow[] }) {
  return (
    <section className="border border-white bg-black p-5 text-white">
      <SectionHeader
        eyebrow="Diagnostic findings_"
        title="Main relationship checks"
        description="These cards explain the main evidence from the diagnostic notebook in plain language."
      />
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {rows.map((row, index) => (
          <article
            key={String(row.takeaway_id)}
            className={`border border-white/24 bg-black p-5 ${
              rows.length % 2 === 1 && index === rows.length - 1 ? "md:col-span-2" : ""
            }`}
          >
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#FF3E00]">
              Finding {row.takeaway_id}
            </p>
            <h3 className="mt-3 text-xl font-bold leading-7 text-white">
              {String(row.finding ?? "Unknown finding")}
            </h3>
            <p className="mt-4 font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
              Evidence_
            </p>
            <p className="mt-2 text-sm leading-7 text-white/76">
              {String(row.evidence ?? "No evidence note available.")}
            </p>
            <p className="mt-4 border-t border-white/18 pt-4 font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
              Meaning_
            </p>
            <p className="mt-2 text-sm leading-7 text-white/62">
              {String(row.interpretation ?? "No interpretation note available.")}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

function DescriptiveDashboard({ summary }: { summary: InsightsSummary }) {
  const kpis = rowsFor(summary, "descriptive", "kpi_snapshot");
  const topGenres = rowsFor(summary, "descriptive", "top_genres");
  const topPlatforms = rowsFor(summary, "descriptive", "top_platforms");
  const ratingBands = rowsFor(summary, "descriptive", "rating_bands");
  const popularitySignals = rowsFor(summary, "descriptive", "popularity_signals");
  const metadataRichness = rowsFor(summary, "descriptive", "metadata_richness");
  const playtimeBands = rowsFor(summary, "descriptive", "playtime_bands");

  return (
    <div className="grid gap-6">
      <section className="grid gap-px border border-white bg-white md:grid-cols-2 xl:grid-cols-4">
        <MetricTile
          label="Total games"
          value={formatNumber(summaryValue(summary, "dataset", "total_games"), 0)}
          note="Current curated app catalog size."
          definition={definitions.curatedSample}
        />
        <MetricTile
          label="Release span"
          value={summaryValue(summary, "dataset", "release_years")}
          note="Selected release-year coverage."
          definition={definitions.releaseSpan}
        />
        <MetricTile
          label="Top genre"
          value={summaryValue(summary, "descriptive", "top_genre")}
          note="Largest genre group in the selected sample."
        />
        <MetricTile
          label="Rating coverage"
          value={formatPercent(summaryValue(summary, "descriptive", "rating_coverage_pct"))}
          note="Games with total rating available."
          definition={definitions.ratingCoverage}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <RankedBars
          eyebrow="Composition_"
          title="Top genres"
          rows={topGenres}
          labelKey="genre_name"
          valueKey="game_count"
          valueLabel="games"
        />
        <RankedBars
          eyebrow="Platform reach_"
          title="Top platforms"
          rows={topPlatforms}
          labelKey="platform_name"
          valueKey="game_count"
          valueLabel="games"
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <DataTable
          eyebrow="Quality coverage_"
          title="Rating bands"
          description="This explains how much of the catalog has enough reception data to support quality-oriented analysis."
          rows={ratingBands}
          columns={[
            { key: "rating_band", label: "Band", definition: definitions.ratingBand },
            { key: "game_count", label: "Games", format: (value) => formatNumber(value, 0) },
          ]}
        />
        <DataTable
          eyebrow="Visibility coverage_"
          title="Popularity signal availability"
          description="These are the main visibility/activity signals available for downstream analysis."
          rows={popularitySignals}
          columns={[
            { key: "popularity_source", label: "Source" },
            {
              key: "popularity_type",
              label: "Signal",
              definition: definitions.visibility,
            },
            {
              key: "games_with_signal",
              label: "Available games",
              format: (value) => formatNumber(value, 0),
            },
            {
              key: "signal_records",
              label: "Records",
              format: (value) => formatNumber(value, 0),
            },
          ]}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <DataTable
          eyebrow="Metadata depth_"
          title="Relationship richness"
          rows={metadataRichness}
          columns={[
            {
              key: "metadata_richness_band",
              label: "Band",
              definition: definitions.metadataRichness,
            },
            { key: "game_count", label: "Games", format: (value) => formatNumber(value, 0) },
            {
              key: "median_relationship_count",
              label: "Median links",
              definition: definitions.median,
              format: (value) => formatNumber(value, 1),
            },
          ]}
        />
        <DataTable
          eyebrow="Playtime_"
          title="Normal playtime bands"
          rows={playtimeBands}
          columns={[
            { key: "playtime_band", label: "Band" },
            { key: "game_count", label: "Games", format: (value) => formatNumber(value, 0) },
            {
              key: "median_normally_hours",
              label: "Median hours",
              definition: definitions.median,
              format: (value) => formatNumber(value, 1),
            },
          ]}
        />
      </section>

      <DataTable
        eyebrow="Snapshot_"
        title="Core descriptive KPIs"
        rows={kpis}
        columns={[
          { key: "kpi", label: "KPI" },
          { key: "value", label: "Value", format: (value) => formatNumber(value, 2) },
          {
            key: "pct_of_games",
            label: "Percent of games",
            definition: definitions.percentOfGames,
            format: (value) => (value === null ? "N/A" : formatPercent(value)),
          },
          { key: "note", label: "Note" },
        ]}
      />
    </div>
  );
}

function DiagnosticDashboard({ summary }: { summary: InsightsSummary }) {
  const takeaways = rowsFor(summary, "diagnostic", "takeaways");
  const snapshot = rowsFor(summary, "diagnostic", "dataset_snapshot");
  const hiddenGemGenres = rowsFor(summary, "diagnostic", "hidden_gems_by_genre");
  const hiddenGemPlatforms = rowsFor(summary, "diagnostic", "hidden_gems_by_platform_family");
  const genreRatings = rowsFor(summary, "diagnostic", "genre_rating_summary");
  const platformRatings = rowsFor(summary, "diagnostic", "platform_family_rating_summary");
  const ratingBandPopscore = rowsFor(summary, "diagnostic", "rating_band_popscore_summary");
  const userCritic = rowsFor(summary, "diagnostic", "user_critic_agreement");

  const reliableGames = metricFromRows(snapshot, "rating_reliable_games");
  const highRatedReliableGames = metricFromRows(snapshot, "high_rated_reliable_games");
  const popscoreCoveredGames = metricFromRows(snapshot, "popscore_covered_games");
  const spearman = userCritic.find(
    (row) => row.metric === "user_critic_spearman_correlation",
  )?.value;

  return (
    <div className="grid gap-6">
      <section className="grid gap-px border border-white bg-white md:grid-cols-2 xl:grid-cols-4">
        <MetricTile
          label="Hidden gems"
          value={formatNumber(summaryValue(summary, "diagnostic", "hidden_gem_count"), 0)}
          note="High-quality, lower-visibility candidates in the project sample."
          definition={definitions.hiddenGem}
        />
        <MetricTile
          label="Reliable rating games"
          value={formatNumber(reliableGames, 0)}
          note="Games with enough rating evidence for stronger quality reads."
          definition={definitions.reliableRating}
        />
        <MetricTile
          label="High-rated reliable"
          value={formatNumber(highRatedReliableGames, 0)}
          note="Reliable games that cross the high-quality threshold."
          definition={definitions.ratingEvidence}
        />
        <MetricTile
          label="User / critic rho"
          value={formatNumber(spearman, 3)}
          note="Spearman relationship between user and critic reception."
          definition={definitions.spearman}
        />
      </section>

      <TakeawayCards rows={takeaways} />

      <section className="grid gap-6 xl:grid-cols-2">
        <RankedBars
          eyebrow="Hidden gems_"
          title="Hidden gems by genre"
          rows={hiddenGemGenres}
          labelKey="genre_name"
          valueKey="hidden_gem_count"
          valueLabel="games"
        />
        <RankedBars
          eyebrow="Hidden gems_"
          title="Hidden gems by platform family"
          rows={hiddenGemPlatforms}
          labelKey="platform_family"
          valueKey="hidden_gem_count"
          valueLabel="games"
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <DataTable
          eyebrow="Quality patterns_"
          title="Highest median-rated genres"
          description="Genres are shown from the diagnostic rating summary, sorted by median total rating."
          rows={genreRatings}
          columns={[
            { key: "genre_name", label: "Genre" },
            {
              key: "game_count",
              label: "Rated games",
              definition: definitions.ratingEvidence,
              format: (value) => formatNumber(value, 0),
            },
            {
              key: "median_total_rating",
              label: "Median rating",
              definition: definitions.median,
              format: (value) => formatNumber(value, 1),
            },
            {
              key: "hidden_gem_count",
              label: "Hidden gems",
              definition: definitions.hiddenGem,
              format: (value) => formatNumber(value, 0),
            },
          ]}
        />
        <DataTable
          eyebrow="Platform lens_"
          title="Platform-family rating summary"
          rows={platformRatings}
          columns={[
            { key: "platform_family", label: "Family" },
            {
              key: "game_count",
              label: "Rated games",
              definition: definitions.ratingEvidence,
              format: (value) => formatNumber(value, 0),
            },
            {
              key: "median_total_rating",
              label: "Median rating",
              definition: definitions.median,
              format: (value) => formatNumber(value, 1),
            },
            {
              key: "hidden_gem_count",
              label: "Hidden gems",
              definition: definitions.hiddenGem,
              format: (value) => formatNumber(value, 0),
            },
          ]}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <DataTable
          eyebrow="Visibility relationship_"
          title="Rating band x PopScore"
          description="This compares quality bands with median visibility signals where PopScore is available."
          rows={ratingBandPopscore}
          columns={[
            { key: "rating_band", label: "Band", definition: definitions.ratingBand },
            { key: "extraction_cohort", label: "Cohort", definition: definitions.cohort },
            {
              key: "game_count",
              label: "Games",
              format: (value) => formatNumber(value, 0),
            },
            {
              key: "median_custom_interest_percentile",
              label: "Median visibility",
              definition: definitions.visibility,
              format: (value) => formatPercent(value),
            },
          ]}
        />
        <DataTable
          eyebrow="Agreement check_"
          title="User versus critic reception"
          rows={userCritic}
          columns={[
            { key: "metric", label: "Metric", format: (value) => formatMetricLabel(String(value)) },
            {
              key: "n",
              label: "N",
              definition: definitions.sampleSize,
              format: (value) => formatNumber(value, 0),
            },
            { key: "value", label: "Value", format: (value) => formatNumber(value, 3) },
            { key: "correlation_status", label: "Status" },
          ]}
        />
      </section>

      <DataTable
        eyebrow="Diagnostic sample_"
        title="Data checks and sample counts"
        rows={snapshot}
        columns={[
          { key: "metric", label: "Metric", format: (value) => formatMetricLabel(String(value)) },
          { key: "value", label: "Value", format: (value) => formatNumber(value, 2) },
          { key: "expected", label: "Expected" },
          {
            key: "passes_expected_check",
            label: "Passes",
            format: (value) => (value === null ? "N/A" : String(value)),
          },
        ]}
      />

      <section className="border border-white bg-black p-5 text-white">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
          <LabelWithTooltip definition={definitions.popscore}>PopScore coverage_</LabelWithTooltip>
        </p>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-white/64">
          {formatNumber(popscoreCoveredGames, 0)} games have PopScore coverage in the
          diagnostic sample. Missing visibility is treated as unknown, not as low
          popularity.
        </p>
      </section>
    </div>
  );
}

export function InsightsDashboardTabs({ summary }: { summary: InsightsSummary }) {
  const [activeTab, setActiveTab] = useState<TabKey>("descriptive");

  const dashboardAvailable = useMemo(() => {
    const descriptiveRows = Object.values(summary.dashboard?.descriptive ?? {}).flat();
    const diagnosticRows = Object.values(summary.dashboard?.diagnostic ?? {}).flat();
    return descriptiveRows.length > 0 || diagnosticRows.length > 0;
  }, [summary.dashboard]);

  if (!dashboardAvailable) {
    return (
      <section className="border border-white bg-black p-6 text-white">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
          Dashboard unavailable_
        </p>
        <p className="mt-4 max-w-3xl leading-7 text-white/68">
          The insights endpoint returned the base summary, but the dashboard artifact
          tables were not available.
        </p>
      </section>
    );
  }

  return (
    <section className="grid gap-6">
      <div className="grid gap-px border border-white bg-white md:grid-cols-2">
        {(["descriptive", "diagnostic"] as TabKey[]).map((tab) => {
          const selected = activeTab === tab;

          return (
            <button
              key={tab}
              type="button"
              aria-pressed={selected}
              onClick={() => setActiveTab(tab)}
              className={`group p-5 text-left transition-none ${
                selected ? "bg-[#FF3E00] text-black" : "bg-black text-white hover:bg-white hover:text-black"
              }`}
            >
              <p className="font-['Arial_Black',Impact,system-ui,sans-serif] text-3xl uppercase leading-none tracking-[-0.05em]">
                {tabCopy[tab].title}_
              </p>
              <p
                className={`mt-3 text-sm leading-6 ${
                  selected ? "text-black/72" : "text-white/62 group-hover:text-black/72"
                }`}
              >
                {tabCopy[tab].description}
              </p>
            </button>
          );
        })}
      </div>

      {activeTab === "descriptive" ? (
        <DescriptiveDashboard summary={summary} />
      ) : (
        <DiagnosticDashboard summary={summary} />
      )}

      <TerminologyPanel activeTab={activeTab} />
    </section>
  );
}
