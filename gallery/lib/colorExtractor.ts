const HEX_RE = /#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b/g;
const RGBA_RE = /rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)/g;

function normalizeHex(hex: string): string {
  hex = hex.toUpperCase();
  if (hex.length === 4) {
    return `#${hex[1]}${hex[1]}${hex[2]}${hex[2]}${hex[3]}${hex[3]}`;
  }
  return hex;
}

export function extractColors(text: string): string[] {
  const colors: string[] = [];
  const seen = new Set<string>();

  const hexMatches = text.match(HEX_RE) || [];
  for (const h of hexMatches) {
    const normalized = normalizeHex(h);
    if (!seen.has(normalized)) {
      seen.add(normalized);
      colors.push(normalized);
    }
  }

  const rgbaMatches = text.match(RGBA_RE) || [];
  for (const r of rgbaMatches) {
    if (!seen.has(r)) {
      seen.add(r);
      colors.push(r);
    }
  }

  return colors;
}
