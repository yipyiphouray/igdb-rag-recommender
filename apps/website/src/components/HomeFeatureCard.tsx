"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

export type HomeFeatureCardData = {
  section: string;
  title: string;
  href: string | null;
  active: boolean;
  description: string;
};

const SCRAMBLE_CHARACTERS =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@$%&*+-/<>[]{}";
const SCRAMBLE_TOTAL_DURATION_MS = 800;
const SCRAMBLE_HOLD_DURATION_MS = 120;
const SCRAMBLE_FRAME_INTERVAL_MS = 32;

function randomCharacter() {
  return SCRAMBLE_CHARACTERS[
    Math.floor(Math.random() * SCRAMBLE_CHARACTERS.length)
  ];
}

function easeInOutCubic(value: number) {
  return value < 0.5
    ? 4 * value * value * value
    : 1 - Math.pow(-2 * value + 2, 3) / 2;
}

function prefersReducedMotion() {
  return (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

function StatusLight({ active }: { active: boolean }) {
  return (
    <span
      aria-label={active ? "active module" : "pending module"}
      className={`home-v3-status-light ${active ? "is-active" : "is-pending"}`}
    />
  );
}

export function HomeFeatureCard({ card }: { card: HomeFeatureCardData }) {
  const [displayTitle, setDisplayTitle] = useState(card.title);
  const frameRef = useRef<number | null>(null);
  const startTimeRef = useRef(0);
  const lastFrameTimeRef = useRef(0);

  useEffect(() => {
    setDisplayTitle(card.title);

    return () => {
      if (frameRef.current !== null) {
        window.cancelAnimationFrame(frameRef.current);
      }
    };
  }, [card.title]);

  function runScramble() {
    if (prefersReducedMotion()) {
      setDisplayTitle(card.title);
      return;
    }

    if (frameRef.current !== null) {
      window.cancelAnimationFrame(frameRef.current);
    }

    startTimeRef.current = performance.now();
    lastFrameTimeRef.current = 0;
    const target = card.title;

    const tick = (timestamp: number) => {
      const elapsed = timestamp - startTimeRef.current;
      const shouldUpdate =
        elapsed >= SCRAMBLE_TOTAL_DURATION_MS ||
        timestamp - lastFrameTimeRef.current >= SCRAMBLE_FRAME_INTERVAL_MS;

      if (!shouldUpdate) {
        frameRef.current = window.requestAnimationFrame(tick);
        return;
      }

      lastFrameTimeRef.current = timestamp;
      const revealProgress =
        Math.max(elapsed - SCRAMBLE_HOLD_DURATION_MS, 0) /
        (SCRAMBLE_TOTAL_DURATION_MS - SCRAMBLE_HOLD_DURATION_MS);
      const easedRevealProgress = easeInOutCubic(
        Math.min(Math.max(revealProgress, 0), 1),
      );
      const revealIndex = Math.floor(
        easedRevealProgress * target.length,
      );
      const nextText = target
        .split("")
        .map((character, index) => {
          if (character === " ") return character;
          if (index < revealIndex) return character;
          return randomCharacter();
        })
        .join("");

      setDisplayTitle(nextText);

      if (elapsed >= SCRAMBLE_TOTAL_DURATION_MS) {
        setDisplayTitle(target);
        frameRef.current = null;
        return;
      }

      frameRef.current = window.requestAnimationFrame(tick);
    };

    frameRef.current = window.requestAnimationFrame(tick);
  }

  const content = (
    <div
      className={`home-v3-card ${card.active ? "" : "is-disabled"}`}
      onFocus={runScramble}
      onPointerEnter={runScramble}
    >
      <div className="flex items-center justify-between">
        <p className="home-v3-micro">{card.section}</p>
        <StatusLight active={card.active} />
      </div>

      <div className="flex flex-1 items-center justify-center py-10 text-center">
        <h3 className="home-v3-card-title home-scramble-title" aria-label={card.title}>
          <span aria-hidden="true">{displayTitle}</span>
        </h3>
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
