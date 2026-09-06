#!/usr/bin/env node

import { Command } from 'commander';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { initCommand } from './commands/init.js';
import { versionsCommand } from './commands/versions.js';
import { updateCommand } from './commands/update.js';
import { uninstallCommand } from './commands/uninstall.js';
import type { AIType } from './types/index.js';
import { AI_TYPES } from './types/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const pkg = JSON.parse(readFileSync(join(__dirname, '../package.json'), 'utf-8'));

const program = new Command();

program
  .name('uipro')
  .description('CLI to install UI/UX Pro Max skill for AI coding assistants')
  .version(pkg.version);

program
  .command('init')
  .description('Install UI/UX Pro Max skill to current project')
  .option('-a, --ai <type>', `AI assistant type (${AI_TYPES.join(', ')})`)
  .option('-f, --force', 'Overwrite existing files')
  .option('-o, --offline', 'Compatibility flag; template installs use bundled assets')
  .option('-g, --global', 'Install globally to home directory (~/) instead of current project')
  .option('-t, --token <token>', 'GitHub Personal Access Token for higher API rate limits')
  .option('--dry-run', 'Preview install actions without writing files')
  .action(async (options) => {
    if (options.ai && !AI_TYPES.includes(options.ai)) {
      console.error(`Invalid AI type: ${options.ai}`);
      console.error(`Valid types: ${AI_TYPES.join(', ')}`);
      process.exit(1);
    }
    await initCommand({
      ai: options.ai as AIType | undefined,
      force: options.force,
      offline: options.offline,
      global: options.global,
      dryRun: options.dryRun,
      token: options.token,
    });
  });

program
  .command('versions')
  .description('List available versions')
  .option('-t, --token <token>', 'GitHub Personal Access Token for higher API rate limits')
  .action(versionsCommand);

program
  .command('update')
  .description('Update UI/UX Pro Max to latest version')
  .option('-a, --ai <type>', `AI assistant type (${AI_TYPES.join(', ')})`)
  .option('-g, --global', 'Update global installation in home directory (~/)')
  .option('-t, --token <token>', 'GitHub Personal Access Token for higher API rate limits')
  .action(async (options) => {
    if (options.ai && !AI_TYPES.includes(options.ai)) {
      console.error(`Invalid AI type: ${options.ai}`);
      console.error(`Valid types: ${AI_TYPES.join(', ')}`);
      process.exit(1);
    }
    await updateCommand({
      ai: options.ai as AIType | undefined,
      global: options.global,
      token: options.token,
    });
  });

program
  .command('uninstall')
  .description('Remove UI/UX Pro Max skill from current project or globally')
  .option('-a, --ai <type>', `AI assistant type (${AI_TYPES.join(', ')})`)
  .option('-g, --global', 'Uninstall from home directory (~/) instead of current project')
  .action(async (options) => {
    if (options.ai && !AI_TYPES.includes(options.ai)) {
      console.error(`Invalid AI type: ${options.ai}`);
      console.error(`Valid types: ${AI_TYPES.join(', ')}`);
      process.exit(1);
    }
    await uninstallCommand({
      ai: options.ai as AIType | undefined,
      global: options.global,
    });
  });

program.parse();
