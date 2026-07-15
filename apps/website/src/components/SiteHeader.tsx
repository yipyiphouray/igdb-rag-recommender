import Link from "next/link";

const links = [
  { href: "/", label: "Home" },
  { href: "/explore", label: "Explore" },
  { href: "/recommendations", label: "Recommendations" },
  { href: "/methodology", label: "Methodology" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-cyan-300/10 bg-[#070a18]/86 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <Link href="/" className="group">
          <p className="text-xs uppercase tracking-[0.34em] text-cyan-200/80">
            QUEST ACCEPTED
          </p>
          <h1 className="neon-text text-xl font-black tracking-tight text-white">
            IGDB Game Discovery
          </h1>
        </Link>
        <div className="flex flex-wrap gap-2">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-full border border-cyan-200/15 px-4 py-2 text-sm text-cyan-50/86 transition hover:border-cyan-200/70 hover:bg-cyan-200/10"
            >
              {link.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
