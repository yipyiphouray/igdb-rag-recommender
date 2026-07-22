"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { GameCard } from "@/components/GameCard";
import { getChatStatus, postChatMessage } from "@/lib/api";
import type {
  ChatHistoryMessage,
  ChatResponse,
  ChatRetrievedGame,
  ChatStatusResponse,
} from "@/types/api";

const starterPrompts = [
  "Find games like League of Legends.",
  "Recommend cozy RPGs on Switch.",
  "Find hidden gems with exploration and fantasy themes.",
  "Explain where your answers come from.",
  "Suggest games similar to Stardew Valley but less obvious.",
];

const MAX_GUIDE_USER_TURNS = 8;
const GUIDE_TURN_WARNING_THRESHOLD = 6;
const HISTORY_TURN_LIMIT = 4;

type GuideTurn = {
  id: string;
  question: string;
  response?: ChatResponse;
  error?: string;
  isLoading?: boolean;
};

type ContextItem = {
  label: string;
  value: string;
};

const preferenceLabels: Array<[string, string]> = [
  ["recent_games", "Recent game"],
  ["platforms", "Platform"],
  ["genres", "Genre"],
  ["themes", "Theme"],
  ["moods", "Mood"],
  ["playtime_preference", "Playtime"],
  ["multiplayer_preference", "Multiplayer"],
  ["discovery_preference", "Discovery"],
  ["rating_preference", "Rating signal"],
  ["avoid_terms", "Avoid"],
];

function statusTone(status?: string) {
  if (status === "ready" || status === "success") {
    return "border-[#39ff14] text-[#39ff14]";
  }
  if (status === "no_results" || status === "degraded") {
    return "border-[#ffcc00] text-[#ffcc00]";
  }
  return "border-[#ff3e00] text-[#ff3e00]";
}

function formatPreferenceValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value
      .map((item) => String(item ?? "").trim())
      .filter(Boolean)
      .join(", ");
  }

  if (typeof value === "string") {
    return value.replaceAll("_", " ").trim();
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  return "";
}

function buildContextItems(response?: ChatResponse): ContextItem[] {
  const preferences = response?.interpreted_preferences ?? {};

  return preferenceLabels
    .map(([key, label]) => ({
      label,
      value: formatPreferenceValue(preferences[key]),
    }))
    .filter((item) => item.value.length > 0);
}

function ScopePanel() {
  return (
    <section className="border border-white/15 bg-black/72 p-5">
      <div className="grid gap-4 lg:grid-cols-[0.75fr_1.25fr] lg:items-start">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
            Guide scope_
          </p>
          <h2 className="mt-2 text-2xl font-black uppercase tracking-[-0.04em] text-white">
            Catalog search assistant, not a general chatbot
          </h2>
        </div>
        <div className="grid gap-3 text-sm leading-7 text-white/62">
          <p>
            Use Ask the Guide for catalog-backed game discovery and project
            explanation. Strong prompts include a game you liked, platform,
            genre, mood, playtime, hidden-gem preference, or rating-quality
            signal.
          </p>
          <p>
            Each search thread is capped at {MAX_GUIDE_USER_TURNS} user
            messages. If the topic changes or the thread gets noisy, start a
            fresh search for cleaner recommendations.
          </p>
        </div>
      </div>
    </section>
  );
}

