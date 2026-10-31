# Platform adapter: Flutter + Flame

Maps `design-system/<slug>/tokens.json` (contract §4.2, leaf names per CC-7) to a Flutter app shell and a Flame game layer. Builds on the stack guidance already shipped in `ui-ux-pro-max` (`search.py --stack flutter`: const constructors, small widgets, `SizedBox` spacing, `LayoutBuilder`); this document only adds what tokens and HUDs need.

Stack ids this file serves: `flutter`, `flutter-flame` (profile `product.stack`). `$extensions.vdp.platformUnit` is `logical`, so every dimension `$value` is a bare number string (`"16"`) and is read 1:1 as Flutter logical pixels. Duration values are `"<n>ms"` strings; easing values are `cubic-bezier(x1, y1, x2, y2)` strings; shadow values are CSS `box-shadow` strings (one or more comma-separated layers).

## 1. Where tokens live

```
lib/design/
├── app_tokens.dart          # GENERATED from tokens.json — never edited by hand
├── app_theme.dart           # ThemeData + ThemeExtension wiring (hand-written, thin)
└── components/              # shared widgets that read tokens (section 3)
    ├── app_button.dart
    ├── app_card.dart
    ├── app_dialog.dart
    ├── app_toast.dart
    └── app_progress_bar.dart
lib/game/hud/                # Flame HUD components, read AppTokens directly (no BuildContext)
```

Naming: one Dart class per token group; token path → `lowerCamelCase` field with dots removed. Keys that start with a digit get an `s` prefix for spacing (`primitive.spacing.4` → `spacing.s4`) and are rewritten for radius (`primitive.radius.2xl` → `radius.xl2`, `primitive.radius.3xl` → `radius.xl3`). Semantic and component names are kept verbatim (`semantic.color.surfaceElevated` → `color.surfaceElevated`, `component.hud.chip.paddingX` → `hud.chip.paddingX`).

### Generation rule (tokens.json → app_tokens.dart)

1. Resolve every `{…}` reference (into `primitive` or `semantic` leaves) first (same resolution as `../design-system/scripts/generate-tokens.cjs`), so the generated Dart contains literals only.
2. Emit `const` classes per primitive group — `AppColors`, `AppSpacing`, `AppRadius`, `AppOutline`, `AppShadow`, `AppFontSize`, `AppLineHeight`, `AppIconSize`, `AppTouchTarget`, `AppDuration`, `AppEasing`, `AppZIndex`, `AppOpacity`, `AppFontFamily` — plus `AppSemantic` (color, radius, outline, elevation, state, typography, spacing) and `AppComponent` (button, card, popup, hud, tile, progress), and `AppTokens` holding one instance of each.
3. Type by `$type`: `color` → `Color(0xAARRGGBB)` (`rgba()` strings → alpha channel); `dimension`/`number` → `double`; `duration` → `Duration(milliseconds: n)`; `cubicBezier` → `Cubic(x1, y1, x2, y2)` (`linear` → `Curves.linear`); `shadow` → `List<BoxShadow>` (each layer `x y blur color` → `BoxShadow(offset: Offset(x, y), blurRadius: blur, color: color)`; `none` → `const []`; `inset` layers are dropped and flagged in a comment); `fontWeight` → `FontWeight.w700`; `fontFamily` → `String`; `semantic.state.*` rows → `AppStateRule(opacity, offsetY, shadow)`.
4. A `dark` layer, if present in tokens.json, produces `AppTokens.dark` with the same shape; otherwise `AppTokens.dark = AppTokens.light`.
5. Header comment carries `$extensions.vdp.generatedFrom` and the tokens.json hash so the `visual-audit` skill can detect a stale file.

Skeleton of the generated file (shape only):

