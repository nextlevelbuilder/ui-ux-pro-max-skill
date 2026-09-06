"use client";

import { StyleData } from "@/lib/types";
import { StylePreview } from "./StylePreview";
import { ColorPalette } from "./ColorPalette";
import { MetadataBadges } from "./MetadataBadges";
import { ExpandableSection } from "./ExpandableSection";
import { CodeSnippet } from "./CodeSnippet";
import { InteractiveChecklist } from "./InteractiveChecklist";

interface StyleCardProps {
  style: StyleData;
  onSelect?: (style: StyleData) => void;
}

export function StyleCard({ style, onSelect }: StyleCardProps) {
  return (
    <div
      className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-lg dark:hover:shadow-gray-900/50 transition-shadow cursor-pointer"
      onClick={() => onSelect?.(style)}
    >
      {/* Header */}
      <div className="px-4 pt-4 pb-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 leading-tight">
            {style.styleCategory}
          </h3>
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400">
              {style.type}
            </span>
            <span className="text-[10px] text-gray-400">{style.eraOrigin}</span>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="px-4">
        <StylePreview style={style} />
      </div>

      {/* Color Palette */}
      <div className="px-4 py-3">
        <ColorPalette colors={style.extractedColors} />
      </div>

      {/* Metadata Badges */}
      <div className="px-4 pb-3">
        <MetadataBadges style={style} />
      </div>

      {/* Expandable Sections */}
      <div className="px-4 pb-2">
        <ExpandableSection title="CSS Code">
          <CodeSnippet code={style.cssTechnicalKeywords} label="CSS/Technical" />
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
          <InteractiveChecklist checklist={style.implementationChecklist} />
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
  );
}
