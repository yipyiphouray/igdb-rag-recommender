"use client";

import { FormEvent, useEffect, useState } from "react";
import { GameCard } from "@/components/GameCard";
import { postRecommendations, getFilterOptions } from "@/lib/api";
import type {
  FilterOptions,
  RecommendationResponse,
  RecommendationResult,
} from "@/types/api";

const ratingOptions = [
  "Any rating",
  "Good or better (70+)",
  "Highly rated (80+)",
  "Exceptional (90+)",
];

const discoveryOptions = ["Balanced", "Hidden gems", "Popular / visible games"];

function splitTextList(value: FormDataEntryValue | null, maxItems = 8): string[] {
  return String(value ?? "")
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, maxItems);
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return `${Math.round(value * 100)}%`;
}

function summaryList(
  summary: Record<string, unknown>,
  key: string,
): string[] {
  const value = summary[key];
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map(String).filter(Boolean);
}

function RecommendationCard({ item }: { item: RecommendationResult }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
      <GameCard game={item} />
      <div className="cyber-panel rounded-2xl p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200/70">
          Rank #{item.rank}
        </p>
        <h3 className="mt-2 text-2xl font-black text-white">{item.name}</h3>
        <p className="mt-4 text-slate-300">{item.explanation}</p>
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <div className="rounded-xl border border-cyan-200/10 bg-black/20 p-3">
            <p className="text-xs text-slate-400">Match score</p>
            <p className="font-bold text-cyan-100">{formatPercent(item.match_score)}</p>
          </div>
          <div className="rounded-xl border border-cyan-200/10 bg-black/20 p-3">
            <p className="text-xs text-slate-400">Similarity</p>
            <p className="font-bold text-cyan-100">{formatPercent(item.similarity_score)}</p>
          </div>
          <div className="rounded-xl border border-cyan-200/10 bg-black/20 p-3">
            <p className="text-xs text-slate-400">Discovery fit</p>
            <p className="font-bold text-cyan-100">{formatPercent(item.hidden_gem_boost)}</p>
          </div>
        </div>
        {item.caveats.length > 0 && (
          <ul className="mt-5 list-disc space-y-2 pl-5 text-sm text-slate-400">
            {item.caveats.map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function RecommendationsPage() {
  const [options, setOptions] = useState<FilterOptions>({});
  const [response, setResponse] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getFilterOptions()
      .then(setOptions)
      .catch(() => setError("Could not load filter options from the API."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResponse(null);

    const formData = new FormData(event.currentTarget);
    const payload = {
      platform: String(formData.get("platform") ?? "") || null,
      genres: formData.getAll("genres").map(String),
      themes: formData.getAll("themes").map(String),
      mood_words: splitTextList(formData.get("mood_words")),
      favorite_games: splitTextList(formData.get("favorite_games"), 5),
      playstyle_preferences: splitTextList(formData.get("playstyle_preferences")),
      discovery_preference: String(formData.get("discovery_preference") ?? "Balanced"),
      rating_quality_importance: String(formData.get("rating_quality_importance") ?? "Any rating"),
      desired_playtime: String(formData.get("desired_playtime") ?? "Any length"),
      max_results: Number(formData.get("max_results") ?? 10),
    };

    try {
      const result = await postRecommendations(payload);
      setResponse(result);
    } catch {
      setError("Recommendation API is unavailable. Start the FastAPI backend and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <section className="cyber-panel rounded-3xl p-8">
        <p className="text-sm uppercase tracking-[0.34em] text-cyan-200/80">
          Recommendations
        </p>
        <h2 className="mt-3 text-4xl font-black text-white">
          One recommendation flow, similarity-ready underneath.
        </h2>
        <p className="mt-4 max-w-3xl text-slate-300">
          This page keeps the final product direction clear: users complete one
          flow, while the backend turns preferences and recent games into
          metadata-based cosine similarity matches.
        </p>
      </section>

      <form onSubmit={handleSubmit} className="cyber-panel grid gap-5 rounded-2xl p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">Platform</span>
            <select name="platform" className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white">
              <option value="">Any platform</option>
              {(options.platforms ?? []).slice(0, 120).map((platform) => (
                <option key={platform} value={platform}>
                  {platform}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">Discovery preference</span>
            <select name="discovery_preference" className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white">
              {discoveryOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">Genres</span>
            <select multiple name="genres" className="min-h-44 rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white">
              {(options.genres ?? []).map((genre) => (
                <option key={genre} value={genre}>
                  {genre}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">Themes / mood</span>
            <select multiple name="themes" className="min-h-44 rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white">
              {(options.themes ?? []).map((theme) => (
                <option key={theme} value={theme}>
                  {theme}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">Quality preference</span>
            <select name="rating_quality_importance" className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white">
              {ratingOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">Playtime</span>
            <select name="desired_playtime" className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white">
              <option>Any length</option>
              <option>Shorter games</option>
              <option>Medium games</option>
              <option>Longer games</option>
            </select>
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">Results</span>
            <input
              type="number"
              min="1"
              max="20"
              name="max_results"
              defaultValue="10"
              className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white"
            />
          </label>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <label className="grid gap-2 lg:col-span-1">
            <span className="text-sm font-semibold text-cyan-100">
              Recent games
            </span>
            <textarea
              name="favorite_games"
              rows={5}
              placeholder={"Baldur's Gate 3\nDisco Elysium\nStardew Valley"}
              className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white placeholder:text-slate-500"
            />
            <span className="text-xs text-slate-400">
              Add up to 5 games you played recently. Use one per line or commas.
            </span>
          </label>

          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">
              Mood words
            </span>
            <textarea
              name="mood_words"
              rows={5}
              placeholder="immersive, cozy, story-rich, strategic"
              className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white placeholder:text-slate-500"
            />
            <span className="text-xs text-slate-400">
              These help the model understand the feeling you want.
            </span>
          </label>

          <label className="grid gap-2">
            <span className="text-sm font-semibold text-cyan-100">
              Playstyle
            </span>
            <textarea
              name="playstyle_preferences"
              rows={5}
              placeholder="single-player, turn-based, exploration, co-op"
              className="rounded-xl border border-cyan-200/20 bg-black/30 px-4 py-3 text-white placeholder:text-slate-500"
            />
            <span className="text-xs text-slate-400">
              Use simple phrases describing how you like to play.
            </span>
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 shadow-neon transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Generating..." : "Generate recommendations"}
        </button>
      </form>

      {error && (
        <div className="rounded-2xl border border-red-300/30 bg-red-500/10 p-5 text-red-100">
          {error}
        </div>
      )}

      {response && (
        <section className="grid gap-5">
          <div className="cyber-panel rounded-2xl p-5">
            <p className="text-sm uppercase tracking-[0.24em] text-cyan-200/70">
              Recommendation mode
            </p>
            <h3 className="mt-2 text-2xl font-black text-white">
              {response.mode}
            </h3>
            <p className="mt-2 text-slate-300">
              Similarity status: {response.similarity_status}
            </p>
            {(summaryList(response.request_summary, "matched_seed_games").length > 0 ||
              summaryList(response.request_summary, "unmatched_seed_games").length > 0) && (
              <div className="mt-5 grid gap-3 md:grid-cols-2">
                <div className="rounded-xl border border-cyan-200/10 bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-cyan-200/70">
                    Matched recent games
                  </p>
                  <p className="mt-2 text-sm text-slate-300">
                    {summaryList(response.request_summary, "matched_seed_games").join(", ") ||
                      "None matched"}
                  </p>
                </div>
                <div className="rounded-xl border border-cyan-200/10 bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-cyan-200/70">
                    Unmatched recent games
                  </p>
                  <p className="mt-2 text-sm text-slate-300">
                    {summaryList(response.request_summary, "unmatched_seed_games").join(", ") ||
                      "None"}
                  </p>
                </div>
              </div>
            )}
          </div>
          {response.items.map((item) => (
            <RecommendationCard key={item.game_id} item={item} />
          ))}
        </section>
      )}
    </>
  );
}