function SearchContextPanel({
  response,
  turnCount,
  onReset,
}: {
  response?: ChatResponse;
  turnCount: number;
  onReset: () => void;
}) {
  const contextItems = buildContextItems(response);
  const progressWidth = `${Math.min(
    100,
    Math.round((turnCount / MAX_GUIDE_USER_TURNS) * 100),
  )}%`;
  const isNearLimit = turnCount >= GUIDE_TURN_WARNING_THRESHOLD;

  return (
    <section className="border border-white/15 bg-black/75 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
            Current search_
          </p>
          <h3 className="mt-2 text-xl font-black uppercase tracking-[-0.04em] text-white">
            Active context
          </h3>
        </div>
        <button
          type="button"
          onClick={onReset}
          className="border border-white/20 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.14em] text-white/75 transition hover:border-[#ff3e00] hover:text-white"
        >
          Start new
        </button>
      </div>

      <div className="mt-4">
        <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
          <span>Thread length</span>
          <span>
            {turnCount}/{MAX_GUIDE_USER_TURNS}
          </span>
        </div>
        <div className="mt-2 h-1 border border-white/15 bg-white/[0.03]">
          <div
            className="h-full bg-[#ff3e00] transition-all"
            style={{ width: progressWidth }}
          />
        </div>
      </div>

      {isNearLimit && (
        <div className="mt-4 border border-[#ffcc00]/35 bg-[#ffcc00]/10 p-3 text-xs leading-6 text-white/72">
          This thread is getting long. Start a new search soon if the
          recommendations begin to feel noisy.
        </div>
      )}

      <div className="mt-5 grid gap-2">
        {contextItems.length > 0 ? (
          contextItems.map((item) => (
            <div
              key={`${item.label}-${item.value}`}
              className="border border-white/10 bg-white/[0.03] p-3"
            >
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/40">
                {item.label}
              </p>
              <p className="mt-1 text-sm font-bold text-white/82">
                {item.value}
              </p>
            </div>
          ))
        ) : (
          <div className="border border-white/10 bg-white/[0.03] p-4 text-sm leading-6 text-white/55">
            No active preferences yet. Start with a game, platform, genre, or
            mood.
          </div>
        )}
      </div>

      {response?.chat_intent && (
        <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.18em] text-white/35">
          Intent: {response.chat_intent}
        </p>
      )}
    </section>
  );
}

function StatusPanel({
  status,
  error,
}: {
  status: ChatStatusResponse | null;
  error: string;
}) {
  const statusLabel = error ? "unavailable" : status?.status ?? "checking";
  const warnings = error ? [error] : status?.warnings ?? [];

  return (
    <section className="grid gap-4 border border-white/15 bg-black/72 p-5 md:grid-cols-[1fr_2fr]">
      <div>
        <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
          Guide status_
        </p>
        <div
          className={`mt-3 inline-flex border px-3 py-1 font-mono text-xs uppercase tracking-[0.18em] ${statusTone(
            statusLabel,
          )}`}
        >
          {statusLabel}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="border border-white/10 bg-white/[0.03] p-3">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
            Catalog
          </p>
          <p className="mt-1 font-black text-white">
            {status?.catalog_available ? "Available" : "Checking"}
          </p>
        </div>
        <div className="border border-white/10 bg-white/[0.03] p-3">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
            Vector store
          </p>
          <p className="mt-1 font-black text-white">
            {status?.vector_store_available ? "Available" : "Checking"}
          </p>
        </div>
        <div className="border border-white/10 bg-white/[0.03] p-3">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
            Engine
          </p>
          <p className="mt-1 font-black text-white">
            {status?.engine ?? "Hybrid RAG"}
          </p>
        </div>
      </div>

      {warnings.length > 0 && (
        <div className="md:col-span-2 border border-[#ff3e00]/30 bg-[#ff3e00]/10 p-4 text-sm leading-6 text-white/78">
          {warnings.join(" ")}
        </div>
      )}
    </section>
  );
}

