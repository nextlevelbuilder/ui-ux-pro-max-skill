"use client";

import { StyleData } from "@/lib/types";
import {
  generatePreviewStyle,
  generateBackgroundGradient,
} from "@/lib/cssGenerator";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

interface StylePreviewProps {
  style: StyleData;
}

export function StylePreview({ style }: StylePreviewProps) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const isDark = mounted ? theme === "dark" : false;
  const cardStyle = generatePreviewStyle(style, isDark);
  const bgGradient = generateBackgroundGradient(style.extractedColors, isDark);
  const accentColor = style.extractedColors[0] || (isDark ? "#6366f1" : "#3b82f6");

  return (
    <div
      className="relative h-40 rounded-lg overflow-hidden"
      style={{ background: bgGradient }}
    >
      {/* Demo card */}
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div
          className="w-full max-w-[200px] p-4 bg-white/80 dark:bg-gray-900/80"
          style={{
            borderRadius: cardStyle.borderRadius || "8px",
            boxShadow:
              cardStyle.boxShadow || "0 4px 12px rgba(0,0,0,0.1)",
            backdropFilter: cardStyle.backdropFilter,
            WebkitBackdropFilter: cardStyle.WebkitBackdropFilter,
            border: cardStyle.border || "1px solid rgba(128,128,128,0.1)",
            fontFamily: cardStyle.fontFamily,
            fontWeight: cardStyle.fontWeight,
            filter: cardStyle.filter,
            textShadow: cardStyle.textShadow,
            letterSpacing: cardStyle.letterSpacing,
            transition: cardStyle.transition || "all 0.2s ease",
          }}
        >
          <div
            className="h-2 rounded-full mb-2 w-3/4"
            style={{ background: accentColor }}
          />
          <div className="h-1.5 rounded-full bg-gray-300 dark:bg-gray-600 mb-1.5 w-full" />
          <div className="h-1.5 rounded-full bg-gray-300 dark:bg-gray-600 mb-1.5 w-5/6" />
          <div className="h-1.5 rounded-full bg-gray-300 dark:bg-gray-600 w-2/3" />
          <div
            className="mt-3 h-6 rounded flex items-center justify-center"
            style={{
              background: accentColor,
              borderRadius: cardStyle.borderRadius
                ? `calc(${cardStyle.borderRadius} / 2)`
                : "4px",
            }}
          >
            <span className="text-[10px] font-medium text-white">
              Button
            </span>
          </div>
        </div>
      </div>

      {/* Style name overlay */}
      <div className="absolute bottom-0 left-0 right-0 px-3 py-1.5 bg-gradient-to-t from-black/40 to-transparent">
        <span className="text-[10px] font-medium text-white/80">
          Preview
        </span>
      </div>
    </div>
  );
}
