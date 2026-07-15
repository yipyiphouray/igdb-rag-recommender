import Link from "next/link";
import { getHealth } from "@/lib/api";

const featureCards = [
  {
    title: "Explore",
    href: "/explore",
    description: "Browse the curated IGDB catalog with searchable, app-ready data.",
  },
  {
    title: "Recommendations",
    href: "/recommendations",
    description: "Answer a guided wizard and receive ranked game suggestions.",
  },
  {
    title: "Methodology",
    href: "/methodology",
    description: "Review the sample design, metric definitions, and caveats.",
  },
];

export default async function HomePage() {
  const health = await getHealth();

  return (
    <>
      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div className="cyber-panel rounded-3xl p-8 sm:p-10">
          <p className="text-sm uppercase tracking-[0.4em] text-cyan-200/80">
            Final website foundation
          </p>
          <h2 className="neon-text mt-4 max-w-4xl text-5xl font-black tracking-tight text-white sm:text-6xl">
            Find the next game worth your time.
          </h2>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
            This website is the polished user-facing layer for the IGDB
            analytics project. It starts with catalog exploration,
            questionnaire-based recommendations, and a transparent methodology
            page built on the existing app-ready artifacts.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/recommendations"
              className="rounded-full bg-cyan-300 px-6 py-3 font-bold text-slate-950 shadow-neon transition hover:bg-white"
            >
              Start recommendations
            </Link>
            <Link
              href="/explore"
              className="rounded-full border border-cyan-200/40 px-6 py-3 font-bold text-cyan-100 transition hover:bg-cyan-200/10"
            >
              Explore catalog
            </Link>
          </div>
        </div>

        <aside className="cyber-panel-magenta rounded-3xl p-7">
          <p className="text-sm uppercase tracking-[0.32em] text-fuchsia-200/80">
            API status
          </p>
          <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-5">
            <p className="text-3xl font-black text-white">
              {health?.status === "ok" ? "Online" : "Offline"}
            </p>
            <p className="mt-2 text-sm text-slate-300">
              {health
                ? `${health.service} v${health.version}`
                : "Start the FastAPI backend to connect live data."}
            </p>
          </div>
        </aside>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {featureCards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="cyber-panel group rounded-2xl p-6 transition hover:-translate-y-1 hover:border-cyan-200/70"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/70">
              MVP page
            </p>
            <h3 className="mt-3 text-2xl font-black text-white group-hover:text-cyan-100">
              {card.title}
            </h3>
            <p className="mt-3 leading-7 text-slate-300">{card.description}</p>
          </Link>
        ))}
      </section>
    </>
  );
}