function GameTitlePreview({ game }: { game: ChatRetrievedGame }) {
  const [previewPosition, setPreviewPosition] = useState<{
    x: number;
    y: number;
  } | null>(null);

  function updatePreviewPosition(clientX: number, clientY: number) {
    const previewWidth = 420;
    const previewHeight = 620;
    const offset = 18;
    const desiredX = clientX + offset;
    const desiredY = clientY - 96;

    if (typeof window === "undefined") {
      setPreviewPosition({
        x: desiredX,
        y: desiredY,
      });
      return;
    }

    const maxX = Math.max(16, window.innerWidth - previewWidth - 16);
    const maxY = Math.max(16, window.innerHeight - previewHeight - 16);

    setPreviewPosition({
      x: Math.min(Math.max(16, desiredX), maxX),
      y: Math.min(Math.max(16, desiredY), maxY),
    });
  }

  return (
    <div
      className="group relative"
      onMouseMove={(event) =>
        updatePreviewPosition(event.clientX, event.clientY)
      }
      onMouseEnter={(event) =>
        updatePreviewPosition(event.clientX, event.clientY)
      }
      onMouseLeave={() => setPreviewPosition(null)}
    >
      <button
        type="button"
        onFocus={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          updatePreviewPosition(rect.right, rect.top);
        }}
        className="flex w-full items-center justify-between gap-4 border border-white/14 bg-white/[0.03] px-4 py-3 text-left transition hover:border-[#ff3e00] focus:border-[#ff3e00] focus:outline-none"
      >
        <span>
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#ff3e00]">
            Match #{game.rank}
          </span>
          <span className="mt-1 block text-lg font-black uppercase tracking-[-0.03em] text-white">
            {game.name}
          </span>
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
          Hover preview
        </span>
      </button>

      {previewPosition && (
        <div
          className="fixed z-50 w-[min(26rem,calc(100vw-2rem))] pointer-events-none"
          style={{
            left: previewPosition.x,
            top: previewPosition.y,
          }}
        >
          <div className="pointer-events-auto border border-[#ff3e00] bg-black p-3 shadow-[0_0_34px_rgba(255,62,0,0.28)]">
            <GameCard game={game} openInNewTab />
            <div className="border-x border-b border-white bg-black p-4">
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#ff3e00]">
                Retrieval evidence_
              </p>
              <p className="mt-2 text-sm leading-6 text-white/68">
                {game.evidence}
              </p>
              <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
                Click the card to open the game page in a new tab.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function RetrievedGameTitleList({ games }: { games: ChatRetrievedGame[] }) {
  return (
    <div className="grid gap-3">
      <div>
        <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#ff3e00]">
          Retrieved titles_
        </p>
        <p className="mt-2 text-sm leading-6 text-white/55">
          Hover over a title to preview the game card. Click the preview card to
          open the detail page in a new tab.
        </p>
      </div>
      <div className="grid gap-2">
        {games.map((game) => (
          <GameTitlePreview key={game.game_id} game={game} />
        ))}
      </div>
    </div>
  );
}

function GuideThinkingBubble() {
  return (
    <div
      aria-busy="true"
      aria-live="polite"
      className="recommend-loading-panel border border-[#ff3e00]/35 bg-black p-5 text-white"
    >
      <div className="relative z-10">
        <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#ff3e00]">
          Guide is searching_
        </p>
        <p className="mt-2 text-sm leading-6 text-white/62">
          Searching semantic vectors, keyword matches, catalog metadata, and
          ranking signals.
        </p>
      </div>

      <div className="recommend-loading-track mt-4" aria-hidden="true">
        <span className="recommend-loading-track-fill" style={{ width: "92%" }} />
        <span className="recommend-loading-track-scan" />
      </div>
    </div>
  );
}

function guideHistoryContent(response: ChatResponse): string {
  const names = response.retrieved_games
    .slice(0, 5)
    .map((game) => game.name)
    .filter(Boolean);

  return [
    response.answer,
    names.length > 0 ? `Retrieved games: ${names.join(", ")}` : "",
  ]
    .filter(Boolean)
    .join(" ");
}

function buildHistory(turns: GuideTurn[]): ChatHistoryMessage[] {
  return turns
    .filter((turn) => turn.response)
    .flatMap((turn) => [
      {
        role: "user" as const,
        content: turn.question,
      },
      {
        role: "guide" as const,
        content: guideHistoryContent(turn.response as ChatResponse),
      },
    ])
    .slice(-(HISTORY_TURN_LIMIT * 2));
}

function ChatTurnPanel({
  turn,
  onFollowUp,
  onReset,
}: {
  turn: GuideTurn;
  onFollowUp: (prompt: string) => void;
  onReset: () => void;
}) {
  const response = turn.response;
  const hasRetrievedGames = Boolean(response?.retrieved_games.length);
  const shouldShowNoResults =
    response?.mode.startsWith("rag_") && response.status === "no_results";

  return (
    <div className="grid gap-4">
      <div className="ml-auto max-w-3xl border border-white bg-white text-black">
        <div className="border-b border-black px-4 py-2 font-mono text-[10px] uppercase tracking-[0.22em]">
          You_
        </div>
        <p className="px-5 py-4 text-base font-semibold leading-7">
          {turn.question}
        </p>
      </div>

      <div className="max-w-5xl border border-white/22 bg-black">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/18 px-4 py-2">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#ff3e00]">
            Guide_
          </p>
          {response && (
            <span
              className={`border px-2 py-1 font-mono text-[10px] uppercase tracking-[0.16em] ${statusTone(
                response.status,
              )}`}
            >
              {response.status}
            </span>
          )}
        </div>

        <div className="p-5">
          {turn.isLoading && <GuideThinkingBubble />}

          {turn.error && (
            <div className="border border-red-300/30 bg-red-500/10 p-4 text-sm leading-6 text-red-100">
              {turn.error}
            </div>
          )}

          {response && (
            <div className="grid gap-5">
              <p className="max-w-4xl text-lg leading-8 text-white/78">
                {response.answer}
              </p>

              {response.caveats.length > 0 && (
                <ul className="list-disc space-y-2 pl-5 text-sm text-white/55">
                  {response.caveats.map((caveat) => (
                    <li key={caveat}>{caveat}</li>
                  ))}
                </ul>
              )}

              {hasRetrievedGames && (
                <RetrievedGameTitleList games={response.retrieved_games} />
              )}

              {shouldShowNoResults && (
                <div className="border border-white/15 bg-black/75 p-5 text-white/70">
                  No catalog-backed games were returned for this question.
                </div>
              )}

              {response.follow_up_prompts.length > 0 && (
                <div className="border-t border-white/15 pt-5">
                  <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#ff3e00]">
                    Continue the thread_
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {response.follow_up_prompts.map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        onClick={() => onFollowUp(prompt)}
                        className="border border-white/18 bg-white/[0.03] px-3 py-2 text-left text-xs font-bold uppercase tracking-[0.08em] text-white/76 transition hover:border-[#ff3e00] hover:text-white"
                      >
                        {prompt}
                      </button>
                    ))}
                    <button
                      type="button"
                      onClick={onReset}
                      className="border border-[#ff3e00]/55 bg-[#ff3e00]/10 px-3 py-2 text-left text-xs font-bold uppercase tracking-[0.08em] text-[#ff3e00] transition hover:border-[#ff3e00] hover:bg-[#ff3e00] hover:text-black"
                    >
                      Start new search
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function GuidePage() {
  const [message, setMessage] = useState("");
  const [maxResults, setMaxResults] = useState(5);
  const [chatStatus, setChatStatus] = useState<ChatStatusResponse | null>(null);
  const [statusError, setStatusError] = useState("");
  const [turns, setTurns] = useState<GuideTurn[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const transcriptRef = useRef<HTMLDivElement | null>(null);

  const trimmedMessage = useMemo(() => message.trim(), [message]);
  const latestResponse = useMemo(
    () =>
      turns
        .slice()
        .reverse()
        .find((turn) => turn.response)?.response,
    [turns],
  );
  const userTurnCount = turns.length;
  const hasReachedTurnLimit = userTurnCount >= MAX_GUIDE_USER_TURNS;
  const isNearTurnLimit = userTurnCount >= GUIDE_TURN_WARNING_THRESHOLD;

  useEffect(() => {
    getChatStatus()
      .then((result) => {
        setChatStatus(result);
        setStatusError("");
      })
      .catch(() => {
        setStatusError("Could not reach the FastAPI chatbot status endpoint.");
      });
  }, []);

  useEffect(() => {
    const transcript = transcriptRef.current;
    if (!transcript) {
      return;
    }

    transcript.scrollTo({
      top: transcript.scrollHeight,
      behavior: "smooth",
    });
  }, [turns]);

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (!trimmedMessage) {
      setError("Type a game discovery question before asking the guide.");
      return;
    }

    if (hasReachedTurnLimit) {
      setError(
        "This Guide thread reached its message limit. Start a new search for cleaner recommendations.",
      );
      return;
    }

    const turnId =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}`;
    const question = trimmedMessage;
    const history = buildHistory(turns);

    setLoading(true);
    setMessage("");
    setTurns((current) => [
      ...current,
      {
        id: turnId,
        question,
        isLoading: true,
      },
    ]);

    try {
      const result = await postChatMessage({
        message: question,
        max_results: maxResults,
        history,
      });
      setTurns((current) =>
        current.map((turn) =>
          turn.id === turnId
            ? { ...turn, response: result, isLoading: false }
            : turn,
        ),
      );
    } catch {
      setTurns((current) =>
        current.map((turn) =>
          turn.id === turnId
            ? {
                ...turn,
                error:
                  "Chat API is unavailable. Start the FastAPI backend and try again.",
                isLoading: false,
              }
            : turn,
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  function resetChat() {
    setMessage("");
    setTurns([]);
    setError("");
  }

  function useFollowUp(prompt: string) {
    if (hasReachedTurnLimit) {
      setError(
        "This Guide thread reached its message limit. Start a new search before continuing.",
      );
      return;
    }
    setMessage(prompt);
  }

  return (
    <main className="explore-v4-shell">
      <div className="explore-v4-content">
        <section className="relative overflow-hidden border border-white bg-black">
          <div className="absolute left-0 top-0 h-1 w-full bg-[#ff3e00]" />
          <div className="relative bg-black p-8 sm:p-10">
            <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#ff3e00]">
              ASK THE GUIDE_ // CATALOG-GROUNDED DISCOVERY
            </p>
            <h1 className="mt-4 max-w-5xl font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.86] tracking-[-0.07em] text-white sm:text-7xl">
              Ask the Guide_
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-white/78">
              Ask a natural-language question and get game suggestions grounded
              in the project catalog, hybrid retrieval, and metadata caveats.
            </p>
          </div>
        </section>

        <StatusPanel status={chatStatus} error={statusError} />

        <ScopePanel />

        <section className="grid gap-5 lg:grid-cols-[1.25fr_0.75fr]">
          <section className="border border-white/15 bg-black/75 p-5">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/15 pb-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
                  Conversation_
                </p>
                <h2 className="mt-2 text-2xl font-black uppercase tracking-[-0.04em] text-white">
                  Talk to the guide
                </h2>
              </div>
              <button
                type="button"
                onClick={resetChat}
                className="border border-white/20 px-4 py-2 text-xs font-bold uppercase tracking-[0.14em] text-white/80 transition hover:border-white hover:text-white"
              >
                Clear chat
              </button>
            </div>

            <div
              ref={transcriptRef}
              className="guide-chat-scroll mt-5 grid max-h-[min(34rem,65vh)] min-h-[22rem] content-start gap-6 overflow-y-auto overflow-x-visible pr-2"
            >
              {turns.length === 0 ? (
                <div className="max-w-4xl border border-white/22 bg-black">
                  <div className="border-b border-white/18 px-4 py-2 font-mono text-[10px] uppercase tracking-[0.22em] text-[#ff3e00]">
                    Guide_
                  </div>
                  <div className="p-5">
                    <p className="text-lg leading-8 text-white/78">
                      Ask me what kind of game you want to find. I will search
                      the project catalog and reply with grounded suggestions.
                    </p>
                    <p className="mt-3 text-sm leading-7 text-white/55">
                      Try mentioning platform, genre, mood, playstyle, or a
                      recent game you liked.
                    </p>
                  </div>
                </div>
              ) : (
                turns.map((turn) => (
                  <ChatTurnPanel
                    key={turn.id}
                    turn={turn}
                    onFollowUp={useFollowUp}
                    onReset={resetChat}
                  />
                ))
              )}
            </div>

            {hasReachedTurnLimit && (
              <div className="mt-5 border border-[#ff3e00]/45 bg-[#ff3e00]/10 p-5">
                <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#ff3e00]">
                  Thread limit reached_
                </p>
                <p className="mt-2 text-sm leading-6 text-white/72">
                  This search thread has reached {MAX_GUIDE_USER_TURNS} user
                  messages. Start a new search to avoid noisy recommendation
                  context.
                </p>
                <button
                  type="button"
                  onClick={resetChat}
                  className="mt-4 bg-[#ff3e00] px-4 py-2 text-xs font-black uppercase tracking-[0.12em] text-black transition hover:bg-white"
                >
                  Start new search
                </button>
              </div>
            )}

            <form
              onSubmit={submitQuestion}
              className="mt-6 border-t border-white/15 pt-5"
            >
              <label className="grid gap-3">
                <span className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
                  Message_
                </span>
                <textarea
                  value={message}
                  rows={4}
                  disabled={hasReachedTurnLimit}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Recommend atmospheric RPGs on PC with strong story and exploration."
                  className="resize-none border border-white/15 bg-black px-4 py-4 text-white placeholder:text-white/35 focus:border-[#ff3e00] focus:outline-none disabled:cursor-not-allowed disabled:opacity-45"
                />
              </label>

              <div className="mt-5 grid gap-4 sm:grid-cols-[1fr_auto] sm:items-end">
                <label className="grid gap-2">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-white/45">
                    Results
                  </span>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={maxResults}
                    onChange={(event) => {
                      const parsed = Number(event.target.value);
                      setMaxResults(
                        Number.isFinite(parsed)
                          ? Math.min(Math.max(parsed, 1), 10)
                          : 5,
                      );
                    }}
                    className="w-full border border-white/15 bg-black px-4 py-3 text-white focus:border-[#ff3e00] focus:outline-none sm:w-36"
                  />
                </label>

                <button
                  type="submit"
                  disabled={loading || hasReachedTurnLimit}
                  className="bg-[#ff3e00] px-6 py-3 text-sm font-black text-black transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Guide is thinking..."
                    : hasReachedTurnLimit
                      ? "Thread limit reached"
                      : "Send message"}
                </button>
              </div>
            </form>
          </section>

          <aside className="grid content-start gap-5">
            <SearchContextPanel
              response={latestResponse}
              turnCount={userTurnCount}
              onReset={resetChat}
            />

            <section className="border border-white/15 bg-black/75 p-6">
              <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
                Prompt starters_
              </p>
              <div className="mt-4 grid gap-2">
                {starterPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    disabled={hasReachedTurnLimit}
                    onClick={() => setMessage(prompt)}
                    className="border border-white/12 bg-white/[0.03] px-4 py-3 text-left text-sm leading-6 text-white/75 transition hover:border-[#ff3e00] hover:text-white disabled:cursor-not-allowed disabled:opacity-45"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
              <p className="mt-5 text-sm leading-7 text-white/55">
                The guide answers from retrieved project data. If the catalog is
                missing a field, it should disclose that limitation instead of
                guessing.
              </p>
              {isNearTurnLimit && !hasReachedTurnLimit && (
                <p className="mt-4 border border-[#ffcc00]/30 bg-[#ffcc00]/10 p-3 text-xs leading-6 text-white/68">
                  You are close to the thread limit. Use Start New when you
                  switch topics.
                </p>
              )}
            </section>
          </aside>
        </section>

        {error && (
          <div className="border border-red-300/30 bg-red-500/10 p-5 text-red-100">
            {error}
          </div>
        )}
      </div>
    </main>
  );
}
