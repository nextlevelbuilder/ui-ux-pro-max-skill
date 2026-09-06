import { existsSync } from 'node:fs';
import { readFile, mkdir, writeFile, cp, access, readdir, lstat, rm } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ASSETS_CANDIDATES = [
  // Bun bundle: dist/index.js
  join(__dirname, '..', 'assets'),
  // TypeScript fallback: dist/utils/template.js
  join(__dirname, '..', '..', 'assets'),
];
const ASSETS_DIR = ASSETS_CANDIDATES.find(path => existsSync(path)) ?? ASSETS_CANDIDATES[0];

export interface PlatformConfig {
  platform: string;
  displayName: string;
  installType: 'full' | 'reference';
  folderStructure: {
    root: string;
    skillPath: string;
    filename: string;
    dataPath?: string;
  };
  scriptPath: string;
  frontmatter: Record<string, string> | null;
  sections: {
    quickReference: boolean;
  };
  title: string;
  description: string;
  skillOrWorkflow: string;
}

// Map AIType to platform config file name
const AI_TO_PLATFORM: Record<string, string> = {
  claude: 'claude',
  cursor: 'cursor',
  windsurf: 'windsurf',
  antigravity: 'agent',
  copilot: 'copilot',
  kiro: 'kiro',
  opencode: 'opencode',
  roocode: 'roocode',
  codex: 'codex',
  qoder: 'qoder',
  gemini: 'gemini',
  trae: 'trae',
  continue: 'continue',
  codebuddy: 'codebuddy',
  droid: 'droid',
  kilocode: 'kilocode',
  warp: 'warp',
  augment: 'augment',
  codewhale: 'codewhale',
  universal: 'universal',
};

async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

/**
 * Load platform configuration from JSON file
 */
export async function loadPlatformConfig(aiType: string): Promise<PlatformConfig> {
  const platformName = AI_TO_PLATFORM[aiType];
  if (!platformName) {
    throw new Error(`Unknown AI type: ${aiType}`);
  }

  const configPath = join(ASSETS_DIR, 'templates', 'platforms', `${platformName}.json`);
  const content = await readFile(configPath, 'utf-8');
  return JSON.parse(content) as PlatformConfig;
}

/**
 * Load all available platform configs
 */
export async function loadAllPlatformConfigs(): Promise<Map<string, PlatformConfig>> {
  const configs = new Map<string, PlatformConfig>();

  for (const [aiType, platformName] of Object.entries(AI_TO_PLATFORM)) {
    try {
      const config = await loadPlatformConfig(aiType);
      configs.set(aiType, config);
    } catch {
      // Skip if config doesn't exist
    }
  }

  return configs;
}

/**
 * Load a template file
 */
async function loadTemplate(templateName: string): Promise<string> {
  const templatePath = join(ASSETS_DIR, 'templates', templateName);
  return readFile(templatePath, 'utf-8');
}

/**
 * Render frontmatter section
 */
function renderFrontmatter(frontmatter: Record<string, string> | null): string {
  if (!frontmatter) return '';

  const lines = ['---'];
  for (const [key, value] of Object.entries(frontmatter)) {
    // Quote values that contain special characters
    if (value.includes(':') || value.includes('"') || value.includes('\n')) {
      lines.push(`${key}: "${value.replace(/"/g, '\\"')}"`);
    } else {
      lines.push(`${key}: ${value}`);
    }
  }
  lines.push('---', '');
  return lines.join('\n');
}

/**
 * Render skill file content from template
 * When isGlobal=true, rewrites script paths to use ~/{root}/ prefix
 */
export async function renderSkillFile(config: PlatformConfig, isGlobal = false): Promise<string> {
  // Load base template
  let content = await loadTemplate('base/skill-content.md');

  // Load quick reference if needed
  let quickReferenceContent = '';
  if (config.sections.quickReference) {
    quickReferenceContent = await loadTemplate('base/quick-reference.md');
  }

  // scriptPath is relative to the platform root. Generated commands run from
  // the user's project root, so local installs need the platform root prefix;
  // global installs need the same path anchored at the user's home directory.
  const rootedScriptPath = `${config.folderStructure.root}/${config.scriptPath}`
    .replace(/\/{2,}/g, '/');
  const commandScriptPath = isGlobal ? `~/${rootedScriptPath}` : rootedScriptPath;

  // Build the final content
  const frontmatter = renderFrontmatter(config.frontmatter);

  // Replace placeholders
  // Add newline before quick reference content if it exists
  const quickRefWithNewline = quickReferenceContent ? '\n' + quickReferenceContent : '';

  content = content
    .replace(/\{\{TITLE\}\}/g, config.title)
    .replace(/\{\{DESCRIPTION\}\}/g, config.description)
    .replace(/\{\{SCRIPT_PATH\}\}/g, commandScriptPath)
    .replace(/\{\{SKILL_OR_WORKFLOW\}\}/g, config.skillOrWorkflow)
    .replace(/\{\{QUICK_REFERENCE\}\}/g, quickRefWithNewline);

  return frontmatter + content;
}

