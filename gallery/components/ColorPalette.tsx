"use client";

import { useState } from "react";

interface ColorPaletteProps {
  colors: string[];
}

export function ColorPalette({ colors }: ColorPaletteProps) {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  if (colors.length === 0) return null;

  async function copyColor(color: string, idx: number) {
    try {
      await navigator.clipboard.writeText(color);
      setCopiedIdx(idx);
      setTimeout(() => setCopiedIdx(null), 2000);
    } catch {
      // Fallback: ignore
    }
  }

  // Show at most 8 colors
  const displayed = colors.slice(0, 8);

  return (
    <div className="flex items-center gap-1.5">
      {displayed.map((color, i) => (
        <div key={`${color}-${i}`} className="group relative">
          <button
            onClick={() => copyColor(color, i)}
            className="w-6 h-6 rounded-full border border-gray-200 dark:border-gray-700 transition-transform hover:scale-125 focus:outline-none focus:ring-2 focus:ring-blue-400"
            style={{ backgroundColor: color }}
            title={color}
          />
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-1.5 py-0.5 text-[10px] font-mono bg-gray-900 text-white rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-10">
            {copiedIdx === i ? "Copied!" : color}
          </div>
        </div>
      ))}
      {colors.length > 8 && (
        <span className="text-xs text-gray-400">+{colors.length - 8}</span>
      )}
    </div>
  );
}
