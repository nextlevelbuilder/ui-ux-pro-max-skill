import { access, mkdtemp, mkdir, readdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import chalk from 'chalk';
import ora from 'ora';
import prompts from 'prompts';
import type { AIType, Release } from '../types/index.js';
import { AI_TYPES } from '../types/index.js';
import { cleanup, copyFolders, extractZip } from '../utils/extract.js';
import { detectAIType, getAITypeDescription } from '../utils/detect.js';
import { downloadRelease, getAssetUrl, getReleaseByTag } from '../utils/github.js';
import { logger } from '../utils/logger.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
// From dist/index.js -> ../assets (one level up to cli/, then assets/)
const ASSETS_DIR = join(__dirname, '..', 'assets');

interface InitOptions {
  ai?: AIType;
  force?: boolean;
  version?: string;
  release?: Release;
}

async function pathExists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

async function resolveExtractRoot(extractDir: string): Promise<string> {
  const entries = await readdir(extractDir, { withFileTypes: true });
  const dirs = entries.filter(entry => entry.isDirectory());
  const files = entries.filter(entry => !entry.isDirectory());

  if (dirs.length === 1 && files.length === 0) {
    return join(extractDir, dirs[0].name);
  }

  return extractDir;
}

async function findAssetsDir(extractDir: string): Promise<string> {
  const rootDir = await resolveExtractRoot(extractDir);
  const candidates = [
    join(rootDir, 'cli', 'assets'),
    join(rootDir, 'assets'),
  ];

  for (const candidate of candidates) {
    if (await pathExists(candidate)) {
      return candidate;
    }
  }

  throw new Error('Release assets not found. Expected "cli/assets" or "assets" in the release zip.');
}

async function installFromRelease(release: Release, aiType: AIType): Promise<string[]> {
  const assetUrl = getAssetUrl(release);
  if (!assetUrl) {
    throw new Error(`No .zip asset found for release ${release.tag_name}`);
  }

  const tempDir = await mkdtemp(join(tmpdir(), 'uipro-'));
  const safeTag = release.tag_name.replace(/[^a-zA-Z0-9._-]/g, '-');
  const zipPath = join(tempDir, `${safeTag}.zip`);
  const extractDir = join(tempDir, 'extract');

  try {
    await mkdir(extractDir, { recursive: true });
    await downloadRelease(assetUrl, zipPath);
    await extractZip(zipPath, extractDir);
    const assetsDir = await findAssetsDir(extractDir);
    return copyFolders(assetsDir, process.cwd(), aiType);
  } finally {
    await cleanup(tempDir);
  }
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

  logger.info(`Installing for: ${chalk.cyan(getAITypeDescription(aiType))}`);

  const spinner = ora('Installing files...').start();

  try {
    const cwd = process.cwd();
    let copiedFolders: string[];

    if (options.release || options.version) {
      const release = options.release ?? await getReleaseByTag(options.version ?? '');
      spinner.text = `Installing ${release.tag_name}...`;
      copiedFolders = await installFromRelease(release, aiType);
    } else {
      copiedFolders = await copyFolders(ASSETS_DIR, cwd, aiType);
    }

    spinner.succeed('Installation complete!');

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
