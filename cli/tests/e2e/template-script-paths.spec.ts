import { expect, test } from '@playwright/test';
import { loadPlatformConfig, renderSkillFile } from '../../src/utils/template.js';

const cases = [
  ['claude', '.claude/skills/ui-ux-pro-max/scripts/search.py'],
  ['codex', '.agents/skills/ui-ux-pro-max/scripts/search.py'],
  ['kiro', '.kiro/steering/ui-ux-pro-max/scripts/search.py'],
  ['droid', '.factory/skills/ui-ux-pro-max/scripts/search.py'],
  ['zcode', '.zcode/skills/ui-ux-pro-max/scripts/search.py'],
  ['kimi', '.kimi-code/skills/ui-ux-pro-max/scripts/search.py'],
  ['amazonq', '.amazonq/skills/ui-ux-pro-max/scripts/search.py'],
  ['openclaw', '.agents/skills/ui-ux-pro-max/scripts/search.py'],
] as const;
const SEARCH_COMMAND_COUNT = 17;

function extractSearchScriptPaths(content: string): string[] {
  return [...content.matchAll(/^python3\s+(\S*search\.py)\b/gm)].map(match => match[1]);
}

for (const [platform, localPath] of cases) {
  test(`${platform} renders project-root and global script paths`, async () => {
    const config = await loadPlatformConfig(platform);

    const localContent = await renderSkillFile(config);
    const localPaths = extractSearchScriptPaths(localContent);
    expect(localPaths).toHaveLength(SEARCH_COMMAND_COUNT);
    expect(new Set(localPaths)).toEqual(new Set([localPath]));
    expect(localContent).not.toContain('{{SCRIPT_PATH}}');

    const globalContent = await renderSkillFile(config, true);
    const globalPaths = extractSearchScriptPaths(globalContent);
    expect(globalPaths).toHaveLength(SEARCH_COMMAND_COUNT);
    expect(new Set(globalPaths)).toEqual(new Set([`~/${localPath}`]));
    expect(globalContent).not.toContain('{{SCRIPT_PATH}}');
  });
}

test('autoclaw renders workspace skills locally and ~/.openclaw-autoclaw/skills globally', async () => {
  const config = await loadPlatformConfig('autoclaw');

  const localPaths = extractSearchScriptPaths(await renderSkillFile(config));
  expect(localPaths).toHaveLength(SEARCH_COMMAND_COUNT);
  expect(new Set(localPaths)).toEqual(new Set(['skills/ui-ux-pro-max/scripts/search.py']));
  expect(await renderSkillFile(config)).not.toContain('{{SCRIPT_PATH}}');

  const globalPaths = extractSearchScriptPaths(await renderSkillFile(config, true));
  expect(globalPaths).toHaveLength(SEARCH_COMMAND_COUNT);
  expect(new Set(globalPaths)).toEqual(
    new Set(['~/.openclaw-autoclaw/skills/ui-ux-pro-max/scripts/search.py'])
  );
  expect(await renderSkillFile(config, true)).not.toContain('{{SCRIPT_PATH}}');
});

test('copilot renders .github/skills paths locally and ~/.copilot/skills globally', async () => {
  const config = await loadPlatformConfig('copilot');

  const localPaths = extractSearchScriptPaths(await renderSkillFile(config));
  expect(localPaths).toHaveLength(SEARCH_COMMAND_COUNT);
  expect(new Set(localPaths)).toEqual(new Set(['.github/skills/ui-ux-pro-max/scripts/search.py']));

  const globalPaths = extractSearchScriptPaths(await renderSkillFile(config, true));
  expect(globalPaths).toHaveLength(SEARCH_COMMAND_COUNT);
  expect(new Set(globalPaths)).toEqual(new Set(['~/.copilot/skills/ui-ux-pro-max/scripts/search.py']));
});
