import { access, mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from '@playwright/test';
import { generatePlatformFiles } from '../../src/utils/template.js';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const skillFiles = [
  '.claude/skills/banner-design/SKILL.md',
  'cli/assets/skills/banner-design/SKILL.md',
];
const unavailableDependencies = [
  'frontend-design',
  'ai-artist',
  'ai-multimodal',
  'chrome-devtools',
  'assets-organizing',
  'docs/brand-guidelines.md',
  'scripts/search.py',
  'inject-brand-context.cjs',
  'gemini_batch_process.py',
  'screenshot.js',
  'nano-banana-pro-examples.md',
];

function extractLocalReferences(content: string): string[] {
  return [...content.matchAll(/`((?:references|scripts)\/[\w./-]+)`/g)].map(match => match[1]);
}

async function expectSelfContained(skillFile: string): Promise<void> {
  const content = await readFile(skillFile, 'utf8');

  for (const dependency of unavailableDependencies) {
    expect(content, dependency).not.toContain(dependency);
  }

  const references = extractLocalReferences(content);
  expect(references).toContain('references/banner-sizes-and-styles.md');
  for (const reference of references) {
    await access(join(dirname(skillFile), reference));
  }
}

for (const relativeSkillFile of skillFiles) {
  test(`${relativeSkillFile} is self-contained`, async () => {
    await expectSelfContained(join(repoRoot, relativeSkillFile));
  });
}

test('Claude CLI installation preserves the banner path contract', async () => {
  const targetDir = await mkdtemp(join(tmpdir(), 'uipro-banner-'));
  try {
    await generatePlatformFiles(targetDir, 'claude');
    await expectSelfContained(join(targetDir, '.claude/skills/banner-design/SKILL.md'));
  } finally {
    await rm(targetDir, { recursive: true, force: true });
  }
});

test('the bundled banner skill matches the plugin source', async () => {
  const [source, bundled] = await Promise.all(
    skillFiles.map(skillFile => readFile(join(repoRoot, skillFile), 'utf8')),
  );
  expect(bundled).toBe(source);
});
