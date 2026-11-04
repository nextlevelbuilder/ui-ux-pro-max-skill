# Platform adapter: Mobile native (SwiftUI and Jetpack Compose)

Maps `design-system/<slug>/tokens.json` (contract §4.2, leaf names per CC-7) to SwiftUI and Jetpack Compose. Both stacks already have guidance in `ui-ux-pro-max` (`search.py --stack swiftui`, `--stack jetpack-compose`); this file adds only the token plumbing, shared components, migration order and screenshot QA. Stack ids: `swiftui`, `jetpack-compose`. `$extensions.vdp.platformUnit`: `pt` for SwiftUI (`"16pt"`), `dp` for Compose (`"16dp"`); the generator strips the suffix. Numeric values are shared because both are density-independent (1 pt ≈ 1 dp for layout; text uses `sp` on Android, see mapping). Durations are `"<n>ms"`, easings `cubic-bezier(...)`, shadows `box-shadow` strings.

## 1. Where tokens live

### SwiftUI

```
Sources/Design/
├── Assets.xcassets/Colors/        # one Color Set per semantic.color.* slot, Any/Dark appearances: color/primary, color/onPrimary ...
├── Tokens.swift                   # GENERATED numeric groups (spacing, radius, outline, shadow, typography, ..., state, component)
├── Theme.swift                    # EnvironmentKey + `.theme` accessor; wraps Tokens + Colors
├── Modifiers/                     # ViewModifiers / ButtonStyles (section 3)
└── Components/                    # AppButton, AppCard, AppDialog, HudChip, Tile, AppProgressBar, AppToast
```

Naming: `Tokens.Spacing.s4`, `Tokens.Radius.control`, `Tokens.Duration.base`, `Tokens.Button.primary.height` (static lets, `lowerCamelCase`; leading digits get an `s` prefix for spacing, `primitive.radius.2xl` → `Radius.xl2`). Colours are asset-catalog colours (`Color("color/primary")`) so dark mode and high-contrast are handled by the system; a generated `AppColors` struct exposes them typed.

```swift
// Tokens.swift (GENERATED from tokens.json — do not edit)
enum Tokens {
    enum Spacing { static let s1: CGFloat = 4, s2: CGFloat = 8, s3: CGFloat = 12, s4: CGFloat = 16, s6: CGFloat = 24 }   // primitive.spacing.*
    enum Radius { static let control: CGFloat = 16, container: CGFloat = 24, popup: CGFloat = 32, tile: CGFloat = 12, chip: CGFloat = 9999 } // semantic.radius.*
    enum Outline { static let control: CGFloat = 3 }                                                                        // semantic.outline.control
    enum Elevation { static let raised = [ShadowLayer(y: 2, blur: 0, opacity: 0.25), ShadowLayer(y: 4, blur: 6, opacity: 0.12)] } // semantic.elevation.* (layers)
    enum Typography { static let body = TextSpec(family: "Nunito", size: 16, lineHeight: 1.5, weight: .medium) }           // semantic.typography.*
    enum IconSize { static let sm: CGFloat = 20, md: CGFloat = 28, lg: CGFloat = 40, xl: CGFloat = 64 }
    enum TouchTarget { static let min: CGFloat = 48, recommended: CGFloat = 48 }
    enum Duration { static let fast: Double = 0.12, base: Double = 0.20, slow: Double = 0.35, reveal: Double = 0.60 }     // seconds
    enum Easing { static let standard = UnitCurve.bezier(startControlPoint: .init(x: 0.34, y: 1.56), endControlPoint: .init(x: 0.64, y: 1))
                  static let exit = UnitCurve.bezier(startControlPoint: .init(x: 0.36, y: 0), endControlPoint: .init(x: 0.66, y: -0.56)) }
    enum ZIndex { static let hud: Double = 100, overlay: Double = 200, popup: Double = 300, toast: Double = 400 }
    enum Opacity { static let disabled = 0.4, hover = 0.92, pressed = 0.85, scrim = 0.5, muted = 0.7 }
    enum State { static let pressed = StateRule(opacity: 0.85, offsetY: 4), disabled = StateRule(opacity: 0.4, offsetY: 0) }
    enum Button { static let primary = ButtonSpec(height: 56, minWidth: 160, paddingX: 24, fontSize: 22, radius: 16, outlineWidth: 3, pressedOffsetY: 4) }
}
struct ShadowLayer { let y: CGFloat; let blur: CGFloat; let opacity: Double }
struct StateRule { let opacity: Double; let offsetY: CGFloat }
```

