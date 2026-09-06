"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { StyleData } from "@/lib/types";
import {
  generatePreviewStyle,
  generateBackgroundGradient,
} from "@/lib/cssGenerator";
import { PhoneMockup } from "./PhoneMockup";
import { UIControlsShowcase } from "./UIControlsShowcase";
import { ColorPalette } from "./ColorPalette";
import { MetadataBadges } from "./MetadataBadges";
import { ExpandableSection } from "./ExpandableSection";
import { CodeSnippet } from "./CodeSnippet";
import { InteractiveChecklist } from "./InteractiveChecklist";

interface StyleDetailModalProps {
  style: StyleData;
  onClose: () => void;
}

export function StyleDetailModal({ style, onClose }: StyleDetailModalProps) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  // ESC to close
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  // Lock body scroll
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  const isDark = mounted ? theme === "dark" : false;
  const cardStyle = generatePreviewStyle(style, isDark);
  const bgGradient = generateBackgroundGradient(style.extractedColors, isDark);

  const accentColor =
    style.extractedColors[0] || (isDark ? "#6366f1" : "#3b82f6");
  const secondaryColor =
    style.extractedColors[1] || style.extractedColors[0] || (isDark ? "#8b5cf6" : "#6366f1");

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      {/* Modal container */}
      <div
        className="relative z-10 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-[95vw] max-w-5xl max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800 shrink-0">
          <button
            onClick={onClose}
            className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
            Close
          </button>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {style.styleCategory}
          </h2>
          <div className="w-16" /> {/* Spacer for centering */}
        </div>

        {/* Body — two-column on desktop, single-column on mobile */}
        <div className="flex-1 overflow-y-auto">
          <div className="flex flex-col lg:flex-row">
            {/* Left: Phone mockup */}
            <div
              className="lg:w-1/2 flex items-start justify-center p-6 lg:border-r border-gray-200 dark:border-gray-800"
              style={{ background: bgGradient }}
            >
              <PhoneMockup>
                <UIControlsShowcase
                  accentColor={accentColor}
                  secondaryColor={secondaryColor}
                  borderRadius={cardStyle.borderRadius?.toString() || "8px"}
                  boxShadow={
                    cardStyle.boxShadow?.toString() ||
                    "0 4px 12px rgba(0,0,0,0.1)"
                  }
                  backdropFilter={cardStyle.backdropFilter?.toString()}
                  fontFamily={cardStyle.fontFamily?.toString()}
                  fontWeight={cardStyle.fontWeight?.toString()}
                  border={cardStyle.border?.toString()}
                  textShadow={cardStyle.textShadow?.toString()}
                  letterSpacing={cardStyle.letterSpacing?.toString()}
                  isDark={isDark}
                />
              </PhoneMockup>
            </div>

            {/* Right: Details */}
            <div className="lg:w-1/2 p-6">
              {/* Color Palette */}
              <div className="mb-4">
                <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Color Palette
                </h4>
                <ColorPalette colors={style.extractedColors} />
              </div>

              {/* Metadata */}
              <div className="mb-4">
                <MetadataBadges style={style} />
              </div>

              {/* Expandable sections */}
              <div>
                <ExpandableSection title="CSS Code" defaultOpen>
                  <CodeSnippet
                    code={style.cssTechnicalKeywords}
                    label="CSS/Technical"
                  />
                  {style.designSystemVariables && (
                    <div className="mt-2">
                      <CodeSnippet
                        code={style.designSystemVariables}
                        label="Design Variables"
                      />
                    </div>
                  )}
                </ExpandableSection>

                <ExpandableSection title="AI Prompt">
                  <CodeSnippet code={style.aiPromptKeywords} />
                </ExpandableSection>

                <ExpandableSection title="Implementation Checklist">
                  <InteractiveChecklist
                    checklist={style.implementationChecklist}
                  />
                </ExpandableSection>

                <ExpandableSection title="Details">
                  <div className="space-y-2 text-xs">
                    {style.bestFor && (
                      <div>
                        <span className="font-medium text-gray-500 dark:text-gray-400">
                          Best for:{" "}
                        </span>
                        <span className="text-gray-700 dark:text-gray-300">
                          {style.bestFor}
                        </span>
                      </div>
                    )}
                    {style.doNotUseFor && (
                      <div>
                        <span className="font-medium text-gray-500 dark:text-gray-400">
                          Avoid for:{" "}
                        </span>
                        <span className="text-gray-700 dark:text-gray-300">
                          {style.doNotUseFor}
                        </span>
                      </div>
                    )}
                    {style.frameworkCompatibility && (
                      <div>
                        <span className="font-medium text-gray-500 dark:text-gray-400">
                          Frameworks:{" "}
                        </span>
                        <span className="text-gray-700 dark:text-gray-300">
                          {style.frameworkCompatibility}
                        </span>
                      </div>
                    )}
                    {style.keywords && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {style.keywords
                          .split(",")
                          .slice(0, 6)
                          .map((kw, i) => (
                            <span
                              key={i}
                              className="px-1.5 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 rounded"
                            >
                              {kw.trim()}
                            </span>
                          ))}
                      </div>
                    )}
                  </div>
                </ExpandableSection>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
