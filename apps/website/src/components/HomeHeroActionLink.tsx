"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

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

export function HomeHeroActionLink({
  href,
  label,
}: {
  href: string;
  label: string;
}) {
  const [displayLabel, setDisplayLabel] = useState(label);
  const frameRef = useRef<number | null>(null);
  const startTimeRef = useRef(0);
  const lastFrameTimeRef = useRef(0);

  useEffect(() => {
    setDisplayLabel(label);

    return () => {
      if (frameRef.current !== null) {
        window.cancelAnimationFrame(frameRef.current);
      }
    };
  }, [label]);

  function runScramble() {
    if (prefersReducedMotion()) {
      setDisplayLabel(label);
      return;
    }

    if (frameRef.current !== null) {
      window.cancelAnimationFrame(frameRef.current);
    }

    startTimeRef.current = performance.now();
    lastFrameTimeRef.current = 0;
    const target = label;

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
      const revealIndex = Math.floor(easedRevealProgress * target.length);
      const nextText = target
        .split("")
        .map((character, index) => {
          if (character === " ") return character;
          if (index < revealIndex) return character;
          return randomCharacter();
        })
        .join("");

      setDisplayLabel(nextText);

      if (elapsed >= SCRAMBLE_TOTAL_DURATION_MS) {
        setDisplayLabel(target);
        frameRef.current = null;
        return;
      }

      frameRef.current = window.requestAnimationFrame(tick);
    };

    frameRef.current = window.requestAnimationFrame(tick);
  }

  return (
    <Link
      href={href}
      className="home-v3-cta home-hero-scramble-cta"
      onFocus={runScramble}
      onPointerEnter={runScramble}
      aria-label={label}
    >
      <span aria-hidden="true">{displayLabel}</span>
    </Link>
  );
}