Generation rule: resolve references; `semantic.color.*` and colour-typed `component.*` leaves → asset catalog entries (`Contents.json` with `appearances: luminosity dark` when `dark.semantic.color` exists); `duration` ms → seconds; `cubicBezier` → `UnitCurve.bezier` (overshoot allowed); `shadow` strings → `[ShadowLayer]` (one per comma-separated layer, `inset` skipped); everything else numeric → `CGFloat`/`Double`. `Theme.swift` adds `extension EnvironmentValues { var theme: Theme }` so previews can inject an alternate theme without touching `Tokens`.

### Jetpack Compose

```
app/src/main/java/<pkg>/design/
├── AppTokens.kt        # GENERATED: Immutable data classes per group + default instances
├── AppTheme.kt         # MaterialTheme(colorScheme = tokensToColorScheme(...)) + CompositionLocalProvider(LocalTokens)
├── Type.kt             # Typography from semantic.typography.* roles
└── components/         # AppButton, AppCard, AppDialog, HudChip, Tile, AppProgressBar, AppToast
```

```kotlin
// AppTokens.kt (GENERATED from tokens.json — do not edit)
@Immutable data class AppColors(val primary: Color, val onPrimary: Color, val primaryHover: Color, val primaryPressed: Color,
    val secondary: Color, val onSecondary: Color, val accent: Color, val onAccent: Color, val background: Color, val surface: Color,
    val surfaceElevated: Color, val border: Color, val borderInteractive: Color, val overlay: Color, val text: Color, val textMuted: Color,
    val success: Color, val warning: Color, val danger: Color, val reward: Color, val focusRing: Color)   // semantic.color.*
@Immutable data class AppSpacing(val s1: Dp = 4.dp, val s2: Dp = 8.dp, val s3: Dp = 12.dp, val s4: Dp = 16.dp, val s6: Dp = 24.dp)
@Immutable data class AppRadius(val control: Dp = 16.dp, val container: Dp = 24.dp, val popup: Dp = 32.dp, val tile: Dp = 12.dp, val chip: Dp = 9999.dp) // semantic.radius.*
@Immutable data class AppOutline(val control: Dp = 3.dp); @Immutable data class AppElevation(val raised: Dp = 2.dp, val elevated: Dp = 4.dp, val floating: Dp = 6.dp) // y-offset of layer 1
@Immutable data class TextSpec(val family: FontFamily, val size: TextUnit, val lineHeight: Float, val weight: FontWeight)
@Immutable data class AppTypography(val display: TextSpec, val title: TextSpec, val body: TextSpec, val label: TextSpec, val caption: TextSpec)
@Immutable data class AppIconSize(val sm: Dp = 20.dp, val md: Dp = 28.dp, val lg: Dp = 40.dp, val xl: Dp = 64.dp)
@Immutable data class AppTouchTarget(val min: Dp = 48.dp, val recommended: Dp = 48.dp)
@Immutable data class AppDuration(val fast: Int = 120, val base: Int = 200, val slow: Int = 350, val reveal: Int = 600)  // ms
@Immutable data class AppEasing(val standard: Easing = CubicBezierEasing(0.34f, 1.56f, 0.64f, 1f), val enter: Easing = CubicBezierEasing(0.34f, 1.56f, 0.64f, 1f),
    val exit: Easing = CubicBezierEasing(0.36f, 0f, 0.66f, -0.56f), val emphasized: Easing = CubicBezierEasing(0.68f, -0.6f, 0.32f, 1.6f))
@Immutable data class AppZIndex(val hud: Float = 100f, val overlay: Float = 200f, val popup: Float = 300f, val toast: Float = 400f)
@Immutable data class AppOpacity(val disabled: Float = 0.4f, val hover: Float = 0.92f, val pressed: Float = 0.85f, val scrim: Float = 0.5f, val muted: Float = 0.7f)
@Immutable data class StateRule(val opacity: Float, val offsetY: Dp)
@Immutable data class AppState(val hover: StateRule, val pressed: StateRule, val focusRingWidth: Dp, val disabled: StateRule)
@Immutable data class ButtonSpec(val bg: Color, val fg: Color, val bgHover: Color, val bgPressed: Color, val outlineWidth: Dp, val outlineColor: Color,
    val radius: Dp, val height: Dp, val minWidth: Dp, val paddingX: Dp, val fontSize: TextUnit, val fontWeight: FontWeight, val pressedOffsetY: Dp)
@Immutable data class AppTokens(val color: AppColors, val spacing: AppSpacing, val radius: AppRadius, val outline: AppOutline, val elevation: AppElevation,
    val typography: AppTypography, val iconSize: AppIconSize, val touchTarget: AppTouchTarget, val duration: AppDuration, val easing: AppEasing,
    val zIndex: AppZIndex, val opacity: AppOpacity, val state: AppState, val button: Map<String, ButtonSpec> /* card, popup, hud, tile, progress likewise */)
val LocalTokens = staticCompositionLocalOf<AppTokens> { error("Wrap in AppTheme") }
```