```dart
// GENERATED from design-system/onet-garden/tokens.json (vdp: japanese-cute-puzzle). Do not edit.
import 'package:flutter/material.dart';

class AppColors {                                   // semantic.color.*
  const AppColors({required this.primary, required this.onPrimary, required this.surface /* ... */});
  final Color primary, onPrimary, surface;
  static const light = AppColors(primary: Color(0xFFF48FB1), onPrimary: Color(0xFF2F2B2A), surface: Color(0xFFFFFFFF));
}
class AppRadius { const AppRadius(); final double none = 0, xs = 2, sm = 4, md = 8, lg = 12, xl = 16, xl2 = 24, xl3 = 32, full = 9999; }
class AppDuration { const AppDuration(); final Duration fast = const Duration(milliseconds: 120), base = const Duration(milliseconds: 200), slow = const Duration(milliseconds: 350), reveal = const Duration(milliseconds: 600); }
class AppEasing { const AppEasing(); final Curve standard = const Cubic(0.22, 1, 0.36, 1), enter = const Cubic(0.34, 1.56, 0.64, 1), exit = const Cubic(0.36, 0, 0.66, -0.56), emphasized = const Cubic(0.68, -0.6, 0.32, 1.6); }
class AppStateRule { const AppStateRule({this.opacity = 1, this.offsetY = 0, this.shadow = const []}); final double opacity, offsetY; final List<BoxShadow> shadow; }

class AppTokens extends ThemeExtension<AppTokens> {
  const AppTokens({required this.color, required this.radius, required this.duration, required this.easing /* ... */});
  final AppColors color; final AppRadius radius; final AppDuration duration; final AppEasing easing;
  static const light = AppTokens(color: AppColors.light, radius: AppRadius(), duration: AppDuration(), easing: AppEasing());
  @override AppTokens copyWith() => this;                 // tokens are immutable per build
  @override AppTokens lerp(AppTokens? other, double t) => t < 0.5 ? this : (other ?? this);
}
extension TokensX on BuildContext { AppTokens get tokens => Theme.of(this).extension<AppTokens>()!; }
```

`app_theme.dart` registers it once: `ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: AppColors.light.primary), extensions: const [AppTokens.light], textTheme: AppTextTheme.build())`. Flame code imports `app_tokens.dart` and uses `AppTokens.light` statically — it never needs a `BuildContext`.

Easing: Flutter's `Cubic` accepts overshooting control points, so every `primitive.easing.*` bezier is used exactly (bouncy `cubic-bezier(0.34, 1.56, 0.64, 1)` behaves like `Curves.easeOutBack`); no name table is needed on this platform.

## 2. Token group → code mapping

