export type AIType = 'claude' | 'cursor' | 'windsurf' | 'antigravity' | 'copilot' | 'kiro' | 'roocode' | 'codex' | 'qoder' | 'gemini' | 'trae' | 'opencode' | 'continue' | 'codebuddy' | 'droid' | 'kilocode' | 'warp' | 'augment' | 'codewhale' | 'universal' | 'all';
export type ConcreteAIType = Exclude<AIType, 'all'>;

export type InstallType = 'full' | 'reference';

export interface Release {
  tag_name: string;
  name: string;
  published_at: string;
  html_url: string;
  assets: Asset[];
}

export interface Asset {
  name: string;
  browser_download_url: string;
  size: number;
}

export interface InstallConfig {
  aiType: AIType;
  version?: string;
  force?: boolean;
}

export interface PlatformConfig {
  platform: string;
  displayName: string;
  installType: InstallType;
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

export const AI_TYPES: AIType[] = ['claude', 'cursor', 'windsurf', 'antigravity', 'copilot', 'roocode', 'kiro', 'codex', 'qoder', 'gemini', 'trae', 'opencode', 'continue', 'codebuddy', 'droid', 'kilocode', 'warp', 'augment', 'codewhale', 'universal', 'all'];

// Legacy folder mapping for backward compatibility with ZIP-based installs.
// Note: .shared is included for platforms that used ZIP installs. Post-ZIP platforms
// (kilocode, warp, augment) include .shared as a no-op for consistent uninstall behavior.
export const AI_FOLDERS: Record<ConcreteAIType, string[]> = {
  claude: ['.claude'],
  cursor: ['.cursor', '.shared'],
  windsurf: ['.windsurf', '.shared'],
  antigravity: ['.agents', '.shared'],
  copilot: ['.github', '.shared'],
  kiro: ['.kiro', '.shared'],
  codex: ['.codex'],
  roocode: ['.roo', '.shared'],
  qoder: ['.qoder', '.shared'],
  gemini: ['.gemini', '.shared'],
  trae: ['.trae', '.shared'],
  opencode: ['.opencode', '.shared'],
  continue: ['.continue'],
  codebuddy: ['.codebuddy'],
  droid: ['.factory'],
  kilocode: ['.kilocode', '.shared'],
  warp: ['.warp', '.shared'],
  augment: ['.augment', '.shared'],
  codewhale: ['.codewhale', '.shared'],
  universal: ['.agents', '.shared'],
};
