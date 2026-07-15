import { EmptyState } from "@/components/EmptyState";
import { getMethodologySummary } from "@/lib/api";

function formatValue(value: unknown) {
  if (typeof value === "number") {
    if (value > 0 && value < 1) return `${(value * 100).toFixed(1)}%`;
    return value.toLocaleString();
  }
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value ?? "Unknown");
}

export default async function MethodologyPage() {
  let summary = null;
  let error = "";

  try {
    summary = await getMethodologySummary();
  } catch {
    error = "The methodology API is unavailable. Start the FastAPI backend and refresh this page.";
  }

  if (error || !summary) {
    return <EmptyState title="Methodology unavailable" message={error} />;
  }

  return (
    <>
      <section className="cyber-panel rounded-3xl p-8">
        <p className="text-sm uppercase tracking-[0.34em] text-cyan-200/80">
          Methodology
        </p>
        <h2 className="mt-3 text-4xl font-black text-white">
          Transparent data, metrics, and caveats.
        </h2>
        <p className="mt-4 max-w-3xl text-slate-300">{summary.data_source}</p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {Object.entries(summary.metrics).map(([key, value]) => (
          <div key={key} className="cyber-panel rounded-2xl p-5">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-200/60">
              {key.replaceAll("_", " ")}
            </p>
            <p className="mt-3 text-2xl font-black text-white">
              {formatValue(value)}
            </p>
          </div>
        ))}
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="cyber-panel rounded-2xl p-6">
          <h3 className="text-2xl font-black text-white">Core caveats</h3>
          <ul className="mt-4 list-disc space-y-3 pl-5 text-slate-300">
            {summary.caveats.map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        </div>
        <div className="cyber-panel-magenta rounded-2xl p-6">
          <h3 className="text-2xl font-black text-white">Implementation notes</h3>
          <ul className="mt-4 list-disc space-y-3 pl-5 text-slate-300">
            {summary.implementation_notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}
