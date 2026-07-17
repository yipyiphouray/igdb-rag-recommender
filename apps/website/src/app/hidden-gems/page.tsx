import Link from "next/link";

import { EmptyState } from "@/components/EmptyState";
import { GameCard } from "@/components/GameCard";
import { getCatalogGames } from "@/lib/api";

type QueryValue = string | string[] | undefined;

type HiddenGemsSearchParams = {
  page?: QueryValue;
};

type PageItem = number | "ellipsis";

function firstValue(value: QueryValue): string {
  if (!value) return "";
  return Array.isArray(value) ? value[0] ?? "" : value;
}

function buildHiddenGemsQuery(searchParams: HiddenGemsSearchParams) {
  const params = new URLSearchParams();
  params.set("hidden_gems_only", "true");
  params.set("sort", "lowest_visibility");
  params.set("page_size", "12");

  const page = firstValue(searchParams.page);
  if (page) params.set("page", page);

  return params.toString();
}

function buildHiddenGemsHref(page: number) {
  return page > 1 ? `/hidden-gems?page=${page}` : "/hidden-gems";
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

export default async function HiddenGemsPage({
  searchParams,
}: {
  searchParams: HiddenGemsSearchParams;
}) {
  let catalog = null;
  let error = "";

  try {
    catalog = await getCatalogGames(buildHiddenGemsQuery(searchParams));
  } catch {
    error =
      "The hidden gems catalog is unavailable. Start the FastAPI backend and refresh this page.";
  }

  return (
    <div className="explore-v4-shell">
      <div className="explore-v4-content">
        <section className="relative overflow-hidden border border-white bg-black">
          <div className="absolute left-0 top-0 h-1 w-full bg-[#FF3E00]" />
          <div className="relative bg-black p-8 sm:p-10">
            <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#FF3E00]">
              HIDDEN GEMS_ // LOW VISIBILITY HIGH QUALITY
            </p>
            <h2 className="mt-4 max-w-5xl font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.86] tracking-[-0.07em] text-white sm:text-7xl">
              Hidden Gems_
            </h2>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-white/78">
              Browse games that show strong quality signals but lower visibility in the
              project catalog. This page is for finding worthwhile titles that may be
              easier to miss.
            </p>
          </div>
        </section>

        <section className="grid gap-px border border-white bg-white md:grid-cols-3">
          <div className="bg-black p-5 text-white">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
              Rule_
            </p>
            <p className="mt-3 leading-7 text-white/74">
              Hidden gems are project-defined, not official IGDB labels.
            </p>
          </div>
          <div className="bg-black p-5 text-white">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
              Signal_
            </p>
            <p className="mt-3 leading-7 text-white/74">
              The page focuses on strong rating evidence plus lower visibility.
            </p>
          </div>
          <div className="bg-black p-5 text-white">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
              Sort_
            </p>
            <p className="mt-3 leading-7 text-white/74">
              Results are ordered toward lower-visibility hidden-gem candidates first.
            </p>
          </div>
        </section>

        {error ? (
          <EmptyState title="Hidden gems unavailable" message={error} />
        ) : catalog && catalog.items.length > 0 ? (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3 border border-white bg-black p-4 font-mono text-xs uppercase tracking-[0.18em] text-white/72">
              <p>
                Page {catalog.page} of {catalog.total_pages} //{" "}
                {catalog.total_items.toLocaleString()} hidden gems
              </p>
              <p>GRID VIEW</p>
            </div>

            <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {catalog.items.map((game) => (
                <GameCard key={game.game_id} game={game} variant="grid" />
              ))}
            </section>

            <nav
              aria-label="Hidden gems pagination"
              className="flex flex-wrap items-center justify-center gap-2 border border-white bg-black p-3"
            >
              <Link
                href={buildHiddenGemsHref(Math.max(catalog.page - 1, 1))}
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
                    href={buildHiddenGemsHref(item)}
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
                href={buildHiddenGemsHref(Math.min(catalog.page + 1, catalog.total_pages))}
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
            title="No hidden gems found"
            message="The app catalog did not return hidden-gem candidates from the current backend data."
          />
        )}
      </div>
    </div>
  );
}
