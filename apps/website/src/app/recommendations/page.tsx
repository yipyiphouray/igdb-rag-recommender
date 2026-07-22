"use client";

import { useEffect, useMemo, useState } from "react";
import { GameCard } from "@/components/GameCard";
import { getFilterOptions, postRecommendations } from "@/lib/api";
import type {
  FilterOptions,
  RecommendationResponse,
  RecommendationResult,
} from "@/types/api";

type WizardState = {
  platform: string;
  genres: string[];
  themes: string[];
  mood_words: string;
  favorite_games: string;
  playstyle_preferences: string;
  discovery_preference: string;
  rating_quality_importance: string;
  desired_playtime: string;
  max_results: number;
};

type MultiSelectField = "genres" | "themes";

const defaultWizardState: WizardState = {
  platform: "",
  genres: [],
  themes: [],
  mood_words: "",
  favorite_games: "",
  playstyle_preferences: "",
  discovery_preference: "Balanced",
  rating_quality_importance: "Any rating",
  desired_playtime: "Any length",
  max_results: 10,
};

const wizardSteps = [
  {
    id: "platform",
    label: "Platform",
    title: "Where do you want to play?",
    description:
      "Pick one platform so the recommendations stay available for your setup.",
  },
  {
    id: "genres",
    label: "Genres",
    title: "What kind of game sounds good?",
    description: "Select any genres that match what you want right now.",
  },
  {
    id: "themes",
    label: "Themes",
    title: "What world or feeling are you looking for?",
    description: "Choose themes that point the recommender toward the right tone.",
  },
  {
    id: "taste",
    label: "Taste",
    title: "Describe your ideal play session.",
    description:
      "Add mood words and playstyle notes so the match is not only based on filters.",
  },
  {
    id: "recent",
    label: "Recent games",
    title: "What have you played recently?",
    description:
      "Add up to 5 games. These help the recommender understand your taste.",
  },
  {
    id: "preferences",
    label: "Preferences",
    title: "How should we tune the results?",
    description:
      "Choose how much quality, discovery style, playtime, and result count matter.",
  },
  {
    id: "review",
    label: "Review",
    title: "Review your answers.",
    description: "Confirm the profile before generating your recommendations.",
  },
] as const;

const ratingOptions = [
  "Any rating",
  "Good or better (70+)",
  "Highly rated (80+)",
  "Exceptional (90+)",
];

const discoveryOptions = ["Balanced", "Hidden gems", "Popular / visible games"];

const playtimeOptions = [
  "Any length",
  "Shorter games (0-10 hrs)",
  "Medium games (11-30 hrs)",
  "Longer games (31+ hrs)",
];

const loadingSignals = [
  "Parsing profile",
  "Scanning catalog",
  "Comparing metadata",
  "Ranking matches",
  "Checking caveats",
  "Preparing cards",
];

function splitTextList(value: string | null | undefined, maxItems = 8): string[] {
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

function scoreWidth(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "0%";
  }
  return `${Math.min(Math.max(Math.round(value * 100), 0), 100)}%`;
}

function sortPlatformsAlphabetically(platforms: string[]): string[] {
  return [...platforms].sort((left, right) => left.localeCompare(right));
}

function summaryList(summary: Record<string, unknown>, key: string): string[] {
  const value = summary[key];
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map(String).filter(Boolean);
}

function readableExplanation(explanation: string): string {
  return explanation
    .replace(
      "shares metadata similarity with recently played game(s):",
      "feels close to games you recently played:",
    )
    .replace(
      "Recommended because it is one of the closest metadata matches in the current catalog.",
      "This is one of the closest matches based on your answers.",
    )
    .replace("is a documented hidden-gem candidate", "may be a hidden gem")
    .replace(
      "has a stronger known visibility signal",
      "has stronger popularity and visibility signals",
    );
}

function optionButtonClass(selected: boolean): string {
  return [
    "rounded-sm border px-3 py-2 text-left text-sm font-semibold transition",
    "focus:outline-none focus:ring-2 focus:ring-[#ff3e00]/70",
    selected
      ? "border-[#ff3e00] bg-[#ff3e00] text-black shadow-[0_0_22px_rgba(255,62,0,0.28)]"
      : "border-white/15 bg-white/[0.04] text-white hover:border-[#ff3e00]/70 hover:bg-[#ff3e00]/10",
  ].join(" ");
}

