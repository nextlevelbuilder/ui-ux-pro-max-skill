import { existsSync } from 'node:fs';
import { join } from 'node:path';
import type { AIType } from '../types/index.js';

interface DetectionResult {
  detected: AIType[];
  suggested: AIType | null;
}

export function detectAIType(cwd: string = process.cwd()): DetectionResult {
  const detected: AIType[] = [];

  if (existsSync(join(cwd, '.claude'))) {
    detected.push('claude');
  }
  if (existsSync(join(cwd, '.cursor'))) {
    detected.push('cursor');
  }
  if (existsSync(join(cwd, '.windsurf'))) {
    detected.push('windsurf');
  }
  if (existsSync(join(cwd, '.agent'))) {
    detected.push('antigravity');
  }
  if (existsSync(join(cwd, '.github'))) {
    detected.push('copilot');
  }

  // Suggest based on what's detected
  let suggested: AIType | null = null;
  if (detected.length === 1) {
    suggested = detected[0];
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
      return 'Cursor (.cursor/commands/ + .shared/)';
    case 'windsurf':
      return 'Windsurf (.windsurf/workflows/ + .shared/)';
    case 'antigravity':
      return 'Antigravity (.agent/workflows/ + .shared/)';
    case 'copilot':
      return 'GitHub Copilot (.github/ + .shared/)';
    case 'all':
      return 'All AI assistants';
  }
}
