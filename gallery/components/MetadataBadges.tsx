import type { StyleData } from "@/lib/types";

interface MetadataBadgesProps {
  style: StyleData;
}

type BadgeVariant = "green" | "yellow" | "red" | "blue" | "gray";

function Badge({
  label,
  accessibleLabel = label,
  variant,
}: {
  label: string;
  accessibleLabel?: string;
  variant: BadgeVariant;
}) {
  const colors = {
    green: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    yellow: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
    red: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
    blue: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    gray: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-[10px] font-medium rounded-full ${colors[variant]}`}>
      <span className="sr-only">{accessibleLabel}</span>
      <span aria-hidden="true">{label}</span>
    </span>
  );
}

function getComplexityVariant(c: string): "green" | "yellow" | "red" {
  if (c === "Low") return "green";
  if (c === "Medium") return "yellow";
  return "red";
}

export function getTaxonomyValue(metadata: string, key: string): string {
  const prefix = `${key}:`;
  const entry = metadata.split("|").find((part) => part.startsWith(prefix));
  return entry?.slice(prefix.length) ?? "unknown";
}

function formatTaxonomyValue(value: string): string {
  return value
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function getLevelVariant(value: string): BadgeVariant {
  if (value === "low" || value === "supported") return "green";
  if (value === "moderate" || value === "conditional") return "yellow";
  if (value === "high" || value === "not-recommended") return "red";
  return "gray";
}

function TaxonomyBadge({
  accessibleLabel,
  label,
  value,
}: {
  accessibleLabel: string;
  label: string;
  value: string;
}) {
  const displayValue = formatTaxonomyValue(value);

  return (
    <Badge
      accessibleLabel={`${accessibleLabel}: ${displayValue}`}
      label={`${label}: ${displayValue}`}
      variant={getLevelVariant(value)}
    />
  );
}

export function MetadataBadges({ style }: MetadataBadgesProps) {
  const performanceCost = getTaxonomyValue(style.performance, "cost");
  const accessibilityRisk = getTaxonomyValue(style.accessibility, "risk");

  return (
    <div aria-label="Style metadata" className="flex flex-wrap gap-1.5" role="group">
      {style.status !== "active" && (
        <Badge
          label={`Status: ${formatTaxonomyValue(style.status)}`}
          variant={style.status === "deprecated" ? "red" : "blue"}
        />
      )}
      <Badge
        label={`Complexity: ${style.complexity}`}
        variant={getComplexityVariant(style.complexity)}
      />
      <TaxonomyBadge
        accessibleLabel="Performance cost"
        label="Cost"
        value={performanceCost}
      />
      <TaxonomyBadge
        accessibleLabel="Accessibility risk"
        label="A11y risk"
        value={accessibilityRisk}
      />
      <TaxonomyBadge accessibleLabel="Light mode support" label="Light" value={style.lightMode} />
      <TaxonomyBadge accessibleLabel="Dark mode support" label="Dark" value={style.darkMode} />
    </div>
  );
}
