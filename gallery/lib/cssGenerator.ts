import React from "react";

const CSS_PROPERTY_MAP: Record<string, string> = {
  "border-radius": "borderRadius",
  "box-shadow": "boxShadow",
  "backdrop-filter": "backdropFilter",
  "-webkit-backdrop-filter": "WebkitBackdropFilter",
  background: "background",
  "background-color": "backgroundColor",
  color: "color",
  "font-family": "fontFamily",
  "font-weight": "fontWeight",
  "font-size": "fontSize",
  border: "border",
  transition: "transition",
  transform: "transform",
  filter: "filter",
  opacity: "opacity",
  "mix-blend-mode": "mixBlendMode",
  "text-shadow": "textShadow",
  "letter-spacing": "letterSpacing",
  gap: "gap",
  padding: "padding",
  "max-width": "maxWidth",
  display: "display",
  "text-transform": "textTransform",
};

export function parseCssKeywords(
  cssTechnical: string
): Record<string, string> {
  const result: Record<string, string> = {};
  if (!cssTechnical) return result;

  // Match patterns like "property: value"
  const re = /([\w-]+)\s*:\s*([^,;]+?)(?=\s*[,;]|\s+[\w-]+\s*:|$)/g;
  let match;

  while ((match = re.exec(cssTechnical)) !== null) {
    const prop = match[1].trim().toLowerCase();
    const val = match[2].trim();
    if (CSS_PROPERTY_MAP[prop]) {
      result[CSS_PROPERTY_MAP[prop]] = val;
    }
  }

  return result;
}

export function generatePreviewStyle(
  style: { extractedColors: string[]; cssProperties: Record<string, string> },
  isDark: boolean
): React.CSSProperties {
  const colors = style.extractedColors;
  const props = style.cssProperties;

  const baseStyle: React.CSSProperties = {};

  // Apply border-radius
  if (props.borderRadius) {
    baseStyle.borderRadius = props.borderRadius;
  }

  // Apply box-shadow
  if (props.boxShadow) {
    baseStyle.boxShadow = props.boxShadow;
  }

  // Apply backdrop-filter
  if (props.backdropFilter) {
    baseStyle.backdropFilter = props.backdropFilter;
    baseStyle.WebkitBackdropFilter = props.backdropFilter;
  }

  // Apply font-family
  if (props.fontFamily) {
    baseStyle.fontFamily = props.fontFamily;
  }

  // Apply font-weight
  if (props.fontWeight) {
    baseStyle.fontWeight = props.fontWeight;
  }

  // Apply border
  if (props.border) {
    baseStyle.border = props.border;
  }

  // Apply transition
  if (props.transition) {
    baseStyle.transition = props.transition;
  }

  // Apply filter
  if (props.filter) {
    baseStyle.filter = props.filter;
  }

  // Apply text-shadow
  if (props.textShadow) {
    baseStyle.textShadow = props.textShadow;
  }

  // Apply letter-spacing
  if (props.letterSpacing) {
    baseStyle.letterSpacing = props.letterSpacing;
  }

  return baseStyle;
}

export function generateBackgroundGradient(
  colors: string[],
  isDark: boolean
): string {
  if (colors.length === 0) {
    return isDark
      ? "linear-gradient(135deg, #1a1a2e, #16213e)"
      : "linear-gradient(135deg, #f5f7fa, #c3cfe2)";
  }
  if (colors.length === 1) {
    const c = colors[0];
    return isDark
      ? `linear-gradient(135deg, ${c}33, ${c}11)`
      : `linear-gradient(135deg, ${c}22, ${c}11)`;
  }
  const c1 = colors[0];
  const c2 = colors[1];
  return isDark
    ? `linear-gradient(135deg, ${c1}44, ${c2}22)`
    : `linear-gradient(135deg, ${c1}22, ${c2}11)`;
}
