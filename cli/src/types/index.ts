export type AIType = 'claude' | 'cursor' | 'windsurf' | 'antigravity' | 'copilot' | 'all';

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

export const AI_TYPES: AIType[] = ['claude', 'cursor', 'windsurf', 'antigravity', 'copilot', 'all'];

export const AI_FOLDERS: Record<Exclude<AIType, 'all'>, string[]> = {
  claude: ['.claude'],
  cursor: ['.cursor', '.shared'],
  windsurf: ['.windsurf', '.shared'],
  antigravity: ['.agent', '.shared'],
  copilot: ['.github', '.shared'],
};
