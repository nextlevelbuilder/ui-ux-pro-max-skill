interface StyleStatusBadgeProps {
  status: string;
}

export function StyleStatusBadge({ status }: StyleStatusBadgeProps) {
  if (!status) return null;

  const colorClass =
    status === "deprecated"
      ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
      : status === "supplemental"
      ? "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
      : "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";

  return (
    <span
      className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${colorClass}`}
    >
      {status}
    </span>
  );
}