| Group (CC-7) | Flutter app UI | Flame HUD |
|---|---|---|
| `primitive.color.*` ramps | never used directly in widgets; only through `semantic.color.*` / `component.*` | same — HUD paints read `component.hud.chip.*` |
| `semantic.color.*` | `AppColors` fields; `ColorScheme.primary/onPrimary/surface` seeded from `semantic.color.primary`, `semantic.color.onPrimary`, `semantic.color.surface`; `semantic.color.danger` → `ColorScheme.error` | `Paint()..color = tokens.color.primary`; `TextPaint(style: TextStyle(color: tokens.color.text))` |
| `semantic.color.borderInteractive` | `AppColors.borderInteractive` → `BorderSide(color: t.color.borderInteractive)` on tiles, icon buttons, the secondary button and tappable HUD capsules (`component.hud.chipInteractive`); cards/dialogs keep `t.color.border` | tile and wallet-capsule stroke `Paint()..color = t.color.borderInteractive` |
| `semantic.color.focusRing` / `semantic.state.focus.*` | `WidgetStateProperty.resolveWith((s) => s.contains(WidgetState.focused) ? BorderSide(width: t.state.focus.ringWidth, color: t.color.focusRing) : side)`; `ringOffset` via an outer `Padding` | keyboard/gamepad focus on HUD buttons: extra stroke `Paint()..color = t.color.focusRing..strokeWidth = t.state.focus.ringWidth` |
| `primitive.spacing.*` / `semantic.spacing.*` | `EdgeInsets.all(t.spacing.s4)`, `SizedBox(height: t.spacing.s2)`; `semantic.spacing.screenGutter` for page padding, `semantic.spacing.stack` between stacked blocks | `Vector2(t.spacing.s4, t.spacing.s4)` for `position`/`margin` in `HudMarginComponent` |
| `primitive.radius.*` / `semantic.radius.*` | `BorderRadius.circular(t.semantic.radius.control)` on controls, `.container` on cards, `.popup` on dialogs; `StadiumBorder()` when the role resolves to `primitive.radius.full` | `RRect.fromRectAndRadius(rect, Radius.circular(t.semantic.radius.tile))` in `render(Canvas)` |
| `primitive.outline.*` / `semantic.outline.control` | `BorderSide(width: t.semantic.outline.control, color: ...)` on `OutlinedBorder`; colour per `semantic.outline.colorRule` is already resolved into each component's `outlineColor` leaf (e.g. `component.button.primary.outlineColor`) | `Paint()..style = PaintingStyle.stroke ..strokeWidth = t.component.tile.outlineWidth` |
| `primitive.shadow.*` / `semantic.elevation.*` | `BoxDecoration(boxShadow: t.semantic.elevation.raised)`; Material `elevation` stays `0` (`semantic.elevation.method` is `shadow`/`tint`/`outline`, never Material elevation) | pre-baked sprite or `canvas.drawShadow`; never a blur `MaskFilter` per frame |
| `primitive.fontSize.*` / `primitive.lineHeight.*` / `primitive.fontFamily.*` → `semantic.typography.*` | `TextStyle(fontFamily: t.typography.body.fontFamily, fontSize: t.typography.body.fontSize, height: t.typography.body.lineHeight, fontWeight: ...)` inside `TextTheme` (`display`→`displayLarge`, `title`→`titleLarge`, `body`→`bodyMedium`, `label`→`labelLarge`, `caption`→`bodySmall`) | `TextPaint(style: TextStyle(fontSize: t.component.hud.chip.fontSize, height: ratio))` — cache per style |
| `primitive.iconSize.*` | `IconTheme(data: IconThemeData(size: t.iconSize.md))`; `Icon(..., size: t.component.button.icon.iconSize)` | `SpriteComponent(size: Vector2.all(t.component.hud.chip.iconSize))` |
| `primitive.touchTarget.*` | `ConstrainedBox(constraints: BoxConstraints(minWidth: t.touchTarget.min, minHeight: t.touchTarget.min))`; `MaterialTapTargetSize.padded` | `TapCallbacks` component sized to at least `primitive.touchTarget.min`; `RectangleHitbox` enlarged to `component.tile.minSize` |
| `primitive.duration.*` | `AnimatedContainer(duration: t.duration.base)`, `AnimationController(duration:)`, `PageRouteBuilder(transitionDuration: t.duration.slow)`; `reveal` for level-complete reveals (CC-8 adds `reward`/`ambient` keys for reward bursts and idle loops when present) | `EffectController(duration: t.duration.base.inMilliseconds / 1000)` |
| `primitive.easing.*` | `CurvedAnimation(curve: t.easing.standard)`; `enter` for things appearing, `exit` for things leaving, `emphasized` for reward moments | `EffectController(curve: t.easing.enter)` |
| `primitive.zIndex.*` | `Stack` order + `Overlay` entries; `Material(elevation)` is NOT z-index | `priority: t.zIndex.hud` on `Component`; `game.overlays` for Flutter widgets above the canvas (`primitive.zIndex.popup`, `primitive.zIndex.toast`) |
| `primitive.opacity.*` | `Opacity(opacity: t.opacity.disabled)`; `color.withValues(alpha: t.opacity.scrim)` for scrims | `OpacityEffect.to(t.opacity.muted, controller)`; `paint.color.withValues(alpha:)` |
| `semantic.state.*` | `WidgetStateProperty.resolveWith` → `hover/pressed/focus/disabled` rules (`semantic.state.pressed.offsetY` via `Transform.translate`, `semantic.state.focus.ringWidth` via `OutlinedBorder` side, `semantic.state.disabled.opacity`) | `onTapDown` → `MoveByEffect(Vector2(0, t.state.pressed.offsetY))` + swap paint to `component.button.primary.bgPressed`; disabled → `OpacityEffect` |
| `component.*` | one shared widget per group: `AppButton` ← `component.button.*`, `AppCard` ← `component.card.*`, `AppDialog` ← `component.popup.*`, `AppProgressBar` ← `component.progress.*` | `HudChip` ← `component.hud.chip.*`, tile frame ← `component.tile.*` |

Rules: no `Color(0x...)`, `EdgeInsets.all(12)`, `Duration(milliseconds: 337)` or `BorderRadius.circular(13)` outside `app_tokens.dart`. `visual-audit` rule ids `color.off-palette`, `radius.off-scale`, `duration.off-scale` flag exactly these literals; `duration.off-scale` tolerates ±10 % of any listed `primitive.duration.*` value (CC-8).

## 3. Component reuse patterns

Every skeleton reads `context.tokens` (widgets) or a `tokens` field (Flame). No literal numbers. The seven documentation names from the catalog (HudPlate, BoosterSlot, PopupPanel, RewardCard, PriceTag, ProgressBar, EffectSequencer) map onto these widgets; they are not shipped code.

### button.primary / secondary / icon (one widget, variant enum)