`AppTheme.kt`: `MaterialTheme(colorScheme = lightColorScheme(primary = t.color.primary, onPrimary = t.color.onPrimary, surface = t.color.surface, error = t.color.danger, ...), typography = appTypography(t.typography)) { CompositionLocalProvider(LocalTokens provides t, content = content) }`; `object Theme { val tokens: AppTokens @Composable get() = LocalTokens.current }`. Dark: a second `AppTokens` instance from `dark.semantic`, chosen by `isSystemInDarkTheme()`.

Easing: `UnitCurve.bezier` and `CubicBezierEasing` both accept overshooting control points, so every `primitive.easing.*` bezier is used exactly; for a genuinely physical feel on `bouncy` profiles, `.spring(response: 0.35, dampingFraction: 0.6)` / `spring(dampingRatio = 0.6f, stiffness = Spring.StiffnessMedium)` may replace `enter` on the popup only — declare it under `intentional_exceptions`.

## 2. Token group → code mapping

| Group (CC-7) | SwiftUI | Jetpack Compose |
|---|---|---|
| `primitive.color.*` ramps | never referenced in views; only via `semantic.color.*` / `component.*` | same |
| `semantic.color.*` | `Color("color/primary")` via `theme.colors.primary`; `.foregroundStyle`, `.background`, `.tint` | `Theme.tokens.color.primary`; `MaterialTheme.colorScheme.primary` for Material components |
| `semantic.color.borderInteractive` | `theme.colors.borderInteractive` for `.stroke(...)` on tiles, icon buttons, the secondary button and tappable HUD capsules (`component.hud.chipInteractive`); cards keep `theme.colors.border` | `Theme.tokens.color.borderInteractive` in `BorderStroke(width, color)` for the same components |
| `semantic.color.focusRing` / `semantic.state.focus.*` | `.focusEffectDisabled()` + `.overlay(RoundedRectangle(cornerRadius:).stroke(theme.colors.focusRing, lineWidth: Tokens.State.focusRingWidth).padding(-Tokens.State.focusRingOffset))` when `@FocusState` is true | `Modifier.onFocusChanged { focused = it.isFocused }` + `.border(t.state.focusRingWidth, if (focused) t.color.focusRing else Color.Transparent, shape)` |
| `primitive.spacing.*` / `semantic.spacing.*` | `.padding(Tokens.Spacing.s4)`, `VStack(spacing: Tokens.Spacing.s3)` (`semantic.spacing.stack`), screen edges `semantic.spacing.screenGutter` | `Modifier.padding(t.spacing.s4)`, `Arrangement.spacedBy(t.spacing.s3)` |
| `primitive.radius.*` / `semantic.radius.*` | `.clipShape(.rect(cornerRadius: Tokens.Radius.control))`; `Capsule()` when the role resolves to `primitive.radius.full` | `RoundedCornerShape(t.radius.control)`; `CircleShape` / `RoundedCornerShape(50)` for `full` |
| `primitive.outline.*` / `semantic.outline.control` | `.overlay(RoundedRectangle(cornerRadius:).stroke(outlineColor, lineWidth: Tokens.Outline.control))`; colour per component (`component.button.primary.outlineColor`) | `Modifier.border(t.outline.control, outlineColor, shape)` |
| `primitive.shadow.*` / `semantic.elevation.*` | one `.shadow(color: .black.opacity(l.opacity), radius: l.blur / 2, y: l.y)` per layer (two layers for double-clay) | `Modifier.shadow(t.elevation.raised, shape, ambientColor = t.color.overlay)` — single layer, approximate |
| `semantic.typography.*` | `.font(.custom(spec.family, size: spec.size).weight(spec.weight))` + `.lineSpacing(spec.size * (spec.lineHeight − 1))`; roles → `Font` extension `AppFont.display/title/body/label/caption` | `TextStyle(fontFamily, fontSize = spec.size, lineHeight = spec.size * spec.lineHeight, fontWeight)` in `Typography` (`display`→`displayLarge`, `title`→`titleLarge`, `body`→`bodyMedium`, `label`→`labelLarge`, `caption`→`bodySmall`) |
| `primitive.iconSize.*` | `Image(systemName:).resizable().frame(width: Tokens.IconSize.md, height: Tokens.IconSize.md)` | `Icon(..., modifier = Modifier.size(t.iconSize.md))` |
| `primitive.touchTarget.*` | `.frame(minWidth: Tokens.TouchTarget.min, minHeight: Tokens.TouchTarget.min).contentShape(Rectangle())` | `Modifier.sizeIn(minWidth = t.touchTarget.min, minHeight = t.touchTarget.min)`; Material's `minimumInteractiveComponentSize()` enforces 48dp |
| `primitive.duration.*` | `.animation(.timingCurve(..., duration: Tokens.Duration.base), value:)`; `reveal` for level-complete reveals (CC-8 `reward`/`ambient` when present) | `tween(durationMillis = t.duration.base)`, `animateFloatAsState(animationSpec = tween(...))` |
| `primitive.easing.*` | `Animation.timingCurve(x1, y1, x2, y2, duration:)` from the same bezier; `enter` on appear, `exit` on dismiss, `emphasized` for reward moments | `tween(easing = t.easing.enter)` / `t.easing.exit` |
| `primitive.zIndex.*` | `.zIndex(Tokens.ZIndex.popup)` inside `ZStack`; overlays via `.overlay`/`.fullScreenCover` | `Modifier.zIndex(t.zIndex.popup)` inside `Box`; `Popup`/`Dialog` composables for true windows |
| `primitive.opacity.*` | `.opacity(Tokens.Opacity.disabled)`; scrim `Tokens.Opacity.scrim` (already folded into `semantic.color.overlay`) | `Modifier.alpha(t.opacity.disabled)` |
| `semantic.state.*` | `ButtonStyle.makeBody(configuration:)` reads `configuration.isPressed` → `.offset(y: Tokens.State.pressed.offsetY)` + pressed colour; `@Environment(\.isEnabled)` → `Tokens.State.disabled.opacity`; `.focusable()` + `.focused` → ring of `semantic.state.focus.ringWidth` in `semantic.state.focus.ringColor` | `interactionSource.collectIsPressedAsState()` → `Modifier.offset(y = t.state.pressed.offsetY)`; `enabled = false` → `alpha(t.state.disabled.opacity)`; `Modifier.focusable()` + `isFocused` → border `t.state.focusRingWidth` in `t.color.focusRing` |
| `component.*` | `Tokens.Button.primary/secondary/icon`, `Tokens.Card`, `Tokens.Popup`, `Tokens.HudChip`, `Tokens.Tile`, `Tokens.Progress` consumed by exactly one view each | `t.button["primary"]`, `t.card`, `t.popup`, `t.hud.chip`, `t.tile`, `t.progress` consumed by exactly one composable each |

