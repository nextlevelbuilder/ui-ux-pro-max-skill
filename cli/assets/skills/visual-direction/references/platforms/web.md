# Platform adapter: Web (CSS variables, Tailwind v4, React / Next / Vue / Svelte)

Maps `design-system/<slug>/tokens.json` (contract §4.2, leaf names per CC-7) to the web. The CSS generator already ships in the sibling `design-system` skill; this adapter tells you what it emits, how to wire Tailwind v4 on top, and how components, motion and screenshots consume it. Stack ids: `react`, `nextjs`, `vue`, `svelte`, `html-tailwind`. `$extensions.vdp.platformUnit` is `px`, so dimension `$value`s are written `"16px"`, durations `"200ms"`, easings `cubic-bezier(...)`, shadows as `box-shadow` strings — the generator copies values verbatim, so only `px` token files produce valid CSS (a `logical`/`dp`/`pt` file generates bare numbers; regenerate the tokens for a web profile instead of hand-editing).

## 1. Where tokens live

```
design-system/<slug>/tokens.json        # source of truth (contract §3)
src/styles/tokens.css                   # GENERATED — never edited by hand
src/styles/theme.css                    # Tailwind v4 @theme mapping (hand-written, thin, section 1.2)
src/styles/globals.css                  # @import order: tailwind → tokens → theme → components
src/components/ui/                      # Button, Card, Dialog, Chip, Tile, ProgressBar, Toast
```

### 1.1 Generate

```bash
node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json -o <out>
node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json -o src/styles/tokens.css
node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json --format tailwind   # legacy v3 colors snippet
```

(The path is skill-relative: `../design-system/scripts/` is the sibling skill folder next to this one; run with the project root as working directory.) Add the second command to `package.json` as `"tokens": "..."` and run it in `prebuild`.