/**
 * Replace a pre-existing non-directory at `path` so a real directory can be
 * created there. Older CLI installs (and Windows checkouts of the repo's
 * symlinked data/scripts) can leave plain "pointer" files at these paths;
 * mkdir then throws EEXIST and the install silently leaves stale files.
 */
async function ensureCleanDir(path: string): Promise<void> {
  try {
    const stat = await lstat(path);
    if (!stat.isDirectory()) {
      await rm(path, { recursive: true, force: true });
    }
  } catch {
    // Nothing exists at the path yet — mkdir will create it.
  }
}

/**
 * Copy data and scripts to target directory
 */
async function copyDataAndScripts(targetSkillDir: string): Promise<void> {
  const dataSource = join(ASSETS_DIR, 'data');
  const scriptsSource = join(ASSETS_DIR, 'scripts');

  const dataTarget = join(targetSkillDir, 'data');
  const scriptsTarget = join(targetSkillDir, 'scripts');

  // Copy data
  if (await exists(dataSource)) {
    await ensureCleanDir(dataTarget);
    await mkdir(dataTarget, { recursive: true });
    await cp(dataSource, dataTarget, { recursive: true });
  }

  // Copy scripts
  if (await exists(scriptsSource)) {
    await ensureCleanDir(scriptsTarget);
    await mkdir(scriptsTarget, { recursive: true });
    await cp(scriptsSource, scriptsTarget, { recursive: true });
  }
}

/**
 * List the static sub-skills bundled under assets/skills/ (everything except
 * the template-rendered orchestrator). Empty if the package predates bundling.
 */
export async function listBundledSubSkills(): Promise<string[]> {
  const skillsSource = join(ASSETS_DIR, 'skills');
  if (!(await exists(skillsSource))) return [];
  const entries = await readdir(skillsSource, { withFileTypes: true });
  return entries.filter(e => e.isDirectory()).map(e => e.name).sort();
}

/**
 * Install the bundled sub-skills as siblings of the orchestrator skill, so a
 * single `uipro init` delivers all 7 skills instead of only ui-ux-pro-max.
 */
async function copySubSkills(skillsParentDir: string, force: boolean): Promise<void> {
  const skillsSource = join(ASSETS_DIR, 'skills');
  if (!(await exists(skillsSource))) return;

  for (const name of await listBundledSubSkills()) {
    const target = join(skillsParentDir, name);
    if (await exists(target) && !force) continue;
    await mkdir(target, { recursive: true });
    await cp(join(skillsSource, name), target, { recursive: true });
  }
}

/**
 * Resolve every path an install touches for one platform. Shared by the real
 * install (generatePlatformFiles) and the read-only preview
 * (planPlatformInstallActions) so the two can never disagree.
 */
function resolveInstallPaths(
  config: PlatformConfig,
  targetDir: string,
  isGlobal: boolean
): {
  skillDir: string;
  skillFilePath: string;
  dataDir: string;
  skillsParentDir: string;
} {
  // For global install, target the user's home directory
  const effectiveDir = isGlobal ? homedir() : targetDir;

  // Determine full skill directory path
  const skillDir = join(
    effectiveDir,
    config.folderStructure.root,
    config.folderStructure.skillPath
  );
  const skillFilePath = join(skillDir, config.folderStructure.filename);

  // Copy data and scripts into the data directory (may differ from skill file location)
  const dataDir = config.folderStructure.dataPath
    ? join(effectiveDir, config.folderStructure.root, config.folderStructure.dataPath)
    : skillDir;

  // The skills parent is the orchestrator's parent dir (skills/ for most
  // platforms, prompts/ for copilot, steering/ for kiro) — derived, not
  // hardcoded. For platforms with a separate dataPath (copilot), the
  // orchestrator's data dir is the anchor.
  const skillsParentDir = join(
    effectiveDir,
    config.folderStructure.root,
    config.folderStructure.dataPath
      ? dirname(config.folderStructure.dataPath)
      : dirname(config.folderStructure.skillPath)
  );

  return { skillDir, skillFilePath, dataDir, skillsParentDir };
}

