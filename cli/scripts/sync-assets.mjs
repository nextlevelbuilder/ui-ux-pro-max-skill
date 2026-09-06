#!/usr/bin/env node

import { createHash } from 'node:crypto';
import {
  access,
  mkdir,
  readdir,
  readFile,
  rm,
  writeFile,
} from 'node:fs/promises';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, '..', '..');
const sourceRoot = join(repoRoot, 'src', 'ui-ux-pro-max');
const assetRoot = join(repoRoot, 'cli', 'assets');
const dirsToSync = ['data', 'scripts', 'templates'];
const checkOnly = process.argv.includes('--check');

// The 6 sibling sub-skills are bundled (as static copies) so `uipro init`
// installs all 7 skills, not just the template-rendered orchestrator. Source
// of truth is .claude/skills/ (the orchestrator ui-ux-pro-max is rendered from
// templates at install time, so it is not mirrored here).
const skillsSourceRoot = join(repoRoot, '.claude', 'skills');
const skillsAssetRoot = join(assetRoot, 'skills');
const subSkills = ['banner-design', 'brand', 'design', 'design-system', 'slides', 'ui-styling'];

// The repo's own .claude/skills/ui-ux-pro-max/{data,scripts} is a second,
// independent copy of src/ui-ux-pro-max/{data,scripts} -- it's what Claude
// Code actually loads when this repo is installed as a plugin. Nothing
// previously checked it against src/, so it silently drifted (missing stack
// CSVs, stale content in several data files). SKILL.md there is hand-authored
// (not template-rendered like the CLI's copy), so only data/ and scripts/
// are mirrored -- never templates/ or SKILL.md itself.
const orchestratorSkillTargetRoot = join(skillsSourceRoot, 'ui-ux-pro-max');
const orchestratorDirsToSync = ['data', 'scripts'];

// ponytail: only text is bundled. Excludes (a) heavy binary assets — the
// canvas fonts are ~5.8MB and a skill registers from its SKILL.md, not its
// fonts — and (b) Python build cruft (__pycache__/*.pyc, .coverage) that would
// otherwise be picked up from a local run.
const isExcludedAssetFile = (rel) =>
  rel.split('/').some((seg) => seg === 'canvas-fonts' || seg === '__pycache__') ||
  /\.(ttf|otf|woff2?|png|jpe?g|gif|ico|coverage|pyc)$/i.test(rel);

// ponytail: all synced assets are text (csv/json/md/py); normalize CRLF->LF so
// the byte hash and the on-disk copy don't drift with git autocrlf across platforms.
const toLF = (text) => text.replace(/\r\n/g, '\n');

async function exists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

function assertInsideRepo(path) {
  const resolvedPath = resolve(path);
  if (!resolvedPath.startsWith(repoRoot)) {
    throw new Error(`Refusing to modify path outside repository: ${resolvedPath}`);
  }
  return resolvedPath;
}

async function listFiles(root) {
  const files = [];

  async function walk(dir) {
    for (const entry of await readdir(dir, { withFileTypes: true })) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(fullPath);
      } else if (entry.isFile()) {
        files.push(relative(root, fullPath).replaceAll('\\', '/'));
      }
    }
  }

  await walk(root);
  return files.sort();
}

async function fileHash(path) {
  const content = toLF(await readFile(path, 'utf8'));
  return createHash('sha256').update(content).digest('hex');
}

