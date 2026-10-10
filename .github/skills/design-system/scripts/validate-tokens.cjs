#!/usr/bin/env node
/**
 * Validate token usage in codebase
 * Finds hardcoded values that should use design tokens
 *
 * Usage:
 *   node validate-tokens.cjs --dir src/
 *   node validate-tokens.cjs --dir src/ --fix
 */

const fs = require('fs');
const path = require('path');

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    dir: null,
    fix: false,
    ignore: ['node_modules', '.git', 'dist', 'build', '.next']
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--dir' || args[i] === '-d') {
      options.dir = args[++i];
    } else if (args[i] === '--fix') {
      options.fix = true;
    } else if (args[i] === '--ignore' || args[i] === '-i') {
      options.ignore.push(args[++i]);
    } else if (args[i] === '--help' || args[i] === '-h') {
      console.log(`
Usage: node validate-tokens.cjs [options]

Options:
  -d, --dir <path>      Directory to scan (required)
  --fix                 Show suggested fixes (no auto-fix)
  -i, --ignore <dir>    Additional directories to ignore
  -h, --help            Show this help

Checks for:
  - Hardcoded hex colors (#RGB, #RRGGBB)
  - Hardcoded pixel values (except 0, 1px)
  - Hardcoded rem values in CSS
      `);
      process.exit(0);
    }
  }

  return options;
}

/**
 * Patterns to detect hardcoded values
 */
const patterns = {
  hexColor: {
    regex: /#([0-9A-Fa-f]{3}){1,2}\b/g,
    message: 'Hardcoded hex color',
    suggestion: 'Use var(--color-*) token'
  },
  rgbColor: {
    regex: /rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)/gi,
    message: 'Hardcoded RGB color',
    suggestion: 'Use var(--color-*) token'
  },
  pixelValue: {
    regex: /:\s*(\d{2,})px/g, // 2+ digit px values
    message: 'Hardcoded pixel value',
    suggestion: 'Use var(--space-*) or var(--radius-*) token'
  },
  remValue: {
    regex: /:\s*\d+\.?\d*rem(?![^{]*\$value)/g, // rem not in token definition
    message: 'Hardcoded rem value',
    suggestion: 'Use var(--space-*) or var(--font-size-*) token'
  }
};

/**
 * File extensions to scan
 */
const extensions = ['.css', '.scss', '.tsx', '.jsx', '.ts', '.js', '.vue', '.svelte'];

/**
 * Files/patterns to skip
 */
const skipPatterns = [
  /\.min\.(css|js)$/,
  /tailwind\.config/,
  /globals\.css/, // Token definitions
  /tokens\.(css|json)/
];

/**
 * Get all files recursively
 */
function getFiles(dir, ignore, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      if (!ignore.includes(entry.name)) {
        getFiles(fullPath, ignore, files);
      }
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name);
      if (extensions.includes(ext)) {
        files.push(fullPath);
      }
    }
  }

  return files;
}

/**
 * Check if file should be skipped
 */
function shouldSkip(filePath) {
  return skipPatterns.some(pattern => pattern.test(filePath));
}

/**
 * Scan file for violations
 */
function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  const violations = [];

  lines.forEach((line, index) => {
    // Skip comments
    if (line.trim().startsWith('//') || line.trim().startsWith('/*')) {
      return;
    }

    // Skip lines that already use CSS variables
    if (line.includes('var(--')) {
      return;
    }

    for (const [name, pattern] of Object.entries(patterns)) {
      const matches = line.match(pattern.regex);
      if (matches) {
        matches.forEach(match => {
          // Skip common exceptions
          if (name === 'hexColor' && ['#000', '#fff', '#FFF', '#000000', '#FFFFFF'].includes(match.toUpperCase())) {
            return; // Skip black/white, often intentional
          }

          violations.push({
            file: filePath,
            line: index + 1,
            column: line.indexOf(match) + 1,
            value: match,
            type: name,
            message: pattern.message,
            suggestion: pattern.suggestion,
            context: line.trim().substring(0, 80)
          });
        });
      }
    }
  });

  return violations;
}

/**
 * Format violation report
 */
function formatReport(violations) {
  if (violations.length === 0) {
    return '✅ No token violations found';
  }

  let report = `⚠️  Found ${violations.length} potential token violations:\n\n`;

  // Group by file
  const byFile = {};
  violations.forEach(v => {
    if (!byFile[v.file]) byFile[v.file] = [];
    byFile[v.file].push(v);
  });

  for (const [file, fileViolations] of Object.entries(byFile)) {
    report += `📁 ${file}\n`;
    fileViolations.forEach(v => {
      report += `   Line ${v.line}: ${v.message}\n`;
      report += `   Found: ${v.value}\n`;
      report += `   Suggestion: ${v.suggestion}\n`;
      report += `   Context: ${v.context}\n\n`;
    });
  }

  // Summary
  const byType = {};
  violations.forEach(v => {
    byType[v.type] = (byType[v.type] || 0) + 1;
  });

  report += `\n📊 Summary:\n`;
  for (const [type, count] of Object.entries(byType)) {
    report += `   ${patterns[type].message}: ${count}\n`;
  }

  return report;
}

/**
 * Main
 */
function main() {
  const options = parseArgs();

  if (!options.dir) {
    console.error('Error: --dir is required');
    process.exit(1);
  }

  const dirPath = path.resolve(process.cwd(), options.dir);

  if (!fs.existsSync(dirPath)) {
    console.error(`Error: Directory not found: ${dirPath}`);
    process.exit(1);
  }

  console.log(`Scanning ${dirPath} for token violations...\n`);

  const files = getFiles(dirPath, options.ignore);
  const allViolations = [];

  for (const file of files) {
    if (shouldSkip(file)) continue;

    const violations = scanFile(file);
    allViolations.push(...violations);
  }

  console.log(formatReport(allViolations));

  // Exit with error code if violations found
  if (allViolations.length > 0) {
    process.exit(1);
  }
}

main();
