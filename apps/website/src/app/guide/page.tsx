"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { postChatMessage } from "@/lib/api";
import type { ChatResponse, ChatRouteMode } from "@/types/api";

const MAX_GUIDE_USER_TURNS = 8;

type GuideTurn = {
  id: string;
  question: string;
  routeMode: ChatRouteMode;
  response?: ChatResponse;
  error?: string;
  isLoading?: boolean;
};

type GuideTopic = {
  id: ChatRouteMode;
  label: string;
  eyebrow: string;
  prompt: string;
  description: string;
};

const guideTopics: GuideTopic[] = [
  {
    id: "explain_project",
    label: "Explain this project",
    eyebrow: "Project map",
    prompt: "Explain this project",
    description:
      "Understand the website goal, analytics pillars, and how the pieces fit together.",
  },
  {
    id: "explain_data",
    label: "Explain the data",
    eyebrow: "IGDB catalog",
    prompt: "Explain the data",
    description:
      "Review the IGDB source, catalog fields, data caveats, and metadata limitations.",
  },
  {
    id: "dataset_size",
    label: "How many games are in the dataset?",
    eyebrow: "Dataset fact",
    prompt: "How many games are in the dataset?",
    description:
      "Return the current game count from the structured methodology metrics artifact.",
  },
  {
    id: "dataset_year_range",
    label: "What years does the dataset cover?",
    eyebrow: "Release span",
    prompt: "What years does the dataset cover?",
    description:
      "Show the current release-year range and extraction target per year.",
  },
  {
    id: "rating_coverage",
    label: "What is rating coverage?",
    eyebrow: "Data quality",
    prompt: "What is rating coverage?",
    description:
      "Explain how much of the catalog has usable rating information.",
  },
  {
    id: "explain_recommendation",
    label: "Explain recommendations",
    eyebrow: "Cosine logic",
    prompt: "Explain recommendations",
    description:
      "Learn how structured answers become a preference profile and ranked matches.",
  },
  {
    id: "recommend_me_guidance",
    label: "Help me use Recommend Me",
    eyebrow: "Better inputs",
    prompt: "Help me use Recommend Me",
    description:
      "Understand what inputs to provide before using the main recommendation workflow.",
  },
  {
    id: "explain_hidden_gems",
    label: "Explain hidden gems",
    eyebrow: "Visibility logic",
    prompt: "Explain hidden gems",
    description:
      "Understand how the project balances quality, metadata coverage, and lower visibility.",
  },
  {
    id: "explain_rag",
    label: "Explain RAG",
    eyebrow: "Project method",
    prompt: "Explain RAG",
    description:
      "Clarify how RAG fits the project after simplifying the Guide to controlled responses.",
  },
  {
    id: "search_catalog",
    label: "Where do I browse games?",
    eyebrow: "Explore Games",
    prompt: "Where do I browse games?",
    description:
      "Point users to the catalog browsing and filtering page.",
  },
  {
    id: "website_navigation",
    label: "Website navigation",
    eyebrow: "Site map",
    prompt: "Website navigation",
    description:
      "Explain which website page should be used for each project task.",
  },
  {
    id: "explain_limitations",
    label: "Explain limitations",
    eyebrow: "Caveats",
    prompt: "Explain limitations",
    description:
      "Summarize the known dataset, metadata, and recommendation limitations.",
  },
];

const routeByPrompt = new Map<string, ChatRouteMode>(
  guideTopics.flatMap((topic) => [
    [topic.prompt.toLowerCase(), topic.id],
    [topic.label.toLowerCase(), topic.id],
  ]),
);

function routeModeLabel(mode?: ChatRouteMode | null): string {
  return guideTopics.find((topic) => topic.id === mode)?.label ?? "Guide instruction";
}

function routeModeForPrompt(prompt: string): ChatRouteMode {
  const exactRoute = routeByPrompt.get(prompt.trim().toLowerCase());
  if (exactRoute) {
    return exactRoute;
  }

  const normalized = prompt.toLowerCase();
  if (normalized.includes("how many") || normalized.includes("dataset size")) {
    return "dataset_size";
  }
  if (normalized.includes("year")) {
    return "dataset_year_range";
  }
  if (normalized.includes("rating coverage")) {
    return "rating_coverage";
  }
  if (normalized.includes("hidden gem")) {
    return "explain_hidden_gems";
  }
  if (normalized.includes("recommend")) {
    return "recommend_me_guidance";
  }
  if (normalized.includes("rag")) {
    return "explain_rag";
  }
  if (normalized.includes("data")) {
    return "explain_data";
  }
  if (normalized.includes("navigation") || normalized.includes("website")) {
    return "website_navigation";
  }
  if (normalized.includes("limitation")) {
    return "explain_limitations";
  }
  return "explain_project";
}

