import { test, expect } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Smoke test for the generated design-system preview pages under /preview.
 * These files are shipped as proof that the design system generator produces
 * working, self-contained HTML (see README "How Design System Generation Works").
 * This guards against a preview shipping with broken markup or JS errors.
 */

const PREVIEW_DIR = path.resolve(__dirname, '../../../preview');
const PREVIEW_FILE = 'xiaomaomi-app.html';

test.describe('generated preview pages', () => {
  test(`${PREVIEW_FILE} renders without console errors`, async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('pageerror', (err) => consoleErrors.push(err.message));

    const fileUrl = pathToFileURL(path.join(PREVIEW_DIR, PREVIEW_FILE)).href;
    await page.goto(fileUrl);

    await expect(page.locator('body')).toBeVisible();
    expect(consoleErrors, `console errors: ${consoleErrors.join('\n')}`).toHaveLength(0);
  });
});
