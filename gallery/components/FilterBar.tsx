"use client";

import { DEFAULT_FILTERS, type Filters } from "../lib/filterStyles";

const STATUS_OPTIONS = ["active", "supplemental", "deprecated"];

interface FilterBarProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  types: string[];
  complexities: string[];
  eras: string[];
  resultCount: number;
  totalCount: number;
}

function FilterGroup({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: string[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div
      aria-label={`${label} filter`}
      className="flex flex-wrap items-center gap-1.5"
      role="group"
    >
      <span aria-hidden="true" className="text-xs font-medium text-gray-500 dark:text-gray-400 mr-1">
        {label}:
      </span>
      <button
        aria-pressed={value === ""}
        onClick={() => onChange("")}
        type="button"
        className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
          value === ""
            ? "bg-blue-500 text-white"
            : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
        }`}
      >
        All
      </button>
      {options.map((opt) => (
        <button
          aria-pressed={value === opt}
          key={opt}
          onClick={() => onChange(value === opt ? "" : opt)}
          type="button"
          className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
            value === opt
              ? "bg-blue-500 text-white"
              : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

export function FilterBar({
  filters,
  onChange,
  types,
  complexities,
  eras,
  resultCount,
  totalCount,
}: FilterBarProps) {
  const hasFilters = Boolean(
    filters.search ||
      filters.status !== DEFAULT_FILTERS.status ||
      filters.type ||
      filters.complexity ||
      filters.era
  );

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-4">
        <FilterGroup
          label="Status"
          options={STATUS_OPTIONS}
          value={filters.status}
          onChange={(status) => onChange({ ...filters, status })}
        />
        <FilterGroup
          label="Type"
          options={types}
          value={filters.type}
          onChange={(type) => onChange({ ...filters, type })}
        />
        <FilterGroup
          label="Complexity"
          options={complexities}
          value={filters.complexity}
          onChange={(complexity) => onChange({ ...filters, complexity })}
        />
      </div>
      <div className="flex flex-wrap gap-4">
        <FilterGroup
          label="Era"
          options={eras}
          value={filters.era}
          onChange={(era) => onChange({ ...filters, era })}
        />
      </div>
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Showing <span className="font-semibold text-gray-700 dark:text-gray-200">{resultCount}</span> of {totalCount} styles
        </p>
        {hasFilters && (
          <button
            onClick={() => onChange(DEFAULT_FILTERS)}
            type="button"
            className="text-xs text-blue-500 hover:text-blue-600 transition-colors"
          >
            Clear all filters
          </button>
        )}
      </div>
    </div>
  );
}
