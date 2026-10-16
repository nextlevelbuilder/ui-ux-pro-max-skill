# Platform adapter: Unity (uGUI and UI Toolkit)

Maps `design-system/<slug>/tokens.json` (contract §4.2, leaf names per CC-7) to Unity. Two UI systems coexist in current Unity versions; this file covers both and gives one decision rule. Stack ids: `unity-ugui`, `unity-ui-toolkit`. `$extensions.vdp.platformUnit` is `px`, so dimension `$value`s carry a `px` suffix (`"16px"`) and are interpreted against the Canvas Scaler / Panel Settings reference resolution (section 1), so values stay portable across devices. Durations are `"<n>ms"`, easings `cubic-bezier(...)`, shadows CSS `box-shadow` strings.

## Decision rule: uGUI vs UI Toolkit

| Pick | When |
|---|---|
| **uGUI** | world-space UI (health bars over characters, in-world signs); heavy particle/VFX mixed with UI; existing project already on uGUI; third-party UI assets that only ship uGUI prefabs; target Unity older than 2021 LTS |
| **UI Toolkit** | new screen-space menus, shop, settings, data-driven lists; you want runtime theming by swapping a stylesheet; designers edit layout without touching prefabs |
| **Both** | allowed per project, never per screen. Typical split: gameplay HUD overlays in uGUI (same canvas as VFX), all menus in UI Toolkit. Both read the same `ThemeAsset` (section 1). |

## 1. Where tokens live

```
Assets/UI/Theme/
├── ThemeAsset.cs            # ScriptableObject definition (one field per token leaf, grouped)
├── Theme_Default.asset      # GENERATED values from tokens.json (serialized), one per light/dark
├── TextStyles.asset         # TMP_StyleSheet: styles named after semantic.typography roles (Display, Title, Body, Label, Caption)
├── tokens.uss               # GENERATED USS variables for UI Toolkit (same generator as the web adapter)
├── AppTheme.tss             # ThemeStyleSheet: @import url("tokens.uss"); @import default runtime theme
├── Sprites/9slice/          # button/card/chip/tile sprites with borders set in Sprite Editor
└── Templates/*.uxml         # UI Toolkit component templates
Assets/UI/Components/        # shared MonoBehaviours / VisualElement subclasses (section 3)
```

Naming: ScriptableObject fields are `PascalCase` per token path with the layer prefix dropped (`semantic.color.surfaceElevated` → `ColorSurfaceElevated`, `primitive.spacing.4` → `Spacing4`, `primitive.radius.2xl` → `Radius2xl`, `component.button.primary.bg` → `ButtonPrimaryBg`). USS variables keep the generator's naming: semantic `--color-primary`, `--radius-control`, `--state-pressed-offsetY`; component `--button-primary-radius`, `--hud-chip-bg`; primitives `--primitive-spacing-4`, `--primitive-duration-base` (identical to the web adapter so one tokens.json is the source for both; camelCase is preserved).

```csharp
[CreateAssetMenu(menuName = "UI/Theme Asset")]
public sealed class ThemeAsset : ScriptableObject
{
    [Header("Generated from tokens.json — edit tokens.json, then re-sync")]
    public string GeneratedFrom;                                   // $extensions.vdp.generatedFrom
    // semantic.color.*
    public Color ColorPrimary, ColorOnPrimary, ColorPrimaryHover, ColorPrimaryPressed, ColorSecondary, ColorOnSecondary,
                 ColorAccent, ColorOnAccent, ColorBackground, ColorSurface, ColorSurfaceElevated, ColorBorder, ColorBorderInteractive, ColorOverlay,
                 ColorText, ColorTextMuted, ColorSuccess, ColorWarning, ColorDanger, ColorReward, ColorFocusRing;
    public float Spacing1, Spacing2, Spacing3, Spacing4, Spacing5, Spacing6, Spacing8;        // primitive.spacing.*
    public float RadiusControl, RadiusContainer, RadiusPopup, RadiusTile, RadiusChip;         // semantic.radius.* (resolved px)
    public float OutlineControl;                                                              // semantic.outline.control
    public ShadowSpec[] ElevationRaised, ElevationElevated, ElevationFloating;                 // semantic.elevation.* (layers)
    public TextStyleSpec TypographyDisplay, TypographyTitle, TypographyBody, TypographyLabel, TypographyCaption;
    public float IconSizeSm, IconSizeMd, IconSizeLg, IconSizeXl, TouchTargetMin, TouchTargetRecommended;
    public float DurationFastMs, DurationBaseMs, DurationSlowMs, DurationRevealMs;            // primitive.duration.*
    public AnimationCurve EasingStandard, EasingEnter, EasingExit, EasingEmphasized;          // baked from cubic-bezier
    public int ZIndexHud, ZIndexOverlay, ZIndexPopup, ZIndexToast, ZIndexTutorial;            // Canvas sortingOrder
    public float OpacityDisabled, OpacityHover, OpacityPressed, OpacityScrim, OpacityMuted;
    public StateRule StateHover, StatePressed, StateFocus, StateDisabled;                     // semantic.state.*
    public ButtonSpec ButtonPrimary, ButtonSecondary, ButtonIcon; public PanelSpec Card, Popup; public ChipSpec HudChip;
    public TileSpec Tile; public ProgressSpec Progress;                                       // component.*
}
```