Rule: no `Color(red:green:blue:)`, `Color(0xFF...)`, `.padding(12)`, `.dp` literals or `durationMillis = 337` outside the generated token files. The `visual-audit` skill scans `.swift` and `.kt` for those patterns (Swift/Kotlin patterns are fixture-only in this wave, CC-12).

## 3. Component reuse patterns

### button.primary / secondary / icon

SwiftUI — one `ButtonStyle`, variants by enum, every value from `component.button.*`:

```swift
enum AppButtonVariant { case primary, secondary, icon }

struct AppButtonStyle: ButtonStyle {
    @Environment(\.theme) private var theme
    @Environment(\.isEnabled) private var isEnabled
    let variant: AppButtonVariant
    func makeBody(configuration: Configuration) -> some View {
        let b = variant == .primary ? Tokens.Button.primary : Tokens.Button.secondary       // icon uses Tokens.Button.icon sizing
        let bg = configuration.isPressed ? theme.colors.button(variant, .bgPressed) : theme.colors.button(variant, .bg)
        configuration.label
            .font(.custom(Tokens.Typography.label.family, size: b.fontSize).weight(.bold))
            .padding(.horizontal, variant == .icon ? 0 : b.paddingX)
            .frame(minWidth: variant == .icon ? Tokens.TouchTarget.recommended : b.minWidth, minHeight: b.height)
            .background(bg, in: RoundedRectangle(cornerRadius: b.radius))
            .overlay(RoundedRectangle(cornerRadius: b.radius).stroke(theme.colors.button(variant, .outlineColor), lineWidth: b.outlineWidth))
            .foregroundStyle(theme.colors.button(variant, .fg))
            .appShadow(configuration.isPressed ? [] : Tokens.Button.primaryShadow)              // layers; pressed collapses the hard layer
            .offset(y: configuration.isPressed ? b.pressedOffsetY : 0)
            .opacity(isEnabled ? 1 : Tokens.State.disabled.opacity)
            .animation(.timingCurve(0.34, 1.56, 0.64, 1, duration: Tokens.Duration.fast), value: configuration.isPressed)
    }
}
// Button("Play") { }.buttonStyle(AppButtonStyle(variant: .primary))
```