function SingleOptionGrid({
  options,
  selected,
  onSelect,
  anyLabel,
}: {
  options: string[];
  selected: string;
  onSelect: (value: string) => void;
  anyLabel?: string;
}) {
  const values = anyLabel ? ["", ...options] : options;

  return (
    <div className="max-h-72 overflow-y-auto pr-1">
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {values.map((option) => {
          const label = option || anyLabel || "Any";
          return (
            <button
              key={label}
              type="button"
              onClick={() => onSelect(option)}
              className={optionButtonClass(selected === option)}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function MultiOptionGrid({
  options,
  selected,
  onToggle,
}: {
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
}) {
  return (
    <div className="max-h-80 overflow-y-auto pr-1">
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onToggle(option)}
            className={optionButtonClass(selected.includes(option))}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

function TextPrompt({
  label,
  helper,
  value,
  placeholder,
  rows = 5,
  onChange,
}: {
  label: string;
  helper: string;
  value: string;
  placeholder: string;
  rows?: number;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid h-full content-start gap-2">
      <span className="text-sm font-black uppercase tracking-[0.18em] text-[#ff3e00]">
        {label}
      </span>
      <textarea
        rows={rows}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="h-52 resize-none rounded-sm border border-white/15 bg-black/60 px-4 py-3 text-white placeholder:text-white/35 focus:border-[#ff3e00] focus:outline-none"
      />
      <span className="min-h-10 text-sm text-white/55">{helper}</span>
    </label>
  );
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-sm border border-white/10 bg-white/[0.04] p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-[#ff3e00]">
        {label}
      </p>
      <p className="mt-2 text-sm text-white/80">{value || "Any"}</p>
    </div>
  );
}

function ScoreBar({
  label,
  value,
  emphasis = false,
  isLast = false,
}: {
  label: string;
  value: number | null | undefined;
  emphasis?: boolean;
  isLast?: boolean;
}) {
  return (
    <div
      className={`flex h-full min-h-0 flex-col justify-center bg-black p-5 ${
        isLast ? "" : "border-b border-white"
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <p
          className={`font-mono text-sm font-black uppercase tracking-[0.18em] ${
            emphasis ? "text-[#ff3e00]" : "text-white"
          }`}
        >
          {label}
        </p>
        <p
          className={`font-mono text-3xl font-black leading-none tracking-[-0.04em] ${
            emphasis ? "text-[#ff3e00]" : "text-white"
          }`}
        >
          {formatPercent(value)}
        </p>
      </div>
      <div className="mt-4 h-6 w-full border border-white bg-black">
        <div
          className={`h-full ${
            emphasis ? "bg-[#ff3e00]" : "bg-white"
          }`}
          style={{ width: scoreWidth(value) }}
        />
      </div>
    </div>
  );
}

function RecommendationCard({ item }: { item: RecommendationResult }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
      <GameCard game={item} openInNewTab />
      <div className="flex h-full flex-col border border-white bg-black p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#ff3e00]">
          Match #{item.rank}
        </p>
        <h3 className="mt-2 text-2xl font-black text-white">{item.name}</h3>
        <p className="mt-4 text-white/75">{readableExplanation(item.explanation)}</p>
        <div className="-mx-6 mt-6 grid flex-1 grid-rows-[repeat(3,minmax(0,1fr))] border-y border-white bg-black">
          <ScoreBar label="Overall fit" value={item.match_score} emphasis />
          <ScoreBar label="Taste match" value={item.similarity_score} />
          <ScoreBar label="Discovery fit" value={item.hidden_gem_boost} isLast />
        </div>
        {item.caveats.length > 0 && (
          <ul className="mt-5 list-disc space-y-2 pl-5 text-sm text-white/55">
            {item.caveats.map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function RecommendationLoadingPanel({ progress }: { progress: number }) {
  const signalLock = Math.min(progress, 95);

  return (
    <section
      aria-busy="true"
      aria-live="polite"
      className="recommend-loading-panel border border-[#ff3e00]/45 bg-black p-8 text-white"
    >
      <div className="relative z-10 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
            Matching sequence_
          </p>
          <h3 className="mt-2 text-2xl font-black uppercase tracking-[-0.03em] text-white">
            Generating recommendations
          </h3>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-white/62">
            Matching your answers against game metadata, recent-game signals, and
            catalog quality indicators.
          </p>
        </div>
        <p className="font-mono text-sm font-black uppercase tracking-[0.22em] text-[#ff3e00]">
          Active scan
        </p>
      </div>

      <div className="recommend-loading-track mt-6" aria-hidden="true">
        <span
          className="recommend-loading-track-fill"
          style={{ width: `${signalLock}%` }}
        />
        <span className="recommend-loading-track-scan" />
      </div>

      <div className="mt-2 flex justify-between font-mono text-[10px] uppercase tracking-[0.2em] text-white/45">
        <span>Signal start</span>
        <span>Continuous scan active</span>
        <span>Finalizing on response</span>
      </div>

      <div className="mt-6 grid gap-px border border-white/20 bg-white/20 md:grid-cols-3">
        {loadingSignals.map((signal, index) => (
          <div
            key={signal}
            className="flex items-center gap-3 bg-black px-4 py-3 font-mono text-[10px] uppercase tracking-[0.18em] text-white/64"
          >
            <span
              className="recommend-loading-pip"
              style={{ animationDelay: `${index * 120}ms` }}
            />
            {signal}
          </div>
        ))}
      </div>
    </section>
  );
}

export default function RecommendationsPage() {
  const [options, setOptions] = useState<FilterOptions>({});
  const [wizardState, setWizardState] = useState(defaultWizardState);
  const [stepIndex, setStepIndex] = useState(0);
  const [response, setResponse] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);

  const currentStep = wizardSteps[stepIndex];
  const isReviewStep = currentStep.id === "review";
  const sortedPlatforms = useMemo(
    () => sortPlatformsAlphabetically(options.platforms ?? []),
    [options.platforms],
  );

  const matchedSeedGames = useMemo(
    () => (response ? summaryList(response.request_summary, "matched_seed_games") : []),
    [response],
  );
  const unmatchedSeedGames = useMemo(
    () =>
      response ? summaryList(response.request_summary, "unmatched_seed_games") : [],
    [response],
  );

  useEffect(() => {
    getFilterOptions()
      .then(setOptions)
      .catch(() => setError("Could not load filter options from the API."));
  }, []);

  useEffect(() => {
    if (!loading) {
      return;
    }

    const interval = window.setInterval(() => {
      setLoadingProgress((current) => {
        if (current >= 95) {
          return current;
        }
        return Math.min(current + Math.max(Math.round((100 - current) * 0.12), 2), 95);
      });
    }, 180);

    return () => window.clearInterval(interval);
  }, [loading]);

  function updateField<K extends keyof WizardState>(
    field: K,
    value: WizardState[K],
  ) {
    setWizardState((current) => ({ ...current, [field]: value }));
  }

  function toggleMulti(field: MultiSelectField, value: string) {
    setWizardState((current) => {
      const selected = current[field];
      return {
        ...current,
        [field]: selected.includes(value)
          ? selected.filter((item) => item !== value)
          : [...selected, value],
      };
    });
  }

  function resetWizard() {
    setWizardState(defaultWizardState);
    setStepIndex(0);
    setResponse(null);
    setError("");
  }

  async function generateRecommendations() {
    setLoading(true);
    setLoadingProgress(0);
    setError("");
    setResponse(null);

    const payload = {
      platform: wizardState.platform || null,
      genres: wizardState.genres,
      themes: wizardState.themes,
      mood_words: splitTextList(wizardState.mood_words),
      favorite_games: splitTextList(wizardState.favorite_games, 5),
      playstyle_preferences: splitTextList(wizardState.playstyle_preferences),
      discovery_preference: wizardState.discovery_preference,
      rating_quality_importance: wizardState.rating_quality_importance,
      desired_playtime: wizardState.desired_playtime,
      max_results: wizardState.max_results,
    };

    try {
      const result = await postRecommendations(payload);
      setLoadingProgress(100);
      setResponse(result);
    } catch {
      setLoadingProgress(100);
      setError(
        "Recommendation API is unavailable. Start the FastAPI backend and try again.",
      );
    } finally {
      window.setTimeout(() => setLoading(false), 350);
    }
  }

  function renderStep() {
    if (currentStep.id === "platform") {
      return (
        <SingleOptionGrid
          anyLabel="Any platform"
          options={sortedPlatforms}
          selected={wizardState.platform}
          onSelect={(value) => updateField("platform", value)}
        />
      );
    }

    if (currentStep.id === "genres") {
      return (
        <MultiOptionGrid
          options={options.genres ?? []}
          selected={wizardState.genres}
          onToggle={(value) => toggleMulti("genres", value)}
        />
      );
    }

    if (currentStep.id === "themes") {
      return (
        <MultiOptionGrid
          options={options.themes ?? []}
          selected={wizardState.themes}
          onToggle={(value) => toggleMulti("themes", value)}
        />
      );
    }

    if (currentStep.id === "taste") {
      return (
        <div className="grid items-stretch gap-5 lg:grid-cols-2">
          <TextPrompt
            label="Mood words"
            helper="Use simple words or short phrases. Separate them with commas or new lines."
            value={wizardState.mood_words}
            placeholder="immersive, cozy, story-rich, strategic"
            rows={6}
            onChange={(value) => updateField("mood_words", value)}
          />
          <TextPrompt
            label="Playstyle"
            helper="Describe how you like to play. Separate ideas with commas or new lines."
            value={wizardState.playstyle_preferences}
            placeholder="single-player, turn-based, exploration, co-op"
            rows={6}
            onChange={(value) => updateField("playstyle_preferences", value)}
          />
        </div>
      );
    }

    if (currentStep.id === "recent") {
      return (
        <TextPrompt
          label="Recent games"
          helper="Add up to 5 games you played recently. Use one per line or commas."
          value={wizardState.favorite_games}
          placeholder={"Baldur's Gate 3\nDisco Elysium\nStardew Valley"}
          rows={7}
          onChange={(value) => updateField("favorite_games", value)}
        />
      );
    }

    if (currentStep.id === "preferences") {
      return (
        <div className="grid gap-6">
          <div>
            <p className="mb-3 text-sm font-black uppercase tracking-[0.18em] text-[#ff3e00]">
              Discovery style
            </p>
            <SingleOptionGrid
              options={discoveryOptions}
              selected={wizardState.discovery_preference}
              onSelect={(value) => updateField("discovery_preference", value)}
            />
          </div>
          <div>
            <p className="mb-3 text-sm font-black uppercase tracking-[0.18em] text-[#ff3e00]">
              Quality preference
            </p>
            <SingleOptionGrid
              options={ratingOptions}
              selected={wizardState.rating_quality_importance}
              onSelect={(value) =>
                updateField("rating_quality_importance", value)
              }
            />
          </div>
          <div>
            <p className="mb-3 text-sm font-black uppercase tracking-[0.18em] text-[#ff3e00]">
              Playtime
            </p>
            <SingleOptionGrid
              options={playtimeOptions}
              selected={wizardState.desired_playtime}
              onSelect={(value) => updateField("desired_playtime", value)}
            />
          </div>
          <label className="grid gap-2">
            <span className="text-sm font-black uppercase tracking-[0.18em] text-[#ff3e00]">
              Number of results
            </span>
            <input
              type="number"
              min="1"
              max="20"
              value={wizardState.max_results}
              onChange={(event) => {
                const parsed = Number(event.target.value);
                updateField(
                  "max_results",
                  Number.isFinite(parsed)
                    ? Math.min(Math.max(parsed, 1), 20)
                    : defaultWizardState.max_results,
                );
              }}
              className="rounded-sm border border-white/15 bg-black/60 px-4 py-3 text-white focus:border-[#ff3e00] focus:outline-none"
            />
          </label>
        </div>
      );
    }

    return (
      <div className="grid gap-3 md:grid-cols-2">
        <ReviewRow label="Platform" value={wizardState.platform} />
        <ReviewRow label="Genres" value={wizardState.genres.join(", ")} />
        <ReviewRow label="Themes" value={wizardState.themes.join(", ")} />
        <ReviewRow
          label="Mood words"
          value={splitTextList(wizardState.mood_words).join(", ")}
        />
        <ReviewRow
          label="Playstyle"
          value={splitTextList(wizardState.playstyle_preferences).join(", ")}
        />
        <ReviewRow
          label="Recent games"
          value={splitTextList(wizardState.favorite_games, 5).join(", ")}
        />
        <ReviewRow
          label="Discovery style"
          value={wizardState.discovery_preference}
        />
        <ReviewRow
          label="Quality"
          value={wizardState.rating_quality_importance}
        />
        <ReviewRow label="Playtime" value={wizardState.desired_playtime} />
        <ReviewRow
          label="Results"
          value={`${wizardState.max_results} recommendations`}
        />
      </div>
    );
  }

  return (
    <main className="explore-v4-shell">
      <div className="explore-v4-content">
        <section className="relative overflow-hidden border border-white bg-black">
          <div className="absolute left-0 top-0 h-1 w-full bg-[#FF3E00]" />
          <div className="relative bg-black p-8 sm:p-10">
            <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#FF3E00]">
              RECOMMEND ME_ // FIND THE GAME YOUR NEXT SESSION NEEDS
            </p>
            <h1 className="mt-4 max-w-5xl font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.86] tracking-[-0.07em] text-white sm:text-7xl">
              Recommend Me_
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-white/78">
              Answer a few questions and find games that match what you actually
              want to play.
            </p>
          </div>
        </section>

        <section className="border border-white/15 bg-black/75">
          <div className="grid lg:grid-cols-[15rem_1fr]">
            <aside className="border-b border-white/15 p-4 lg:border-b-0 lg:border-r">
              <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
                Wizard menu_
              </p>
              <div className="mt-4 grid gap-2">
                {wizardSteps.map((step, index) => (
                  <button
                    key={step.id}
                    type="button"
                    onClick={() => setStepIndex(index)}
                    className={[
                      "border px-3 py-2 text-left text-xs font-black uppercase tracking-[0.14em] transition",
                      index === stepIndex
                        ? "border-[#ff3e00] bg-[#ff3e00] text-black"
                        : index < stepIndex
                          ? "border-white/20 bg-white/[0.06] text-white"
                          : "border-white/10 bg-white/[0.02] text-white/45",
                    ].join(" ")}
                  >
                    {step.label}
                  </button>
                ))}
              </div>
            </aside>

            <div className="p-5 md:p-7">
              <div className="mb-6">
                <p className="text-xs uppercase tracking-[0.28em] text-white/45">
                  Step {stepIndex + 1} of {wizardSteps.length}
                </p>
                <h2 className="mt-2 text-3xl font-black text-white">
                  {currentStep.title}
                </h2>
                <p className="mt-3 text-white/60">{currentStep.description}</p>
              </div>

              <div className="border border-white/10 bg-white/[0.03] p-5">
                {renderStep()}
              </div>

              <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={resetWizard}
                  className="border border-white/20 px-5 py-3 text-sm font-bold text-white/80 transition hover:border-[#ff3e00] hover:text-white"
                >
                  Reset
                </button>
                <div className="flex flex-wrap gap-3">
                  <button
                    type="button"
                    disabled={stepIndex === 0}
                    onClick={() =>
                      setStepIndex((current) => Math.max(current - 1, 0))
                    }
                    className="border border-white/20 px-5 py-3 text-sm font-bold text-white/80 transition hover:border-white hover:text-white disabled:cursor-not-allowed disabled:opacity-35"
                  >
                    Back
                  </button>
                  {isReviewStep ? (
                    <button
                      type="button"
                      disabled={loading}
                      onClick={generateRecommendations}
                      className="bg-[#ff3e00] px-6 py-3 text-sm font-black text-black transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {loading ? "Generating..." : "Generate recommendations"}
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() =>
                        setStepIndex((current) =>
                          Math.min(current + 1, wizardSteps.length - 1),
                        )
                      }
                      className="bg-white px-6 py-3 text-sm font-black text-black transition hover:bg-[#ff3e00]"
                    >
                      Next
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {loading && <RecommendationLoadingPanel progress={loadingProgress} />}

        {error && (
          <div className="border border-red-300/30 bg-red-500/10 p-5 text-red-100">
            {error}
          </div>
        )}

        {response && (
          <section className="grid gap-5">
            {(matchedSeedGames.length > 0 || unmatchedSeedGames.length > 0) && (
              <div className="grid gap-3 md:grid-cols-2">
                <div className="border border-white/10 bg-black/70 p-5">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#ff3e00]">
                    Recent games understood
                  </p>
                  <p className="mt-2 text-sm text-white/70">
                    {matchedSeedGames.join(", ") || "No recent games matched."}
                  </p>
                </div>
                <div className="border border-white/10 bg-black/70 p-5">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#ff3e00]">
                    Could not match
                  </p>
                  <p className="mt-2 text-sm text-white/70">
                    {unmatchedSeedGames.join(", ") || "Everything matched."}
                  </p>
                </div>
              </div>
            )}

            {response.items.map((item) => (
              <RecommendationCard key={item.game_id} item={item} />
            ))}
          </section>
        )}
      </div>
    </main>
  );
}
