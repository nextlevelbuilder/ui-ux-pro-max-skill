import { writeFile } from 'node:fs/promises';
import type { Release } from '../types/index.js';

const REPO_OWNER = 'nextlevelbuilder';
const REPO_NAME = 'ui-ux-pro-max-skill';
const API_BASE = 'https://api.github.com';
const USER_AGENT = 'ui-ux-pro-max-cli';

export class GitHubRateLimitError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'GitHubRateLimitError';
  }
}

export class GitHubDownloadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'GitHubDownloadError';
  }
}

export function getGitHubTokenGuidance(): string {
  return (
    'To increase your GitHub API rate limit, set the UI_PRO_MAX_GITHUB_TOKEN environment variable\n' +
    'to a GitHub Personal Access Token (no scopes needed for public repos).\n' +
    'Create one at: https://github.com/settings/tokens\n' +
    'Example: UI_PRO_MAX_GITHUB_TOKEN=ghp_xxx uipro init\n' +
    'Or pass it directly: uipro init --token ghp_xxx'
  );
}

function checkRateLimit(response: Response): void {
  const remaining = response.headers.get('x-ratelimit-remaining');
  if (response.status === 403 && remaining === '0') {
    const resetTime = response.headers.get('x-ratelimit-reset');
    const resetDate = resetTime ? new Date(parseInt(resetTime) * 1000).toLocaleTimeString() : 'unknown';
    throw new GitHubRateLimitError(
      `GitHub API rate limit exceeded. Resets at ${resetDate}.\n${getGitHubTokenGuidance()}`
    );
  }
  if (response.status === 429) {
    throw new GitHubRateLimitError(
      `GitHub API rate limit exceeded (429 Too Many Requests).\n${getGitHubTokenGuidance()}`
    );
  }
}

function getAuthHeaders(token?: string): Record<string, string> {
  const resolved = (token || process.env['UI_PRO_MAX_GITHUB_TOKEN'] || process.env['GITHUB_TOKEN'])?.trim();
  return resolved ? { 'Authorization': `Bearer ${resolved}` } : {};
}

export async function fetchReleases(token?: string): Promise<Release[]> {
  const url = `${API_BASE}/repos/${REPO_OWNER}/${REPO_NAME}/releases`;

  const response = await fetch(url, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': USER_AGENT,
      ...getAuthHeaders(token),
    },
  });

  checkRateLimit(response);

  if (!response.ok) {
    throw new GitHubDownloadError(`Failed to fetch releases: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function getLatestRelease(token?: string): Promise<Release> {
  const url = `${API_BASE}/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest`;

  const response = await fetch(url, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': USER_AGENT,
      ...getAuthHeaders(token),
    },
  });

  checkRateLimit(response);

  if (!response.ok) {
    throw new GitHubDownloadError(`Failed to fetch latest release: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function downloadRelease(url: string, dest: string, token?: string): Promise<void> {
  const response = await fetch(url, {
    headers: {
      'User-Agent': USER_AGENT,
      'Accept': 'application/octet-stream',
      ...getAuthHeaders(token),
    },
  });

  checkRateLimit(response);

  if (!response.ok) {
    throw new GitHubDownloadError(`Failed to download: ${response.status} ${response.statusText}`);
  }

  const buffer = await response.arrayBuffer();
  await writeFile(dest, Buffer.from(buffer));
}

export function getAssetUrl(release: Release): string | null {
  // First try to find an uploaded ZIP asset
  const asset = release.assets.find(a => a.name.endsWith('.zip'));
  if (asset?.browser_download_url) {
    return asset.browser_download_url;
  }

  // Fall back to GitHub's auto-generated archive
  // Format: https://github.com/{owner}/{repo}/archive/refs/tags/{tag}.zip
  if (release.tag_name) {
    return `https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/tags/${release.tag_name}.zip`;
  }

  return null;
}
