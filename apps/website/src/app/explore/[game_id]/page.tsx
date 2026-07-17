import Link from "next/link";

import { EmptyState } from "@/components/EmptyState";
import { ExpandableText } from "@/components/ExpandableText";
import { ScrollToTop } from "@/components/ScrollToTop";
import { getCatalogGame } from "@/lib/api";
import type { GameDetail } from "@/types/api";

function formatRating(value?: number | null) {
  if (value === null || value === undefined) return "Unknown";
  return `${value.toFixed(1)}/100`;
}

function formatNumber(value?: number | null) {
  if (value === null || value === undefined) return "Unknown";
  return value.toLocaleString();
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined) return "Unknown";
  return `${Math.round(value * 100)}%`;
}

function formatBoolean(value: boolean) {
  return value ? "Yes" : "No";
}

function upgradedImageUrl(value?: string | null, size: "cover" | "wide" = "cover") {
  if (!value) return null;
  const normalized = value.startsWith("//") ? `https:${value}` : value;
  const target = size === "wide" ? "t_1080p" : "t_cover_big_2x";
  return normalized.replace(/\/t_[^/]+\//, `/${target}/`);
}

function MetricCard({
  label,
  value,
}: {
  label: string;
  value: string | number | null | undefined;
}) {
  return (
    <div className="border border-white bg-black p-4">
      <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
        {label}
      </p>
      <p className="mt-2 font-black text-white">{value ?? "Unknown"}</p>
    </div>
  );
}

function ExpandableTextPanel({
  title,
  children,
}: {
  title: string;
  children: string | null | undefined;
}) {
  return (
    <section className="border border-white bg-black p-5">
      <h3 className="font-mono text-sm uppercase tracking-[0.24em] text-[#FF3E00]">
        {title}
      </h3>
      <ExpandableText text={children} className="mt-4 leading-8 text-white/78" />
    </section>
  );
}

function TagPanel({ title, values }: { title: string; values: string[] }) {
  return (
    <section className="border border-white bg-black p-5">
      <h3 className="font-mono text-sm uppercase tracking-[0.24em] text-[#FF3E00]">
        {title}
      </h3>
      {values.length > 0 ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {values.map((value) => (
            <span
              key={value}
              className="border border-white/28 px-4 py-1.5 font-mono text-xs uppercase tracking-[0.16em] text-white/76"
            >
              {value}
            </span>
          ))}
        </div>
      ) : (
        <p className="mt-4 text-white/56">No data is available.</p>
      )}
    </section>
  );
}