Compose:

```kotlin
enum class AppButtonVariant { Primary, Secondary, Icon }

@Composable
fun AppButton(onClick: () -> Unit, variant: AppButtonVariant = AppButtonVariant.Primary, enabled: Boolean = true,
              modifier: Modifier = Modifier, content: @Composable RowScope.() -> Unit) {
    val t = Theme.tokens
    val b = t.button[if (variant == AppButtonVariant.Secondary) "secondary" else "primary"]!!   // component.button.*
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val offset by animateDpAsState(if (pressed) b.pressedOffsetY else 0.dp, tween(t.duration.fast, easing = t.easing.standard), label = "press")
    Button(onClick = onClick, enabled = enabled, interactionSource = interaction, shape = RoundedCornerShape(b.radius),
        colors = ButtonDefaults.buttonColors(containerColor = if (pressed) b.bgPressed else b.bg, contentColor = b.fg,
            disabledContainerColor = b.bg.copy(alpha = t.state.disabled.opacity)),
        border = BorderStroke(b.outlineWidth, b.outlineColor),
        elevation = ButtonDefaults.buttonElevation(defaultElevation = t.elevation.elevated, pressedElevation = 0.dp),
        contentPadding = if (variant == AppButtonVariant.Icon) PaddingValues(0.dp) else PaddingValues(horizontal = b.paddingX),
        modifier = modifier.offset(y = offset).sizeIn(minWidth = if (variant == AppButtonVariant.Icon) t.touchTarget.recommended else b.minWidth, minHeight = b.height),
        content = content)
}
```

