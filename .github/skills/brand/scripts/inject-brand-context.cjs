#!/usr/bin/env node
/**
 * inject-brand-context.cjs
 *
 * Extracts brand context from markdown brand guidelines
 * and outputs a formatted system prompt addition.
 *
 * Usage:
 *   node inject-brand-context.cjs [path-to-guidelines]
 *   node inject-brand-context.cjs --json [path-to-guidelines]
 *
 * Default path: docs/brand-guidelines.md
 */

const fs = require("fs");
const path = require("path");

// Default brand guidelines path
const DEFAULT_GUIDELINES_PATH = "docs/brand-guidelines.md";

/**
 * Extract hex colors from text
 */
function extractHexColors(text) {
  const hexPattern = /#[0-9A-Fa-f]{6}\b/g;
  return [...new Set(text.match(hexPattern) || [])];
}

/**
 * Extract color data from markdown table
 */
function extractColorsFromTable(content) {
  const colors = {
    primary: [],
    secondary: [],
    neutral: [],
    semantic: [],
  };

  // Find color tables
  const primaryMatch = content.match(
    /### Primary Colors[\s\S]*?\|[\s\S]*?(?=###|$)/i
  );
  const secondaryMatch = content.match(
    /### Secondary Colors[\s\S]*?\|[\s\S]*?(?=###|$)/i
  );
  const neutralMatch = content.match(
    /### Neutral[\s\S]*?\|[\s\S]*?(?=###|$)/i
  );
  const semanticMatch = content.match(
    /### Semantic[\s\S]*?\|[\s\S]*?(?=###|$)/i
  );

  if (primaryMatch) colors.primary = extractHexColors(primaryMatch[0]);
  if (secondaryMatch) colors.secondary = extractHexColors(secondaryMatch[0]);
  if (neutralMatch) colors.neutral = extractHexColors(neutralMatch[0]);
  if (semanticMatch) colors.semantic = extractHexColors(semanticMatch[0]);

  return colors;
}

/**
 * Extract typography info
 */
