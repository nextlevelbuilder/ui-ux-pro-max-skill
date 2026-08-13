import { StyleData } from "./types";

export interface Filters {
  search: string;
  status: string;
  type: string;
  complexity: string;
  era: string;
}

export const DEFAULT_FILTERS: Filters = {
  search: "",
  status: "active",
  type: "",
  complexity: "",
  era: "",
};

export function getUniqueValues(
  styles: StyleData[],
  key: keyof StyleData
): string[] {
  const set = new Set<string>();
  for (const s of styles) {
    const val = String(s[key]).trim();
    if (val) set.add(val);
  }
  return Array.from(set).sort();
}

export function filterStyles(
  styles: StyleData[],
  filters: Filters
): StyleData[] {
  const query = filters.search.toLowerCase();

  return styles.filter((s) => {
    if (filters.status && s.status !== filters.status) return false;
    if (filters.type && s.type !== filters.type) return false;
    if (filters.complexity && s.complexity !== filters.complexity) return false;
    if (filters.era && s.eraOrigin !== filters.era) return false;

    if (query) {
      const searchable = [
        s.styleId,
        s.styleCategory,
        ...s.aliases,
        s.keywords,
        s.bestFor,
        s.eraOrigin,
        s.type,
        s.complexity,
      ]
        .join(" ")
        .toLowerCase();
      if (!searchable.includes(query)) return false;
    }

    return true;
  });
}