/**
 * Generate platform files for a specific AI type
 * All platforms use self-contained installation with data and scripts
 * When isGlobal=true, installs to ~/home directory with absolute script paths
 */
export async function generatePlatformFiles(
  targetDir: string,
  aiType: string,
  isGlobal = false,
  force = false
): Promise<string[]> {
  const config = await loadPlatformConfig(aiType);
  const createdFolders: string[] = [];
  const { skillDir, skillFilePath, dataDir, skillsParentDir } = resolveInstallPaths(
    config,
    targetDir,
    isGlobal
  );

  // Create directory structure
  await mkdir(skillDir, { recursive: true });

  // Render and write skill file (pass isGlobal to adjust paths)
  const skillContent = await renderSkillFile(config, isGlobal);

  const fileAlreadyExists = await exists(skillFilePath);
  if (fileAlreadyExists && !force) {
    console.log(`  Skipped (already exists): ${skillFilePath} — use --force to overwrite`);
    return [];
  }

  await writeFile(skillFilePath, skillContent, 'utf-8');
  createdFolders.push(config.folderStructure.root);

  await mkdir(dataDir, { recursive: true });
  await copyDataAndScripts(dataDir);

  // Install the sibling sub-skills (banner-design, brand, design, ...) next to
  // the orchestrator so all 7 skills are delivered.
  await copySubSkills(skillsParentDir, force);

  return createdFolders;
}

/**
 * Preview the actions generatePlatformFiles would take for one AI type,
 * without writing anything. Used by `uipro init --dry-run`.
 */
export async function planPlatformInstallActions(
  targetDir: string,
  aiType: string,
  isGlobal = false,
  force = false
): Promise<string[]> {
  const config = await loadPlatformConfig(aiType);
  const { skillFilePath, dataDir, skillsParentDir } = resolveInstallPaths(config, targetDir, isGlobal);

  const actions: string[] = [];
  const skillFileExists = await exists(skillFilePath);
  actions.push(
    skillFileExists && !force
      ? `Would skip (exists, use --force): ${skillFilePath}`
      : `Would write: ${skillFilePath}`
  );
  actions.push(`Would copy data + scripts: ${dataDir}`);

  const subSkills = await listBundledSubSkills();
  if (subSkills.length > 0) {
    actions.push(
      `Would copy ${subSkills.length} sub-skills (${subSkills.join(', ')}): ${skillsParentDir}`
    );
  }

  return actions;
}

/**
 * Preview the actions generateAllPlatformFiles would take, grouped per unique
 * platform layout, without writing anything. Used by `uipro init --dry-run`.
 */
export async function planAllPlatformInstallActions(
  targetDir: string,
  isGlobal = false,
  force = false
): Promise<Map<string, string[]>> {
  const planned = new Map<string, string[]>();
  const generatedSkillFiles = new Set<string>();

  for (const aiType of Object.keys(AI_TO_PLATFORM)) {
    try {
      const config = await loadPlatformConfig(aiType);
      const skillFile = join(
        config.folderStructure.root,
        config.folderStructure.skillPath,
        config.folderStructure.filename
      );
      if (generatedSkillFiles.has(skillFile)) continue;
      generatedSkillFiles.add(skillFile);

      planned.set(aiType, await planPlatformInstallActions(targetDir, aiType, isGlobal, force));
    } catch {
      // Skip if config doesn't exist
    }
  }

  return planned;
}

/**
 * Generate files for all AI types
 */
export async function generateAllPlatformFiles(targetDir: string, isGlobal = false, force = false): Promise<string[]> {
  const allFolders = new Set<string>();
  const generatedSkillFiles = new Set<string>();

  for (const aiType of Object.keys(AI_TO_PLATFORM)) {
    try {
      const config = await loadPlatformConfig(aiType);
      const skillFile = join(
        config.folderStructure.root,
        config.folderStructure.skillPath,
        config.folderStructure.filename
      );
      if (generatedSkillFiles.has(skillFile)) continue;

      const folders = await generatePlatformFiles(targetDir, aiType, isGlobal, force);
      generatedSkillFiles.add(skillFile);
      folders.forEach(f => allFolders.add(f));
    } catch {
      // Skip if generation fails for a platform
    }
  }

  return Array.from(allFolders);
}

/**
 * Get list of supported AI types
 */
export function getSupportedAITypes(): string[] {
  return Object.keys(AI_TO_PLATFORM);
}
