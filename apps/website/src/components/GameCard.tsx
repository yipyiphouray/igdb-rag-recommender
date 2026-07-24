import Link from "next/link";

import type { GameSummary } from "@/types/api";

function formatRating(value?: number | null) {
  if (value === null || value === undefined) return "Unrated";
  return `${value.toFixed(1)}/100`;
}

function formatVisibility(value?: number | null) {
  if (value === null || value === undefined) return "Unknown";
  return `${Math.round(value * 100)}%`;
}

function topItems(values: string[], limit = 3) {
  return values.slice(0, limit);
}

function upgradedImageUrl(value?: string | null, size: "cover" | "wide" = "cover") {
  if (!value) return null;
  const normalized = value.startsWith("//") ? `https:${value}` : value;
  const target = size === "wide" ? "t_1080p" : "t_cover_big_2x";
  return normalized.replace(/\/t_[^/]+\//, `/${target}/`);
}

export function GameCard({
  game,
  variant = "grid",
  openInNewTab = false,
}: {
  game: GameSummary;
  variant?: "grid" | "list";
  openInNewTab?: boolean;
}) {
  const isList = variant === "list";
  const imageUrl = upgradedImageUrl(game.cover_url, "cover");

  return (
    <article className="group flex h-full flex-col overflow-hidden border border-white bg-black text-white transition hover:border-[#FF3E00]">
      <Link
        href={`/explore/${game.game_id}`}
        target={openInNewTab ? "_blank" : undefined}
        rel={openInNewTab ? "noreferrer" : undefined}
        className={`flex flex-1 ${isList ? "flex-col md:flex-row" : "flex-col"}`}
      >
        {imageUrl ? (
          <div
            className={`flex shrink-0 items-center justify-center bg-[#050505] ${
              isList ? "h-80 w-full md:w-72 lg:w-80" : "h-80 w-full"
            }`}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt=""
              className="h-full max-h-full w-full max-w-full object-contain p-3 saturate-125 contrast-105"
            />
          </div>
        ) : (
          <div
            className={`flex items-center justify-center bg-[#050505] font-mono text-sm uppercase tracking-[0.3em] text-white/42 ${
              isList ? "h-80 w-full md:w-72 lg:w-80" : "h-80 w-full"
            }`}
          >
            No Cover
          </div>
        )}

        <div
          className={`flex flex-1 flex-col gap-4 border-white/24 p-5 ${
            isList ? "border-t md:border-l md:border-t-0" : "border-t"
          }`}
        >
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#FF3E00]">
              {game.release_year ?? "Unknown year"}
            </p>
            <h3
              className={`mt-2 font-['Arial_Black',Impact,system-ui,sans-serif] uppercase leading-[0.95] tracking-[-0.04em] text-white ${
                isList ? "text-3xl" : "text-2xl"
              }`}
            >
              {game.name}
            </h3>
          </div>

          <p
            className={`${
              isList ? "line-clamp-5" : "line-clamp-4"
            } text-sm leading-6 text-white/72`}
          >
            {game.summary || "No summary is available for this game."}
          </p>

          <div
            className={`grid gap-px bg-white text-sm ${
              isList ? "sm:grid-cols-3" : "grid-cols-2"
            }`}
          >
            <div className="bg-black p-3">
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-white/45">
                Rating
              </p>
              <p className="mt-1 font-black text-white">
                {formatRating(game.total_rating)}
              </p>
            </div>
            <div className="bg-black p-3">
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-white/45">
                Reviews
              </p>
              <p className="mt-1 font-black text-white">
                {game.total_rating_count ?? "Unknown"}
              </p>
            </div>
            {isList && (
              <div className="bg-black p-3">
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-white/45">
                  Visibility
                </p>
                <p className="mt-1 font-black text-white">
                  {formatVisibility(game.custom_interest_percentile)}
                </p>
              </div>
            )}
          </div>

          <p className="mt-auto font-mono text-[10px] uppercase tracking-[0.22em] text-[#FF3E00]">
            Open game file_
          </p>
        </div>
      </Link>

      <div className="flex flex-wrap gap-2 border-t border-white/24 p-5">
        {game.hidden_gem_balanced_flag && (
          <Link
            href="/hidden-gems"
            className="border border-[#FF3E00] bg-[#FF3E00] px-4 py-1.5 font-mono text-xs uppercase tracking-[0.18em] text-black hover:bg-black hover:text-[#FF3E00]"
          >
            Hidden gem
          </Link>
        )}
        {topItems(game.genres).map((genre) => (
          <Link
            key={genre}
            href={`/explore?genre=${encodeURIComponent(genre)}`}
            scroll={false}
            className="border border-white/28 px-4 py-1.5 font-mono text-xs uppercase tracking-[0.16em] text-white/76 hover:border-[#FF3E00] hover:bg-[#FF3E00] hover:text-black"
          >
            {genre}
          </Link>
        ))}
      </div>
    </article>
  );
}
