export type AIType = 'claude' | 'amp' | 'cursor' | 'windsurf' | 'antigravity' | 'copilot' | 'kiro' | 'roocode' | 'codex' | 'qoder' | 'gemini' | 'trae' | 'all';

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

export const AI_TYPES: AIType[] = ['claude', 'amp', 'cursor', 'windsurf', 'antigravity', 'copilot', 'roocode', 'kiro', 'codex', 'qoder', 'gemini', 'trae', 'all'];

export const AI_FOLDERS: Record<Exclude<AIType, 'all'>, string[]> = {
  claude: ['.claude'],
  amp: ['.agents'],
  cursor: ['.cursor', '.shared'],
  windsurf: ['.windsurf', '.shared'],
  antigravity: ['.agent', '.shared'],
  copilot: ['.github', '.shared'],
  kiro: ['.kiro', '.shared'],
  codex: ['.codex'],
  roocode: ['.roo', '.shared'],
  qoder: ['.qoder', '.shared'],
  gemini: ['.gemini', '.shared'],
  trae: ['.trae', '.shared'],
};
