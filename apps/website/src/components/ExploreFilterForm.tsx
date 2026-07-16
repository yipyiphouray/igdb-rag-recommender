"use client";

import Link from "next/link";
import { FormEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";

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

const SORT_OPTIONS = [
  { value: "highest_rating", label: "Highest rating" },
  { value: "most_rating_evidence", label: "Most reviews" },
  { value: "highest_visibility", label: "Highest visibility" },
  { value: "lowest_visibility", label: "Lowest visibility" },
  { value: "newest_release", label: "Newest release" },
  { value: "name", label: "Name" },
];

const MIN_RATING_OPTIONS = [
  { value: "", label: "Any rating" },
  { value: "60", label: "60+" },
  { value: "70", label: "70+" },
  { value: "80", label: "80+" },
  { value: "90", label: "90+" },
];

const MIN_REVIEW_OPTIONS = [
  { value: "", label: "Any reviews" },
  { value: "10", label: "10+" },
  { value: "25", label: "25+" },
  { value: "50", label: "50+" },
  { value: "100", label: "100+" },
];

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

function isChecked(
  searchParams: ExploreSearchParams,
  key: "platform" | "genre" | "theme",
  value: string,
) {
  return valuesFor(searchParams[key]).includes(value);
}

function SelectField({
  label,
  name,
  defaultValue,
  children,
}: {
  label: string;
  name: string;
  defaultValue: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
        {label}
      </span>
      <span className="relative mt-3 block">
        <select
          name={name}
          defaultValue={defaultValue}
          className="w-full appearance-none border border-white/24 bg-black py-3 pl-4 pr-12 text-white outline-none focus:border-[#FF3E00]"
        >
          {children}
        </select>
        <span className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 font-mono text-sm text-[#FF3E00]">
          v
        </span>
      </span>
    </label>
  );
}

function FilterGroup({
  title,
  name,
  options,
  selected,
}: {
  title: string;
  name: "platform" | "genre" | "theme";
  options: string[];
  selected: ExploreSearchParams;
}) {
  return (
    <fieldset className="border border-white/18 bg-black/30 p-4">
      <legend className="px-2 font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
        {title}
      </legend>
      <div className="mt-3 grid max-h-56 gap-2 overflow-y-auto pr-1">
        {options.map((option) => (
          <label
            key={option}
            className="flex cursor-pointer items-center gap-3 border border-white/10 bg-black/40 px-3 py-2.5 text-sm text-white/86 transition hover:border-white/40 hover:bg-white hover:text-black"
          >
            <input
              type="checkbox"
              name={name}
              value={option}
              defaultChecked={isChecked(selected, name, option)}
              className="h-4 w-4 accent-[#FF3E00]"
            />
            <span>{option}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}

export function ExploreFilterForm({
  searchParams,
  releaseYears,
  platforms,
  genres,
  themes,
  currentView,
  selectedSort,
  selectedCount,
}: {
  searchParams: ExploreSearchParams;
  releaseYears: number[];
  platforms: string[];
  genres: string[];
  themes: string[];
  currentView: "grid" | "list";
  selectedSort: string;
  selectedCount: number;
}) {
  const router = useRouter();
  const formRef = useRef<HTMLFormElement>(null);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const formKey = [
    firstValue(searchParams.search),
    valuesFor(searchParams.platform).join("|"),
    valuesFor(searchParams.genre).join("|"),
    valuesFor(searchParams.theme).join("|"),
    firstValue(searchParams.release_year_min),
    firstValue(searchParams.release_year_max),
    firstValue(searchParams.min_rating),
    firstValue(searchParams.min_reviews),
    selectedSort,
    currentView,
  ].join("::");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const params = new URLSearchParams();

    [
      "search",
      "release_year_min",
      "release_year_max",
      "min_rating",
      "min_reviews",
      "sort",
      "view",
    ].forEach((key) => {
      const value = String(formData.get(key) ?? "").trim();
      if (value) params.set(key, value);
    });

    ["platform", "genre", "theme"].forEach((key) => {
      formData.getAll(key).forEach((value) => {
        const text = String(value).trim();
        if (text) params.append(key, text);
      });
    });

    const query = params.toString();
    router.push(query ? `/explore?${query}` : "/explore", { scroll: false });
  }

  function clearFilters() {
    formRef.current?.reset();
    router.push("/explore", { scroll: false });
  }

  return (
    <form
      key={formKey}
      ref={formRef}
      onSubmit={handleSubmit}
      className="border border-white bg-black text-white"
    >
      <input type="hidden" name="view" value={currentView} />

      <div className="grid gap-px bg-white lg:grid-cols-[1.1fr_0.9fr]">
        <div className="bg-black p-5">
          <label className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
            Search
          </label>
          <input
            name="search"
            defaultValue={firstValue(searchParams.search)}
            placeholder="Search title or summary"
            className="mt-3 w-full border border-white/24 bg-black px-4 py-3 text-white outline-none placeholder:text-white/36 focus:border-[#FF3E00]"
          />
        </div>

        <div className="grid gap-px bg-white sm:grid-cols-2">
          <div className="bg-black p-5">
            <SelectField label="Sort" name="sort" defaultValue={selectedSort}>
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </SelectField>
          </div>

          <div className="bg-black p-5">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#FF3E00]">
              View
            </p>
            <div className="mt-3 grid grid-cols-2 gap-px border border-white bg-white">
              <Link
                href={buildExploreHref(searchParams, { view: "grid", page: null })}
                scroll={false}
                className={`px-4 py-3 text-center font-black uppercase ${
                  currentView === "grid"
                    ? "bg-white text-black"
                    : "bg-black text-white hover:bg-white hover:text-black"
                }`}
              >
                Grid
              </Link>
              <Link
                href={buildExploreHref(searchParams, { view: "list", page: null })}
                scroll={false}
                className={`px-4 py-3 text-center font-black uppercase ${
                  currentView === "list"
                    ? "bg-white text-black"
                    : "bg-black text-white hover:bg-white hover:text-black"
                }`}
              >
                List
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-white">
        <button
          type="button"
          aria-expanded={filtersOpen}
          onClick={() => setFiltersOpen((current) => !current)}
          className="flex w-full items-center justify-between bg-black p-5 text-left font-black uppercase tracking-[-0.02em] text-white hover:bg-white hover:text-black"
        >
          <span>Filters_ {selectedCount > 0 ? `// ${selectedCount} active` : ""}</span>
          <span className="font-mono text-2xl leading-none">
            {filtersOpen ? "-" : "+"}
          </span>
        </button>

        <div
          className={
            filtersOpen
              ? "grid gap-5 border-t border-white p-5 xl:grid-cols-3"
              : "hidden"
          }
        >
          <FilterGroup
            title="Platforms"
            name="platform"
            options={platforms}
            selected={searchParams}
          />
          <FilterGroup
            title="Genres"
            name="genre"
            options={genres}
            selected={searchParams}
          />
          <FilterGroup
            title="Themes"
            name="theme"
            options={themes}
            selected={searchParams}
          />
        </div>

        <div
          className={
            filtersOpen
              ? "grid gap-px border-t border-white bg-white md:grid-cols-4"
              : "hidden"
          }
        >
          <div className="bg-black p-5">
            <SelectField
              label="From year"
              name="release_year_min"
              defaultValue={firstValue(searchParams.release_year_min)}
            >
              <option value="">Any start</option>
              {releaseYears.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </SelectField>
          </div>

          <div className="bg-black p-5">
            <SelectField
              label="To year"
              name="release_year_max"
              defaultValue={firstValue(searchParams.release_year_max)}
            >
              <option value="">Any end</option>
              {releaseYears.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </SelectField>
          </div>

          <div className="bg-black p-5">
            <SelectField
              label="Min rating"
              name="min_rating"
              defaultValue={firstValue(searchParams.min_rating)}
            >
              {MIN_RATING_OPTIONS.map((option) => (
                <option key={option.value || "any"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </SelectField>
          </div>

          <div className="bg-black p-5">
            <SelectField
              label="Min reviews"
              name="min_reviews"
              defaultValue={firstValue(searchParams.min_reviews)}
            >
              {MIN_REVIEW_OPTIONS.map((option) => (
                <option key={option.value || "any"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </SelectField>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white p-5">
        <p className="font-mono text-xs uppercase tracking-[0.22em] text-white/58">
          {selectedCount} selected category filters
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={clearFilters}
            className="border border-white px-5 py-3 font-black uppercase text-white hover:bg-white hover:text-black"
          >
            Clear
          </button>
          <button
            type="submit"
            className="border border-white bg-white px-5 py-3 font-black uppercase text-black hover:bg-[#FF3E00]"
          >
            Apply filters
          </button>
        </div>
      </div>
    </form>
  );
}