function extractTypography(content) {
  const typography = {
    heading: null,
    body: null,
    mono: null,
  };

  // Look for font definitions
  const headingMatch = content.match(/--font-heading:\s*['"]([^'"]+)['"]/);
  const bodyMatch = content.match(/--font-body:\s*['"]([^'"]+)['"]/);
  const monoMatch = content.match(/--font-mono:\s*['"]([^'"]+)['"]/);

  // Fallback: look in tables
  const fontStackMatch = content.match(/### Font Stack[\s\S]*?(?=###|##|$)/i);
  if (fontStackMatch) {
    const stackText = fontStackMatch[0];
    const headingAlt = stackText.match(/heading[^']*['"]([^'"]+)['"]/i);
    const bodyAlt = stackText.match(/body[^']*['"]([^'"]+)['"]/i);

    if (headingAlt) typography.heading = headingAlt[1];
    if (bodyAlt) typography.body = bodyAlt[1];
  }

  if (headingMatch) typography.heading = headingMatch[1];
  if (bodyMatch) typography.body = bodyMatch[1];
  if (monoMatch) typography.mono = monoMatch[1];

  return typography;
}

/**
 * Extract voice/tone information
 */
function extractVoice(content) {
  const voice = {
    traits: [],
    prohibited: [],
    personality: "",
  };

  // Extract personality traits from table
  const personalityMatch = content.match(
    /### Brand Personality[\s\S]*?\|[\s\S]*?(?=###|##|$)/i
  );
  if (personalityMatch) {
    const traits = personalityMatch[0].match(
      /\*\*([^*]+)\*\*\s*\|\s*([^|]+)/g
    );
    if (traits) {
      voice.traits = traits.map((t) => {
        const match = t.match(/\*\*([^*]+)\*\*/);
        return match ? match[1].trim() : "";
      }).filter(Boolean);
    }
  }

  // Extract prohibited terms
  const prohibitedMatch = content.match(
    /### Prohibited[\s\S]*?(?=###|##|$)/i
  );
  if (prohibitedMatch) {
    const terms = prohibitedMatch[0].match(/\|\s*([^|]+)\s*\|/g);
    if (terms) {
      voice.prohibited = terms
        .map((t) => t.replace(/\|/g, "").trim())
        .filter((t) => t && !t.includes("Avoid") && !t.includes("---"));
    }
  }

  // Fallback: look for Forbidden Phrases
  const forbiddenMatch = content.match(
    /### Forbidden Phrases[\s\S]*?(?=###|##|$)/i
  );
  if (forbiddenMatch && voice.prohibited.length === 0) {
    const items = forbiddenMatch[0].match(/-\s*["']?([^"'\n(]+)/g);
    if (items) {
      voice.prohibited = items
        .map((item) => item.replace(/^-\s*["']?/, "").trim())
        .filter(Boolean);
    }
  }

  voice.personality = voice.traits.join(", ");

  return voice;
}

/**
 * Extract core attributes
 */
function extractCoreAttributes(content) {
  const attributes = [];

  const attributesMatch = content.match(
    /### Core Attributes[\s\S]*?\|[\s\S]*?(?=###|##|$)/i
  );
  if (attributesMatch) {
    const rows = attributesMatch[0].match(
      /\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|/g
    );
    if (rows) {
      rows.forEach((row) => {
        const match = row.match(/\*\*([^*]+)\*\*\s*\|\s*([^|]+)/);
        if (match) {
          attributes.push({
            name: match[1].trim(),
            description: match[2].trim(),
          });
        }
      });
    }
  }

  return attributes;
}

/**
 * Extract AI image generation context
 */
function extractImageStyle(content) {
  const imageStyle = {
    basePrompt: "",
    keywords: [],
    mood: [],
    donts: [],
    examplePrompts: [],
  };

  // Extract base prompt template (content between ``` blocks after "Base Prompt Template")
  const basePromptMatch = content.match(
    /### Base Prompt Template[\s\S]*?```\n?([\s\S]*?)```/i
  );
  if (basePromptMatch) {
    imageStyle.basePrompt = basePromptMatch[1].trim().replace(/\n/g, " ");
  }

  // Extract style keywords from table
  const keywordsMatch = content.match(
    /### Style Keywords[\s\S]*?\|[\s\S]*?(?=###|##|$)/i
  );
  if (keywordsMatch) {
    const keywordRows = keywordsMatch[0].match(/\|\s*\*\*[^*]+\*\*\s*\|\s*([^|]+)\|/g);
    if (keywordRows) {
      keywordRows.forEach((row) => {
        const match = row.match(/\|\s*\*\*[^*]+\*\*\s*\|\s*([^|]+)\|/);
        if (match) {
          const keywords = match[1].split(",").map((k) => k.trim()).filter(Boolean);
          imageStyle.keywords.push(...keywords);
        }
      });
    }
  }

  // Extract visual mood descriptors (bullet points)
  const moodMatch = content.match(
    /### Visual Mood Descriptors[\s\S]*?(?=###|##|$)/i
  );
  if (moodMatch) {
    const moodItems = moodMatch[0].match(/-\s*([^\n]+)/g);
    if (moodItems) {
      imageStyle.mood = moodItems.map((item) => item.replace(/^-\s*/, "").trim());
    }
  }

  // Extract visual don'ts from table
  const dontsMatch = content.match(
    /### Visual Don'ts[\s\S]*?\|[\s\S]*?(?=###|##|$)/i
  );
  if (dontsMatch) {
    const dontRows = dontsMatch[0].match(/\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|/g);
    if (dontRows) {
      dontRows.forEach((row) => {
        const match = row.match(/\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|/);
        if (match && !match[1].includes("Avoid") && !match[1].includes("---")) {
          imageStyle.donts.push(match[1].trim());
        }
      });
    }
  }

  // Extract example prompts (content between ``` blocks after specific headers)
  const exampleMatch = content.match(/### Example Prompts[\s\S]*?(?=##|$)/i);
  if (exampleMatch) {
    const prompts = exampleMatch[0].match(/\*\*([^*]+)\*\*:\s*```\n?([\s\S]*?)```/g);
    if (prompts) {
      prompts.forEach((p) => {
        const match = p.match(/\*\*([^*]+)\*\*:\s*```\n?([\s\S]*?)```/);
        if (match) {
          imageStyle.examplePrompts.push({
            type: match[1].trim(),
            prompt: match[2].trim().replace(/\n/g, " "),
          });
        }
      });
    }
  }

  return imageStyle;
}

/**
 * Generate system prompt addition
 */
function generatePromptAddition(brandContext) {
  const { colors, typography, voice, attributes, imageStyle } = brandContext;

  let prompt = `
BRAND CONTEXT:
==============

VISUAL IDENTITY:
- Primary Colors: ${colors.primary.join(", ") || "Not specified"}
- Secondary Colors: ${colors.secondary.join(", ") || "Not specified"}
- Typography: ${typography.heading || typography.body || "System fonts"}

BRAND VOICE:
- Personality: ${voice.personality || "Professional"}
- Core Attributes: ${attributes.map((a) => a.name).join(", ") || "Not specified"}

CONTENT RULES:
- Prohibited Terms: ${voice.prohibited.join(", ") || "None specified"}
`;

  // Add image style context if available
  if (imageStyle && imageStyle.basePrompt) {
    prompt += `
IMAGE GENERATION:
- Base Prompt: ${imageStyle.basePrompt}
- Style Keywords: ${imageStyle.keywords.slice(0, 10).join(", ") || "Not specified"}
- Visual Mood: ${imageStyle.mood.slice(0, 5).join("; ") || "Not specified"}
- Avoid: ${imageStyle.donts.join(", ") || "None specified"}
`;
  }

  prompt += `
Apply these brand guidelines to all generated content.
Maintain consistent voice, colors, and messaging.
`;

  return prompt.trim();
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);
  const jsonOutput = args.includes("--json");
  const guidelinesPath = args.find((a) => !a.startsWith("--")) || DEFAULT_GUIDELINES_PATH;

  // Resolve path
  const resolvedPath = path.isAbsolute(guidelinesPath)
    ? guidelinesPath
    : path.join(process.cwd(), guidelinesPath);

  // Check if file exists
  if (!fs.existsSync(resolvedPath)) {
    console.error(`Error: Brand guidelines not found at ${resolvedPath}`);
    console.error(`Create brand guidelines at ${DEFAULT_GUIDELINES_PATH} or specify a path.`);
    process.exit(1);
  }

  // Read file
  const content = fs.readFileSync(resolvedPath, "utf-8");

  // Extract brand context
  const brandContext = {
    colors: extractColorsFromTable(content),
    typography: extractTypography(content),
    voice: extractVoice(content),
    attributes: extractCoreAttributes(content),
    imageStyle: extractImageStyle(content),
    source: resolvedPath,
    extractedAt: new Date().toISOString(),
  };

  // Output
  if (jsonOutput) {
    console.log(JSON.stringify(brandContext, null, 2));
  } else {
    console.log(generatePromptAddition(brandContext));
  }
}

main();
