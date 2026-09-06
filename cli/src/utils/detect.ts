import { existsSync } from 'node:fs';
import { join } from 'node:path';
import type { AIType, ConcreteAIType } from '../types/index.js';

interface DetectionResult {
  detected: ConcreteAIType[];
  suggested: AIType | null;
}

export function detectAIType(cwd: string = process.cwd()): DetectionResult {
  const detected: ConcreteAIType[] = [];

  if (existsSync(join(cwd, '.claude')) || existsSync(join(cwd, '.claude-plugin'))) {
    detected.push('claude');
  }
  if (existsSync(join(cwd, '.cursor'))) {
    detected.push('cursor');
  }
  if (existsSync(join(cwd, '.windsurf'))) {
    detected.push('windsurf');
  }
  if (existsSync(join(cwd, '.agents'))) {
    detected.push('antigravity');
    detected.push('codex');
    detected.push('universal');
  } else if (existsSync(join(cwd, '.agent'))) {
    detected.push('antigravity');
  }
  if (existsSync(join(cwd, '.github'))) {
    detected.push('copilot');
  }
  if (existsSync(join(cwd, '.kiro'))) {
    detected.push('kiro');
  }
  if (existsSync(join(cwd, '.codex')) && !detected.includes('codex')) {
    detected.push('codex');
  }
  if (existsSync(join(cwd, '.roo'))) {
    detected.push('roocode');
  }
  if (existsSync(join(cwd, '.qoder'))) {
    detected.push('qoder');
  }
  if (existsSync(join(cwd, '.gemini'))) {
    detected.push('gemini');
  }
  if (existsSync(join(cwd, '.trae'))) {
    detected.push('trae');
  }
  if (existsSync(join(cwd, '.opencode'))) {
    detected.push('opencode');
  }
  if (existsSync(join(cwd, '.continue'))) {
    detected.push('continue');
  }
  if (existsSync(join(cwd, '.codebuddy'))) {
    detected.push('codebuddy');
  }
  if (existsSync(join(cwd, '.factory'))) {
    detected.push('droid');
  }
  if (existsSync(join(cwd, '.kilocode'))) {
    detected.push('kilocode');
  }
  if (existsSync(join(cwd, '.warp'))) {
    detected.push('warp');
  }
  if (existsSync(join(cwd, '.augment'))) {
    detected.push('augment');
  }
  if (existsSync(join(cwd, '.codewhale'))) {
    detected.push('codewhale');
  }

  // Suggest based on what's detected
  let suggested: AIType | null = null;
  if (detected.length === 1) {
    suggested = detected[0];
  } else if (
    (detected.length === 2 || detected.length === 3) &&
    detected.includes('antigravity') &&
    detected.includes('codex')
  ) {
    // Platforms share `.agents`; avoid suggesting an install for every AI.
    suggested = 'codex';
  } else if (detected.length > 1) {
    suggested = 'all';
  }

  return { detected, suggested };
}

export function getAITypeDescription(aiType: AIType): string {
  switch (aiType) {
    case 'claude':
      return 'Claude Code (.claude/skills/)';
    case 'cursor':
      return 'Cursor (.cursor/skills/)';
    case 'windsurf':
      return 'Windsurf (.windsurf/skills/)';
    case 'antigravity':
      return 'Antigravity (.agents/skills/)';
    case 'copilot':
      return 'GitHub Copilot (.github/prompts/)';
    case 'kiro':
      return 'Kiro (.kiro/steering/)';
    case 'codex':
      return 'Codex (.agents/skills/)';
    case 'roocode':
      return 'RooCode (.roo/skills/)';
    case 'qoder':
      return 'Qoder (.qoder/skills/)';
    case 'gemini':
      return 'Gemini CLI (.gemini/skills/)';
    case 'trae':
      return 'Trae (.trae/skills/)';
    case 'opencode':
      return 'OpenCode (.opencode/skills/)';
    case 'continue':
      return 'Continue (.continue/skills/)';
    case 'codebuddy':
      return 'CodeBuddy (.codebuddy/skills/)';
    case 'droid':
      return 'Droid (Factory) (.factory/skills/)';
    case 'kilocode':
      return 'KiloCode (.kilocode/skills/)';
    case 'warp':
      return 'Warp (.warp/skills/)';
    case 'augment':
      return 'Augment (.augment/skills/)';
    case 'codewhale':
      return 'CodeWhale (.codewhale/skills/)';
    case 'universal':
      return 'Universal (.agents/skills/)';
    case 'all':
      return 'All AI assistants';
  }
}
