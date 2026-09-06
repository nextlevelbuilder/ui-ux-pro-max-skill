#!/usr/bin/env node
/**
 * sync-brand-to-tokens.cjs
 *
 * Syncs brand-guidelines.md colors → design-tokens.json → design-tokens.css
 *
 * Usage:
 *   node sync-brand-to-tokens.cjs
 *   node sync-brand-to-tokens.cjs --dry-run
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// Paths
const BRAND_GUIDELINES = 'docs/brand-guidelines.md';
const DESIGN_TOKENS_JSON = 'assets/design-tokens.json';
const DESIGN_TOKENS_CSS = 'assets/design-tokens.css';
// Sibling sub-skill, resolved from this file's location so it works in every
// install context (plugin cache, project or --global CLI install), not only
// when the process runs from a project root that contains .claude/skills/.
const GENERATE_TOKENS_SCRIPT = path.resolve(__dirname, '..', '..', 'design-system', 'scripts', 'generate-tokens.cjs');

/**
 * Extract color info from brand guidelines markdown
 */
function extractColorsFromMarkdown(content) {
  const colors = {
    primary: { name: 'primary', shades: {} },
    secondary: { name: 'secondary', shades: {} },
    accent: { name: 'accent', shades: {} }
  };

  // Match a "| Label | #hex |" markdown table row. Bold around the label
  // (**Label**) is optional, so this handles both the bundled starter template
  // ("| Primary Blue | #2563EB |") and bolded variants.
  const rowRe = /\|\s*\*{0,2}([^*|]+?)\*{0,2}\s*\|\s*#([A-Fa-f0-9]{6})\b/g;

  // 1) Quick Reference table — hex only, no parenthesized name required.
  const quickRef = {
    primary: /Primary Color\s*\|\s*#([A-Fa-f0-9]{6})/i,
    secondary: /Secondary Color\s*\|\s*#([A-Fa-f0-9]{6})/i,
    accent: /Accent Color\s*\|\s*#([A-Fa-f0-9]{6})/i
  };
  for (const key of Object.keys(quickRef)) {
    const m = content.match(quickRef[key]);
    if (m) colors[key].base = `#${m[1]}`;
  }

  // 2) Dedicated "### <Role> Colors" tables — assign base/dark/light by the
  //    row label keyword.
  const assignFromSection = (heading, target) => {
    const section = content.match(new RegExp(`### ${heading}[\\s\\S]*?(?=\\n###|$)`, 'i'));
    if (!section) return;
    for (const m of section[0].matchAll(rowRe)) {
      const label = m[1].trim().toLowerCase();
      const hex = `#${m[2]}`;
      if (label.includes('dark')) target.dark = hex;
      else if (label.includes('light')) target.light = hex;
      else if (!target.base) target.base = hex;
    }
  };
  assignFromSection('Primary Colors', colors.primary);
  assignFromSection('Secondary Colors', colors.secondary);
  assignFromSection('Accent Colors', colors.accent);

  // 3) Fallback: an accent swatch may live in another table (the starter
  //    lists "Accent Green" under Secondary Colors).
  if (!colors.accent.base) {
    for (const m of content.matchAll(rowRe)) {
      if (m[1].trim().toLowerCase().includes('accent')) {
        colors.accent.base = `#${m[2]}`;
        break;
      }
    }
  }

  return colors;
}

/**
 * Generate color scale from base color (simple approach)
 */
function generateColorScale(baseHex, darkHex, lightHex) {
  // Use provided shades or generate approximations
  return {
    "50": { "$value": lightHex || adjustBrightness(baseHex, 0.9), "$type": "color" },
    "100": { "$value": lightHex || adjustBrightness(baseHex, 0.8), "$type": "color" },
    "200": { "$value": adjustBrightness(baseHex, 0.6), "$type": "color" },
    "300": { "$value": adjustBrightness(baseHex, 0.4), "$type": "color" },
    "400": { "$value": adjustBrightness(baseHex, 0.2), "$type": "color" },
    "500": { "$value": baseHex, "$type": "color" },
    "600": { "$value": darkHex || adjustBrightness(baseHex, -0.15), "$type": "color" },
    "700": { "$value": adjustBrightness(baseHex, -0.3), "$type": "color" },
    "800": { "$value": adjustBrightness(baseHex, -0.45), "$type": "color" },
    "900": { "$value": adjustBrightness(baseHex, -0.6), "$type": "color" }
  };
}

/**
 * Adjust hex color brightness
 */
function adjustBrightness(hex, percent) {
  if (typeof hex !== 'string') return '#000000';
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, Math.max(0, (num >> 16) + Math.round(255 * percent)));
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + Math.round(255 * percent)));
  const b = Math.min(255, Math.max(0, (num & 0x0000FF) + Math.round(255 * percent)));
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0').toUpperCase()}`;
}

/**
 * Update design tokens JSON
 */
