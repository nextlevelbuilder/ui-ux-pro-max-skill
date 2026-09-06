import { rm, stat } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';
import chalk from 'chalk';
import ora from 'ora';
import prompts from 'prompts';
import type { AIType, ConcreteAIType } from '../types/index.js';
import { AI_TYPES, AI_FOLDERS } from '../types/index.js';
import { detectAIType, getAITypeDescription } from '../utils/detect.js';
import { listBundledSubSkills, loadPlatformConfig } from '../utils/template.js';
import { logger } from '../utils/logger.js';

interface UninstallOptions {
  ai?: AIType;
  global?: boolean;
}

/**
 * Remove skill directory for a given AI type
 */
async function removeSkillDir(baseDir: string, aiType: ConcreteAIType): Promise<string[]> {
  const removed: string[] = [];

  // The orchestrator plus the bundled sibling sub-skills installed by init.
  const skillNames = ['ui-ux-pro-max', ...(await listBundledSubSkills())];

  // Parent directories to clean. Derive the real install location from the
  // platform config's skillPath (same source the installer uses), so
  // non-`skills/` platforms are handled — copilot installs under
  // `.github/prompts/`, kiro under `.kiro/steering/`. Also clean the legacy
  // `<folder>/skills/` layout (incl. `.shared/`) so older installs are removed.
  const parents = new Set<string>();
  // Standalone skill files to remove (platforms with a dataPath keep the
  // rendered skill file apart from the data directory — e.g. copilot's
  // `.github/prompts/ui-ux-pro-max.prompt.md`).
  const skillFiles = new Set<string>();
  try {
    const { folderStructure } = await loadPlatformConfig(aiType);
    if (folderStructure.dataPath) {
      skillFiles.add(join(folderStructure.root, folderStructure.skillPath, folderStructure.filename));
      parents.add(join(folderStructure.root, dirname(folderStructure.dataPath)));
    } else {
      parents.add(join(folderStructure.root, dirname(folderStructure.skillPath)));
    }
  } catch {
    // No platform config — fall back to the legacy folders below.
  }
  for (const folder of AI_FOLDERS[aiType]) {
    parents.add(join(folder, 'skills'));
  }

  for (const skillFile of skillFiles) {
    const filePath = join(baseDir, skillFile);
    try {
      await stat(filePath);
      await rm(filePath, { force: true });
      removed.push(skillFile.replaceAll('\\', '/'));
    } catch (err: unknown) {
      // Skip non-existent files; re-throw permission or other errors
      if ((err as NodeJS.ErrnoException).code !== 'ENOENT') throw err;
    }
  }

  for (const parent of parents) {
    for (const name of skillNames) {
      const skillDir = join(baseDir, parent, name);
      try {
        await stat(skillDir);
        await rm(skillDir, { recursive: true, force: true });
        removed.push(`${parent.replaceAll('\\', '/')}/${name}`);
      } catch (err: unknown) {
        // Skip non-existent dirs; re-throw permission or other errors
        if ((err as NodeJS.ErrnoException).code !== 'ENOENT') throw err;
      }
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
