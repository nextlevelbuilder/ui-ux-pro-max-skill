import { expect, test } from '@playwright/test';
import { mkdtemp, readdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  listBundledSubSkills,
  planAllPlatformInstallActions,
  planPlatformInstallActions,
} from '../../src/utils/template.js';

// The bundled set grows when a sub-skill is added under .claude/skills and listed in
// cli/scripts/sync-assets.mjs, so the expected count is derived, never hard-coded.
async function subSkillPrefix(): Promise<string> {
  return `Would copy ${(await listBundledSubSkills()).length} sub-skills (`;
}

test('dry-run plan lists the install actions for one platform', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-'));

  const actions = await planPlatformInstallActions(scratch, 'claude');

  const joined = actions.join('\n');
  expect(joined).toContain(
    join(scratch, '.claude', 'skills', 'ui-ux-pro-max', 'SKILL.md')
  );
  expect(joined).toContain('Would copy data + scripts:');
  expect(joined).toContain(await subSkillPrefix());
});

test('dry-run plan writes nothing to the target directory', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-write-'));
  const before = await readdir(scratch);

  await planPlatformInstallActions(scratch, 'claude');
  await planAllPlatformInstallActions(scratch);

  expect(await readdir(scratch)).toEqual(before);
});

test('dry-run plan supports the zcode platform layout', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-zcode-'));

  const actions = await planPlatformInstallActions(scratch, 'zcode');

  const joined = actions.join('\n');
  expect(joined).toContain(
    join(scratch, '.zcode', 'skills', 'ui-ux-pro-max', 'SKILL.md')
  );
  expect(joined).toContain('Would copy data + scripts:');
  expect(joined).toContain(await subSkillPrefix());
});

test('dry-run plan supports the kimi platform layout', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-kimi-'));

  const actions = await planPlatformInstallActions(scratch, 'kimi');

  const joined = actions.join('\n');
  expect(joined).toContain(
    join(scratch, '.kimi-code', 'skills', 'ui-ux-pro-max', 'SKILL.md')
  );
  expect(joined).toContain('Would copy data + scripts:');
  expect(joined).toContain('Would copy 6 sub-skills (');
});

test('dry-run plan keeps amazonq data and sub-skills out of the rules folder', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-amazonq-'));

  const actions = await planPlatformInstallActions(scratch, 'amazonq');

  expect(actions[0]).toBe(
    `Would write: ${join(scratch, '.amazonq', 'rules', 'ui-ux-pro-max.md')}`
  );
  expect(actions[1]).toBe(
    `Would copy data + scripts: ${join(scratch, '.amazonq', 'skills', 'ui-ux-pro-max')}`
  );
  expect(actions[2].startsWith(await subSkillPrefix())).toBe(true);
  expect(actions[2].endsWith(`: ${join(scratch, '.amazonq', 'skills')}`)).toBe(true);
});

test('dry-run plan supports the openclaw platform layout', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-openclaw-'));

  const actions = await planPlatformInstallActions(scratch, 'openclaw');

  const joined = actions.join('\n');
  expect(joined).toContain(
    join(scratch, '.agents', 'skills', 'ui-ux-pro-max', 'SKILL.md')
  );
  expect(joined).toContain('Would copy data + scripts:');
  expect(joined).toContain(await subSkillPrefix());
});

test('dry-run plan for all platforms covers every unique layout', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-all-'));

  const planned = await planAllPlatformInstallActions(scratch);

  expect(planned.size).toBeGreaterThan(1);
  expect(planned.get('claude')!.length).toBeGreaterThan(0);
});

test('bundled sub-skills include the Visual Design Pro Max skills', async () => {
  const bundled = await listBundledSubSkills();
  for (const name of ['visual-direction', 'reference-analysis', 'visual-audit']) {
    expect(bundled).toContain(name);
  }
});
