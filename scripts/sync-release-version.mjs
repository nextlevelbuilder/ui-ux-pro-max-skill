#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const version = process.argv[2];
if (!version) {
  console.error('Usage: node scripts/sync-release-version.mjs <version>');
  process.exit(1);
}

function readJson(path) {
  return JSON.parse(readFileSync(resolve(path), 'utf8'));
}

function replaceJsonVersion(path, updater) {
  const fullPath = resolve(path);
  const original = readFileSync(fullPath, 'utf8');
  const data = JSON.parse(original);
  updater(data);
  let next = original;
  const replacements = [];

  function setTopLevelVersion(value) {
    replacements.push([/(\"version\"\s*:\s*)\"[^\"]+\"/, `$1\"${value}\"`]);
  }

  function setMetadataVersion(value) {
    replacements.push([/(\"metadata\"\s*:\s*\{[\s\S]*?\"version\"\s*:\s*)\"[^\"]+\"/, `$1\"${value}\"`]);
  }

  function setPluginVersions(value) {
    replacements.push([/(\"plugins\"\s*:\s*\[[\s\S]*?\"version\"\s*:\s*)\"[^\"]+\"/, `$1\"${value}\"`]);
  }

  if (path === '.claude-plugin/marketplace.json') {
    setMetadataVersion(data.metadata?.version);
    if (data.plugins?.[0]?.version) setPluginVersions(data.plugins[0].version);
  } else {
    setTopLevelVersion(data.version);
    if (data.packages?.['']?.version) {
      replacements.push([/(\"packages\"\s*:\s*\{\s*\"\"\s*:\s*\{[\s\S]*?\"version\"\s*:\s*)\"[^\"]+\"/, `$1\"${data.packages[''].version}\"`]);
    }
  }

  for (const [pattern, replacement] of replacements) next = next.replace(pattern, replacement);
  writeFileSync(fullPath, next);
}

replaceJsonVersion('skill.json', (data) => {
  data.version = version;
});

replaceJsonVersion('.claude-plugin/plugin.json', (data) => {
  data.version = version;
});

replaceJsonVersion('.claude-plugin/marketplace.json', (data) => {
  if (data.metadata) data.metadata.version = version;
  if (Array.isArray(data.plugins)) {
    for (const item of data.plugins) item.version = version;
  }
});

replaceJsonVersion('cli/package.json', (data) => {
  data.version = version;
});

try {
  replaceJsonVersion('cli/package-lock.json', (data) => {
    data.version = version;
    if (data.packages?.['']) data.packages[''].version = version;
  });
} catch (err) {
  if (err.code !== 'ENOENT') throw err;
}

console.log(`Synced release version ${version} across skill, plugin, marketplace, and CLI manifests.`);