// Compares one source dir against one target dir; pushes human-readable
// drift descriptions (prefixed with `label`) onto `drift`.
async function diffDir(sourceDir, targetDir, label, drift) {
  if (!(await exists(sourceDir))) {
    drift.push(`missing source directory: ${relative(repoRoot, sourceDir)}`);
    return;
  }
  if (!(await exists(targetDir))) {
    drift.push(`missing asset directory: ${relative(repoRoot, targetDir)}`);
    return;
  }

  const sourceFiles = (await listFiles(sourceDir)).filter((f) => !isExcludedAssetFile(f));
  const targetFiles = (await listFiles(targetDir)).filter((f) => !isExcludedAssetFile(f));
  const allFiles = [...new Set([...sourceFiles, ...targetFiles])].sort();

  for (const file of allFiles) {
    const sourcePath = join(sourceDir, file);
    const targetPath = join(targetDir, file);

    if (!sourceFiles.includes(file)) {
      drift.push(`extra asset file: ${label}/${file}`);
    } else if (!targetFiles.includes(file)) {
      drift.push(`missing asset file: ${label}/${file}`);
    } else if ((await fileHash(sourcePath)) !== (await fileHash(targetPath))) {
      drift.push(`stale asset file: ${label}/${file}`);
    }
  }
}

// Mirrors sourceDir -> targetDir (deletes targetDir first, so removed
// source files don't linger as orphans in the target).
async function syncDir(sourceDir, targetDir) {
  if (!(await exists(sourceDir))) {
    throw new Error(`Source directory does not exist: ${sourceDir}`);
  }

  const resolvedTarget = assertInsideRepo(targetDir);
  if (await exists(resolvedTarget)) {
    await rm(resolvedTarget, { recursive: true, force: true });
  }

  for (const file of await listFiles(sourceDir)) {
    if (isExcludedAssetFile(file)) continue;
    const targetPath = assertInsideRepo(join(resolvedTarget, file));
    await mkdir(dirname(targetPath), { recursive: true });
    await writeFile(targetPath, toLF(await readFile(join(sourceDir, file), 'utf8')));
  }
}

async function checkAssets() {
  const drift = [];

  for (const dir of dirsToSync) {
    await diffDir(join(sourceRoot, dir), join(assetRoot, dir), dir, drift);
  }

  // Sub-skills (text content only; fonts/binaries intentionally excluded)
  for (const name of subSkills) {
    await diffDir(join(skillsSourceRoot, name), join(skillsAssetRoot, name), `skills/${name}`, drift);
  }

  // Orchestrator skill's own data/scripts copy under .claude/skills/ui-ux-pro-max/
  // (the copy Claude Code actually loads when this repo is a plugin).
  for (const dir of orchestratorDirsToSync) {
    await diffDir(
      join(sourceRoot, dir),
      join(orchestratorSkillTargetRoot, dir),
      `.claude/skills/ui-ux-pro-max/${dir}`,
      drift,
    );
  }

  if (drift.length > 0) {
    console.error('Assets are out of sync with src/ui-ux-pro-max:');
    for (const item of drift) {
      console.error(`  - ${item}`);
    }
    console.error('\nRun: npm run sync:assets');
    process.exit(1);
  }

  console.log('Assets are in sync.');
}

async function syncAssets() {
  assertInsideRepo(assetRoot);
  await mkdir(assetRoot, { recursive: true });

  for (const dir of dirsToSync) {
    await syncDir(join(sourceRoot, dir), join(assetRoot, dir));
  }

  // Sub-skills: copy text content only (fonts/binaries excluded) so all 7
  // skills ship in the package without bloating it with ~5.8MB of fonts.
  const skillsTarget = assertInsideRepo(skillsAssetRoot);
  if (await exists(skillsTarget)) {
    await rm(skillsTarget, { recursive: true, force: true });
  }
  for (const name of subSkills) {
    await syncDir(join(skillsSourceRoot, name), join(skillsTarget, name));
  }

  // Orchestrator skill's own data/scripts copy under .claude/skills/ui-ux-pro-max/.
  for (const dir of orchestratorDirsToSync) {
    await syncDir(join(sourceRoot, dir), join(orchestratorSkillTargetRoot, dir));
  }

  console.log('Synced CLI assets + .claude/skills/ui-ux-pro-max data/scripts from src/ui-ux-pro-max, and 6 sub-skills (normalized to LF).');
}

if (checkOnly) {
  await checkAssets();
} else {
  await syncAssets();
}