function statusTone(status?: string) {
  if (status === "success") {
    return "border-white/45 text-white/72";
  }
  if (status === "no_results" || status === "degraded") {
    return "border-[#ffcc00] text-[#ffcc00]";
  }
  return "border-[#ff3e00] text-[#ff3e00]";
}

function GuideAvatar() {
  return (
    <div className="ask-guide-avatar" aria-hidden="true">
      <div className="ask-guide-face-image-wrap">
        <img
          src="/images/digital-face-representation.jpg"
          alt=""
          className="ask-guide-face-image"
        />
        <span className="ask-guide-face-image-glitch ask-guide-face-image-glitch-red" />
        <span className="ask-guide-face-image-glitch ask-guide-face-image-glitch-white" />
      </div>
      <div className="ask-guide-data-rain">
        <span>CORTANA</span>
        <span>AI</span>
        <span>PROJECTION</span>
        <span>IGDB</span>
        <span>GUIDE</span>
        <span>TRACE</span>
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
        <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
          Guide is selecting response_
        </p>
        <p className="mt-2 text-sm leading-6 text-white/62">
          Reading the selected instruction and returning the matching project
          explanation.
        </p>
      </div>

      <div className="recommend-loading-track mt-4" aria-hidden="true">
        <span className="recommend-loading-track-fill" style={{ width: "88%" }} />
        <span className="recommend-loading-track-scan" />
      </div>
    </div>
  );
}

