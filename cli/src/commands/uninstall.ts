import { rm, stat } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';
import chalk from 'chalk';
import ora from 'ora';
import prompts from 'prompts';
import type { AIType } from '../types/index.js';
import { AI_TYPES, AI_FOLDERS } from '../types/index.js';
import { detectAIType, getAITypeDescription } from '../utils/detect.js';
import { logger } from '../utils/logger.js';

interface UninstallOptions {
  ai?: AIType;
  global?: boolean;
}

/**
 * Remove skill directory for a given AI type
 */
async function removeSkillDir(baseDir: string, aiType: Exclude<AIType, 'all'>): Promise<string[]> {
  const folders = AI_FOLDERS[aiType];
  const removed: string[] = [];

  for (const folder of folders) {
    const skillDir = join(baseDir, folder, 'skills', 'ui-ux-pro-max');
    try {
      await stat(skillDir);
      await rm(skillDir, { recursive: true, force: true });
      removed.push(`${folder}/skills/ui-ux-pro-max`);
    } catch (err: unknown) {
      // Skip non-existent dirs; re-throw permission or other errors
      if ((err as NodeJS.ErrnoException).code !== 'ENOENT') throw err;
    }
  }

  return removed;
}

export async function uninstallCommand(options: UninstallOptions): Promise<void> {
  logger.title('UI/UX Pro Max Uninstaller');

  const isGlobal = !!options.global;
  const baseDir = isGlobal ? homedir() : process.cwd();
  const locationLabel = isGlobal ? '~/ (global)' : process.cwd();

  let aiType = options.ai;
  const { detected: initialDetected } = detectAIType(baseDir);

  // Auto-detect or prompt for AI type
  if (!aiType) {
    const detected = initialDetected;

    if (detected.length === 0) {
      logger.warn('No installed AI skill directories detected.');
      return;
    }

    logger.info(`Detected installations: ${detected.map(t => chalk.cyan(t)).join(', ')}`);

    const choices = [
      ...detected.map(type => ({
        title: getAITypeDescription(type),
        value: type,
      })),
      { title: 'All detected', value: 'all' as AIType },
    ];

    const response = await prompts({
      type: 'select',
      name: 'aiType',
      message: 'Select which AI skill to uninstall:',
      choices,
    });

    if (!response.aiType) {
      logger.warn('Uninstall cancelled');
      return;
    }

    aiType = response.aiType as AIType;
  }

  // Confirm before removing
  const { confirmed } = await prompts({
    type: 'confirm',
    name: 'confirmed',
    message: `Remove UI/UX Pro Max skill for ${chalk.cyan(getAITypeDescription(aiType))} from ${locationLabel}?`,
    initial: false,
  });

  if (!confirmed) {
    logger.warn('Uninstall cancelled');
    return;
  }

  const spinner = ora('Removing skill files...').start();

  try {
    const allRemoved: string[] = [];

    if (aiType === 'all') {
      // Remove for all detected platforms
      for (const type of initialDetected) {
        if (type === 'all') continue;
        const removed = await removeSkillDir(baseDir, type);
        allRemoved.push(...removed);
      }
    } else {
      const removed = await removeSkillDir(baseDir, aiType);
      allRemoved.push(...removed);
    }

    if (allRemoved.length === 0) {
      spinner.warn('No skill files found to remove');
      return;
    }

    spinner.succeed('Skill files removed!');

    console.log();
    logger.info('Removed:');
    allRemoved.forEach(folder => {
      console.log(`  ${chalk.red('-')} ${folder}`);
    });

    console.log();
    logger.success('UI/UX Pro Max uninstalled successfully!');
    console.log();
  } catch (error) {
    spinner.fail('Uninstall failed');
    if (error instanceof Error) {
      logger.error(error.message);
    }
    process.exit(1);
  }
}