```dart
enum AppButtonVariant { primary, secondary, icon }

class AppButton extends StatelessWidget {
  const AppButton({super.key, required this.variant, required this.onPressed, this.label, this.icon});
  final AppButtonVariant variant; final VoidCallback? onPressed; final String? label; final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final t = context.tokens;
    final b = switch (variant) { AppButtonVariant.primary => t.component.button.primary, AppButtonVariant.secondary => t.component.button.secondary, _ => t.component.button.secondary };
    final style = ButtonStyle(
      minimumSize: WidgetStatePropertyAll(Size(b.minWidth, b.height)),
      backgroundColor: WidgetStateProperty.resolveWith((s) => s.contains(WidgetState.pressed) ? b.bgPressed : s.contains(WidgetState.hovered) ? b.bgHover : b.bg),
      foregroundColor: WidgetStatePropertyAll(b.fg),
      textStyle: WidgetStatePropertyAll(TextStyle(fontSize: b.fontSize, fontWeight: b.fontWeight)),
      padding: WidgetStatePropertyAll(EdgeInsets.symmetric(horizontal: b.paddingX)),
      shape: WidgetStatePropertyAll(RoundedRectangleBorder(borderRadius: BorderRadius.circular(b.radius), side: BorderSide(width: b.outlineWidth, color: b.outlineColor))),
      animationDuration: t.duration.fast,
    );
    if (variant == AppButtonVariant.icon) return IconButton(style: style, onPressed: onPressed, icon: Icon(icon, size: t.component.button.icon.iconSize));
    return FilledButton.icon(style: style, onPressed: onPressed, icon: icon == null ? const SizedBox.shrink() : Icon(icon), label: Text(label ?? ''));
  }
}
```

The double-clay shadow (`component.button.primary.shadow`) and the pressed drop (`component.button.primary.pressedOffsetY`, shadow collapses to `semantic.state.pressed.shadow`) are applied once, globally, by wrapping the button in a `DecoratedBox` + `AnimatedSlide(offset: pressed ? Offset(0, b.pressedOffsetY / b.height) : Offset.zero, duration: t.duration.fast, curve: t.easing.standard)` inside `AppButton`, not per call site. Disabled: `Opacity(opacity: t.state.disabled.opacity)`.

### card / panel

```dart
class AppCard extends StatelessWidget {
  const AppCard({super.key, required this.child, this.elevated = false});
  final Widget child; final bool elevated;
  @override
  Widget build(BuildContext context) {
    final t = context.tokens; final c = t.component.card;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: elevated ? t.color.surfaceElevated : c.bg,
        borderRadius: BorderRadius.circular(c.radius),
        border: Border.all(width: c.borderWidth, color: c.borderColor),
        boxShadow: elevated ? t.semantic.elevation.elevated : c.shadow,
      ),
      child: Padding(padding: EdgeInsets.all(c.padding), child: child),
    );
  }
}
```

### popup / dialog

Theme once, then use `showDialog` everywhere: `DialogThemeData(backgroundColor: p.bg, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(p.radius), side: BorderSide(width: p.outlineWidth, color: p.outlineColor)), elevation: 0)` in `app_theme.dart` with `p = AppTokens.light.component.popup`; the scrim is `component.popup.scrim` passed as `barrierColor`; body padding `component.popup.padding`, width capped at `component.popup.maxWidth`. Entry motion: `showGeneralDialog(transitionDuration: p.enterDuration, transitionBuilder: (ctx, a, _, child) => ScaleTransition(scale: CurvedAnimation(parent: a, curve: p.enterEasing), child: child))`; exit uses `primitive.easing.exit`. The dialog body never redeclares radius/outline/shadow — `component.popup.*` owns them.

### HUD chip (Flame)

```dart
class HudChip extends PositionComponent {
  HudChip({required this.text, required this.tokens, super.position}) : super(priority: tokens.component.hud.chip.zIndex);
  final String text; final AppTokens tokens;
  late final _c = tokens.component.hud.chip;
  late final _bg = Paint()..color = _c.bg;
  late final _stroke = Paint()..color = _c.outlineColor..style = PaintingStyle.stroke..strokeWidth = _c.outlineWidth;
  late final _label = TextComponent(text: text, anchor: Anchor.center,
      textRenderer: TextPaint(style: TextStyle(color: _c.fg, fontSize: _c.fontSize, fontWeight: _c.fontWeight)));
  @override Future<void> onLoad() async {
    size = Vector2(_label.width + _c.paddingX * 2, _c.height);
    _label.position = size / 2; add(_label);
  }
  @override void render(Canvas c) {
    final r = RRect.fromRectAndRadius(size.toRect(), Radius.circular(_c.radius));
    c.drawRRect(r, _bg); c.drawRRect(r, _stroke);
  }
  void bump() => add(ScaleEffect.by(Vector2.all(1.08),
      EffectController(duration: tokens.duration.fast.inMilliseconds / 1000, reverseDuration: tokens.duration.fast.inMilliseconds / 1000, curve: tokens.easing.enter)));
}
```