function DetailSection({ game }: { game: GameDetail }) {
  return (
    <div className="grid gap-5">
      <div className="grid gap-px bg-white md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Game ID" value={game.game_id} />
        <MetricCard label="Release year" value={game.release_year ?? "Unknown"} />
        <MetricCard label="Rating band" value={game.rating_band ?? "Unknown"} />
        <MetricCard label="Extraction cohort" value={game.extraction_cohort ?? "Unknown"} />
        <MetricCard label="Total rating" value={formatRating(game.total_rating)} />
        <MetricCard label="Reviews" value={formatNumber(game.total_rating_count)} />
        <MetricCard
          label="Visibility percentile"
          value={formatPercent(game.custom_interest_percentile)}
        />
        <MetricCard
          label="Normal playtime"
          value={
            game.normal_playtime_hours === null || game.normal_playtime_hours === undefined
              ? "Unknown"
              : `${game.normal_playtime_hours.toFixed(1)} hours`
          }
        />
        <MetricCard label="Reliable rating" value={formatBoolean(game.rating_reliable_flag)} />
        <MetricCard label="Main game" value={formatBoolean(game.main_game_flag)} />
        <MetricCard label="Hidden gem" value={formatBoolean(game.hidden_gem_balanced_flag)} />
        <MetricCard label="RAG ready" value={formatBoolean(game.rag_ready_flag)} />
      </div>

      <ExpandableTextPanel title="Storyline">{game.storyline}</ExpandableTextPanel>

      <div className="grid gap-5 lg:grid-cols-2">
        <TagPanel title="Platforms" values={game.platforms} />
        <TagPanel title="Genres" values={game.genres} />
        <TagPanel title="Themes" values={game.themes} />
        <TagPanel title="Game modes" values={game.game_modes} />
        <TagPanel title="Player perspectives" values={game.player_perspectives} />
        <TagPanel title="Developers" values={game.developers} />
        <TagPanel title="Publishers" values={game.publishers} />
        <TagPanel title="Keywords" values={game.keywords} />
      </div>

      <section className="border border-white bg-black p-5">
        <h3 className="font-mono text-sm uppercase tracking-[0.24em] text-[#FF3E00]">
          Data caveats
        </h3>
        {game.data_caveats.length > 0 ? (
          <ul className="mt-4 list-disc space-y-2 pl-5 text-white/72">
            {game.data_caveats.map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-white/56">No specific caveats were generated for this game.</p>
        )}
      </section>
    </div>
  );
}

export default async function GameDetailPage({
  params,
}: {
  params: { game_id: string };
}) {
  let game: GameDetail | null = null;

  try {
    game = await getCatalogGame(params.game_id);
  } catch {
    game = null;
  }

  if (!game) {
    return (
      <div className="explore-v4-shell">
        <ScrollToTop />
        <div className="explore-v4-content">
          <EmptyState
            title="Game unavailable"
            message="The game detail API is unavailable, or this game was not found in the app catalog."
          />
        </div>
      </div>
    );
  }

  const coverUrl = upgradedImageUrl(game.cover_url, "cover");
  const screenshotUrl = upgradedImageUrl(game.screenshot_url, "wide");

  return (
    <div className="explore-v4-shell">
      <ScrollToTop />
      <div className="explore-v4-content">
        <Link
          href="/explore"
          className="w-fit border border-white bg-black px-5 py-3 font-black uppercase text-white hover:bg-white hover:text-black"
        >
          Back to catalog
        </Link>

        <section className="grid gap-px border border-white bg-white lg:grid-cols-[0.42fr_0.58fr]">
          <div className="bg-black p-5">
            {coverUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={coverUrl}
                alt=""
                className="mx-auto max-h-[34rem] w-full object-contain"
              />
            ) : (
              <div className="grid min-h-96 place-items-center bg-[#050505] font-mono text-sm uppercase tracking-[0.3em] text-white/42">
                No Cover
              </div>
            )}
          </div>

          <div className="bg-black p-8 sm:p-10">
            <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#FF3E00]">
              GAME FILE_ // {game.game_id}
            </p>
            <h1 className="mt-4 font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.88] tracking-[-0.07em] text-white sm:text-7xl">
              {game.name}
            </h1>
            <ExpandableText
              text={game.summary}
              emptyText="No summary is available for this game."
              className="mt-6 max-w-3xl leading-8 text-white/76"
            />

            <div className="mt-8 flex flex-wrap gap-2">
              {game.hidden_gem_balanced_flag && (
                <Link
                  href="/hidden-gems"
                  className="border border-[#FF3E00] bg-[#FF3E00] px-3 py-1 font-mono text-xs uppercase tracking-[0.18em] text-black hover:bg-black hover:text-[#FF3E00]"
                >
                  Hidden gem
                </Link>
              )}
              {game.rag_ready_flag && (
                <span className="border border-white px-3 py-1 font-mono text-xs uppercase tracking-[0.18em] text-white">
                  RAG ready
                </span>
              )}
              {game.rating_reliable_flag && (
                <span className="border border-white px-3 py-1 font-mono text-xs uppercase tracking-[0.18em] text-white">
                  Reliable rating
                </span>
              )}
            </div>
          </div>
        </section>

        {screenshotUrl && (
          <section className="border border-white bg-black p-5">
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
              Screenshot
            </p>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={screenshotUrl}
              alt=""
              className="mt-4 max-h-[34rem] w-full object-contain"
            />
          </section>
        )}

        <DetailSection game={game} />
      </div>
    </div>
  );
}
