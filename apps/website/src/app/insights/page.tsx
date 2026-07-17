import { EmptyState } from "@/components/EmptyState";
import { InsightsDashboardTabs } from "@/components/InsightsDashboardTabs";
import { getInsightsSummary } from "@/lib/api";
import type { InsightsSummary } from "@/types/api";

function InsightsUnavailable({ message }: { message: string }) {
  return (
    <div className="insights-v1-shell">
      <div className="insights-v1-content">
        <EmptyState title="Insights unavailable" message={message} />
      </div>
    </div>
  );
}

export default async function InsightsPage() {
  let summary: InsightsSummary | null = null;
  let error = "";

  try {
    summary = await getInsightsSummary();
  } catch {
    error = "The insights API is unavailable. Start the FastAPI backend and refresh this page.";
  }

  if (error || !summary) {
    return (
      <InsightsUnavailable
        message={
          error ||
          "The insights summary did not return data. Start the FastAPI backend and refresh this page."
        }
      />
    );
  }

  return (
    <div className="insights-v1-shell">
      <div className="insights-v1-content">
        <section className="relative overflow-hidden border border-white bg-black text-center">
          <div className="absolute left-0 top-0 h-1 w-full bg-[#FF3E00]" />
          <div className="relative flex flex-col items-center bg-black p-8 sm:p-10">
            <h1 className="font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.86] tracking-[-0.07em] text-white sm:text-7xl">
              Insights_
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-white/78">
              Review the key descriptive and diagnostic findings from the curated IGDB
              catalog.
            </p>
          </div>
        </section>

        <InsightsDashboardTabs summary={summary} />

        <section className="border border-white bg-black p-6 text-white sm:p-8">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#FF3E00]">
            Interpretation note_
          </p>
          <p className="mt-4 max-w-4xl leading-8 text-white/72">
            These insights describe the curated project sample, not the entire video game
            market. Treat them as project-level evidence for exploration, recommendation
            design, and storytelling.
          </p>
        </section>
      </div>
    </div>
  );
}
