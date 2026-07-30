import Link from "next/link";

import { EmptyState } from "@/components/EmptyState";
import { ExploreFilterForm } from "@/components/ExploreFilterForm";
import { GameCard } from "@/components/GameCard";
import { getCatalogGames, getFilterOptions } from "@/lib/api";

type QueryValue = string | string[] | undefined;

type ExploreSearchParams = {
  search?: QueryValue;
  platform?: QueryValue;
  genre?: QueryValue;
  theme?: QueryValue;
  release_year_min?: QueryValue;
  release_year_max?: QueryValue;
  min_rating?: QueryValue;
  min_reviews?: QueryValue;
  sort?: QueryValue;
  view?: QueryValue;
  page?: QueryValue;
};

type PageItem = number | "ellipsis";

function valuesFor(value: QueryValue): string[] {
  if (!value) return [];
  return Array.isArray(value) ? value.filter(Boolean) : [value].filter(Boolean);
}

function firstValue(value: QueryValue): string {
  return valuesFor(value)[0] ?? "";
}

function appendValues(params: URLSearchParams, key: string, values: string[]) {
  values.forEach((value) => {
    if (value) params.append(key, value);
  });
}

function buildCatalogQuery(searchParams: ExploreSearchParams) {
  const params = new URLSearchParams();
  params.set("page_size", "12");

  const singleValueKeys = [
    "search",
    "release_year_min",
    "release_year_max",
    "min_rating",
    "min_reviews",
    "sort",
    "page",
  ] as const;

  singleValueKeys.forEach((key) => {
    const value = firstValue(searchParams[key]);
    if (value) params.set(key, value);
  });

  appendValues(params, "platform", valuesFor(searchParams.platform));
  appendValues(params, "genre", valuesFor(searchParams.genre));
  appendValues(params, "theme", valuesFor(searchParams.theme));

  return params.toString();
}

function buildExploreHref(
  searchParams: ExploreSearchParams,
  overrides: Record<string, string | null>,
) {
  const params = new URLSearchParams();

  const keys = [
    "search",
    "platform",
    "genre",
    "theme",
    "release_year_min",
    "release_year_max",
    "min_rating",
    "min_reviews",
    "sort",
    "view",
    "page",
  ] as const;

  keys.forEach((key) => {
    appendValues(params, key, valuesFor(searchParams[key]));
  });

  Object.entries(overrides).forEach(([key, value]) => {
    params.delete(key);
    if (value) params.set(key, value);
  });

  const query = params.toString();
  return query ? `/explore?${query}` : "/explore";
}

