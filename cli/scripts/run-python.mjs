#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import { platform } from 'node:os';

const cmd = platform() === 'win32' ? 'python' : 'python3';
const args = process.argv.slice(2);

const result = spawnSync(cmd, args, {
  stdio: 'inherit',
  cwd: process.cwd()
});

if (result.error) {
  console.error(`Failed to start ${cmd}: ${result.error.message}`);
  process.exit(1);
}
process.exit(result.status ?? 0);