**Emitted variable names** (from the generator's `flattenTokens`: primitives keep a `--primitive-` prefix, semantic and component layers are unprefixed, camelCase is preserved, nested groups join with `-`):

| Layer | tokens.json path | CSS variable |
|---|---|---|
| primitive | `primitive.color.brand.500` | `--primitive-color-brand-500` |
| primitive | `primitive.radius.2xl`, `primitive.duration.base`, `primitive.easing.enter` | `--primitive-radius-2xl`, `--primitive-duration-base`, `--primitive-easing-enter` |
| semantic | `semantic.color.primary`, `semantic.color.surfaceElevated` | `--color-primary`, `--color-surfaceElevated` |
| semantic | `semantic.radius.control`, `semantic.elevation.raised`, `semantic.spacing.inset` | `--radius-control`, `--elevation-raised`, `--spacing-inset` |
| semantic | `semantic.state.pressed.offsetY`, `semantic.typography.body.fontSize` | `--state-pressed-offsetY`, `--typography-body-fontSize` |
| component | `component.button.primary.radius`, `component.hud.chip.bg`, `component.progress.fillDuration` | `--button-primary-radius`, `--hud-chip-bg`, `--progress-fillDuration` |
| dark | `dark.semantic.color.surface` | `--color-surface` under `.dark` |

References are resolved to literals, so `tokens.css` has no `var()` chains; dark mode is a `.dark` class block (toggle on `<html>`). `$extensions` is ignored by the generator.

### 1.2 Tailwind v4 `@theme` mapping

Tailwind v4 reads design tokens from CSS, so `theme.css` is a mapping, not a copy. `reference` stops Tailwind from re-emitting `--color-primary` on `:root` (which would self-reference the value from `tokens.css`); `inline` makes utilities carry the `var()` so the `.dark` block still wins at runtime.

```css
/* src/styles/globals.css */
@import "tailwindcss";
@import "./tokens.css";

@theme inline reference {
  /* semantic.color.* → bg-primary, text-on-primary, border-border ... */
  --color-primary: var(--color-primary);        --color-on-primary: var(--color-onPrimary);
  --color-secondary: var(--color-secondary);    --color-on-secondary: var(--color-onSecondary);
  --color-accent: var(--color-accent);          --color-on-accent: var(--color-onAccent);
  --color-background: var(--color-background);  --color-surface: var(--color-surface);
  --color-surface-elevated: var(--color-surfaceElevated); --color-border: var(--color-border);
  --color-overlay: var(--color-overlay);        --color-text: var(--color-text);
  --color-text-muted: var(--color-textMuted);   --color-success: var(--color-success);
  --color-warning: var(--color-warning);        --color-danger: var(--color-danger);  --color-reward: var(--color-reward);
  /* primitive.spacing.* → p-4, gap-2 (Tailwind multiplies --spacing by the utility number; map each step instead) */
  --spacing-1: var(--primitive-spacing-1);  --spacing-2: var(--primitive-spacing-2);  --spacing-4: var(--primitive-spacing-4);
  /* semantic.radius.* → rounded-control, rounded-container, rounded-popup, rounded-tile, rounded-chip */
  --radius-control: var(--radius-control);  --radius-container: var(--radius-container);  --radius-chip: var(--radius-chip);
  --shadow-raised: var(--elevation-raised); --shadow-elevated: var(--elevation-elevated); --shadow-floating: var(--elevation-floating);
  --text-body: var(--typography-body-fontSize); --text-body--line-height: var(--typography-body-lineHeight);
  --ease-standard: var(--primitive-easing-standard); --ease-enter: var(--primitive-easing-enter); --ease-exit: var(--primitive-easing-exit);
}
```

Tailwind v4 has no `--duration-*`, `--z-index-*`, `--opacity-*` or `--outline-*` theme namespaces; those groups are used as `duration-(--primitive-duration-base)`, `z-(--primitive-zIndex-popup)`, `opacity-(--primitive-opacity-disabled)` (v4 CSS-variable shorthand) or inside `@utility` definitions. Keep camelCase from tokens.json in `tokens.css` names (the generator does not kebab-case) and expose kebab-case only through `@theme`.

### Easing name table for JS libraries (from token-derivation §1.11)

| motion class | `primitive.easing.standard` | `primitive.easing.enter` | `primitive.easing.exit` | `primitive.easing.emphasized` |
|---|---|---|---|---|
| `static` | `none` | `none` | `none` | `none` |
| `snappy` | `power2.out` | `power2.out` | `power2.in` | `power2.out` |
| `soft` | `power1.inOut` | `power2.out` | `power2.in` | `sine.inOut` |
| `bouncy` | `back.out(1.7)` | `back.out(1.7)` | `back.in(1.7)` | `back.inOut(2)` |
| `dramatic` | `expo.out` | `expo.out` | `expo.in` | `expo.inOut` |

CSS transitions use the bezier verbatim; GSAP users either register `CustomEase.create('standard', bezierFromVar('--primitive-easing-standard'))` (exact) or use this table (approximation).

## 2. Token group → code mapping

| Group (CC-7) | Plain CSS (`tokens.css`) | Tailwind v4 utility | JS/TS access |
|---|---|---|---|
| `primitive.color.*` ramps | `var(--primitive-color-brand-500)` — only inside `tokens.css`-adjacent overrides, never in components | not mapped (components use semantic colours) | — |
| `semantic.color.*` | `background: var(--color-primary); color: var(--color-onPrimary)` | `bg-primary text-on-primary border-border` via `@theme` colors | `getComputedStyle(root).getPropertyValue('--color-primary')` |
| `semantic.color.borderInteractive` | `border-color: var(--color-borderInteractive)` on tiles, icon buttons, the secondary button and tappable HUD capsules (`var(--hud-chipInteractive-outlineColor)`); decorative cards/popups keep `var(--color-border)` | `border-border-interactive` after mapping `--color-border-interactive: var(--color-borderInteractive)` in `@theme` | `getComputedStyle(root).getPropertyValue('--color-borderInteractive')` |
| `semantic.color.focusRing` / `semantic.state.focus.*` | `:focus-visible { outline: var(--state-focus-ringWidth) solid var(--state-focus-ringColor); outline-offset: var(--state-focus-ringOffset) }` — `--state-focus-ringColor` resolves to `--color-focusRing` (≥ 3:1 vs background and surface) | `focus-visible:outline-(--state-focus-ringColor)` with `outline-(length:--state-focus-ringWidth)` | `getComputedStyle(root).getPropertyValue('--color-focusRing')` |
| `primitive.spacing.*` / `semantic.spacing.*` | `padding: var(--spacing-inset); gap: var(--spacing-stack); padding-inline: var(--spacing-screenGutter)` | `p-4 gap-2` after mapping `--spacing-N` | — |
| `primitive.radius.*` / `semantic.radius.*` | `border-radius: var(--radius-control)` (controls), `var(--radius-container)` (cards), `var(--radius-popup)`, `var(--radius-tile)`, `var(--radius-chip)` | `rounded-control rounded-container rounded-chip` | — |
| `primitive.outline.*` / `semantic.outline.control` | `border-width: var(--outline-control)` (cartoon outline = border, not CSS `outline`); colour already resolved into `--button-primary-outlineColor` etc. | `border-(length:--outline-control)` | — |
| `primitive.shadow.*` / `semantic.elevation.*` | `box-shadow: var(--elevation-raised)`; component shadows `var(--button-primary-shadow)` (double-clay literal with the fill's 700 shade) | `shadow-raised shadow-elevated shadow-floating` | — |
| `semantic.typography.*` | `font-family: var(--typography-body-fontFamily); font-size: var(--typography-body-fontSize); line-height: var(--typography-body-lineHeight); font-weight: var(--typography-body-fontWeight)` (roles `display`, `title`, `body`, `label`, `caption`) | `text-body` (size + paired line-height) | — |
| `primitive.iconSize.*` | `inline-size: var(--primitive-iconSize-md)` on `svg` | `size-(--primitive-iconSize-md)` | icon component `size` prop reads the var |
| `primitive.touchTarget.*` | `min-inline-size: var(--primitive-touchTarget-min); min-block-size: var(--primitive-touchTarget-min)` | `min-w-(--primitive-touchTarget-min) min-h-(--primitive-touchTarget-min)` | — |
| `primitive.duration.*` | `transition-duration: var(--primitive-duration-base)`; `reveal` for page/level reveals (CC-8 `reward`/`ambient` keys when present) | `duration-(--primitive-duration-base)` | `parseFloat(var) / 1000` for GSAP (section 3) |
| `primitive.easing.*` | `transition-timing-function: var(--primitive-easing-enter)` on appearing elements, `--primitive-easing-exit` on leaving ones | `ease-enter ease-exit` via `@theme` | `CustomEase` or the name table |
| `primitive.zIndex.*` | `z-index: var(--primitive-zIndex-popup)` (`hud` 100 < `overlay` 200 < `popup` 300 < `toast` 400 < `tutorial` 500) | `z-(--primitive-zIndex-popup)` | portal containers read the same var |
| `primitive.opacity.*` | `opacity: var(--primitive-opacity-disabled)`; scrims use `--color-overlay` (already carries `primitive.opacity.scrim`) | `opacity-(--primitive-opacity-disabled)` | — |
| `semantic.state.*` | `:hover { opacity: var(--state-hover-opacity) } :active { translate: 0 var(--state-pressed-offsetY); box-shadow: var(--state-pressed-shadow) } :focus-visible { outline: var(--state-focus-ringWidth) solid var(--state-focus-ringColor); outline-offset: var(--state-focus-ringOffset) } :disabled { opacity: var(--state-disabled-opacity) }` | `hover:opacity-(--state-hover-opacity) active:translate-y-(--state-pressed-offsetY) disabled:opacity-(--state-disabled-opacity)` | — |
| `component.*` | `--button-primary-*`, `--button-secondary-*`, `--button-icon-*`, `--card-*`, `--popup-*`, `--hud-chip-*`, `--tile-*`, `--progress-*` consumed by exactly one CSS file each | — | — |

Rule: no hex, px, ms or `cubic-bezier` literals in component files; the `visual-audit` skill scans `.css/.scss/.tsx/.jsx/.vue/.svelte` for `#rrggbb`, `\d+px`, `\d+ms` outside `tokens.css`. `node ../design-system/scripts/validate-tokens.cjs --dir src/` gives a quick hard-coded-value sweep for projects that already use the `design-system` skill.

## 3. Component reuse patterns

One implementation per component, variants through a `variant` prop / `data-variant` attribute, all values from `tokens.css`. The CSS below is framework-neutral; the framework skeletons only add the wrapper.

```css
/* src/components/ui/button.css — reads component.button.* only */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: var(--spacing-inline);
  min-inline-size: var(--button-primary-minWidth); block-size: var(--button-primary-height);
  padding-inline: var(--button-primary-paddingX);
  border: var(--button-primary-outlineWidth) solid var(--button-primary-outlineColor); border-radius: var(--button-primary-radius);
  font-family: var(--typography-label-fontFamily); font-size: var(--button-primary-fontSize); font-weight: var(--button-primary-fontWeight);
  transition: translate var(--primitive-duration-fast) var(--primitive-easing-standard), box-shadow var(--primitive-duration-fast), opacity var(--primitive-duration-fast); }
.btn[data-variant="primary"]   { background: var(--button-primary-bg);   color: var(--button-primary-fg);   box-shadow: var(--button-primary-shadow); }
.btn[data-variant="secondary"] { background: var(--button-secondary-bg); color: var(--button-secondary-fg); border-color: var(--button-secondary-outlineColor); box-shadow: var(--button-secondary-shadow); }
.btn[data-variant="icon"]      { padding: 0; min-inline-size: 0; inline-size: var(--button-icon-size); block-size: var(--button-icon-size); border-radius: var(--button-icon-radius); background: var(--button-icon-bg); color: var(--button-icon-fg); }
.btn[data-variant="icon"] svg  { inline-size: var(--button-icon-iconSize); block-size: var(--button-icon-iconSize); }
.btn[data-variant="primary"]:hover  { background: var(--button-primary-bgHover); }
.btn[data-variant="primary"]:active { background: var(--button-primary-bgPressed); translate: 0 var(--button-primary-pressedOffsetY); box-shadow: var(--state-pressed-shadow); }
.btn:focus-visible { outline: var(--state-focus-ringWidth) solid var(--state-focus-ringColor); outline-offset: var(--state-focus-ringOffset); }
.btn:disabled { opacity: var(--state-disabled-opacity); pointer-events: none; }
```

### React / Next (`src/components/ui/Button.tsx`)

```tsx
import './button.css';
type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'icon' };
export function Button({ variant = 'primary', className = '', ...rest }: Props) {
  return <button data-variant={variant} className={`btn ${className}`} {...rest} />;
}
```

Next.js: import `globals.css` once in `app/layout.tsx`; `tokens.css` is static so it is safe in Server Components. Set the `.dark` class on `<html>` in the layout (cookie-driven) to avoid a flash.

### Vue (`Button.vue`)

```vue
<script setup lang="ts">defineProps<{ variant?: 'primary' | 'secondary' | 'icon' }>()</script>
<template><button class="btn" :data-variant="variant ?? 'primary'"><slot /></button></template>
<style src="./button.css"></style>
```

### Svelte (`Button.svelte`)

```svelte
<script lang="ts">let { variant = 'primary', children, ...rest } = $props();</script>
<button class="btn" data-variant={variant} {...rest}>{@render children()}</button>
<style>@import './button.css';</style>
```

### card / panel
`.card { background: var(--card-bg); color: var(--card-fg); border: var(--card-borderWidth) solid var(--card-borderColor); border-radius: var(--card-radius); padding: var(--card-padding); box-shadow: var(--card-shadow); display: grid; gap: var(--card-gap); }` `.card[data-elevated] { background: var(--color-surfaceElevated); box-shadow: var(--elevation-elevated); }`. Dialog, toast and HUD chip have their own component tokens; they never redeclare radius/outline from `.card`.

### popup / dialog
Native `<dialog>` styled from `component.popup.*`: `.popup { background: var(--popup-bg); color: var(--popup-fg); border: var(--popup-outlineWidth) solid var(--popup-outlineColor); border-radius: var(--popup-radius); padding: var(--popup-padding); max-inline-size: var(--popup-maxWidth); box-shadow: var(--popup-shadow); z-index: var(--popup-zIndex); }` `.popup::backdrop { background: var(--popup-scrim); }`; open animation `@starting-style { opacity: 0; scale: 0.9 }` with `transition: opacity var(--popup-enterDuration) var(--popup-enterEasing), scale var(--popup-enterDuration) var(--popup-enterEasing)`; closing uses `--primitive-duration-fast` + `--primitive-easing-exit`. Frameworks wrap it (React portal / Vue `<Teleport>` / Svelte `{#if open}`) but reuse the same CSS file.

### HUD chip
`.chip { display: inline-flex; align-items: center; gap: var(--spacing-inline); block-size: var(--hud-chip-height); padding-inline: var(--hud-chip-paddingX); border-radius: var(--hud-chip-radius); background: var(--hud-chip-bg); color: var(--hud-chip-fg); border: var(--hud-chip-outlineWidth) solid var(--hud-chip-outlineColor); box-shadow: var(--hud-chip-shadow); font-size: var(--hud-chip-fontSize); font-weight: var(--hud-chip-fontWeight); z-index: var(--hud-chip-zIndex); }` `.chip svg { inline-size: var(--hud-chip-iconSize); }`. Value bump: toggle `data-bump` which runs `@keyframes chip-bump` (scale 1→1.08→1) for `var(--primitive-duration-fast)` with `var(--primitive-easing-enter)`.

### tile
`.tile { aspect-ratio: 1; min-inline-size: var(--tile-minSize); background: var(--tile-bg); border-radius: var(--tile-radius); border: var(--tile-outlineWidth) solid var(--tile-outlineColor); box-shadow: var(--tile-shadow); }` `.tile[aria-selected="true"] { background: var(--tile-bgSelected); border-color: var(--tile-outlineColorSelected); scale: 1.06; transition: scale var(--primitive-duration-fast) var(--primitive-easing-enter); }` `.tile[data-cleared] { opacity: 0; transition: opacity var(--primitive-duration-base) var(--primitive-easing-exit); }`. Game boards render tiles in CSS Grid with `gap: var(--tile-gap)`.

### progress bar
`<progress>` is hard to theme consistently; use `.bar { block-size: var(--progress-height); border-radius: var(--progress-radius); background: var(--progress-track); border: var(--progress-outlineWidth) solid var(--progress-outlineColor); overflow: hidden; } .bar > i { display: block; block-size: 100%; inline-size: calc(var(--value) * 100%); background: var(--progress-fill); transition: inline-size var(--progress-fillDuration) var(--progress-fillEasing); } .bar[data-reward] > i { background: var(--progress-fillReward); }` with `style="--value: 0.42"` and `role="progressbar"` + `aria-valuenow`.

### toast
`.toast { /* same declarations as .popup minus max-inline-size */ position: fixed; inset-block-end: var(--spacing-inset); z-index: var(--primitive-zIndex-toast); }` `.toast[data-kind="success"] svg { color: var(--color-success); }` (same for `warning`/`danger`/`reward`). Lifetime is not a CC-7 token: `setTimeout(close, ms('--primitive-duration-reveal') * 6)` in the shared toast module (a multiplier on a listed duration, documented in `interaction-guidelines.md`).

### Motion from tokens (GSAP and CSS)

```ts
// src/lib/motion.ts — one place that converts token strings for JS animation
const root = () => getComputedStyle(document.documentElement);
export const ms = (name: string) => parseFloat(root().getPropertyValue(name)) || 0;   // '200ms' → 200
export const sec = (name: string) => ms(name) / 1000;
const EASE: Record<string, string> = { standard: 'back.out(1.7)', enter: 'back.out(1.7)', exit: 'back.in(1.7)', emphasized: 'back.inOut(2)' }; // bouncy row of the name table
export const ease = (token: keyof typeof EASE) => EASE[token];     // or CustomEase.create(token, bezierFromVar(`--primitive-easing-${token}`))
export const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

// gsap.to(el, { y: -4, scale: 1.02, duration: reduced() ? 0 : sec('--primitive-duration-base'), ease: ease('standard') });
```

Rule: GSAP snippets from `ui-ux-pro-max` (`search.py --domain gsap`) are templates; replace their literal `duration`/`ease` with `sec()`/`ease()`. CSS transitions use the vars directly and `@media (prefers-reduced-motion: reduce) { * { transition-duration: 0ms !important; animation-duration: 0ms !important; } }` honours `motion.reduced_motion: respect`.

## 4. Migration order when fixing drift

1. **Tokens**: edit `tokens.json`, regenerate `tokens.css`; diff `tokens.css` — removed variables are the breaking list. `node ../design-system/scripts/validate-tokens.cjs --dir src/` lists remaining hard-coded values.
2. **`theme.css`**: update the `@theme` mapping for renamed tokens; `grep -rn "var(--" src | grep -v tokens.css` for orphaned references.
3. **Shared components** in dependency order: `button.css` → `card.css` → `popup`/`toast`/`chip` → `tile` → `progress`.
4. **Pages/routes** leaf-first: settings/about → home → shop → gameplay (depends on tile/chip/dialog). Replace local `<button className="rounded-[13px] bg-[#FF7F50]">` with `<Button variant>`; arbitrary-value utilities (`[...]`) are the drift signal.
5. **Delete duplicates** flagged `component.duplicate-implementation`; re-run the `visual-audit` skill scan (`audit.py scan`) and the Playwright matrix after each step.

## 5. What not to touch

- Data fetching, state stores, routing, auth, payments, analytics, game logic in workers/canvas.
- Component public props: add `variant`/`kind` with defaults, do not rename existing props.
- Third-party component internals (shadcn/ui generated files are yours; `node_modules` is not — override via CSS variables they already expose).
- Build config beyond adding the `tokens` npm script.

## 6. Screenshot capture for QA

Playwright, one project per device, `toHaveScreenshot` with animations disabled:

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: 'qa/screens', snapshotPathTemplate: 'qa/screens/__shots__/{arg}_{projectName}{ext}',
  use: { colorScheme: 'light', locale: 'en-US', timezoneId: 'UTC', reducedMotion: 'reduce' },
  expect: { toHaveScreenshot: { animations: 'disabled', caret: 'hide', maxDiffPixelRatio: 0.005, scale: 'css' } },
  projects: [
    { name: 'phone_small', use: { ...devices['iPhone SE'] } },
    { name: 'phone_tall',  use: { ...devices['iPhone 14 Pro'] } },
    { name: 'android',     use: { ...devices['Pixel 7'] } },
    { name: 'tablet',      use: { ...devices['iPad (gen 7)'] } },
    { name: 'desktop',     use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } } },
  ],
});
// qa/screens/screens.spec.ts
for (const screen of ['home', 'gameplay', 'shop'])
  test(screen, async ({ page }) => { await page.clock.setFixedTime('2026-01-01T09:41:00Z'); await page.goto(`/${screen}?qa=1&seed=42`);
    await page.evaluate(() => document.fonts.ready); await expect(page).toHaveScreenshot(`${screen}.png`, { fullPage: true }); });
