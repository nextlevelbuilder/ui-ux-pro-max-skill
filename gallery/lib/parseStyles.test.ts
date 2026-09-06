import assert from "node:assert/strict";
import test from "node:test";

import { DEFAULT_FILTERS, filterStyles } from "./filterStyles";
import { parseStylesCSV } from "./parseStyles";

const headers = [
  "Status", "Style Category", "No", "Style ID", "Aliases", "Parent Style ID",
  "Replacement Domain", "Replacement ID", "Preferred Mode", "Type", "Keywords", "Primary Colors",
  "Secondary Colors", "Effects & Animation", "Best For", "Do Not Use For",
  "Light Mode ✓", "Dark Mode ✓", "Performance", "Accessibility",
  "Mobile-Friendly", "Conversion-Focused", "Framework Compatibility", "Era/Origin",
  "Complexity", "AI Prompt Keywords", "CSS/Technical Keywords",
  "Implementation Checklist", "Design System Variables",
];

function row(status: string, id: string, replacement = ""): string {
  const values: Record<string, string> = {
    Status: status, "Style Category": id, No: status === "active" ? "1" : "2",
    "Style ID": id, Aliases: `${id}-alias`, "Replacement Domain": replacement,
    "Replacement ID": replacement ? "Hero + CTA" : "", Type: "General",
    Keywords: "clean", "Primary Colors": "#ffffff", "Secondary Colors": "#000000",
    "CSS/Technical Keywords": "display: grid", Complexity: "Low",
  };
  return headers.map((header) => JSON.stringify(values[header] || "")).join(",");
}

test("parses taxonomy fields by header name", () => {
  const styles = parseStylesCSV([
    headers.join(","),
    row("deprecated", "legacy-layout", "landing"),
  ].join("\n"));
  assert.equal(styles[0].styleId, "legacy-layout");
  assert.equal(styles[0].status, "deprecated");
  assert.equal(styles[0].replacementDomain, "landing");
  assert.equal(styles[0].replacementId, "Hero + CTA");
});

test("gallery defaults to active and exposes explicit status views", () => {
  const styles = parseStylesCSV([
    headers.join(","),
    row("active", "active-style"),
    row("supplemental", "candidate-style"),
    row("deprecated", "legacy-style", "landing"),
  ].join("\n"));
  assert.deepEqual(filterStyles(styles, DEFAULT_FILTERS).map((s) => s.styleId), [
    "active-style",
  ]);
  assert.deepEqual(
    filterStyles(styles, { ...DEFAULT_FILTERS, status: "supplemental" }).map(
      (style) => style.styleId
    ),
    ["candidate-style"],
  );
  assert.equal(filterStyles(styles, { ...DEFAULT_FILTERS, status: "" }).length, 3);
});

test("parser rejects missing or unknown status", () => {
  assert.throws(
    () => parseStylesCSV([headers.join(","), row("", "missing-status")].join("\n")),
    /Unknown or missing style status/,
  );
  assert.throws(
    () => parseStylesCSV([headers.join(","), row("draft", "draft-style")].join("\n")),
    /Unknown or missing style status/,
  );
});

test("parses quoted multiline fields as one record", () => {
  const multiline = row("active", "multiline-style").replace(
    '"clean"',
    '"clean\nlayered"',
  );
  const styles = parseStylesCSV([headers.join(","), multiline].join("\r\n"));
  assert.equal(styles.length, 1);
  assert.equal(styles[0].keywords, "clean\nlayered");
});
