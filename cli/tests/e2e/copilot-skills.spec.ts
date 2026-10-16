import { expect, test } from '@playwright/test';
import { existsSync } from 'node:fs';
import { mkdir, mkdtemp, readdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { removeSkillDir } from '../../src/commands/uninstall.js';
import { detectAIType } from '../../src/utils/detect.js';
import {
  generatePlatformFiles,
  listBundledSubSkills,
  loadPlatformConfig,
  planPlatformInstallActions,
  renderSkillFile,
} from '../../src/utils/template.js';

// GitHub Copilot loads project skills from .github/skills/<name>/SKILL.md and
// personal skills from ~/.copilot/skills/<name>/SKILL.md:
// https://docs.github.com/en/copilot/concepts/agents/about-agent-skills

function scratchDir(name: string): Promise<string> {
  return mkdtemp(join(tmpdir(), `uipro-copilot-${name}-`));
}

/** What `uipro init --ai copilot` installed before it targeted Agent Skills. */
async function writeLegacyPromptInstall(dir: string): Promise<void> {
  const prompts = join(dir, '.github', 'prompts');
  await mkdir(join(prompts, 'ui-ux-pro-max', 'scripts'), { recursive: true });
  await writeFile(join(prompts, 'ui-ux-pro-max.prompt.md'), '---\nmode: agent\n---\n');
  await writeFile(join(prompts, 'ui-ux-pro-max', 'scripts', 'search.py'), '');
  await mkdir(join(prompts, 'design'));
  await writeFile(join(prompts, 'design', 'SKILL.md'), '---\nname: design\n---\n');
}

test('copilot SKILL.md has the name and description frontmatter Agent Skills require', async () => {
  const config = await loadPlatformConfig('copilot');
  const content = await renderSkillFile(config);
  const frontmatter = content.match(/^---\n([\s\S]*?)\n---\n/)?.[1] ?? '';

  expect(frontmatter).toMatch(/^name: ui-ux-pro-max$/m);
  expect(frontmatter).toMatch(/^description: "UI\/UX design intelligence/m);
  expect(frontmatter).not.toMatch(/^mode:/m);
  expect(config.frontmatter!.description.length).toBeLessThanOrEqual(1024);
});

test('copilot dry-run plans the .github/skills layout and writes nothing', async () => {
  const scratch = await scratchDir('dry-run');

  const actions = await planPlatformInstallActions(scratch, 'copilot');

  const skillDir = join(scratch, '.github', 'skills', 'ui-ux-pro-max');
  expect(actions[0]).toBe(`Would write: ${join(skillDir, 'SKILL.md')}`);
  expect(actions[1]).toBe(`Would copy data + scripts: ${skillDir}`);
  expect(actions[2].startsWith(`Would copy ${(await listBundledSubSkills()).length} sub-skills (`)).toBe(true);
  expect(actions[2].endsWith(`: ${join(scratch, '.github', 'skills')}`)).toBe(true);
  expect(actions).toHaveLength(3);
  expect(await readdir(scratch)).toEqual([]);
});

/** Run fn with os.homedir() pointing at home (HOME on POSIX, USERPROFILE on Windows). */
async function withHome<T>(home: string, fn: () => Promise<T>): Promise<T> {
  const saved = { HOME: process.env.HOME, USERPROFILE: process.env.USERPROFILE };
  process.env.HOME = home;
  process.env.USERPROFILE = home;
  try {
    return await fn();
  } finally {
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
}

test('copilot --global plans the personal ~/.copilot/skills folder', async () => {
  const home = await scratchDir('home');

  const actions = await withHome(home, async () =>
    planPlatformInstallActions(await scratchDir('project'), 'copilot', true)
  );

  expect(actions[0]).toBe(
    `Would write: ${join(home, '.copilot', 'skills', 'ui-ux-pro-max', 'SKILL.md')}`
  );
});

test('copilot --global installs to and uninstalls from ~/.copilot/skills', async () => {
  const home = await scratchDir('global');

  await withHome(home, async () => generatePlatformFiles(await scratchDir('project'), 'copilot', true));

  const skillFile = join(home, '.copilot', 'skills', 'ui-ux-pro-max', 'SKILL.md');
  expect(existsSync(skillFile)).toBe(true);
  expect(existsSync(join(home, '.github'))).toBe(false);

  const removed = await removeSkillDir(home, 'copilot', true);

  expect(removed).toContain('.copilot/skills/ui-ux-pro-max');
  expect(await readdir(join(home, '.copilot', 'skills'))).toEqual([]);
});

test('copilot installs the skill, its data and the sub-skills under .github/skills', async () => {
  const scratch = await scratchDir('install');

  await generatePlatformFiles(scratch, 'copilot');

  const skills = join(scratch, '.github', 'skills');
  expect(existsSync(join(skills, 'ui-ux-pro-max', 'SKILL.md'))).toBe(true);
  expect(existsSync(join(skills, 'ui-ux-pro-max', 'scripts', 'search.py'))).toBe(true);
  expect(existsSync(join(skills, 'ui-ux-pro-max', 'data'))).toBe(true);
  for (const name of await listBundledSubSkills()) {
    expect(existsSync(join(skills, name, 'SKILL.md')), name).toBe(true);
  }
  expect(existsSync(join(scratch, '.github', 'prompts'))).toBe(false);
});

test('copilot replaces an earlier .github/prompts install and keeps the user\'s prompts', async () => {
  const scratch = await scratchDir('migrate');
  await writeLegacyPromptInstall(scratch);
  const prompts = join(scratch, '.github', 'prompts');
  await writeFile(join(prompts, 'release-notes.prompt.md'), '# mine\n');
  // A user's own folder that shares a sub-skill name but holds no SKILL.md.
  await mkdir(join(prompts, 'slides'));
  await writeFile(join(prompts, 'slides', 'notes.md'), '# mine\n');

  const plan = await planPlatformInstallActions(scratch, 'copilot');
  expect(plan.slice(3)).toEqual([
    `Would remove legacy install: ${join(prompts, 'ui-ux-pro-max.prompt.md')}`,
    `Would remove legacy install: ${join(prompts, 'ui-ux-pro-max')}`,
    `Would remove legacy install: ${join(prompts, 'design')}`,
  ]);

  await generatePlatformFiles(scratch, 'copilot');

  expect(existsSync(join(scratch, '.github', 'skills', 'ui-ux-pro-max', 'SKILL.md'))).toBe(true);
  expect(existsSync(join(prompts, 'ui-ux-pro-max.prompt.md'))).toBe(false);
  expect(existsSync(join(prompts, 'ui-ux-pro-max'))).toBe(false);
  expect(existsSync(join(prompts, 'design'))).toBe(false);
  expect(existsSync(join(prompts, 'release-notes.prompt.md'))).toBe(true);
  expect(existsSync(join(prompts, 'slides', 'notes.md'))).toBe(true);
});

test('a .github folder without Copilot files does not detect copilot', async () => {
  const scratch = await scratchDir('detect-workflows');
  await mkdir(join(scratch, '.github', 'workflows'), { recursive: true });
  await writeFile(join(scratch, '.github', 'dependabot.yml'), 'version: 2\n');

  expect(detectAIType(scratch).detected).not.toContain('copilot');
});

for (const marker of [
  '.github/copilot-instructions.md',
  '.github/instructions',
  '.github/prompts',
  '.github/agents',
  '.github/skills',
  '.github/hooks',
  '.copilot/skills',
]) {
  test(`${marker} detects copilot`, async () => {
    const scratch = await scratchDir('detect');
    const path = join(scratch, marker);
    if (marker.endsWith('.md')) {
      await mkdir(dirname(path), { recursive: true });
      await writeFile(path, '');
    } else {
      await mkdir(path, { recursive: true });
    }

    expect(detectAIType(scratch)).toEqual({ detected: ['copilot'], suggested: 'copilot' });
  });
}

test('uninstall removes the .github/skills install and an earlier .github/prompts one', async () => {
  const scratch = await scratchDir('uninstall');
  await generatePlatformFiles(scratch, 'copilot');
  await writeLegacyPromptInstall(scratch);
  await mkdir(join(scratch, '.github', 'workflows'));

  const removed = await removeSkillDir(scratch, 'copilot');

  expect(removed).toEqual(expect.arrayContaining([
    '.github/skills/ui-ux-pro-max',
    '.github/skills/design',
    '.github/prompts/ui-ux-pro-max.prompt.md',
    '.github/prompts/ui-ux-pro-max',
    '.github/prompts/design',
  ]));
  expect(await readdir(join(scratch, '.github', 'skills'))).toEqual([]);
  expect(await readdir(join(scratch, '.github', 'prompts'))).toEqual([]);
  expect(existsSync(join(scratch, '.github', 'workflows'))).toBe(true);
});
