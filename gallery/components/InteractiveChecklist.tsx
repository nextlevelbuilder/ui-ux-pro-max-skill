"use client";

import { useState } from "react";

interface InteractiveChecklistProps {
  checklist: string;
}

function parseItems(raw: string): string[] {
  return raw
    .split(/,\s*(?=☐)/)
    .map((s) => s.replace(/^☐\s*/, "").trim())
    .filter(Boolean);
}

export function InteractiveChecklist({ checklist }: InteractiveChecklistProps) {
  const items = parseItems(checklist);
  const [checked, setChecked] = useState<Set<number>>(new Set());

  if (items.length === 0) return null;

  function toggle(idx: number) {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  }

  return (
    <div>
      <div className="text-[10px] text-gray-400 mb-2">
        {checked.size} of {items.length} completed
      </div>
      <div className="space-y-1.5">
        {items.map((item, i) => (
          <label
            key={i}
            className="flex items-start gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              checked={checked.has(i)}
              onChange={() => toggle(i)}
              className="mt-0.5 rounded border-gray-300 dark:border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span
              className={`text-xs leading-relaxed transition-colors ${
                checked.has(i)
                  ? "line-through text-gray-400 dark:text-gray-600"
                  : "text-gray-700 dark:text-gray-300"
              }`}
            >
              {item}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}