### card / panel
SwiftUI: `struct AppCard<Content: View>: View` applying `.padding(Tokens.Card.padding).background(elevated ? colors.surfaceElevated : colors.card.bg, in: .rect(cornerRadius: Tokens.Card.radius)).overlay(stroke Tokens.Card.borderWidth in colors.card.borderColor).appShadow(elevated ? Tokens.Elevation.elevated : Tokens.Elevation.raised)`; `VStack(spacing: Tokens.Card.gap)` inside. Compose: `@Composable fun AppCard(elevated: Boolean = false, content)` = `Surface(shape = RoundedCornerShape(t.card.radius), color = if (elevated) t.color.surfaceElevated else t.card.bg, border = BorderStroke(t.card.borderWidth, t.card.borderColor), shadowElevation = if (elevated) t.elevation.elevated else t.elevation.raised) { Column(Modifier.padding(t.card.padding), verticalArrangement = Arrangement.spacedBy(t.card.gap)) { content() } }`.

### popup / dialog
SwiftUI: a `.appDialog(isPresented:)` ViewModifier that overlays `colors.popup.scrim` + a panel styled from `component.popup.*` (`bg`, `radius`, `padding`, `outlineWidth`/`outlineColor`, `maxWidth`) in a `ZStack` at `Tokens.ZIndex.popup`, transition `.scale(scale: 0.9).combined(with: .opacity)` with `.animation(.timingCurve(enter bezier, duration: Tokens.Popup.enterDuration))`. Compose: `Dialog(onDismissRequest, properties = DialogProperties(usePlatformDefaultWidth = false)) { ... }` with `AnimatedVisibility(enter = scaleIn(tween(t.popup.enterDuration, easing = t.popup.enterEasing)) + fadeIn(), exit = scaleOut(tween(t.duration.fast, easing = t.easing.exit)) + fadeOut())`; scrim colour `t.popup.scrim`, width capped at `t.popup.maxWidth`.

### HUD chip
Capsule row from `component.hud.chip.*`: height `height`, icon `iconSize`, text `fontSize`/`fontWeight`, padding `paddingX`, background `bg`, stroke `outlineWidth` in `outlineColor`, shadow layers from `shadow`, `zIndex` → `.zIndex(Tokens.ZIndex.hud)` / `Modifier.zIndex(t.zIndex.hud)`. Bump: SwiftUI `.scaleEffect(bump ? 1.08 : 1).animation(.timingCurve(enter bezier, duration: Tokens.Duration.fast), value: bump)`; Compose `animateFloatAsState` + `Modifier.graphicsLayer { scaleX = s; scaleY = s }`. The chip (36) is shorter than `primitive.touchTarget.min`; if it becomes tappable, enlarge the hit area, not the visual.

### tile
Square (`aspectRatio(1)`), `component.tile.radius` (profile may lower it for `gameplay-hud`), stroke `component.tile.outlineWidth` in `component.tile.outlineColor` → `component.tile.outlineColorSelected` and background `component.tile.bg` → `component.tile.bgSelected` when selected, `component.tile.minSize` minimum, grid gap `component.tile.gap`, selection scale 1.06 over `Duration.fast` with `enter`, clear = opacity to 0 over `Duration.base` with `exit`. SwiftUI uses `.contentShape(Rectangle())` so the whole hit area counts; Compose uses `Modifier.clickable(interactionSource, indication = null)` to suppress the Material ripple when the profile forbids it.

