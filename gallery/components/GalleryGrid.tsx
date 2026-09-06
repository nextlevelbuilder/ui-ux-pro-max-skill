"use client";

import { useMemo, useState } from "react";
import { StyleData } from "@/lib/types";
import {
  Filters,
  DEFAULT_FILTERS,
  filterStyles,
  getUniqueValues,
} from "@/lib/filterStyles";
import { StyleCard } from "./StyleCard";
import { StyleDetailModal } from "./StyleDetailModal";
import { SearchInput } from "./SearchInput";
import { FilterBar } from "./FilterBar";
import { DarkModeToggle } from "./DarkModeToggle";

interface GalleryGridProps {
  styles: StyleData[];
}

export function GalleryGrid({ styles }: GalleryGridProps) {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [selectedStyle, setSelectedStyle] = useState<StyleData | null>(null);

  const statusScoped = useMemo(
    () =>
      styles.filter(
        (style) => !filters.status || style.status === filters.status
      ),
    [styles, filters.status]
  );
  const types = useMemo(
    () => getUniqueValues(statusScoped, "type"),
    [statusScoped]
  );
  const complexities = useMemo(
    () => getUniqueValues(statusScoped, "complexity"),
    [statusScoped]
  );
  const eras = useMemo(
    () => getUniqueValues(statusScoped, "eraOrigin"),
    [statusScoped]
  );

  const filtered = useMemo(
    () => filterStyles(styles, filters),
    [styles, filters]
  );
  const activeCount = useMemo(
    () => filterStyles(styles, DEFAULT_FILTERS).length,
    [styles]
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Style Gallery
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Browse {activeCount} active UI styles from Antigravity Kit
          </p>
        </div>
        <DarkModeToggle />
      </div>

      {/* Search */}
      <div className="mb-4">
        <SearchInput
          value={filters.search}
          onChange={(search) => setFilters((f) => ({ ...f, search }))}
        />
      </div>

      {/* Filters */}
      <div className="mb-6">
        <FilterBar
          filters={filters}
          onChange={setFilters}
          types={types}
          complexities={complexities}
          eras={eras}
          resultCount={filtered.length}
          totalCount={statusScoped.length}
        />
      </div>

      {/* Grid */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((style) => (
            <StyleCard
              key={style.styleId}
              style={style}
              onSelect={setSelectedStyle}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-gray-500 dark:text-gray-400">
            No styles match your filters.
          </p>
          <button
            onClick={() => setFilters(DEFAULT_FILTERS)}
            className="mt-2 text-sm text-blue-500 hover:text-blue-600"
          >
            Clear all filters
          </button>
        </div>
      )}

      {/* Style Detail Modal */}
      {selectedStyle && (
        <StyleDetailModal
          style={selectedStyle}
          onClose={() => setSelectedStyle(null)}
        />
      )}
    </div>
  );
}