`component.hud.chip.height` (36) is below `primitive.touchTarget.min`; a chip is display-only. If it becomes tappable, enlarge the hitbox to `touchTarget.min`, not the visual.

### tile (board piece)

`SpriteComponent` subclass; the sprite is the art, the frame/outline/selection are token-driven: `render` draws an `RRect` with `component.tile.radius` and `component.tile.outlineWidth` in `component.tile.outlineColor`, switching to `component.tile.outlineColorSelected` + `component.tile.bgSelected` when selected (profile `intentional_exceptions` may lower the radius for `gameplay-hud`). Selection feedback: `SequenceEffect([ScaleEffect.to(Vector2.all(1.1), ctrl(fast, enter)), ScaleEffect.to(Vector2.all(1), ctrl(fast, exit))])`. Match-clear: `OpacityEffect.fadeOut(ctrl(base))` then `removeFromParent()`. Tap target: `RectangleHitbox(size: Vector2.all(max(size.x, tokens.component.tile.minSize)))`. Grid gap: `component.tile.gap`.

### progress bar

Widget: `ClipRRect(borderRadius: BorderRadius.circular(p.radius), child: LinearProgressIndicator(minHeight: p.height, color: reward ? p.fillReward : p.fill, backgroundColor: p.track))` with `p = t.component.progress`, wrapped in a `DecoratedBox` border of `p.outlineWidth`/`p.outlineColor`. Flame: `PositionComponent` with two `Paint`s and a `fraction` setter that lerps in `update(dt)` with `dt / (p.fillDuration.inMilliseconds / 1000)` shaped by `p.fillEasing`.

### toast

One `AppToast.show(context, message, kind)` that uses `ScaffoldMessenger` with `SnackBarThemeData(backgroundColor: t.component.popup.bg, shape: /* popup radius + outline */, behavior: SnackBarBehavior.floating, insetPadding: EdgeInsets.all(t.semantic.spacing.inset))`; `kind` picks `semantic.color.success/warning/danger/reward` for the leading icon. Lifetime is not a CC-7 token: compute it as `t.duration.reveal * 6` in the shared widget (a multiplier on a listed duration, not a new literal) and document the multiplier in `interaction-guidelines.md`. In-game toasts are `game.overlays.add('toast')` so the same widget serves both layers at `primitive.zIndex.toast`.

## 4. Migration order when fixing drift

1. **Tokens**: regenerate `app_tokens.dart`; fix nothing else yet. Run `flutter analyze` — compile errors list every renamed token.
2. **Theme wiring**: `app_theme.dart` (`ThemeData`, `TextTheme` from `semantic.typography.*`, `DialogThemeData`, `SnackBarThemeData`, `IconThemeData`). This fixes every Material widget that already relies on theme defaults.
3. **Shared components** in dependency order: `AppButton` → `AppCard` → `AppDialog`/`AppToast` (they embed `AppCard`/`AppButton`) → `AppProgressBar`.
4. **Flame HUD primitives**: `HudChip`, tile frame, progress bar — they share `AppTokens.light` with the widgets so colours flip together.
5. **Screens**, leaf first: splash/settings (few deps) → home → shop → gameplay overlays (depends on HUD + dialogs). Replace literals with tokens; replace local button/card copies with the shared widgets (`component.duplicate-implementation` findings).
6. Re-run the `visual-audit` skill scan (`audit.py scan`) and golden tests after each step, not at the end.

## 5. What not to touch

- Game loop, match rules, scoring, level data, save/load, IAP, analytics, navigation state.
- `update(dt)` logic of gameplay components — only `render` and effect timings may change.
- Asset pipeline (sprite sheets, atlases). Replacing art is `visual-direction` + asset work, not drift fixing.
- Public constructor signatures of gameplay components; add a `tokens` parameter with a default (`AppTokens.light`) rather than changing call sites.

## 6. Screenshot capture for QA

