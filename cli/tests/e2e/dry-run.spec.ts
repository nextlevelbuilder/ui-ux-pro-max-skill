import { expect, test } from '@playwright/test';
import { mkdtemp, readdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  planAllPlatformInstallActions,
  planPlatformInstallActions,
} from '../../src/utils/template.js';

test('dry-run plan lists the install actions for one platform', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-'));

  const actions = await planPlatformInstallActions(scratch, 'claude');

  const joined = actions.join('\n');
  expect(joined).toContain(
    join(scratch, '.claude', 'skills', 'ui-ux-pro-max', 'SKILL.md')
  );
  expect(joined).toContain('Would copy data + scripts:');
  expect(joined).toContain('Would copy 6 sub-skills (');
});

test('dry-run plan writes nothing to the target directory', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-write-'));
  const before = await readdir(scratch);

  await planPlatformInstallActions(scratch, 'claude');
  await planAllPlatformInstallActions(scratch);

  expect(await readdir(scratch)).toEqual(before);
});

test('dry-run plan for all platforms covers every unique layout', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'uipro-dry-run-all-'));

  const planned = await planAllPlatformInstallActions(scratch);

  expect(planned.size).toBeGreaterThan(1);
  expect(planned.get('claude')!.length).toBeGreaterThan(0);
});
