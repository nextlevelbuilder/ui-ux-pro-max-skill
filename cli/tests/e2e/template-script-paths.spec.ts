import { expect, test } from '@playwright/test';
import { loadPlatformConfig, renderSkillFile } from '../../src/utils/template.js';

const cases = [
  ['claude', '.claude/skills/ui-ux-pro-max/scripts/search.py'],
  ['codex', '.agents/skills/ui-ux-pro-max/scripts/search.py'],
  ['copilot', '.github/prompts/ui-ux-pro-max/scripts/search.py'],
  ['kiro', '.kiro/steering/ui-ux-pro-max/scripts/search.py'],
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