```

Commands: `npx playwright test --project=phone_small` (compare), `npx playwright test --update-snapshots` (re-baseline after an approved change). The PNGs land as `<screen>_<device>.png` (the `visual_qa.py manifest` convention); feed them to `visual_qa.py diff` (`visual-audit` skill) when comparing against design references rather than previous builds.

**Determinism:** `reducedMotion: 'reduce'` + `animations: 'disabled'`; `page.clock` fixed time; `?qa=1&seed=42` makes the app seed RNG and skip intro/tutorial; self-hosted fonts for `primitive.fontFamily.display` / `primitive.fontFamily.body` (no Google Fonts network in CI) and `document.fonts.ready`; `mask: [page.locator('[data-dynamic]')]` for live counters; fixed `deviceScaleFactor` from the device preset; same browser channel in CI and local (`chromium` only for baselines); disable service workers (`serviceWorkers: 'block'`).

## 7. Performance notes

- `tokens.css` is small and static — inline it in the document head (Next: import in root layout; Vite: `?inline`) to avoid a render-blocking round trip and theme flash.
- `@theme inline reference` keeps the generated CSS to utilities only; without `reference` Tailwind duplicates every variable.
- Animate `transform`/`opacity`/`scale`/`translate` only; `inline-size` transitions in the progress bar are acceptable once per update, not per frame.
- Use `gsap.quickTo` for hover on many tiles; one `ResizeObserver`, not one per tile.
- `content-visibility: auto` on off-screen shop lists; `will-change` only on the element currently animating.
- Respect `prefers-reduced-motion` at the CSS layer so JS never needs to branch per element.

## 8. Known limitations

- `generate-tokens.cjs` preserves camelCase (`--color-surfaceElevated`) and prefixes primitives with `--primitive-`; the `@theme` block is where kebab-case lives — keep both in sync by hand (no automation yet).
- Its `--format tailwind` output targets Tailwind v3 `theme.extend.colors`; v4 projects use the `@theme` block instead.
- `@theme inline reference` behaviour should be verified on the project's Tailwind minor; if variables are duplicated, drop `inline`.
- Only `dark.semantic` is emitted for dark mode; dark `component` overrides are not generated, and component tokens with literal colours (double-clay shadows, outline colours) do not flip.
- The generator writes `$value` strings verbatim: `primitive.radius.full` becomes `9999px`, which is fine for `border-radius` but must not be mapped into Tailwind's `--spacing` namespace.
- The canonical example tokens.json carries `primitive.duration.{instant,fast,base,slow,reveal}`; CC-8 `reward`/`ambient` variables exist only when the emitting profile includes them.
- GSAP easing is an approximation unless `CustomEase` is registered; CSS uses the bezier exactly.
- Playwright device presets emulate viewport/DPR/UA, not real GPU rendering; treat mobile baselines as layout checks, not pixel truth.
