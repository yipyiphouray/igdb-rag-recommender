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
  "Recommend story-rich RPGs on PC.",
  "Find hidden gems with exploration and fantasy themes.",
  "What are good co-op games with strong ratings?",
  "Suggest games similar to Stardew Valley but less obvious.",
  "Find shorter games with atmospheric worlds.",
];

type GuideTurn = {
  id: string;
  question: string;
  response?: ChatResponse;
  error?: string;
  isLoading?: boolean;
};

function statusTone(status?: string) {
  if (status === "ready" || status === "success") {
    return "border-[#39ff14] text-[#39ff14]";
  }
  if (status === "no_results" || status === "degraded") {
    return "border-[#ffcc00] text-[#ffcc00]";
  }
  return "border-[#ff3e00] text-[#ff3e00]";
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
    .slice(-10);
}

function ChatTurnPanel({
  turn,
  onFollowUp,
}: {
  turn: GuideTurn;
  onFollowUp: (prompt: string) => void;
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
                  />
                ))
              )}
            </div>

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
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Recommend atmospheric RPGs on PC with strong story and exploration."
                  className="resize-none border border-white/15 bg-black px-4 py-4 text-white placeholder:text-white/35 focus:border-[#ff3e00] focus:outline-none"
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
                  disabled={loading}
                  className="bg-[#ff3e00] px-6 py-3 text-sm font-black text-black transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? "Guide is thinking..." : "Send message"}
                </button>
              </div>
            </form>
          </section>

          <aside className="border border-white/15 bg-black/75 p-6">
            <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
              Prompt starters_
            </p>
            <div className="mt-4 grid gap-2">
              {starterPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => setMessage(prompt)}
                  className="border border-white/12 bg-white/[0.03] px-4 py-3 text-left text-sm leading-6 text-white/75 transition hover:border-[#ff3e00] hover:text-white"
                >
                  {prompt}
                </button>
              ))}
            </div>
            <p className="mt-5 text-sm leading-7 text-white/55">
              The guide should only answer from retrieved project data. If the
              catalog is missing a field, the response should disclose that
              limitation instead of guessing.
            </p>
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