function RecommendMeCallout() {
  return (
    <section className="ask-guide-lower-callout">
      <div>
        <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#ff3e00]">
          Want game recommendations?_
        </p>
        <h2 className="mt-2 text-2xl font-black uppercase tracking-[-0.05em] text-white">
          Go to Recommend Me_
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-white/62">
          Ask the Guide_ explains the project. Recommend Me_ is the page that
          turns your preferences into ranked game matches.
        </p>
      </div>
      <Link
        href="/recommendations"
        className="inline-flex bg-[#ff3e00] px-5 py-3 text-xs font-black uppercase tracking-[0.14em] text-black transition hover:bg-white"
      >
        Open Recommend Me
      </Link>
    </section>
  );
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
  const shouldShowRecommendMeCta =
    response?.mode === "recommend_me_guidance" ||
    response?.chat_intent === "recommend_me_guidance";

  return (
    <div className="ask-guide-turn grid gap-4">
      <div className="ask-guide-user-command ml-auto max-w-3xl bg-white text-black">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-black px-4 py-2 font-mono text-xs uppercase tracking-[0.22em]">
          <span>You selected_</span>
          <span>{routeModeLabel(turn.routeMode)}_</span>
        </div>
        <p className="px-5 py-4 text-base font-semibold leading-7">
          {turn.question}
        </p>
      </div>

      <div className="ask-guide-response max-w-5xl bg-black">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/18 px-4 py-2">
          <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
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
              <p className="max-w-4xl whitespace-pre-line text-lg leading-8 text-white/78">
                {response.answer}
              </p>

              {response.caveats.length > 0 && (
                <ul className="list-disc space-y-2 pl-5 text-sm text-white/55">
                  {response.caveats.map((caveat) => (
                    <li key={caveat}>{caveat}</li>
                  ))}
                </ul>
              )}

              {shouldShowRecommendMeCta && (
                <div className="border border-[#ff3e00]/35 bg-[#ff3e00]/10 p-4 text-sm leading-6 text-white/68">
                  For actual ranked matches, continue on Recommend Me_.
                </div>
              )}

              {response.follow_up_prompts.length > 0 && (
                <div className="border-t border-white/15 pt-5">
                  <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                    Continue with_
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
                      Start new topic
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
  const [selectedTopicId, setSelectedTopicId] =
    useState<ChatRouteMode>("explain_project");
  const [turns, setTurns] = useState<GuideTurn[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectionPulse, setSelectionPulse] = useState(false);
  const transcriptRef = useRef<HTMLDivElement | null>(null);

  const selectedTopic = useMemo(
    () => guideTopics.find((topic) => topic.id === selectedTopicId) ?? guideTopics[0],
    [selectedTopicId],
  );
  const userTurnCount = turns.length;
  const hasReachedTurnLimit = userTurnCount >= MAX_GUIDE_USER_TURNS;

  function handleTopicChange(nextTopicId: ChatRouteMode) {
    setSelectedTopicId(nextTopicId);
    setSelectionPulse(true);
    window.setTimeout(() => setSelectionPulse(false), 520);
  }

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

  async function sendGuideInstruction(topic: GuideTopic) {
    setError("");

    if (hasReachedTurnLimit) {
      setError(
        "This Guide thread reached its message limit. Start a new topic for cleaner context.",
      );
      return;
    }

    const turnId =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}`;

    setLoading(true);
    setTurns((current) => [
      ...current,
      {
        id: turnId,
        question: topic.prompt,
        routeMode: topic.id,
        isLoading: true,
      },
    ]);

    try {
      const result = await postChatMessage({
        message: topic.prompt,
        route_mode: topic.id,
        max_results: 5,
        history: [],
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
    setTurns([]);
    setError("");
  }

  function useFollowUp(prompt: string) {
    const routeMode = routeModeForPrompt(prompt);
    const topic =
      guideTopics.find((guideTopic) => guideTopic.id === routeMode) ??
      guideTopics[0];
    void sendGuideInstruction({
      ...topic,
      prompt,
    });
  }

  return (
    <main className="ask-guide-shell">
      <div className="ask-guide-content">
        <section className="ask-guide-stage">
          <div className="ask-guide-stage-grid">
            <section className="ask-guide-terminal">
              <div className="ask-guide-terminal-header">
                <div>
                  <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#ff3e00]">
                    AI guide projection_
                  </p>
                  <h1 className="mt-2 text-3xl font-black uppercase tracking-[-0.06em] text-white sm:text-5xl">
                    Ask the Guide_
                  </h1>
                </div>
              </div>

              <div className="ask-guide-welcome-bubble">
                <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
                  Guide_
                </p>
                <p className="mt-3 text-lg leading-8 text-white/78">
                  I am your controlled project guide. Select an instruction
                  and I will return the matching explanation from the IGDB
                  game-discovery system.
                </p>
              </div>

              <div className="ask-guide-control-row">
                <label className="grid flex-1 gap-2">
                  <span className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                    Supported instructions_
                  </span>
                  <select
                    value={selectedTopicId}
                    disabled={loading || hasReachedTurnLimit}
                    onChange={(event) =>
                      handleTopicChange(event.target.value as ChatRouteMode)
                    }
                    className="border border-white/18 bg-black px-4 py-3 font-mono text-xs uppercase tracking-[0.1em] text-white outline-none transition focus:border-[#ff3e00] disabled:cursor-not-allowed disabled:opacity-45"
                  >
                    {guideTopics.map((topic) => (
                      <option key={topic.id} value={topic.id}>
                        {topic.label}
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  type="button"
                  disabled={loading || hasReachedTurnLimit}
                  onClick={() => sendGuideInstruction(selectedTopic)}
                  className="bg-[#ff3e00] px-5 py-3 text-xs font-black uppercase tracking-[0.14em] text-black transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-45"
                >
                  {loading ? "Transmitting..." : "Run instruction"}
                </button>
                <button
                  type="button"
                  onClick={resetChat}
                  className="border border-white/18 px-5 py-3 text-xs font-black uppercase tracking-[0.14em] text-white/72 transition hover:border-white hover:text-white"
                >
                  Clear chat
                </button>
              </div>

              <div
                className={`ask-guide-topic-preview ${
                  selectionPulse ? "ask-guide-topic-preview-active" : ""
                }`}
              >
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                  {selectedTopic.eyebrow}_
                </p>
                <p className="mt-2 text-sm leading-6 text-white/58">
                  {selectedTopic.description}
                </p>
              </div>

              <div
                ref={transcriptRef}
                className="guide-chat-scroll ask-guide-transcript grid max-h-[min(34rem,65vh)] min-h-[22rem] content-start gap-6 overflow-y-auto overflow-x-visible"
              >
                {turns.length === 0 ? (
                  <div className="ask-guide-terminal-waiting">
                    <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                      terminal idle_
                    </p>
                    <p className="ask-guide-terminal-line">
                      <span>guide@igdb:~$ awaiting selected instruction</span>
                      <span className="ask-guide-terminal-cursor" />
                    </p>
                    <p className="mt-3 text-xs leading-6 text-white/38">
                      Select an instruction above, then run it to open the next
                      guide response.
                    </p>
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
                <div className="border border-[#ff3e00]/45 bg-[#ff3e00]/10 p-5">
                  <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                    Thread limit reached_
                  </p>
                  <p className="mt-2 text-sm leading-6 text-white/72">
                    This guide thread has reached {MAX_GUIDE_USER_TURNS} user
                    selections. Start a new topic to keep the context clean.
                  </p>
                </div>
              )}
            </section>

            <GuideAvatar />
          </div>
        </section>

        <RecommendMeCallout />

        <section className="ask-guide-disclaimer">
          <p className="font-mono text-xs uppercase tracking-[0.26em] text-[#ff3e00]">
            Guide boundaries_
          </p>
          <p className="mt-3 text-sm leading-7 text-white/58">
            Ask the Guide_ uses predefined instructions by design. It explains
            the project, data, methodology, RAG concept, hidden-gem logic,
            limitations, and navigation. It does not accept open-ended typing
            or replace the structured Recommend Me_ workflow.
          </p>
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
