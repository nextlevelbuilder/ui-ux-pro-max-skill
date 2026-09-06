import { existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import chalk from 'chalk';
import ora from 'ora';
import prompts from 'prompts';
import type { AIType } from '../types/index.js';
import { AI_TYPES } from '../types/index.js';
import { copyFolders, installFromZip, createTempDir, cleanup } from '../utils/extract.js';
import {
  generatePlatformFiles,
  generateAllPlatformFiles,
  planPlatformInstallActions,
  planAllPlatformInstallActions,
} from '../utils/template.js';
import { detectAIType, getAITypeDescription } from '../utils/detect.js';
import { logger } from '../utils/logger.js';
import {
  getLatestRelease,
  getAssetUrl,
  downloadRelease,
  getGitHubTokenGuidance,
  GitHubRateLimitError,
  GitHubDownloadError,
} from '../utils/github.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ASSETS_CANDIDATES = [
  // Bun bundle: dist/index.js
  join(__dirname, '..', 'assets'),
  // TypeScript fallback: dist/commands/init.js
  join(__dirname, '..', '..', 'assets'),
];
const ASSETS_DIR = ASSETS_CANDIDATES.find(path => existsSync(path)) ?? ASSETS_CANDIDATES[0];

interface InitOptions {
  ai?: AIType;
  force?: boolean;
  offline?: boolean;
  legacy?: boolean; // Use old ZIP-based install
  global?: boolean; // Install to home directory (global mode)
  dryRun?: boolean; // Preview install actions without writing files
  token?: string; // GitHub PAT for higher API rate limits
}

/**
 * Try to install from GitHub release (legacy method)
 * Returns the copied folders if successful, null if failed
 */
async function tryGitHubInstall(
  targetDir: string,
  aiType: AIType,
  spinner: ReturnType<typeof ora>,
  token?: string
): Promise<string[] | null> {
  let tempDir: string | null = null;

  try {
    spinner.text = 'Fetching latest release from GitHub...';
    const release = await getLatestRelease(token);
    const assetUrl = getAssetUrl(release);

    if (!assetUrl) {
      throw new GitHubDownloadError('No ZIP asset found in latest release');
    }

    spinner.text = `Downloading ${release.tag_name}...`;
    tempDir = await createTempDir();
    const zipPath = join(tempDir, 'release.zip');

    await downloadRelease(assetUrl, zipPath, token);

    spinner.text = 'Extracting and installing files...';
    const { copiedFolders, tempDir: extractedTempDir } = await installFromZip(
      zipPath,
      targetDir,
      aiType
    );

    // Cleanup temp directory
    await cleanup(extractedTempDir);

    return copiedFolders;
  } catch (error) {
    // Cleanup temp directory on error
    if (tempDir) {
      await cleanup(tempDir);
    }

    if (error instanceof GitHubRateLimitError) {
      spinner.warn(`GitHub rate limit reached, falling back to bundled assets.\n${getGitHubTokenGuidance()}`);
      return null;
    }

    if (error instanceof GitHubDownloadError) {
      spinner.warn('GitHub download failed, using template generation...');
      return null;
    }

    // Network errors or other fetch failures
    if (error instanceof TypeError && error.message.includes('fetch')) {
      spinner.warn('Network error, using template generation...');
      return null;
    }

    // Unknown errors - still fall back
    spinner.warn('Download failed, using template generation...');
    return null;
  }
}

/**
 * Install using template generation (new method)
 */
async function templateInstall(
  targetDir: string,
  aiType: AIType,
  spinner: ReturnType<typeof ora>,
  isGlobal = false,
  force = false
): Promise<string[]> {
  spinner.text = isGlobal
    ? 'Generating skill files globally...'
    : 'Generating skill files from templates...';

  if (aiType === 'all') {
    return generateAllPlatformFiles(targetDir, isGlobal, force);
  }

  return generatePlatformFiles(targetDir, aiType, isGlobal, force);
}

