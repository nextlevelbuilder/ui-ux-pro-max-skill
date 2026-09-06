import chalk from 'chalk';
import ora from 'ora';
import { fetchReleases } from '../utils/github.js';
import { logger } from '../utils/logger.js';

interface VersionsOptions {
  token?: string;
}

export async function versionsCommand(options: VersionsOptions = {}): Promise<void> {
  const spinner = ora('Fetching available versions...').start();

  try {
    const releases = await fetchReleases(options.token);

    if (releases.length === 0) {
      spinner.warn('No releases found');
      return;
    }

    spinner.succeed(`Found ${releases.length} version(s)\n`);

    console.log(chalk.bold('Available versions:\n'));

    releases.forEach((release, index) => {
      const isLatest = index === 0;
      const tag = release.tag_name;
      const date = new Date(release.published_at).toLocaleDateString();

      if (isLatest) {
        console.log(`  ${chalk.green('*')} ${chalk.bold(tag)} ${chalk.dim(`(${date})`)} ${chalk.green('[latest]')}`);
      } else {
        console.log(`    ${tag} ${chalk.dim(`(${date})`)}`);
      }
    });

    console.log();
    logger.dim('Update the CLI package first, then run: uipro init --ai <platform>');
  } catch (error) {
    spinner.fail('Failed to fetch versions');
    if (error instanceof Error) {
      logger.error(error.message);
    }
    process.exit(1);
  }
}
