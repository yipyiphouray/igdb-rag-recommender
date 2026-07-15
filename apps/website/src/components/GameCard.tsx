import type { GameSummary } from "@/types/api";

function formatRating(value?: number | null) {
  if (value === null || value === undefined) return "Unrated";
  return `${value.toFixed(1)}/100`;
}

function topItems(values: string[], limit = 3) {
  return values.slice(0, limit);
}

export function GameCard({ game }: { game: GameSummary }) {
  return (
    <article className="cyber-panel flex h-full flex-col overflow-hidden rounded-2xl">
      {game.cover_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={game.cover_url}
          alt=""
          className="h-48 w-full object-cover opacity-90"
        />
      ) : (
        <div className="flex h-48 items-center justify-center bg-cyan-400/5 text-sm uppercase tracking-[0.3em] text-cyan-100/50">
          No Cover
        </div>
      )}
      <div className="flex flex-1 flex-col gap-4 p-5">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-cyan-200/70">
            {game.release_year ?? "Unknown year"}
          </p>
          <h3 className="mt-1 text-xl font-bold text-white">{game.name}</h3>
        </div>

        <p className="line-clamp-4 text-sm leading-6 text-slate-300">
          {game.summary || "No summary is available for this game."}
        </p>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-xl border border-cyan-200/10 bg-black/20 p-3">
            <p className="text-slate-400">Rating</p>
            <p className="font-semibold text-cyan-100">
              {formatRating(game.total_rating)}
            </p>
          </div>
          <div className="rounded-xl border border-cyan-200/10 bg-black/20 p-3">
            <p className="text-slate-400">Evidence</p>
            <p className="font-semibold text-cyan-100">
              {game.total_rating_count ?? "Unknown"}
            </p>
          </div>
        </div>

        <div className="mt-auto flex flex-wrap gap-2">
          {game.hidden_gem_balanced_flag && (
            <span className="rounded-full border border-fuchsia-300/40 bg-fuchsia-400/10 px-3 py-1 text-xs text-fuchsia-100">
              Hidden gem
            </span>
          )}
          {topItems(game.genres).map((genre) => (
            <span
              key={genre}
              className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-xs text-cyan-100"
            >
              {genre}
            </span>
          ))}
        </div>
      </div>
    </article>
  );
}