function updateDesignTokens(tokens, colors) {
  // Update brand name
  const brandName = `ClaudeKit Marketing - ${colors.primary.name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}`;
  tokens.brand = brandName;

  // Update primitive colors with new names
  tokens.primitive = tokens.primitive || {};
  const primitiveColors = tokens.primitive.color || {};

  // Remove old color keys, add new ones
  delete primitiveColors.coral;
  delete primitiveColors.purple;
  delete primitiveColors.mint;

  // Add new named colors. Skip any role with no base hex rather than crashing
  // on an unexpected guidelines format.
  for (const role of ['primary', 'secondary', 'accent']) {
    const c = colors[role];
    if (!c.base) {
      console.warn(`⚠️  No base hex found for ${role} color — skipping its token scale.`);
      continue;
    }
    primitiveColors[c.name] = generateColorScale(c.base, c.dark, c.light);
  }

  tokens.primitive.color = primitiveColors;

  // Update ALL semantic color references
  if (tokens.semantic?.color) {
    const sem = tokens.semantic.color;
    const p = colors.primary.name;
    const s = colors.secondary.name;
    const a = colors.accent.name;

    // Primary variants
    sem.primary = { "$value": `{primitive.color.${p}.500}`, "$type": "color" };
    sem['primary-hover'] = { "$value": `{primitive.color.${p}.600}`, "$type": "color" };
    sem['primary-active'] = { "$value": `{primitive.color.${p}.700}`, "$type": "color" };
    sem['primary-light'] = { "$value": `{primitive.color.${p}.400}`, "$type": "color" };
    sem['primary-lighter'] = { "$value": `{primitive.color.${p}.100}`, "$type": "color" };
    sem['primary-dark'] = { "$value": `{primitive.color.${p}.600}`, "$type": "color" };

    // Secondary variants
    sem.secondary = { "$value": `{primitive.color.${s}.500}`, "$type": "color" };
    sem['secondary-hover'] = { "$value": `{primitive.color.${s}.600}`, "$type": "color" };
    sem['secondary-light'] = { "$value": `{primitive.color.${s}.300}`, "$type": "color" };
    sem['secondary-dark'] = { "$value": `{primitive.color.${s}.600}`, "$type": "color" };

    // Accent variants
    sem.accent = { "$value": `{primitive.color.${a}.500}`, "$type": "color" };
    sem['accent-hover'] = { "$value": `{primitive.color.${a}.600}`, "$type": "color" };
    sem['accent-light'] = { "$value": `{primitive.color.${a}.300}`, "$type": "color" };

    // Status colors (use accent for success, primary for error/info)
    sem.success = { "$value": `{primitive.color.${a}.500}`, "$type": "color" };
    sem['success-light'] = { "$value": `{primitive.color.${a}.300}`, "$type": "color" };
    sem.error = { "$value": `{primitive.color.${p}.500}`, "$type": "color" };
    sem['error-light'] = { "$value": `{primitive.color.${p}.300}`, "$type": "color" };
    sem.info = { "$value": `{primitive.color.${s}.500}`, "$type": "color" };
    sem['info-light'] = { "$value": `{primitive.color.${s}.300}`, "$type": "color" };
  }

  // Update component references (button uses primary color with opacity)
  if (tokens.component?.button?.secondary && colors.primary.base) {
    const primaryBase = colors.primary.base;
    tokens.component.button.secondary['bg-hover'] = {
      "$value": `${primaryBase}1A`,
      "$type": "color"
    };
  }

  return tokens;
}

/**
 * Main
 */
function main() {
  const dryRun = process.argv.includes('--dry-run');

  console.log('🔄 Syncing brand guidelines → design tokens\n');

  // Read brand guidelines
  const guidelinesPath = path.resolve(process.cwd(), BRAND_GUIDELINES);
  if (!fs.existsSync(guidelinesPath)) {
    console.error(`❌ Brand guidelines not found: ${guidelinesPath}`);
    process.exit(1);
  }
  const guidelinesContent = fs.readFileSync(guidelinesPath, 'utf-8');

  // Extract colors
  const colors = extractColorsFromMarkdown(guidelinesContent);
  console.log('📊 Extracted colors:');
  console.log(`   Primary: ${colors.primary.name} (${colors.primary.base})`);
  console.log(`   Secondary: ${colors.secondary.name} (${colors.secondary.base})`);
  console.log(`   Accent: ${colors.accent.name} (${colors.accent.base})\n`);

  // Read existing tokens
  const tokensPath = path.resolve(process.cwd(), DESIGN_TOKENS_JSON);
  let tokens = {};
  if (fs.existsSync(tokensPath)) {
    tokens = JSON.parse(fs.readFileSync(tokensPath, 'utf-8'));
  }

  // Update tokens
  tokens = updateDesignTokens(tokens, colors);

  if (dryRun) {
    console.log('📋 Would update design-tokens.json:');
    console.log(JSON.stringify(tokens.primitive.color, null, 2).slice(0, 500) + '...');
    console.log('\n⏭️  Dry run - no files changed');
    return;
  }

  // Write updated tokens
  fs.writeFileSync(tokensPath, JSON.stringify(tokens, null, 2));
  console.log(`✅ Updated: ${DESIGN_TOKENS_JSON}`);

  // Regenerate CSS
  const generateScript = GENERATE_TOKENS_SCRIPT;
  if (fs.existsSync(generateScript)) {
    try {
      execFileSync('node', [generateScript, '--config', DESIGN_TOKENS_JSON, '-o', DESIGN_TOKENS_CSS], {
        cwd: process.cwd(),
        stdio: 'inherit'
      });
      console.log(`✅ Regenerated: ${DESIGN_TOKENS_CSS}`);
    } catch (e) {
      console.error('⚠️  Failed to regenerate CSS:', e.message);
    }
  } else {
    console.warn(`⚠️  design-system sub-skill not found at ${generateScript}; ${DESIGN_TOKENS_CSS} not regenerated`);
  }

  console.log('\n✨ Brand sync complete!');
}

main();
