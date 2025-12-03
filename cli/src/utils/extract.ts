import { mkdir, rm, access, cp } from 'node:fs/promises';
import { join, basename } from 'node:path';
import { exec } from 'node:child_process';
import { promisify } from 'node:util';
import type { AIType } from '../types/index.js';
import { AI_FOLDERS } from '../types/index.js';

const execAsync = promisify(exec);

const EXCLUDED_FILES = ['settings.local.json'];

export async function extractZip(zipPath: string, destDir: string): Promise<void> {
  try {
    const isWindows = process.platform === 'win32';
    if (isWindows) {
      await execAsync(`powershell -Command "Expand-Archive -Path '${zipPath}' -DestinationPath '${destDir}' -Force"`);
    } else {
      await execAsync(`unzip -o "${zipPath}" -d "${destDir}"`);
    }
  } catch (error) {
    throw new Error(`Failed to extract zip: ${error}`);
  }
}

async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

export async function copyFolders(
  sourceDir: string,
  targetDir: string,
  aiType: AIType
): Promise<string[]> {
  const copiedFolders: string[] = [];

  const foldersToCopy = aiType === 'all'
    ? ['.claude', '.cursor', '.windsurf', '.agent', '.shared']
    : AI_FOLDERS[aiType];

  // Deduplicate folders (e.g., .shared might be listed multiple times)
  const uniqueFolders = [...new Set(foldersToCopy)];

  for (const folder of uniqueFolders) {
    const sourcePath = join(sourceDir, folder);
    const targetPath = join(targetDir, folder);

    // Check if source folder exists
    const sourceExists = await exists(sourcePath);
    if (!sourceExists) {
      continue;
    }

    // Create target directory if needed
    await mkdir(targetPath, { recursive: true });

    // Filter function to exclude certain files
    const filterFn = (src: string): boolean => {
      const fileName = basename(src);
      return !EXCLUDED_FILES.includes(fileName);
    };

    // Copy recursively
    try {
      await cp(sourcePath, targetPath, { recursive: true, filter: filterFn });
      copiedFolders.push(folder);
    } catch {
      // Try shell fallback for older Node versions
      try {
        if (process.platform === 'win32') {
          await execAsync(`xcopy "${sourcePath}" "${targetPath}" /E /I /Y`);
        } else {
          await execAsync(`cp -r "${sourcePath}/." "${targetPath}"`);
        }
        copiedFolders.push(folder);
      } catch {
        // Skip if copy fails
      }
    }
  }

  return copiedFolders;
}

export async function cleanup(tempDir: string): Promise<void> {
  try {
    await rm(tempDir, { recursive: true, force: true });
  } catch {
    // Ignore cleanup errors
  }
}
