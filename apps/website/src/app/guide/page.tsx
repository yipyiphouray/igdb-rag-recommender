"use client";

import Link from "next/link";
import { FormEvent, useEffect, useRef, useState } from "react";
import { postChatMessage } from "@/lib/api";
import type { ChatHistoryMessage, ChatResponse } from "@/types/api";

const MAX_GUIDE_USER_TURNS = 10;

type GuideTurn = {
  id: string;
  question: string;
  response?: ChatResponse;
  error?: string;
  isLoading?: boolean;
};

type StarterPrompt = {
  label: string;
  eyebrow: string;
  prompt: string;
  description: string;
};

const starterPrompts: StarterPrompt[] = [
  {
    label: "Explain this project",
    eyebrow: "Project map",
    prompt: "Explain this project and how the website works.",
    description:
      "Understand the website goal, analytics pillars, and how the pieces fit together.",
  },
  {
    label: "Dataset size",
    eyebrow: "Dataset fact",
    prompt: "How many games are in the dataset?",
    description:
      "Return the current game count from the structured methodology metrics artifact.",
  },
  {
    label: "Recommend Me logic",
    eyebrow: "Cosine workflow",
    prompt: "How does Recommend Me work?",
    description:
      "Learn how structured answers become a preference profile and ranked matches.",
  },
  {
    label: "Hidden gems",
    eyebrow: "Discovery logic",
    prompt: "What is a hidden gem in this project?",
    description:
      "Understand how the project balances quality, metadata coverage, and lower visibility.",
  },
  {
    label: "RAG role",
    eyebrow: "Guide grounding",
    prompt: "What does RAG do in this chatbot?",
    description:
      "Clarify how retrieval grounds the Guide before an LLM phrases the answer.",
  },
  {
    label: "Website navigation",
    eyebrow: "Site map",
    prompt: "Where should I go for recommendations, insights, and methodology?",
    description:
      "Find the correct website page for each project task.",
  },
];

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
          src="/images/athena.png"
          alt=""
          className="ask-guide-face-image"
        />
        <span className="ask-guide-face-image-glitch ask-guide-face-image-glitch-red" />
        <span className="ask-guide-face-image-glitch ask-guide-face-image-glitch-white" />
      </div>
      <div className="ask-guide-data-rain">
        <span>ATHENA</span>
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
      className="ask-guide-loading-panel border border-[#ff3e00]/35 bg-black p-4 text-white"
    >
      <div className="relative z-10">
        <p className="ask-guide-scramble-loader font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
          Guide is retrieving context_
        </p>
        <p className="mt-2 font-mono text-xs uppercase tracking-[0.16em] text-white/48">
          SEARCHING_PROJECT_CONTEXT // VERIFYING_SCOPE // FORMING_RESPONSE
        </p>
      </div>

      <div className="recommend-loading-track mt-3" aria-hidden="true">
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
          Want ranked game recommendations?_
        </p>
        <h2 className="mt-2 text-2xl font-black uppercase tracking-[-0.05em] text-white">
          Go to Recommend Me_
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-white/62">
          Ask the Guide_ explains the project and helps you ask better questions.
          Recommend Me_ is the page that turns your preferences into ranked game matches.
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
  const followUpPrompts = response?.follow_up_prompts.slice(0, 3) ?? [];
  const nextActions =
    response?.next_actions.slice(0, Math.max(0, 3 - followUpPrompts.length)) ??
    [];
  const shouldShowRecommendMeCta =
    response?.mode === "recommend_me_guidance" ||
    response?.mode === "rag_guided_recommendation_redirect" ||
    response?.chat_intent === "recommend_me_guidance";

  return (
    <div className="ask-guide-turn grid gap-4">
      <div className="ask-guide-user-command ml-auto max-w-3xl bg-white text-black">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-black px-4 py-2 font-mono text-xs uppercase tracking-[0.22em]">
          <span>You_</span>
          <span>Subject input_</span>
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
              <p className="max-w-4xl whitespace-pre-line font-mono text-[0.96rem] leading-7 text-white/76">
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
                  This page explains the project. For personalized ranked game
                  matches, use the Recommend Me_ page.
                </div>
              )}

              {(nextActions.length > 0 || followUpPrompts.length > 0) && (
                <div className="border-t border-white/15 pt-5">
                  <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                    Continue the thread_
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {followUpPrompts.map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        onClick={() => onFollowUp(prompt)}
                        className="border border-white/18 bg-white/[0.03] px-3 py-2 text-left text-xs font-bold uppercase tracking-[0.08em] text-white/76 transition hover:border-[#ff3e00] hover:text-white"
                      >
                        {prompt}
                      </button>
                    ))}
                    {nextActions.map((action) => (
                      <Link
                        key={`${action.href}-${action.label}`}
                        href={action.href}
                        className="border border-[#ff3e00]/55 bg-[#ff3e00]/10 px-3 py-2 text-left text-xs font-bold uppercase tracking-[0.08em] text-[#ff3e00] transition hover:border-[#ff3e00] hover:bg-[#ff3e00] hover:text-black"
                      >
                        {action.label}
                      </Link>
                    ))}
                    <button
                      type="button"
                      onClick={onReset}
                      className="border border-white/18 px-3 py-2 text-left text-xs font-bold uppercase tracking-[0.08em] text-white/58 transition hover:border-white hover:text-white"
                    >
                      Start new thread
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
  const [turns, setTurns] = useState<GuideTurn[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showHelpPrompts, setShowHelpPrompts] = useState(false);
  const transcriptRef = useRef<HTMLDivElement | null>(null);
  const userTurnCount = turns.filter((turn) => !turn.isLoading || turn.question).length;
  const hasReachedTurnLimit = userTurnCount >= MAX_GUIDE_USER_TURNS;

  useEffect(() => {
    const transcript = transcriptRef.current;
    if (!transcript) {
      return;
    }

    transcript.scrollTo({
      top: transcript.scrollHeight,
      behavior: "smooth",
    });
  }, [turns, showHelpPrompts]);

  function buildHistory(): ChatHistoryMessage[] {
    return turns
      .filter((turn) => turn.response)
      .flatMap((turn) => [
        { role: "user" as const, content: turn.question },
        { role: "guide" as const, content: turn.response?.answer ?? "" },
      ])
      .filter((item) => item.content.trim())
      .slice(-8);
  }

  async function sendGuideMessage(nextMessage: string) {
    const cleanedMessage = nextMessage.trim();
    if (!cleanedMessage || loading) {
      return;
    }

    setError("");

    if (cleanedMessage.toLowerCase() === "/help") {
      setShowHelpPrompts(true);
      setMessage("");
      return;
    }

    if (hasReachedTurnLimit) {
      setError(
        "This Guide thread reached its message limit. Start a new thread for cleaner context.",
      );
      return;
    }

    const turnId =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}`;

    setLoading(true);
    setMessage("");
    setTurns((current) => [
      ...current,
      {
        id: turnId,
        question: cleanedMessage,
        isLoading: true,
      },
    ]);

    try {
      const result = await postChatMessage({
        message: cleanedMessage,
        route_mode: "custom_question",
        max_results: 5,
        history: buildHistory(),
      });
      setShowHelpPrompts(false);
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

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendGuideMessage(message);
  }

  function resetChat() {
    setTurns([]);
    setError("");
    setMessage("");
    setShowHelpPrompts(false);
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
                    Scoped RAG AI guide_
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
                  Submit a project-scoped question. I answer only within this
                  IGDB system: dataset, methodology, analytics findings, RAG
                  design, recommendation logic, hidden-gem criteria, and website
                  navigation.
                </p>
              </div>

              <div
                ref={transcriptRef}
                className="guide-chat-scroll ask-guide-transcript grid max-h-[min(36rem,65vh)] min-h-[22rem] content-start gap-6 overflow-y-auto overflow-x-visible"
              >
                {turns.length === 0 ? (
                  <div className="ask-guide-terminal-waiting">
                    <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                      terminal idle_
                    </p>
                    <p className="ask-guide-terminal-line">
                      <span>guide@igdb:~$ awaiting project question</span>
                      <span className="ask-guide-terminal-cursor" />
                    </p>
                    <p className="mt-3 text-xs leading-6 text-white/38">
                      Type /help to reveal supported example prompts. Otherwise,
                      enter a project-scoped question below.
                    </p>
                  </div>
                ) : (
                  turns.map((turn) => (
                    <ChatTurnPanel
                      key={turn.id}
                      turn={turn}
                      onFollowUp={sendGuideMessage}
                      onReset={resetChat}
                    />
                  ))
                )}

                {showHelpPrompts && (
                  <div className="ask-guide-topic-preview">
                    <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                      /help returned supported examples_
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {starterPrompts.map((prompt) => (
                        <button
                          key={prompt.prompt}
                          type="button"
                          disabled={loading || hasReachedTurnLimit}
                          onClick={() => sendGuideMessage(prompt.prompt)}
                          className="ask-guide-starter-chip text-left disabled:cursor-not-allowed disabled:opacity-45"
                        >
                          <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#ff3e00]/82">
                            {prompt.eyebrow}
                          </span>
                          <span className="block text-xs font-black uppercase tracking-[0.08em] text-white/72">
                            {prompt.label}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <form onSubmit={handleSubmit} className="ask-guide-input-deck">
                <label className="grid gap-2">
                  <span className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                    Subject query_
                  </span>
                  <textarea
                    value={message}
                    disabled={loading || hasReachedTurnLimit}
                    onChange={(event) => setMessage(event.target.value)}
                    placeholder="Type /help or ask a project-scoped question."
                    rows={3}
                    className="ask-guide-terminal-input resize-none px-4 py-3 text-sm leading-6 text-white outline-none transition placeholder:text-white/30 disabled:cursor-not-allowed disabled:opacity-45"
                  />
                </label>
                <div className="flex flex-wrap gap-3">
                  <button
                    type="submit"
                    disabled={loading || hasReachedTurnLimit || !message.trim()}
                    className="bg-[#ff3e00] px-5 py-3 text-xs font-black uppercase tracking-[0.14em] text-black transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-45"
                  >
                    {loading ? "Transmitting..." : "Ask Guide"}
                  </button>
                  <button
                    type="button"
                    onClick={resetChat}
                    className="border border-white/18 px-5 py-3 text-xs font-black uppercase tracking-[0.14em] text-white/72 transition hover:border-white hover:text-white"
                  >
                    Clear chat
                  </button>
                </div>
              </form>

              {hasReachedTurnLimit && (
                <div className="border border-[#ff3e00]/45 bg-[#ff3e00]/10 p-5">
                  <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#ff3e00]">
                    Thread limit reached_
                  </p>
                  <p className="mt-2 text-sm leading-6 text-white/72">
                    This guide thread has reached {MAX_GUIDE_USER_TURNS} user
                    messages. Start a new thread to keep the context clean.
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
            Ask the Guide_ answers questions about this IGDB project, its dataset,
            methodology, analytics findings, recommendation architecture, RAG
            design, hidden-gem logic, and website navigation. It does not replace
            the Recommend Me_ engine. Use Recommend Me_ when the objective is a
            ranked list of games.
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
