import { EmptyState } from "@/components/EmptyState";
import { GameCard } from "@/components/GameCard";
import { getCatalogGames, getFilterOptions } from "@/lib/api";

type ExploreSearchParams = {
  search?: string;
  platform?: string;
  genre?: string;
  theme?: string;
  sort?: string;
  page?: string;
};

function buildQuery(searchParams: ExploreSearchParams) {
  const params = new URLSearchParams();
  params.set("page_size", "12");

  Object.entries(searchParams).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });

  return params.toString();
}

export default async function ExplorePage({
  searchParams,
}: {
  searchParams: ExploreSearchParams;
}) {
  let catalog = null;
  let options = null;
  let error = "";

  try {
    [catalog, options] = await Promise.all([
      getCatalogGames(buildQuery(searchParams)),
      getFilterOptions(),
    ]);
  } catch {
    error = "The catalog API is unavailable. Start the FastAPI backend and refresh this page.";
  }

  return (
    <>
      <section className="cyber-panel rounded-3xl p-8">
        <p className="text-sm uppercase tracking-[0.34em] text-cyan-200/80">
          Explore
        </p>
        <h2 className="mt-3 text-4xl font-black text-white">
          Browse the curated game catalog.
        </h2>
        <p className="mt-4 max-w-3xl text-slate-300">
          This page reads the app-ready catalog through the FastAPI backend.
          It proves the final website can render real project data without
          depending on Streamlit.
        </p>
      </section>

      <form className="cyber-panel grid gap-4 rounded-2xl p-5 md:grid-cols-5">
        <input
          name="search"
          defaultValue={searchParams.search ?? ""}
          placeholder="Search title or summary"
          className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-sm text-white outline-none focus:border-cyan-200 md:col-span-2"
        />
        <select
          name="platform"
          defaultValue={searchParams.platform ?? ""}
          className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-sm text-white outline-none focus:border-cyan-200"
        >
          <option value="">Any platform</option>
          {(options?.platforms ?? []).slice(0, 120).map((platform) => (
            <option key={platform} value={platform}>
              {platform}
            </option>
          ))}
        </select>
        <select
          name="genre"
          defaultValue={searchParams.genre ?? ""}
          className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-sm text-white outline-none focus:border-cyan-200"
        >
          <option value="">Any genre</option>
          {(options?.genres ?? []).map((genre) => (
            <option key={genre} value={genre}>
              {genre}
            </option>
          ))}
        </select>
        <select
          name="sort"
          defaultValue={searchParams.sort ?? "highest_rating"}
          className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-sm text-white outline-none focus:border-cyan-200"
        >
          <option value="highest_rating">Highest rating</option>
          <option value="most_rating_evidence">Most rating evidence</option>
          <option value="highest_visibility">Highest visibility</option>
          <option value="newest_release">Newest release</option>
          <option value="name">Name</option>
        </select>
        <button
          type="submit"
          className="rounded-xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 shadow-neon transition hover:bg-white md:col-span-5"
        >
          Apply filters
        </button>
      </form>

      {error ? (
        <EmptyState title="Catalog unavailable" message={error} />
      ) : catalog && catalog.items.length > 0 ? (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-300">
            <p>
              Showing page {catalog.page} of {catalog.total_pages} ·{" "}
              {catalog.total_items.toLocaleString()} matching games
            </p>
          </div>
          <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {catalog.items.map((game) => (
              <GameCard key={game.game_id} game={game} />
            ))}
          </section>
        </>
      ) : (
        <EmptyState
          title="No games found"
          message="Try removing a filter or searching for a broader term."
        />
      )}
    </>
  );
}
