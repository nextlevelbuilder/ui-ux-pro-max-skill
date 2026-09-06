import { expect, test } from '@playwright/test';
import { loadAllPlatformConfigs, renderSkillFile } from '../../src/utils/template.js';

const DESCRIPTION =
  'UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces, including pages, components, design systems, accessibility, interaction, responsive layout, typography, color, charts, and stack-specific UI implementation. Searchable local data: 79 searchable styles (50 active), 192 product palettes and reasoning profiles, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types, and 22 stacks.';

test('all platform metadata uses one accurate activation description', async () => {
  const configs = await loadAllPlatformConfigs();
  expect(configs.size).toBe(20);
  for (const [platform, config] of configs) {
    expect(config.description, platform).toBe(DESCRIPTION);
    if (config.frontmatter?.description) {
      expect(config.frontmatter.description, platform).toBe(DESCRIPTION);
    }
  }
});

test('rendered guides expose the deterministic query contract', async () => {
  const configs = await loadAllPlatformConfigs();
  for (const [platform, config] of configs) {
    const content = await renderSkillFile(config);
    expect(content, platform).toContain('## Query Contract');
    expect(content, platform).toContain('one dominant intent');
    expect(content, platform).toContain('2–5 meaningful terms');
    expect(content, platform).toContain('Retry once');
    expect(content, platform).toContain('Do not persist unverified output');
    expect(content, platform).toContain('explicit accessibility outcome terms');
    expect(content, platform).toContain('semantic UX outcome first, then the detected stack');
    expect(content, platform).toContain('orphan heading line balance' + '" --domain ux');
    expect(content, platform).toContain('badge chip label wraps' + '" --domain ux');
    expect(content, platform).toContain('live badge count screen reader' + '" --domain ux');
    expect(content, platform).toContain('rapid chip animation interrupted' + '" --domain ux');
    expect(content, platform).toContain('chip badge overflow nowrap' + '" --stack html-tailwind');
    expect(content, platform).toContain('React/Next.js performance');
    expect(content, platform).toContain('Native/app interface guidance');
    expect(content, platform).not.toContain('React Native perf | `react`');
    expect(content, platform).not.toContain('Searches domains in parallel');
    expect(content, platform).not.toContain('Always start with `--design-system`');
  }
});

test('rendered examples encode mode, retry, and persistence boundaries', async () => {
  const config = await loadAllPlatformConfigs().then(configs => configs.get('codex'));
  expect(config).toBeDefined();
  const content = await renderSkillFile(config!);
  expect(content).toContain('keyboard focus modal' + '" --domain ux');
  expect(content).toContain('rerender memo list' + '" --domain react');
  expect(content).toContain('virtualized list' + '" --stack react-native');
  expect(content).toContain('--output-dir "<project-root>"');
  expect(content).toContain('Read an existing `MASTER.md` before deciding whether `--force` is justified');
});