function paginationItems(currentPage: number, totalPages: number): PageItem[] {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, index) => index + 1);
  }

  const pages = new Set<number>([
    1,
    totalPages,
    currentPage,
    currentPage - 1,
    currentPage + 1,
  ]);

  if (currentPage <= 3) {
    pages.add(2);
    pages.add(3);
    pages.add(4);
  }

  if (currentPage >= totalPages - 2) {
    pages.add(totalPages - 1);
    pages.add(totalPages - 2);
    pages.add(totalPages - 3);
  }

  const sortedPages = Array.from(pages)
    .filter((page) => page >= 1 && page <= totalPages)
    .sort((a, b) => a - b);

  return sortedPages.flatMap((page, index) => {
    const previous = sortedPages[index - 1];
    if (previous && page - previous > 1) {
      return ["ellipsis" as const, page];
    }
    return [page];
  });
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
      getCatalogGames(buildCatalogQuery(searchParams)),
      getFilterOptions(),
    ]);
  } catch {
    error =
      "The catalog API is unavailable. Start the FastAPI backend and refresh this page.";
  }

  const releaseYears = options?.release_years ?? [];
  const platforms = options?.platforms ?? [];
  const genres = options?.genres ?? [];
  const themes = (options?.themes ?? []).slice(0, 28);
  const currentView = firstValue(searchParams.view) === "list" ? "list" : "grid";
  const selectedSort = firstValue(searchParams.sort) || "highest_rating";
  const selectedCount =
    valuesFor(searchParams.platform).length +
    valuesFor(searchParams.genre).length +
    valuesFor(searchParams.theme).length;

  return (
    <div className="explore-v4-shell">
      <div className="explore-v4-content">
      <section className="relative overflow-hidden border border-white bg-black">
        <div className="absolute left-0 top-0 h-1 w-full bg-[#FF3E00]" />
        <div className="relative bg-black p-8 sm:p-10">
          <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#FF3E00]">
            EXPLORE_ // GAME DISCOVERY GRID
          </p>
          <h2 className="mt-4 max-w-5xl font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.86] tracking-[-0.07em] text-white sm:text-7xl">
            Explore the catalog. Find your next world_
          </h2>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-white/78">
            Use search, filters, sorting, and view controls to quickly browse
            the game catalog and narrow it down to titles that match what you
            want to play.
          </p>
        </div>
      </section>

      <ExploreFilterForm
        searchParams={searchParams}
        releaseYears={releaseYears}
        platforms={platforms}
        genres={genres}
        themes={themes}
        currentView={currentView}
        selectedSort={selectedSort}
        selectedCount={selectedCount}
      />

      {error ? (
        <EmptyState title="Catalog unavailable" message={error} />
      ) : catalog && catalog.items.length > 0 ? (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3 border border-white bg-black p-4 font-mono text-xs uppercase tracking-[0.18em] text-white/72">
            <p>
              Page {catalog.page} of {catalog.total_pages} //{" "}
              {catalog.total_items.toLocaleString()} matching games
            </p>
            <p>{currentView.toUpperCase()} VIEW</p>
          </div>

          <section
            className={
              currentView === "list"
                ? "grid gap-5"
                : "grid gap-5 md:grid-cols-2 xl:grid-cols-3"
            }
          >
            {catalog.items.map((game) => (
              <GameCard key={game.game_id} game={game} variant={currentView} />
            ))}
          </section>

          <nav
            aria-label="Catalog pagination"
            className="flex flex-wrap items-center justify-center gap-2 border border-white bg-black p-3"
          >
            <Link
              href={buildExploreHref(searchParams, {
                page: String(Math.max(catalog.page - 1, 1)),
              })}
              scroll={false}
              aria-disabled={catalog.page <= 1}
              className={`border border-white px-5 py-3 font-black uppercase ${
                catalog.page <= 1
                  ? "pointer-events-none bg-black text-white/30"
                  : "bg-black text-white hover:bg-[#FF3E00] hover:text-black"
              }`}
            >
              Previous
            </Link>
            {paginationItems(catalog.page, catalog.total_pages).map((item, index) =>
              item === "ellipsis" ? (
                <span
                  key={`ellipsis-${index}`}
                  className="border border-white/20 bg-black px-4 py-3 font-mono text-white/42"
                >
                  ...
                </span>
              ) : (
                <Link
                  key={item}
                  href={buildExploreHref(searchParams, { page: String(item) })}
                  scroll={false}
                  aria-current={item === catalog.page ? "page" : undefined}
                  className={`min-w-12 border border-white px-4 py-3 text-center font-black ${
                    item === catalog.page
                      ? "bg-white text-black"
                      : "bg-black text-white hover:bg-white hover:text-black"
                  }`}
                >
                  {item}
                </Link>
              ),
            )}
            <Link
              href={buildExploreHref(searchParams, {
                page: String(Math.min(catalog.page + 1, catalog.total_pages)),
              })}
              scroll={false}
              aria-disabled={catalog.page >= catalog.total_pages}
              className={`border border-white px-5 py-3 font-black uppercase ${
                catalog.page >= catalog.total_pages
                  ? "pointer-events-none bg-black text-white/30"
                  : "bg-black text-white hover:bg-[#FF3E00] hover:text-black"
              }`}
            >
              Next
            </Link>
          </nav>
        </>
      ) : (
        <EmptyState
          title="No games found"
          message="Try removing a filter or searching for a broader term."
        />
      )}
      </div>
    </div>
  );
}
