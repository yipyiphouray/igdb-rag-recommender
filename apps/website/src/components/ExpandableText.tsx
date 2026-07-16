"use client";

import { useState } from "react";

export function ExpandableText({
  text,
  emptyText = "No data is available for this field.",
  className = "",
  collapsedClassName = "line-clamp-5",
}: {
  text?: string | null;
  emptyText?: string;
  className?: string;
  collapsedClassName?: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const content = text?.trim();
  const shouldToggle = Boolean(content && content.length > 260);

  if (!content) {
    return <p className={className}>{emptyText}</p>;
  }

  return (
    <div>
      <p className={`${className} ${expanded ? "" : collapsedClassName}`}>
        {content}
      </p>
      {shouldToggle && (
        <button
          type="button"
          onClick={() => setExpanded((current) => !current)}
          className="mt-4 inline-flex font-mono text-xs uppercase tracking-[0.18em] text-[#FF3E00] underline-offset-4 hover:text-white hover:underline"
        >
          {expanded ? "Read less" : "Read more"}
        </button>
      )}
    </div>
  );
}