**Mechanism A — widget goldens (fast, hermetic):** `flutter test --update-goldens test/golden/` with `matchesGoldenFile('goldens/home_phone_small.png')`. Set the device per test: `tester.view.physicalSize = const Size(750, 1334); tester.view.devicePixelRatio = 2.0;` and reset in `addTearDown`. Load real fonts (`primitive.fontFamily.display` / `primitive.fontFamily.body`) with `FontLoader` in `setUpAll` (the default golden font is Ahem, which hides typography drift).

**Mechanism B — integration screenshots (real engine, for Flame):**

```dart
// integration_test/screens_test.dart
void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('capture screens', (tester) async {
    app.main(); await tester.pumpAndSettle();
    await binding.convertFlutterSurfaceToImage();           // Android only; no-op elsewhere
    for (final route in ['home', 'gameplay', 'shop']) {
      await tester.tap(find.byKey(Key('nav_$route'))); await tester.pumpAndSettle();
      await binding.takeScreenshot('${route}_phone_small');    // name becomes the file name
    }
  });
}
```

Run: `flutter drive --driver=test_driver/integration_test.dart --target=integration_test/screens_test.dart -d <deviceId>`; the driver's `onScreenshot` callback writes `screenshots/<name>.png`. File names follow the `visual_qa.py manifest` convention `<screen>_<device>.png`; feed pairs into `visual_qa.py diff` (both in the `visual-audit` skill).

**Device matrix (logical × DPR):** `phone_small` 375×667 @2 (iPhone SE class), `phone_tall` 393×852 @3 (iPhone 15 class), `android` 412×915 @2.625 (Pixel 7 class), `tablet` 820×1180 @2. Portrait only unless the profile lists landscape.

**Determinism:** fixed `physicalSize`/`devicePixelRatio`; `timeDilation = 1`; `tester.pump(Duration.zero)` then `pumpAndSettle` — for Flame, call `game.pauseEngine()` then `game.update(0)` N times so effects land on the same frame; seed `Random(42)` in level generators behind a `--dart-define=QA_SEED`; fix `Localizations` locale and `MediaQuery.textScaler = TextScaler.noScaling`; replace wall-clock reads (`DateTime.now()`) with an injected clock; run goldens on one OS (goldens differ per renderer — tag with `@Tags(['golden'])` and skip elsewhere).

## 7. Performance notes

- Keep `AppTokens` fully `const`; a non-const extension defeats `const` widget subtrees (stack CSV rule "Use const constructors").
- Wrap the Flame HUD and every widget overlay in `RepaintBoundary`; HUD text updates must not repaint the board.
- Cache `TextPaint`/`Paint` objects in `late final` fields (shown above); never build them in `render`.
- Prefer sprite-based shadows/glows for tiles; the double-clay `component.tile.shadow` has a blurred second layer — bake it, `MaskFilter.blur` on hundreds of tiles per frame is the first thing the profiler flags.
- Effects: reuse `EffectController`s where possible; remove finished effects (`removeOnFinish: true`).
- Overlay widgets above the game canvas should be few and small; each is a separate layer composited every frame.
- `ColorScheme.fromSeed` is computed once in `app_theme.dart`; do not call it inside `build`.

## 8. Known limitations

- No generator script for `app_tokens.dart` ships in this wave; the rule in section 1 is deterministic enough to hand-write once and keep under audit.
- The canonical example tokens.json carries `primitive.duration.{instant,fast,base,slow,reveal}`; the `reward`/`ambient` keys from CC-8 appear only when the emitting `vd.py init` includes them — generate fields conditionally.
- `ThemeExtension.lerp` is a step function here; theme crossfades between light/dark will snap unless colours are lerped field by field.
- Flame components cannot read `Theme.of(context)`; a runtime theme switch must call `game.tokens = AppTokens.dark` and rebuild cached `Paint`s.
- `inset` shadow layers (`primitive.shadow.inset`, pressed state on offset-soft styles) have no `BoxShadow` equivalent; emulate with an inner `Border` or a gradient overlay and record it as an intentional exception.
- Goldens are renderer-specific (Skia vs Impeller, macOS vs Linux CI); keep one reference platform.
- `takeScreenshot` on iOS captures via the driver and can lag one frame behind `pumpAndSettle`; add one extra `pump`.
- `primitive.touchTarget.*` applies to Flame via hitboxes only; Flutter's `MaterialTapTargetSize` does not reach the canvas.