### progress bar
SwiftUI: `GeometryReader` + `Capsule().fill(colors.progress.track)` under `Capsule().fill(reward ? colors.progress.fillReward : colors.progress.fill).frame(width: geo.size.width * value)` with `.overlay(Capsule().stroke(colors.progress.outlineColor, lineWidth: Tokens.Progress.outlineWidth))`, height `Tokens.Progress.height`, `.animation(.timingCurve(standard bezier, duration: Tokens.Progress.fillDuration), value: value)`. Compose: `LinearProgressIndicator(progress = { animated }, color = t.progress.fill, trackColor = t.progress.track, strokeCap = StrokeCap.Round, modifier = Modifier.height(t.progress.height).border(t.progress.outlineWidth, t.progress.outlineColor, CircleShape))` with `animateFloatAsState(value, tween(t.progress.fillDuration, easing = t.progress.fillEasing))`.

### toast
SwiftUI: `.appToast(item:)` modifier rendering a popup-styled panel (`component.popup.*`) at `Tokens.ZIndex.toast`, bottom inset `Tokens.Spacing.s4` (`semantic.spacing.inset`), icon tinted by kind (`semantic.color.success/warning/danger/reward`). Compose: `SnackbarHost` with a custom `Snackbar` composable using the same panel, `zIndex(t.zIndex.toast)`. Lifetime is not a CC-7 token: `Tokens.Duration.reveal * 6` / `t.duration.reveal * 6` computed in the toast component (a multiplier on a listed duration), the multiplier documented in `interaction-guidelines.md`.

## 4. Migration order when fixing drift

1. **Tokens**: regenerate `Tokens.swift` / asset catalog colours, `AppTokens.kt`. Build — compile errors enumerate renamed tokens.
2. **Theme wiring**: `Theme.swift` environment + `AppTheme.kt` (`MaterialTheme` colour scheme, `Typography` from `semantic.typography.*`). Material defaults then flip for free.
3. **Shared components** in order: `AppButtonStyle`/`AppButton` → `AppCard` → `AppDialog`, `AppToast` (embed card/button) → `HudChip` → `AppProgressBar` → `Tile`.
4. **Screens** leaf-first: Settings → Home → Shop → Gameplay (HUD + dialogs) → Reward/level-complete flows.
5. Replace bespoke `Button { }.padding(12).background(Color(hex:))` and `Button(colors = ButtonDefaults.buttonColors(Color(0xFF...)))` with the shared components; re-run the `visual-audit` skill scan (`audit.py scan`) and snapshot tests after each step.

## 5. What not to touch

- ViewModels / `ObservableObject` / `StateFlow`, repositories, networking, persistence (SwiftData/Room), in-app purchase, analytics, game logic.
- Navigation graphs (`NavigationStack` paths, `NavHost` routes) — only the screens' visual layer.
- Accessibility labels and traits already present; the token pass may add focus visuals, never remove labels.
- Xcode/Gradle build settings, signing, flavors; only new source files under `Design/` are added.

## 6. Screenshot capture for QA

**iOS:** XCUITest per device in a test plan:

```swift
final class ScreenshotSuite: XCTestCase {
    func testScreens() {
        let app = XCUIApplication(); app.launchArguments += ["-qa", "-seed", "42", "-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryL"]
        app.launch()
        for screen in ["home", "gameplay", "shop"] {
            app.buttons["nav_\(screen)"].tap(); _ = app.otherElements["screen_\(screen)"].waitForExistence(timeout: 5)
            let shot = XCTAttachment(screenshot: app.screenshot()); shot.name = "\(screen)_phone_small"; shot.lifetime = .keepAlways; add(shot)
        }
    }
}
```

Run: `xcodebuild test -scheme App -testPlan Screenshots -destination 'platform=iOS Simulator,name=iPhone SE (3rd generation)' -resultBundlePath qa/ios.xcresult`, then `xcrun xcresulttool export attachments --path qa/ios.xcresult --output-path qa/screens/ios`. Alternative for ad-hoc captures: `xcrun simctl io booted screenshot qa/screens/home_phone_small.png`. Status bar: `xcrun simctl status_bar booted override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4`. Third-party snapshot libraries (view-level, not UI-test-level) are optional; the contract only needs PNGs.

