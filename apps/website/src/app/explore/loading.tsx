export default function ExploreLoading() {
  return (
    <div className="explore-v4-shell">
      <div className="explore-v4-content">
      <section className="relative overflow-hidden border border-white bg-black">
        <div className="absolute left-0 top-0 h-1 w-full bg-[#FF3E00]" />
        <div className="relative bg-black p-8 sm:p-10">
          <p className="font-mono text-xs uppercase tracking-[0.34em] text-[#FF3E00]">
            EXPLORE_ // LOADING CATALOG
          </p>
          <h2 className="mt-4 max-w-5xl font-['Arial_Black',Impact,system-ui,sans-serif] text-5xl uppercase leading-[0.86] tracking-[-0.07em] text-white sm:text-7xl">
            Scanning the catalog_
          </h2>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-white/78">
            Loading matching games and preparing the discovery grid.
          </p>
        </div>
      </section>

      <div className="grid gap-px border border-white bg-white md:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <div key={item} className="min-h-64 bg-black p-5">
            <div className="h-48 animate-pulse bg-white/10" />
            <div className="mt-5 h-4 w-24 animate-pulse bg-[#FF3E00]/70" />
            <div className="mt-4 h-8 w-3/4 animate-pulse bg-white/16" />
            <div className="mt-4 h-4 w-full animate-pulse bg-white/10" />
            <div className="mt-2 h-4 w-2/3 animate-pulse bg-white/10" />
          </div>
        ))}
      </div>
      </div>
    </div>
  );
}