export async function initCommand(options: InitOptions): Promise<void> {
  logger.title('UI/UX Pro Max Installer');

  let aiType = options.ai;

  // Auto-detect or prompt for AI type
  if (!aiType) {
    const { detected, suggested } = detectAIType();

    if (detected.length > 0) {
      logger.info(`Detected: ${detected.map(t => chalk.cyan(t)).join(', ')}`);
    }

    const response = await prompts({
      type: 'select',
      name: 'aiType',
      message: 'Select AI assistant to install for:',
      choices: AI_TYPES.map(type => ({
        title: getAITypeDescription(type),
        value: type,
      })),
      initial: suggested ? AI_TYPES.indexOf(suggested) : 0,
    });

    if (!response.aiType) {
      logger.warn('Installation cancelled');
      return;
    }

    aiType = response.aiType as AIType;
  }

  const isGlobal = !!options.global;
  const modeLabel = isGlobal ? ' (global)' : '';
  logger.info(`Installing for: ${chalk.cyan(getAITypeDescription(aiType))}${modeLabel}`);

  // Dry run: print what the install would do, write nothing, exit 0
  if (options.dryRun) {
    const cwd = process.cwd();
    console.log();
    logger.info('Planned install actions (nothing will be written):');

    if (aiType === 'all') {
      const planned = await planAllPlatformInstallActions(cwd, isGlobal, options.force);
      planned.forEach((actions, type) => {
        console.log();
        console.log(chalk.bold(getAITypeDescription(type as AIType)));
        actions.forEach(action => console.log(`  ${chalk.cyan('·')} ${action}`));
      });
    } else {
      const actions = await planPlatformInstallActions(cwd, aiType, isGlobal, options.force);
      actions.forEach(action => console.log(`  ${chalk.cyan('·')} ${action}`));
    }

    console.log();
    logger.success('Dry run complete — no files were written.');
    return;
  }

  const spinner = ora('Installing files...').start();
  const cwd = process.cwd();
  let copiedFolders: string[] = [];
  let installMethod = 'template';

  try {
    // Use legacy ZIP-based install if --legacy flag is set
    if (options.legacy) {
      if (isGlobal) {
        spinner.warn('--global is not supported with --legacy mode, installing locally instead');
      }
      // Try GitHub download first (unless offline mode)
      if (!options.offline) {
        const githubResult = await tryGitHubInstall(cwd, aiType, spinner, options.token);
        if (githubResult) {
          copiedFolders = githubResult;
          installMethod = 'github';
        }
      }

      // Fall back to bundled assets if GitHub failed or offline mode
      if (installMethod !== 'github') {
        spinner.text = 'Installing from bundled assets...';
        copiedFolders = await copyFolders(ASSETS_DIR, cwd, aiType);
        installMethod = 'bundled';
      }
    } else {
      // Use new template-based generation (default)
      copiedFolders = await templateInstall(cwd, aiType, spinner, isGlobal, options.force);
      installMethod = 'template';
    }

    const methodMessage = {
      github: 'Installed from GitHub release!',
      bundled: 'Installed from bundled assets!',
      template: 'Generated from templates!',
    }[installMethod];

    spinner.succeed(methodMessage);

    // Summary
    console.log();
    logger.info('Installed folders:');
    copiedFolders.forEach(folder => {
      console.log(`  ${chalk.green('+')} ${folder}`);
    });

    console.log();
    logger.success('UI/UX Pro Max installed successfully!');

    // Next steps
    console.log();
    console.log(chalk.bold('Next steps:'));
    console.log(chalk.dim('  1. Restart your AI coding assistant'));
    console.log(chalk.dim('  2. Try: "Build a landing page for a SaaS product"'));
    console.log();
  } catch (error) {
    spinner.fail('Installation failed');
    if (error instanceof Error) {
      logger.error(error.message);
    }
    process.exit(1);
  }
}
