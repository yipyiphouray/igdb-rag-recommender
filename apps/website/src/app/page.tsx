import Link from "next/link";

const featureCards = [
  {
    section: "SEC_01 //",
    title: "RECOMMEND ME_",
    href: "/recommendations",
    active: true,
    description: "Get personalized game picks.",
  },
  {
    section: "SEC_02 //",
    title: "EXPLORE GAMES_",
    href: "/explore",
    active: true,
    description: "Search and browse the curated game catalog.",
  },
  {
    section: "SEC_03 //",
    title: "ASK THE GUIDE_",
    href: null,
    active: false,
    description: "A future chatbot for natural-language game discovery.",
  },
  {
    section: "SEC_04 //",
    title: "HIDDEN GEMS_",
    href: "/hidden-gems",
    active: true,
    description: "Find strong games that may be easier to miss.",
  },
  {
    section: "SEC_05 //",
    title: "INSIGHTS_",
    href: "/insights",
    active: true,
    description: "See the main patterns found in the project data.",
  },
  {
    section: "SEC_06 //",
    title: "METHOD_",
    href: "/methodology",
    active: true,
    description: "Understand the data, signals, and limitations.",
  },
] as const;

function StatusLight({ active }: { active: boolean }) {
  return (
    <span
      aria-label={active ? "active module" : "pending module"}
      className={`home-v3-status-light ${active ? "is-active" : "is-pending"}`}
    />
  );
}

function FeatureCard({ card }: { card: (typeof featureCards)[number] }) {
  const content = (
    <div className={`home-v3-card ${card.active ? "" : "is-disabled"}`}>
      <div className="flex items-center justify-between">
        <p className="home-v3-micro">{card.section}</p>
        <StatusLight active={card.active} />
      </div>

      <div className="flex flex-1 items-center justify-center py-10 text-center">
        <h3 className="home-v3-card-title">{card.title}</h3>
      </div>

      <p className="home-v3-card-description">{card.description}</p>
    </div>
  );

  if (!card.href) {
    return <div aria-disabled="true">{content}</div>;
  }

  return (
    <Link href={card.href} className="block h-full">
      {content}
    </Link>
  );
}

export default async function HomePage() {
  return (
    <div className="home-v3-bleed">
      <section className="home-v3-hero">
        <div className="home-v3-hero-main">
          <p className="home-v3-micro text-[#FF3E00]">
            INDEX_ // IGDB GAME DISCOVERY
          </p>
          <h2 className="home-v3-title home-v7-glitch">
            <span>FIND YOUR</span>
            <span>NEXT GAME_</span>
          </h2>
          <p className="home-v9-hero-subtitle mx-auto mt-8 max-w-2xl text-xl leading-9">
            Browse the catalog, tune your preferences, and find games that
            actually match what you want to play.
          </p>

          <div className="mx-auto mt-10 grid max-w-4xl gap-px border border-white bg-white sm:grid-cols-3">
            <Link href="/recommendations" className="home-v3-cta">
              RECOMMEND ME
            </Link>
            <Link href="/explore" className="home-v3-cta">
              EXPLORE
            </Link>
            <span className="home-v3-cta is-disabled">ASK GUIDE</span>
          </div>
        </div>
      </section>

      <section className="home-v3-menu">
        <div className="home-v3-section-label">
          <p className="home-v3-micro text-[#FF3E00]">SELECT MODULE_</p>
        </div>

        <div className="grid gap-px border-y border-white bg-white md:grid-cols-2 xl:grid-cols-3">
          {featureCards.map((card) => (
            <FeatureCard key={card.title} card={card} />
          ))}
        </div>
      </section>

      <footer className="home-v3-footer">
        <p>QUEST ACCEPTED // BUSA 649</p>
        <a
          href="https://github.com/yipyiphouray/igdb-rag-recommender"
          target="_blank"
          rel="noreferrer"
        >
          GITHUB REFERENCE
        </a>
      </footer>
    </div>
  );
}
