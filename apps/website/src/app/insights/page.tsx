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
        <section className="border border-white bg-black p-8 text-white sm:p-10">
          <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#FF3E00]">
            INSIGHTS_ // READ THE SIGNALS BEHIND THE CATALOG
          </p>
          <h1 className="mt-4 max-w-5xl font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.88] tracking-[-0.07em] text-white sm:text-7xl">
            Insights_
          </h1>
          <p className="mt-6 max-w-4xl text-lg leading-8 text-white/74">
            Review the key descriptive and diagnostic findings from the curated IGDB
            catalog.
          </p>
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
