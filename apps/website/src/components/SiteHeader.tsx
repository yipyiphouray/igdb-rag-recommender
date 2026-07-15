"use client";

import Link from "next/link";
import { useState } from "react";

const links = [
  { href: "/", label: "HOME_", status: "ACTIVE" },
  { href: "/explore", label: "EXPLORE_", status: "ACTIVE" },
  { href: "/recommendations", label: "RECOMMEND_", status: "ACTIVE" },
  { href: "/methodology", label: "METHOD_", status: "ACTIVE" },
];

const pendingLinks = [
  { label: "ASK THE GUIDE_", status: "PENDING" },
  { label: "HIDDEN GEMS_", status: "SOON" },
  { label: "INSIGHTS_", status: "SOON" },
];

export function SiteHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-white bg-black text-white">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
        <Link href="/" className="group" onClick={() => setOpen(false)}>
          <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-[#FF3E00]">
            QUEST ACCEPTED
          </p>
          <h1 className="font-black uppercase tracking-[-0.04em] text-white">
            IGDB GAME DISCOVERY_
          </h1>
        </Link>

        <div className="relative">
          <button
            type="button"
            aria-expanded={open}
            aria-controls="site-menu"
            onClick={() => setOpen((current) => !current)}
            className="group grid h-12 w-16 place-items-center border border-white bg-black transition-none hover:bg-white"
          >
            <span className="sr-only">Toggle navigation menu</span>
            <span className="grid w-8 gap-1.5">
              <span className="h-px bg-white group-hover:bg-black" />
              <span className="h-px bg-white group-hover:bg-black" />
              <span className="h-px bg-white group-hover:bg-black" />
            </span>
          </button>

          {open && (
            <div
              id="site-menu"
              className="absolute right-0 top-[calc(100%+1px)] w-80 border border-white bg-black"
            >
              <div className="border-b border-white px-4 py-3 font-mono text-[10px] uppercase tracking-[0.28em] text-[#FF3E00]">
                MENU_INDEX_
              </div>

              <div className="grid">
                {links.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className="flex items-center justify-between border-b border-white px-4 py-4 font-black uppercase tracking-[-0.03em] transition-none hover:bg-white hover:text-black"
                  >
                    <span>{link.label}</span>
                    <span className="font-mono text-[10px] tracking-[0.18em] text-[#39FF14]">
                      {link.status}
                    </span>
                  </Link>
                ))}

                {pendingLinks.map((link) => (
                  <div
                    key={link.label}
                    className="flex cursor-not-allowed items-center justify-between border-b border-white px-4 py-4 font-black uppercase tracking-[-0.03em] text-white/42"
                  >
                    <span>{link.label}</span>
                    <span className="font-mono text-[10px] tracking-[0.18em] text-[#FF3E00]">
                      {link.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
