import chalk from 'chalk';
import ora from 'ora';
import { getLatestRelease } from '../utils/github.js';
import { logger } from '../utils/logger.js';
import { initCommand } from './init.js';
import type { AIType } from '../types/index.js';

interface UpdateOptions {
  ai?: AIType;
}

export async function updateCommand(options: UpdateOptions): Promise<void> {
  logger.title('UI/UX Pro Max Updater');

  const spinner = ora('Checking for updates...').start();

  try {
    const release = await getLatestRelease();
    spinner.succeed(`Latest version: ${chalk.cyan(release.tag_name)}`);

    console.log();
    logger.info('Installing latest release...');
    console.log();

    await initCommand({
      ai: options.ai,
      force: true,
      release,
    });
  } catch (error) {
    spinner.fail('Update check failed');
    if (error instanceof Error) {
      logger.error(error.message);
    }
    process.exit(1);
  }
}