**Android:** Compose Preview Screenshot Testing (official Gradle plugin `com.android.compose.screenshot`): annotate `@Preview` composables in `src/screenshotTest/`, then `./gradlew updateDebugScreenshotTest` (baseline) and `./gradlew validateDebugScreenshotTest` (compare, HTML report). For full-device captures: `adb shell settings put global animator_duration_scale 0` (also `transition_animation_scale`, `window_animation_scale`), `adb shell settings put global sysui_demo_allowed 1` + `adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941`, launch with `-e qa 1 -e seed 42`, `adb exec-out screencap -p > qa/screens/home_android.png`.

**Device matrix** (names follow the `visual_qa.py manifest` convention `<screen>_<device>.png`, `visual-audit` skill): `phone_small` iPhone SE (3rd gen) 375×667 @2, `phone_tall` iPhone 15 393×852 @3, `tablet` iPad (10th gen) 820×1180 @2; `android` Pixel 7 412×915 @2.625, `android_small` 360×800 @2, `android_tablet` 800×1280 @2. Portrait; add Dynamic Type `XL` / font scale 1.3 as one extra row for text-overflow checks.

**Determinism:** fixed seed + `-qa` flag skipping intros; `UIView.setAnimationsEnabled(false)` / `animator_duration_scale 0`; fixed content size category / font scale; locale `en_US`, timezone `UTC`; bundled fonts only (`primitive.fontFamily.display` / `primitive.fontFamily.body` in the app bundle); status-bar overrides above; same simulator/emulator OS image pinned in CI; Compose previews use `LocalInspectionMode` to swap live data for fixtures; disable GPU-dependent blur (`.ultraThinMaterial`) behind the QA flag since it renders differently per device.

## 7. Performance notes

- SwiftUI: `Tokens` are static lets (no allocation); keep `Theme` in the environment, not in `@State`. Avoid `.shadow` on hundreds of tiles — the double-clay `component.tile.shadow` is two layers per tile; pre-render into an `Image` or use one shadow on the board container. Use `.drawingGroup()` for complex HUD layers; `.animation(_:value:)` scoped to the value, never the implicit form on the root.
- Compose: all token classes are `@Immutable` so `AppButton` skips recomposition when tokens are unchanged; `staticCompositionLocalOf` because tokens change rarely (a swap recomposes everything, which is intended). `Modifier.shadow` is a separate render node — share one per card, not per child. Use `graphicsLayer { scaleX = ... }` for press/bump animations to avoid relayout. `LazyVerticalGrid` with stable keys for boards; `derivedStateOf` for progress fractions.
- Both: duration/easing read once per animation spec; never rebuild `tween()`/`Animation` objects inside hot loops.

## 8. Known limitations

- No generator script ships for `Tokens.swift` / asset catalog / `AppTokens.kt` in this wave; the rules in section 1 are hand-applied.
- The canonical example tokens.json carries `primitive.duration.{instant,fast,base,slow,reveal}`; CC-8 `reward`/`ambient` fields are generated only when present.
- SwiftUI stacks two `.shadow` modifiers for double-clay tokens; Compose `Modifier.shadow` is single-layer elevation, not a blur radius — the second layer and `primitive.shadow.inset` are approximated or baked into an asset.
- Compose text uses `sp`; if the profile disables font scaling for HUD text, use `TextUnit` with `fontScale`-independent values via `LocalDensity` — note it as an `intentional_exception`.
- `primitive.zIndex.*` works inside a `ZStack`/`Box` only; `Dialog`/`fullScreenCover` create separate windows that ignore it.
- `semantic.state.hover` has no native equivalent on touch; pointer hover (iPadOS trackpad, ChromeOS) uses `.hoverEffect` / `hoverable()` as a best effort.
- `primitive.touchTarget.min` is the maximum across the profile's platforms (48 when Android is listed), so iOS-only views get a 44 pt minimum only if the profile lists `mobile-ios` alone.
- Compose Preview Screenshot Testing is still marked experimental in the Android Gradle plugin; API names may shift between AGP releases.