Sync rule (editor script, `Assets/Editor/ThemeSync.cs`, menu item `UI/Sync Theme From tokens.json`): read tokens.json with `JsonUtility`-free parsing (Unity's `JsonUtility` cannot read `$value` keys; use `Newtonsoft.Json` if already in the project or a 40-line hand parser), resolve `{...}` references, strip the `px`/`ms` suffixes, write fields, `EditorUtility.SetDirty`, and regenerate `tokens.uss` in the same pass with `node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json -o Assets/UI/Theme/tokens.uss` (skill-relative path, run from the project root). Cubic-bezier easing → `AnimationCurve` by sampling 16 points on the bezier and `AnimationCurve(keys)` with smooth tangents; overshooting beziers (bouncy `exit`/`emphasized`) sample fine. Shadow strings → `ShadowSpec[]` (`x y blur color` per comma-separated layer; `inset` layers are flagged and skipped).

### Canvas Scaler (uGUI) and Panel Settings (UI Toolkit)

Portrait mobile: reference resolution **1080×1920**, `Scale With Screen Size`, `Screen Match Mode = Match Width Or Height`, `Match = 0` (width-locked: tall phones get more vertical space, tiles never shrink). Tablets: a second Canvas Scaler profile with `Match = 0.5` selected at startup by aspect ratio. Panel Settings mirror these: `Scale Mode = Scale With Screen Size`, same reference, `Match = 0`. Token `px` values are authored against this reference.

### Easing name table (USS enum, from token-derivation §1.11)

| motion class | `primitive.easing.standard` | `primitive.easing.enter` | `primitive.easing.exit` | `primitive.easing.emphasized` |
|---|---|---|---|---|
| `static` | `linear` | `linear` | `linear` | `linear` |
| `snappy` | `ease-out-cubic` | `ease-out` | `ease-in` | `ease-out-cubic` |
| `soft` | `ease-in-out` | `ease-out` | `ease-in` | `ease-in-out-sine` |
| `bouncy` | `ease-out-back` | `ease-out-back` | `ease-in-back` | `ease-in-out-back` |
| `dramatic` | `ease-out-circ` | `ease-out-circ` | `ease-in-circ` | `ease-in-out-circ` |

The sync script writes the chosen enum name as a comment next to each `--primitive-easing-*` line in `tokens.uss`; uGUI uses the exact `AnimationCurve`.

## 2. Token group → code mapping

| Group (CC-7) | uGUI | UI Toolkit (USS/UXML/C#) |
|---|---|---|
| `primitive.color.*` ramps | not referenced by prefabs; only via `semantic.color.*` / `component.*` | `--primitive-color-brand-500` exists in `tokens.uss` but components use semantic/component vars only |
| `semantic.color.*` | `Image.color = theme.ColorPrimary`; `TMP_Text.color = theme.ColorText`; `ColorBlock` on `Button` built from `component.button.primary.{bg,bgHover,bgPressed}` | `.btn--primary { background-color: var(--button-primary-bg); color: var(--button-primary-fg); }`; C#: `style.backgroundColor = theme.ColorPrimary` |
| `semantic.color.borderInteractive` | `theme.ColorBorderInteractive` tints the outline band of tile, icon-button, secondary-button and wallet-capsule (`component.hud.chipInteractive`) sprites; panels keep `ColorBorder` | `border-color: var(--color-borderInteractive)` on `.tile`, `.btn--icon`, `.btn--secondary`, `.hud-chip--interactive` (`var(--hud-chipInteractive-outlineColor)`) |
| `semantic.color.focusRing` / `semantic.state.focus.*` | `Selectable` navigation: a focus-frame `Image` (9-slice ring, width `StateFocusRingWidth`) tinted `theme.ColorFocusRing`, enabled in `OnSelect`/`OnDeselect` | `.btn:focus { border-color: var(--state-focus-ringColor); border-width: var(--state-focus-ringWidth); }` — `--state-focus-ringColor` = `--color-focusRing` |
| `primitive.spacing.*` / `semantic.spacing.*` | `LayoutGroup.padding`, `spacing`; `RectTransform.offsetMin/Max` set from `theme.Spacing4`; screen edges from `semantic.spacing.screenGutter` | `padding: var(--primitive-spacing-4)`; `margin-bottom: var(--spacing-stack)` |
| `primitive.radius.*` / `semantic.radius.*` | 9-slice sprite whose corner radius matches `RadiusControl` / `RadiusContainer` / `RadiusPopup` / `RadiusTile` at reference resolution; `Image.Type = Sliced`, `pixelsPerUnitMultiplier = 1` (bigger multiplier = smaller visual radius) | `border-radius: var(--radius-control)` (native, no sprite); `var(--radius-chip)` resolves `primitive.radius.full` = `9999px` |
| `primitive.outline.*` / `semantic.outline.control` | outline band baked into the 9-slice sprite at `OutlineControl` px, tinted per component `outlineColor` (`component.button.primary.outlineColor` = brand 700); the `Outline` component is a fallback for text only | `border-width: var(--button-primary-outlineWidth); border-color: var(--button-primary-outlineColor)` |
| `primitive.shadow.*` / `semantic.elevation.*` | `Shadow` component (`effectDistance`, `effectColor`) for the hard offset layer; baked sprite for the blurred layer | USS has no `box-shadow`; a second element with `translate` + `opacity`, or a 9-slice shadow sprite as `background-image` with `-unity-slice-*` |
| `semantic.typography.*` (`fontFamily`, `fontSize`, `lineHeight`, `fontWeight`) | `TMP_StyleSheet` styles `Display/Title/Body/Label/Caption` with `size`, font asset per `primitive.fontFamily.display` / `.body`; `TMP_Text.textStyle` — never `fontSize` on the component; `lineSpacing = (lineHeight − 1) × 100` | `font-size: var(--typography-body-fontSize)`; `-unity-font-definition` per family; USS classes `.text-display`, `.text-body` |
| `primitive.iconSize.*` | `LayoutElement.preferredWidth/Height = theme.IconSizeMd` on icon `Image` | `width: var(--primitive-iconSize-md); height: var(--primitive-iconSize-md)` |
| `primitive.touchTarget.*` | invisible `Image` (`raycastTarget = true`, alpha 0) sized to `TouchTargetMin` behind small buttons; `LayoutElement.minWidth/minHeight` | `min-width: var(--primitive-touchTarget-min); min-height: var(--primitive-touchTarget-min)` on `.btn` |
| `primitive.duration.*` | `theme.DurationBaseMs / 1000f` fed to coroutine/tween (section 3); `DurationRevealMs` for level-complete reveals (CC-8 `reward`/`ambient` keys when present) | `transition-duration: var(--primitive-duration-base)` (USS accepts `ms`; verify `var()` inside transitions on your version, else let the sync script inline `200ms`) |
| `primitive.easing.*` | `theme.EasingStandard.Evaluate(t)` in the tween | `transition-timing-function: ease-out-back` — enum per the name table above |
| `primitive.zIndex.*` | `Canvas.sortingOrder = ZIndexHud / ZIndexPopup / ZIndexToast` per layer canvas; never sibling-index hacks | hierarchy order; `BringToFront()` for popups/toasts; `position: absolute` layers in a root UXML ordered hud → overlay → popup → toast → tutorial |
| `primitive.opacity.*` | `CanvasGroup.alpha = theme.OpacityDisabled` (also disables raycasts in one place); scrim `OpacityScrim` | `opacity: var(--primitive-opacity-disabled)`; `.disabled { opacity: ...; }` |
| `semantic.state.*` | `Button.colors` (`ColorBlock`) from `StateHover/StatePressed/StateDisabled` + `fadeDuration = DurationFastMs / 1000f`; pressed offset = `semantic.state.pressed.offsetY` via `RectTransform.anchoredPosition` tween and the hard shadow layer hidden (`semantic.state.pressed.shadow` = none) | `:hover`, `:active`, `:focus`, `:disabled` pseudo-classes in USS, values from `--state-hover-opacity`, `--state-pressed-offsetY`, `--state-focus-ringWidth`, `--state-disabled-opacity` |
| `component.*` | one prefab per group: `Button_Base` ← `component.button.*`, `Panel_Base` ← `component.card.*`, `PopupHost` ← `component.popup.*`, `HudChip` ← `component.hud.chip.*`, `Tile` ← `component.tile.*`, `ProgressBar` ← `component.progress.*` | one UXML template + USS block per group reading `--button-primary-*`, `--card-*`, `--popup-*`, `--hud-chip-*`, `--tile-*`, `--progress-*` |

Rule: no literal colours, sizes or times in prefabs or C# outside `ThemeAsset`/`tokens.uss`. The `visual-audit` skill scans `.cs`, `.uss`, `.uxml`, and `.prefab`/`.unity` YAML (`m_Color`, `m_fontSize`, `m_Spacing`) for off-scale literals (Unity C#/USS coverage is fixture-only in this wave, CC-12).

## 3. Component reuse patterns

### button.primary / secondary / icon (uGUI)

```csharp
public enum ButtonVariant { Primary, Secondary, Icon }

[RequireComponent(typeof(Button), typeof(Image))]
public sealed class ThemedButton : MonoBehaviour
{
    [SerializeField] ThemeAsset theme; [SerializeField] ButtonVariant variant;
    [SerializeField] TMP_Text label; [SerializeField] Image icon; [SerializeField] LayoutElement layout;

    void OnEnable() => Apply();
    public void Apply()
    {
        var spec = variant switch { ButtonVariant.Primary => theme.ButtonPrimary, ButtonVariant.Secondary => theme.ButtonSecondary, _ => theme.ButtonIcon };
        var img = GetComponent<Image>(); var btn = GetComponent<Button>();
        img.type = Image.Type.Sliced; img.color = Color.white;        // sprite carries radius + outline band; ColorBlock tints it
        if (label) { label.color = spec.Fg; label.textStyle = theme.TextStyles.Body; }
        if (icon)  { icon.rectTransform.sizeDelta = Vector2.one * theme.ButtonIcon.IconSize; }
        layout.minWidth = spec.MinWidth; layout.minHeight = spec.Height;
        var c = btn.colors;
        c.normalColor = spec.Bg; c.highlightedColor = spec.BgHover; c.pressedColor = spec.BgPressed;
        c.disabledColor = spec.Bg * new Color(1, 1, 1, theme.StateDisabled.Opacity); c.fadeDuration = theme.DurationFastMs / 1000f;
        btn.colors = c;
    }
}
```

Pressed drop (`component.button.primary.pressedOffsetY`, hard shadow layer hidden) is added by one `PressOffset` component (timing helper below) on the same prefab; variants are prefab variants of a single `Button_Base.prefab`, never copies.

### button (UI Toolkit)

UXML template `Templates/AppButton.uxml` with `<ui:Button class="btn btn--primary" />`; USS:

```css
.btn { min-width: var(--primitive-touchTarget-min); min-height: var(--button-primary-height);
       border-radius: var(--button-primary-radius); border-width: var(--button-primary-outlineWidth);
       padding: 0 var(--button-primary-paddingX); font-size: var(--button-primary-fontSize);
       transition-property: translate, opacity; transition-duration: var(--primitive-duration-fast);
       transition-timing-function: ease-out-back; }                       /* primitive.easing.standard, bouncy */
.btn--primary   { background-color: var(--button-primary-bg);   color: var(--button-primary-fg);   border-color: var(--button-primary-outlineColor); }
.btn--secondary { background-color: var(--button-secondary-bg); color: var(--button-secondary-fg); border-color: var(--button-secondary-outlineColor); }
.btn--icon      { width: var(--button-icon-size); height: var(--button-icon-size); padding: 0; border-radius: var(--button-icon-radius); }
.btn--primary:hover  { background-color: var(--button-primary-bgHover); }
.btn--primary:active { background-color: var(--button-primary-bgPressed); translate: 0 var(--state-pressed-offsetY); }
.btn:focus      { border-color: var(--state-focus-ringColor); border-width: var(--state-focus-ringWidth); }
.btn:disabled   { opacity: var(--state-disabled-opacity); }
```

### card / panel

uGUI: `Panel_Base.prefab` = `Image` (9-slice `card.png` with the `component.card.borderWidth` band tinted `component.card.borderColor`, colour `component.card.bg`) + `Shadow` (`ElevationRaised[0]`) + `VerticalLayoutGroup` (padding `component.card.padding`, spacing `component.card.gap`). UI Toolkit: `.card { background-color: var(--card-bg); border-radius: var(--card-radius); border-width: var(--card-borderWidth); border-color: var(--card-borderColor); padding: var(--card-padding); }`, `.card--elevated { background-color: var(--color-surfaceElevated); }`.

### popup / dialog

One `PopupHost` per scene on the `ZIndexPopup` canvas (`component.popup.zIndex`): scrim `Image` (`component.popup.scrim`, `CanvasGroup`) + a panel child styled from `component.popup.*` (`bg`, `radius`, `padding`, `outlineWidth`/`outlineColor`, width capped at `maxWidth`). `Show(content)` tweens scrim alpha 0→1 over `component.popup.enterDuration` and panel scale 0.9→1 with `component.popup.enterEasing`; `Hide` uses `primitive.easing.exit` over `primitive.duration.fast`. UI Toolkit: a root `VisualElement.popup-layer` (`position: absolute; inset: 0`) toggled with `.is-open`, scale/opacity via USS transitions reading `--popup-enterDuration`.

### HUD chip

uGUI prefab: `HorizontalLayoutGroup` (padding `component.hud.chip.paddingX`, height `component.hud.chip.height`), 9-slice pill background (`component.hud.chip.bg`, outline band `component.hud.chip.outlineWidth` in `component.hud.chip.outlineColor`), icon `Image` sized `component.hud.chip.iconSize`, `TMP_Text` sized `component.hud.chip.fontSize` weight `component.hud.chip.fontWeight`. Its canvas has `sortingOrder = ZIndexHud` (`component.hud.chip.zIndex`). Value bumps call `PressOffset.Pulse()` (same component as buttons, no second tween implementation).

### tile

`SpriteRenderer` (world) or `Image` (canvas) for the art; the frame is a child `Image` with the 9-slice `tile_frame.png` (radius `component.tile.radius`, band `component.tile.outlineWidth`) tinted `component.tile.outlineColor`, switching to `component.tile.outlineColorSelected` + background `component.tile.bgSelected` when selected; smaller radius allowed only when the profile lists it under `intentional_exceptions`. Grid spacing `component.tile.gap`. Hit area: a `BoxCollider2D`/raycast `Image` of at least `component.tile.minSize`.

### progress bar

uGUI: `Image` background (`component.progress.track`, pill sprite with `component.progress.outlineWidth` band in `component.progress.outlineColor`, height `component.progress.height`) + filled `Image` (`Image.Type.Filled`, `fillMethod = Horizontal`, `component.progress.fill`, or `component.progress.fillReward` for reward meters); `SetFraction(f)` tweens `fillAmount` over `component.progress.fillDuration` with `component.progress.fillEasing`. UI Toolkit: `.bar { height: var(--progress-height); border-radius: var(--progress-radius); background-color: var(--progress-track); }` with a child whose `style.width = Length.Percent(f * 100)` set from C# and USS `transition-duration: var(--progress-fillDuration)`.

### toast

`ToastHost` on the `ZIndexToast` canvas, a queue of popup-styled panels (`component.popup.*`) + icon tinted by kind (`semantic.color.success/warning/danger/reward`); enters from below over `DurationBaseMs` with `EasingEnter`, exits over `DurationFastMs` with `EasingExit`. Lifetime is not a CC-7 token: `DurationRevealMs * 6` computed in `ToastHost` (a multiplier on a listed duration), the multiplier documented in `interaction-guidelines.md`.

### Timing helper (tween-library agnostic)

```csharp
public static class ThemeTween
{
    // Use with any tween lib (DOTween-style: tween.SetEase(theme.EasingStandard).SetDuration(ms / 1000f))
    // or this coroutine when no lib is present.
    public static IEnumerator Run(float durationMs, AnimationCurve ease, System.Action<float> apply)
    {
        float d = Mathf.Max(0.0001f, durationMs / 1000f), t = 0f;
        while (t < d) { t += Time.unscaledDeltaTime; apply(ease.Evaluate(Mathf.Clamp01(t / d))); yield return null; }
        apply(1f);
    }
}
// PressOffset: StartCoroutine(ThemeTween.Run(theme.DurationFastMs, theme.EasingStandard,
//     k => rect.anchoredPosition = Vector2.down * Mathf.Lerp(0f, theme.StatePressed.OffsetY, k)));
```

`Time.unscaledDeltaTime` so UI keeps animating while gameplay is paused.

## 4. Migration order when fixing drift

1. **Tokens**: run `UI/Sync Theme From tokens.json`; commit `Theme_Default.asset` + `tokens.uss`. Nothing visual changes yet where components already read the asset.
2. **TMP styles / 9-slice sprites**: regenerate `TextStyles.asset` sizes from `semantic.typography.*`; re-export button/card/chip/tile sprites at the new `semantic.radius.*` / `semantic.outline.control` (art task, but blocking).
3. **Shared prefabs / templates**: `Button_Base` → `Panel_Base` → `PopupHost`/`ToastHost` (contain panels and buttons) → `HudChip` → `ProgressBar` → `Tile` frame.
4. **Canvases**: set `sortingOrder` from `ZIndex*`; verify every scene has exactly one HUD / popup / toast canvas.
5. **Screens in dependency order**: Settings → Home → Shop → Gameplay HUD → Level-complete / reward popups (depend on everything).
6. Replace duplicated prefabs with prefab variants (`component.duplicate-implementation`), re-run the `visual-audit` skill scan (`audit.py scan`) and the screenshot suite after each step.

## 5. What not to touch

- Gameplay MonoBehaviours, `FixedUpdate` physics, board/match logic, level ScriptableObjects, economy/IAP, save data, analytics, addressables groups.
- Scene hierarchy of world objects; only UI canvases/`UIDocument`s are in scope.
- Input mappings; a bigger touch target is a UI change, a changed gesture is not.
- Build settings, quality settings, URP/HDRP pipeline assets (except a dedicated "QA screenshot" quality level, section 6).

## 6. Screenshot capture for QA

**Editor preview:** Device Simulator (`Window > General > Device Simulator`) with a saved device list; good for eyeballing safe areas, not for regression PNGs.

**Automated:** a PlayMode test that loads each screen and captures at end of frame:

```csharp
public class ScreenshotSuite
{
    static readonly (string name, int w, int h)[] Devices = { ("phone_small", 750, 1334), ("phone_tall", 1170, 2532), ("android", 1080, 2400), ("tablet", 1640, 2360) };
    [UnityTest] public IEnumerator Capture()
    {
        Random.InitState(42); Time.captureDeltaTime = 1f / 60f; QualitySettings.vSyncCount = 0;
        foreach (var d in Devices) {
            Screen.SetResolution(d.w, d.h, false); yield return null;           // standalone player only
            foreach (var screen in new[] { "Home", "Gameplay", "Shop" }) {
                yield return SceneManager.LoadSceneAsync(screen); yield return QaHooks.Settle(); // deterministic state hook
                for (int i = 0; i < 3; i++) yield return new WaitForEndOfFrame();
                ScreenCapture.CaptureScreenshot($"screenshots/{screen.ToLower()}_{d.name}.png"); yield return null;
            }
        }
    }
}
```

Run from CLI: `Unity -batchmode -projectPath . -runTests -testPlatform PlayMode -testResults results.xml` (PlayMode tests render in the editor player; `-nographics` would blank the capture, do not pass it). For true device pixels, build a Development player and run the same suite via a `-qa-screenshots` command-line flag. File names match the `visual_qa.py manifest` convention `<screen>_<device>.png` (`visual-audit` skill).

**Device matrix:** `phone_small` 750×1334, `phone_tall` 1170×2532, `android` 1080×2400, `tablet` 1640×2360 — portrait; add landscape only if the profile lists it.

**Determinism:** `Time.captureDeltaTime` (fixed frame step), `Random.InitState`, `QaHooks.Settle()` seeds the board and skips intro tweens; static TMP font atlases (dynamic atlases rasterize differently per run); disable post-processing grain/vignette/bloom with a `QA` quality level; fixed `Application.targetFrameRate`; locale fixed via your localization package; hide FPS counters/debug overlays (`ZIndexDebug` canvas) behind the same flag; `Screen.SetResolution` is ignored in the editor — editor runs use the Game view size you set in the test (`UnityEditor.GameViewSizeHelper`-style utility) or run the standalone player.

## 7. Performance notes

- One `ThemeAsset` referenced everywhere; never `Resources.Load` it per component — inject via serialized field or a static `Theme.Current`.
- uGUI: every colour/text change dirties the whole Canvas; keep HUD, popups and toasts on **separate canvases** (also needed for `primitive.zIndex.*`). Disable `raycastTarget` on decorative images.
- 9-slice sprites: set `Mesh Type = Full Rect`, pack into one atlas per theme; `pixelsPerUnitMultiplier` changes are free, sprite swaps are not.
- TMP: static atlases for the five text styles; avoid per-frame `SetText` with string concatenation (use `SetText(format, value)`).
- UI Toolkit: USS transitions run on the main thread but avoid layout thrash; animate `scale`/`opacity`/`translate`, not `width`/`height`/`padding`. Keep `var()` depth shallow (resolved at style resolution).
- `CanvasGroup.alpha` for disabled/muted states instead of recolouring every child.
- Tweens use `unscaledDeltaTime` and are pooled/cached; a popup open/close must not allocate.

## 8. Known limitations

- `tokens.uss` is the web generator's CSS: `box-shadow` strings and `cubic-bezier()` values are emitted as custom properties USS cannot consume. The sync script should drop or comment `--*-shadow`, `--elevation-*`, `--primitive-shadow-*` and `--primitive-easing-*` lines after generation; verify the USS importer does not warn on the rest for your Unity version.
- USS has no `line-height`; the `lineHeight` leaves (`semantic.typography.body.lineHeight` and siblings) map to approximations (TMP handles it in uGUI via `lineSpacing`).
- USS easing is an enum; cubic-bezier tokens are approximated per the name table and recorded in `tokens.uss` comments. uGUI gets the exact curve via `AnimationCurve`.
- Shadows with blur need baked sprites in both systems; the blurred layer of `primitive.shadow.*` / double-clay component shadows is advisory. `primitive.shadow.inset` has no equivalent.
- The canonical example tokens.json carries `primitive.duration.{instant,fast,base,slow,reveal}`; CC-8 `reward`/`ambient` fields are generated only when present.
- Unity's `JsonUtility` cannot parse `$value`/`$type` keys; the sync script needs a small custom parser or Newtonsoft.
- `Screen.SetResolution` is a no-op in the editor; editor screenshot runs need a Game-view-size helper or a standalone player.
- UI Toolkit runtime has no world-space UI (verify on your Unity version); world-anchored elements stay on uGUI.
- The decision rule assumes Unity 2022 LTS or newer; older projects use uGUI only.
