import { StyleData } from "./types";
import { extractColors } from "./colorExtractor";
import { parseCssKeywords } from "./cssGenerator";

function parseCSVLine(line: string): string[] {
  const fields: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (inQuotes) {
      if (char === '"') {
        if (i + 1 < line.length && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        current += char;
      }
    } else {
      if (char === '"') {
        inQuotes = true;
      } else if (char === ",") {
        fields.push(current.trim());
        current = "";
      } else {
        current += char;
      }
    }
  }
  fields.push(current.trim());
  return fields;
}

function splitCSVRecords(content: string): string[] {
  const records: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < content.length; i++) {
    const char = content[i];
    if (char === '"') {
      current += char;
      if (inQuotes && content[i + 1] === '"') {
        current += content[++i];
      } else {
        inQuotes = !inQuotes;
      }
    } else if (!inQuotes && (char === "\n" || char === "\r")) {
      if (current.trim()) records.push(current);
      current = "";
      if (char === "\r" && content[i + 1] === "\n") i++;
    } else {
      current += char;
    }
  }
  if (current.trim()) records.push(current);
  if (inQuotes) throw new Error("Unterminated quoted CSV field");
  return records;
}

export function parseStylesCSV(csvContent: string): StyleData[] {
  const lines = splitCSVRecords(csvContent);
  if (lines.length < 2) return [];

  const headers = parseCSVLine(lines[0]);
  const column = new Map(headers.map((header, index) => [header, index]));
  const value = (fields: string[], header: string): string => {
    const index = column.get(header);
    return index === undefined ? "" : fields[index] || "";
  };

  const dataLines = lines.slice(1);
  return dataLines.map((line) => {
    const f = parseCSVLine(line);
    const primaryColors = value(f, "Primary Colors");
    const secondaryColors = value(f, "Secondary Colors");
    const cssTechnicalKeywords = value(f, "CSS/Technical Keywords");
    const status = value(f, "Status");
    if (!(["active", "supplemental", "deprecated"] as string[]).includes(status)) {
      throw new Error(`Unknown or missing style status: ${status || "<empty>"}`);
    }

    return {
      no: parseInt(value(f, "No")) || 0,
      styleId: value(f, "Style ID"),
      styleCategory: value(f, "Style Category"),
      aliases: value(f, "Aliases").split("|").map((alias) => alias.trim()).filter(Boolean),
      status: status as StyleData["status"],
      parentStyleId: value(f, "Parent Style ID"),
      replacementDomain: value(f, "Replacement Domain"),
      replacementId: value(f, "Replacement ID"),
      preferredMode: (value(f, "Preferred Mode") || "auto") as StyleData["preferredMode"],
      type: value(f, "Type"),
      keywords: value(f, "Keywords"),
      primaryColors,
      secondaryColors,
      effectsAnimation: value(f, "Effects & Animation"),
      bestFor: value(f, "Best For"),
      doNotUseFor: value(f, "Do Not Use For"),
      lightMode: value(f, "Light Mode ✓"),
      darkMode: value(f, "Dark Mode ✓"),
      performance: value(f, "Performance"),
      accessibility: value(f, "Accessibility"),
      mobileFriendly: value(f, "Mobile-Friendly"),
      conversionFocused: value(f, "Conversion-Focused"),
      frameworkCompatibility: value(f, "Framework Compatibility"),
      eraOrigin: value(f, "Era/Origin"),
      complexity: value(f, "Complexity"),
      aiPromptKeywords: value(f, "AI Prompt Keywords"),
      cssTechnicalKeywords,
      implementationChecklist: value(f, "Implementation Checklist"),
      designSystemVariables: value(f, "Design System Variables"),
      extractedColors: extractColors(`${primaryColors} ${secondaryColors}`),
      cssProperties: parseCssKeywords(cssTechnicalKeywords),
    };
  });
}
