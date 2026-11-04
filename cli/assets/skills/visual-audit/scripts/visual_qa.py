#!/usr/bin/env python3
"""visual_qa.py - screenshot regression diff, QA checklist and capture manifest
for the visual-audit skill (integration contract section 4.5).

Commands
    diff <a.png> <b.png> [--threshold 0.5] [--tolerance 16] [--ignore x0,y0,x1,y1]...
                         [--out diff.png] [--json]
        --threshold is a PERCENT of compared pixels (0.5 = 0.5 %). Output carries
        diff_ratio (fraction) and diff_percent. bbox is [x0, y0, x1, y1] with an
        EXCLUSIVE max corner. Exit 0 PASS, 1 FAIL, 3 BLOCKED (Pillow missing,
        unreadable image, size mismatch), 2 usage error.
    checklist --profile style-profile.json [--screen gameplay] [--format md|json] [--json] [--out file]
        qa_criteria from the profile + generic per-screen items; every item starts
        as NOT RUN. --screen: home, gameplay, level-select, pause, win, lose, settings,
        shop, rewards, profile, tutorial, or a pages/<name>.md next to the profile.
        Exit 0 ok, 1 invalid profile, 2 missing file / unknown screen / usage.
    manifest --stack <stack> --screens home,gameplay [--devices phone-m,...]
             [--profile style-profile.json] [--out screens.json] [--json]
        Capture INSTRUCTIONS per stack and device, never executed. Exit 0 ok,
        2 unsupported stack / usage.
    devices [--json]
        Print the device matrix.

Pillow is optional and imported lazily inside diff only; everything else is stdlib.
"""
import argparse
import datetime
import json
import os
import sys

EXIT_PASS, EXIT_FAIL, EXIT_USAGE, EXIT_BLOCKED = 0, 1, 2, 3

DEVICES = [
    {"name": "phone-s", "logical_size": [375, 667], "dpr": 2, "represents": "iPhone SE / small Android",
     "mandatory_for": "all mobile (smallest safe area)", "status_bar_mask": [0, 0, 375, 20]},
    {"name": "phone-m", "logical_size": [390, 844], "dpr": 3, "represents": "iPhone 14/15, most Android",
     "mandatory_for": "all mobile", "status_bar_mask": [0, 0, 390, 47]},
    {"name": "phone-l", "logical_size": [430, 932], "dpr": 3, "represents": "iPhone Pro Max, large Android",
     "mandatory_for": "all mobile", "status_bar_mask": [0, 0, 430, 59]},
    {"name": "tablet", "logical_size": [768, 1024], "dpr": 2, "represents": "iPad / Android tablet, portrait",
     "mandatory_for": "product.platforms includes tablet", "status_bar_mask": [0, 0, 768, 24]},
    {"name": "desktop", "logical_size": [1440, 900], "dpr": 1, "represents": "web / desktop",
     "mandatory_for": "product.platforms includes web or desktop", "status_bar_mask": None},
]
DEVICE_BY_NAME = {d["name"]: d for d in DEVICES}
MOBILE_DEVICES = ["phone-s", "phone-m", "phone-l"]

NOT_EXECUTED = "manual/automation hint, not executed"

STACKS = {
    "flutter": {
        "tool": "integration_test",
        "mechanism": "integration_test package + IntegrationTestWidgetsFlutterBinding.takeScreenshot('<name>'); golden tests (matchesGoldenFile) for widget-level; run with `flutter drive --driver test_driver/integration_test.dart --target integration_test/<screen>_test.dart`",
        "snippet": "final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();\n"
                   "testWidgets('<<screen>> <<device>>', (tester) async {\n"
                   "  tester.view.physicalSize = const Size(<<pw>>, <<ph>>); tester.view.devicePixelRatio = <<dpr>>;\n"
                   "  timeDilation = 1.0; // disable animations via binding.transitionDuration where available\n"
                   "  await tester.pumpWidget(const App(seed: 42)); await tester.pumpAndSettle();\n"
                   "  await binding.takeScreenshot('<<file_stem>>');\n"
                   "});",
        "settle": "pumpAndSettle() after navigation; fixed seed data; fonts bundled (no network); pin physicalSize/devicePixelRatio via tester.view",
        "default_devices": MOBILE_DEVICES,
    },
    "flutter-flame": {
        "tool": "integration_test",
        "mechanism": "same as flutter: integration_test + takeScreenshot; for Flame set GameWidget with a fixed FixedResolutionViewport, pause the game loop (game.pauseEngine()) at the settled state before capture",
        "snippet": "testWidgets('<<screen>> <<device>>', (tester) async {\n"
                   "  tester.view.physicalSize = const Size(<<pw>>, <<ph>>); tester.view.devicePixelRatio = <<dpr>>;\n"
                   "  final game = MyGame(seed: 42); await tester.pumpWidget(GameWidget(game: game));\n"
                   "  await game.ready(); game.pauseEngine(); await tester.pump();\n"
                   "  await binding.takeScreenshot('<<file_stem>>');\n"
                   "});",
        "settle": "game.pauseEngine() after the screen reaches its end state; disable particle components or mask them with --ignore; deterministic seed",
        "default_devices": MOBILE_DEVICES,
    },
    "unity-ugui": {
        "tool": "ScreenCapture",
        "mechanism": "ScreenCapture.CaptureScreenshot(path, superSize) or Camera.Render to a RenderTexture + Texture2D.ReadPixels inside a Play Mode test (Unity Test Framework); Device Simulator package for the matrix",
        "snippet": "[UnityTest] public IEnumerator Capture_<<screen_id>>_<<device_id>>() {\n"
                   "  Screen.SetResolution(<<pw>>, <<ph>>, false); Time.timeScale = 0f; Application.targetFrameRate = 60;\n"
                   "  yield return SceneManager.LoadSceneAsync(\"<<screen>>\"); yield return null; yield return null;\n"
                   "  ScreenCapture.CaptureScreenshot(\"<<file>>\"); yield return null;\n"
                   "}",
        "settle": "Time.timeScale = 0 (and DOTween.timeScale = 0) after reaching the end state; disable ParticleSystems or mask them; deterministic seeds",
        "default_devices": MOBILE_DEVICES,
    },
    "unity-ui-toolkit": {
        "tool": "ScreenCapture",
        "mechanism": "ScreenCapture.CaptureScreenshot(path, superSize) in a Play Mode test after the UIDocument is laid out (yield two frames); PanelSettings with a fixed reference resolution per device row",
        "snippet": "[UnityTest] public IEnumerator Capture_<<screen_id>>_<<device_id>>() {\n"
                   "  Screen.SetResolution(<<pw>>, <<ph>>, false); Time.timeScale = 0f;\n"
                   "  var doc = Object.FindObjectOfType<UIDocument>(); doc.panelSettings.referenceResolution = new Vector2Int(<<pw>>, <<ph>>);\n"
                   "  yield return null; yield return null; ScreenCapture.CaptureScreenshot(\"<<file>>\"); yield return null;\n"
                   "}",
        "settle": "two frames after layout; transitions disabled via USS (transition-duration: 0) in a test theme; deterministic data",
        "default_devices": MOBILE_DEVICES,
    },
    "web": {
        "tool": "playwright",
        "mechanism": "Playwright page.screenshot({ fullPage: false }) with setViewportSize, deviceScaleFactor, colorScheme, reducedMotion: 'reduce'; addStyleTag to kill transitions; mask option or --ignore for live regions",
        "snippet": "test('<<screen>> <<device>>', async ({ browser }) => {\n"
                   "  const ctx = await browser.newContext({ viewport: { width: <<w>>, height: <<h>> }, deviceScaleFactor: <<dpr>>, reducedMotion: 'reduce', colorScheme: 'light', locale: 'en-US' });\n"
                   "  const page = await ctx.newPage(); await page.clock.install(); await page.goto('/<<screen>>');\n"
                   "  await page.addStyleTag({ content: '*{transition:none!important;animation:none!important;caret-color:transparent!important}' });\n"
                   "  await page.evaluate(() => document.fonts.ready); await page.waitForLoadState('networkidle');\n"
                   "  await page.screenshot({ path: '<<file>>' });\n"
                   "});",
        "settle": "document.fonts.ready + networkidle; page.clock for timers; route mocks for data; same locale and colorScheme as the baseline sidecar",
        "default_devices": ["desktop", "phone-m"],
    },
    "swiftui": {
        "tool": "XCTest",
        "mechanism": "XCUIScreen.main.screenshot() inside an XCTest UI test (XCTAttachment with lifetime .keepAlways) on a named simulator per device row; 'Reduce Motion' on; fixed locale",
        "snippet": "func test_<<screen_id>>_<<device_id>>() {\n"
                   "  let app = XCUIApplication(); app.launchArguments += [\"-UITestSeed\", \"42\", \"-ReduceMotion\", \"1\"]; app.launch()\n"
                   "  app.buttons[\"<<screen>>\"].tap(); _ = app.staticTexts.firstMatch.waitForExistence(timeout: 5)\n"
                   "  let shot = XCUIScreen.main.screenshot(); let att = XCTAttachment(screenshot: shot); att.name = \"<<file_stem>>\"; att.lifetime = .keepAlways; add(att)\n"
                   "}",
        "settle": "waitForExistence on the screen's last element; simulator sized per device row (xcrun simctl); Reduce Motion enabled",
        "default_devices": MOBILE_DEVICES,
    },
    "jetpack-compose": {
        "tool": "captureToImage",
        "mechanism": "ComposeTestRule onRoot().captureToImage() (instrumented) or Roborazzi / Paparazzi for JVM screenshot tests with a DeviceConfig per device row; animations disabled via composeTestRule.mainClock.autoAdvance = false",
        "snippet": "@Test fun capture_<<screen_id>>_<<device_id>>() {\n"
                   "  composeRule.mainClock.autoAdvance = false\n"
                   "  composeRule.setContent { AppTheme { <<screen_pascal>>Screen(seed = 42) } }\n"
                   "  composeRule.mainClock.advanceTimeBy(1_000)\n"
                   "  composeRule.onRoot().captureToImage().asAndroidBitmap().save(\"<<file>>\")  // or Roborazzi captureRoboImage(\"<<file>>\")\n"
                   "}",
        "settle": "mainClock paused after advancing past transitions; fixed DeviceConfig (<<w>>x<<h>> @ <<dpr>>x); fixed locale and font scale 1.0",
        "default_devices": MOBILE_DEVICES,
    },
}
STACK_ALIASES = {"react": "web", "nextjs": "web", "vue": "web", "svelte": "web", "html-tailwind": "web",
                 "astro": "web", "nuxtjs": "web", "unity": "unity-ugui"}

# Generic checklist items (ids refer to references/ux-audit-checklist.md). screens: list or "*"
GENERIC_ITEMS = [
    ("A1", "*", "any", "One primary action per screen, visually dominant (size, semantic.color.primary/accent); count competing CTAs"),
    ("A3", "*", "any", "Screen title / context visible without scrolling on every device row"),
    ("B1", "non-root", "any", "Visible back/close within the top 15 % of the viewport (or system back works)"),
    ("C1", "*", "any", "Body text >= 14 px/sp (web 16 px), captions >= 12; every size is a primitive.fontSize step"),
    ("C2", "*", "any", "Contrast >= 4.5:1 body, >= 3:1 large text/icons, measured on the rendered background"),
    ("C4", "*", "any", "Only the contract families (semantic.typography display/body); display family not used for body copy"),
    ("D1", "*", "any", "Every tappable target >= minTouchTarget (44 pt / 48 dp / 44 px) incl. padding; >= 8 between targets"),
    ("E1", "*", "any", "Interactive components show default / hover (web) / pressed / focus / disabled per semantic.state"),
    ("F1", "*", "any", "Every tap gives feedback within 100 ms (visual state change, haptic or sound)"),
    ("G1", "*", "any", "Icon-only buttons have accessible names (Semantics / tooltip / aria-label)"),
    ("G3", "*", "any", "No information conveyed by colour alone (status, selected tile, rarity)"),
    ("A4", ["gameplay", "result"], "game", "HUD: score / lives / timer / currency in consistent corners across gameplay screens"),
    ("C5", ["gameplay", "reward", "result"], "game", "Text over imagery/characters has a scrim, outline (primitive.outline) or plate"),
    ("C6", ["gameplay", "shop"], "game", "Numbers in HUD/score use tabular figures or fixed width (no jitter)"),
    ("D2", ["gameplay", "shop", "home"], "any", "Primary CTA within the bottom thumb zone on phones (lower 60 % of viewport)"),
    ("E3", ["gameplay", "result", "reward", "popup"], "game", "Paused / game-over / level-complete / out-of-lives / reward-claimed states styled per popup rules"),
    ("F2", ["gameplay", "reward", "result"], "any", "Durations from primitive.duration; nothing > slow on the critical path; reward sequences skippable"),
    ("G4", ["gameplay", "reward"], "game", "Flashing content <= 3 flashes/s; particle bursts have a reduced-motion variant"),
    ("B3", ["home", "menu", "settings"], "any", "Bottom nav / tab bar <= 5 items, labels present, active state uses the selected colour"),
    ("B5", ["home", "menu", "shop", "reward", "result"], "game", "home -> play -> result -> home loop in <= 2 taps per hop; shop/reward screens return to origin"),
    ("E2", ["home", "shop", "settings", "menu"], "any", "Loading, empty, error and offline states exist for every data-driven screen"),
    ("D3", ["shop", "reward"], "any", "Destructive/purchase buttons not adjacent to frequent actions; purchase has an explicit confirm"),
    ("F3", ["shop", "reward", "result", "gameplay"], "any", "Success/failure feedback uses semantic.color.success/danger plus a non-colour cue"),
    ("B2", ["popup", "shop", "settings", "reward"], "any", "Popups/dialogs dismiss via close button AND scrim tap/back; destructive confirms need explicit action"),
    ("F4", ["popup", "gameplay", "shop"], "any", "Toasts/snackbars never cover the primary CTA or HUD; auto-dismiss >= 4 s"),
    ("D5", ["settings", "home", "shop"], "any", "Keyboard/web: focus visible (semantic.state.focus), tab order = reading order, Esc closes dialogs"),
    ("E5", ["settings", "home"], "any", "Dark mode / reduced-motion honoured when the profile declares them (motion.reduced_motion)"),
    ("G2", ["settings", "home", "shop"], "any", "Text scales with the OS font size (textScaleFactor / rem / sp) without clipping at 130 %"),
    ("E4", ["shop", "settings", "popup"], "any", "Long content / i18n expansion (+30 % text) does not clip or overflow"),
]
SCREEN_ALIASES = {"rewards": "reward", "main-menu": "menu", "mainmenu": "menu", "level-complete": "result",
                  "game-over": "result", "gameover": "result", "win": "result", "lose": "result", "dialog": "popup",
                  "modal": "popup", "store": "shop", "play": "gameplay", "game": "gameplay", "level": "gameplay",
                  "options": "settings", "start": "home", "title": "home"}
ROOT_SCREENS = {"home", "menu"}
# --screen accepts ONLY these ids (or a pages/<name>.md next to the profile). Value = item group used
# to pick the generic checks (GENERIC_ITEMS screen lists).
KNOWN_SCREENS = {
    "home": "home", "gameplay": "gameplay", "level-select": "menu", "pause": "popup", "win": "result",
    "lose": "result", "settings": "settings", "shop": "shop", "rewards": "reward", "profile": "settings",
    "tutorial": "popup",
}


class Blocked(Exception):
    pass


class UnknownScreen(ValueError):
    """--screen value that is neither a known screen id nor a pages/<name>.md next to the profile (exit 2)."""


# ------------------------------------------------------------------- diff
def _pil():
    """Lazy, guarded import. Returns (Image, ImageChops) or None when Pillow is missing."""
    try:
        from PIL import Image, ImageChops  # noqa: F401
    except ImportError:
        return None
    return Image, ImageChops


def write_text(path, text):
    """Write an output file, creating parent directories (qa-logs/… on first run)."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def parse_rect(text):
    try:
        parts = [int(p) for p in str(text).split(",")]
    except ValueError:
        raise argparse.ArgumentTypeError("ignore region must be x0,y0,x1,y1 integers: %r" % text)
    if len(parts) != 4 or parts[2] <= parts[0] or parts[3] <= parts[1]:
        raise argparse.ArgumentTypeError("ignore region must be x0,y0,x1,y1 with x1>x0 and y1>y0: %r" % text)
    return parts


def non_negative_float(text):
    try:
        v = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a number, got %r" % text)
    if v < 0:
        raise argparse.ArgumentTypeError("must be >= 0, got %s" % text)
    return v


def clusters_from_mask(mask, width, height, cell=8, top=5):
    """Connected components (4-neighbour) of changed pixels on a cell grid.
    Returns up to `top` clusters sorted by changed-pixel count desc."""
    cells = {}
    data = mask.getdata()
    for idx, v in enumerate(data):
        if v:
            key = ((idx % width) // cell, (idx // width) // cell)
            cells[key] = cells.get(key, 0) + 1
    seen = set()
    comps = []
    for start in sorted(cells):
        if start in seen:
            continue
        stack, members = [start], []
        seen.add(start)
        while stack:
            c = stack.pop()
            members.append(c)
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + d[0], c[1] + d[1])
                if n in cells and n not in seen:
                    seen.add(n)
                    stack.append(n)
        xs, ys = [m[0] for m in members], [m[1] for m in members]
        comps.append({
            "bbox": [min(xs) * cell, min(ys) * cell, min((max(xs) + 1) * cell, width), min((max(ys) + 1) * cell, height)],
            "changed_pixels": sum(cells[m] for m in members),
            "cells": len(members),
        })
    comps.sort(key=lambda c: (-c["changed_pixels"], c["bbox"]))
    return comps[:top]


def diff_images(a_path, b_path, threshold=0.5, tolerance=16, ignore=(), out=None):
    """Compare two images. threshold is PERCENT; tolerance is per-channel 0..255.
    Returns the result dict (status PASS/FAIL/BLOCKED); never raises for Pillow/IO problems."""
    base = {"status": "BLOCKED", "a": str(a_path), "b": str(b_path), "threshold": threshold, "tolerance": tolerance,
            "ignore": [list(r) for r in ignore], "diff_ratio": None, "diff_percent": None, "bbox": None}
    pil = _pil()
    if pil is None:
        base["reason"] = "Pillow not installed (pip install pillow); diff cannot run"
        return base
    Image, ImageChops = pil
    imgs = []
    for p in (a_path, b_path):
        try:
            im = Image.open(p)
            im.load()
            imgs.append(im.convert("RGB"))
        except (OSError, ValueError) as e:
            base["reason"] = "unreadable image: %s (%s)" % (p, e.__class__.__name__)
            return base
    a, b = imgs
    if a.size != b.size:
        base["reason"] = "size mismatch %dx%d vs %dx%d (compare per-device baselines; never resize)" % (a.size[0], a.size[1], b.size[0], b.size[1])
        base["size_a"], base["size_b"] = list(a.size), list(b.size)
        return base
    w, h = a.size
    d = ImageChops.difference(a, b)
    r, g, bl = d.split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), bl)
    tol = int(tolerance)
    mask = m.point(lambda v: 255 if v > tol else 0)
    ign = Image.new("L", (w, h), 0)
    for x0, y0, x1, y1 in ignore:
        ign.paste(255, (max(0, x0), max(0, y0), min(w, x1), min(h, y1)))
    mask = ImageChops.subtract(mask, ign)
    masked = ign.histogram()[255]
    changed = mask.histogram()[255]
    denom = w * h - masked
    ratio = (changed / float(denom)) if denom > 0 else 0.0
    bbox = mask.getbbox()
    status = "FAIL" if ratio * 100.0 > threshold else "PASS"
    result = dict(base)
    result.update({
        "status": status, "size": [w, h], "changed_pixels": changed, "masked_pixels": masked,
        "masked_ratio": round(masked / float(w * h), 6) if w * h else 0.0,
        "diff_ratio": round(ratio, 6), "diff_percent": round(ratio * 100.0, 4),
        "bbox": list(bbox) if bbox else None,
        "clusters": clusters_from_mask(mask, w, h) if bbox else [],
        "diff_image": None,
    })
    result.pop("reason", None)
    if out:
        grey = b.convert("L").convert("RGB")
        red = Image.new("RGB", (w, h), (255, 0, 0))
        alpha = mask.point(lambda v: 178 if v else 0)
        heat = Image.composite(red, grey, alpha)
        canvas = Image.new("RGB", (w * 3, h), (255, 255, 255))
        canvas.paste(a, (0, 0))
        canvas.paste(b, (w, 0))
        canvas.paste(heat, (w * 2, 0))
        parent = os.path.dirname(os.path.abspath(str(out)))
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        canvas.save(out)
        result["diff_image"] = str(out)
    return result


# -------------------------------------------------------------- checklist
def normalise_screen(name):
    """Item group for a free screen name (used for pages/<name>.md screens): aliases, else the name itself."""
    s = (name or "").strip().lower().replace("_", "-")
    if s in KNOWN_SCREENS:
        return KNOWN_SCREENS[s]
    return SCREEN_ALIASES.get(s, s) or "other"


def page_screens(profile_path):
    """Screen names from pages/*.md next to the profile (design-system/<slug>/pages/<name>.md)."""
    if not profile_path:
        return []
    pages = os.path.join(os.path.dirname(os.path.abspath(profile_path)), "pages")
    if not os.path.isdir(pages):
        return []
    return sorted(os.path.splitext(f)[0].lower() for f in os.listdir(pages) if f.lower().endswith(".md"))


def resolve_screen(screen, pages=()):
    """Return (screen_id, item_group). Raises UnknownScreen listing the valid ids."""
    if not screen:
        return "all", "all"
    sid = screen.strip().lower()
    if sid in KNOWN_SCREENS:
        return sid, KNOWN_SCREENS[sid]
    pages = [p.lower() for p in pages]
    if sid in pages:
        return sid, normalise_screen(sid)
    valid = list(KNOWN_SCREENS) + ["pages/%s.md" % p for p in pages if p not in KNOWN_SCREENS]
    raise UnknownScreen("unknown screen %r; valid ids: %s%s" % (
        screen, ", ".join(valid), "" if pages else " (or add pages/<name>.md next to the profile)"))


def build_checklist(profile, screen=None, pages=()):
    """Items from profile.qa_criteria + generic per-screen items. Raises UnknownScreen for a --screen
    that is not a known id or a pages/<name>.md, ValueError when qa_criteria is missing or not a list of strings."""
    sid, scr = resolve_screen(screen, pages)
    if not isinstance(profile, dict):
        raise ValueError("profile must be a JSON object (vdp/1)")
    criteria = profile.get("qa_criteria")
    if not isinstance(criteria, list) or not all(isinstance(c, str) for c in criteria):
        raise ValueError("profile.qa_criteria must be a list of strings (contract 4.1); got %r" % type(criteria).__name__)
    kind = (profile.get("product") or {}).get("kind", "app")
    root = sid == "home" or (sid not in KNOWN_SCREENS and scr in ROOT_SCREENS)
    items = []
    for i, text in enumerate(criteria, 1):
        items.append({"id": "QA-P-%02d" % i, "text": text, "source": "qa_criteria", "screen": sid,
                      "status": "NOT RUN", "label": "", "evidence": ""})
    for cid, screens, k, text in GENERIC_ITEMS:
        if k != "any" and k != kind:
            continue
        if screens == "*":
            applies = True
        elif screens == "non-root":
            applies = scr == "all" or not root
        else:
            applies = scr == "all" or scr in screens
        if applies:
            items.append({"id": "QA-G-%s" % cid, "text": text, "source": "generic:%s" % cid, "screen": sid,
                          "status": "NOT RUN", "label": "", "evidence": ""})
    for ap in profile.get("anti_patterns") or []:
        if isinstance(ap, str):
            items.append({"id": "QA-A-%02d" % (len([x for x in items if x["id"].startswith("QA-A-")]) + 1),
                          "text": "Anti-pattern absent: %s" % ap, "source": "anti_patterns", "screen": sid,
                          "status": "NOT RUN", "label": "", "evidence": ""})
    return {
        "schema": "visual-qa-checklist/1",
        "project": (profile.get("project") or {}).get("name"),
        "style": (profile.get("style") or {}).get("id"),
        "kind": kind,
        "screen": sid,
        "screen_type": scr,
        "status_values": ["PASS", "FAIL", "BLOCKED", "NOT RUN"],
        "labels": ["RUNTIME-VERIFIED", "STATIC-VERIFIED", "TOOL-ANALYZED", "NOT RUN"],
        "items": items,
    }


def checklist_markdown(cl):
    out = ["# Visual QA checklist — %s — screen: %s" % (cl.get("project") or "project", cl["screen"]),
           "style: %s · kind: %s · status per item: PASS / FAIL / BLOCKED / NOT RUN (default) · label: RUNTIME-VERIFIED / STATIC-VERIFIED / TOOL-ANALYZED / NOT RUN" % (cl.get("style") or "-", cl["kind"]),
           ""]
    groups = [("qa_criteria", "Profile qa_criteria"), ("generic", "Generic per-screen checks (references/ux-audit-checklist.md)"), ("anti_patterns", "Profile anti_patterns")]
    for key, title in groups:
        rows = [i for i in cl["items"] if i["source"].split(":")[0] == key]
        if not rows:
            continue
        out.append("## %s" % title)
        for i in rows:
            out.append("- [ ] %s — %s — status: %s — evidence: (file:line, screenshot path or measurement)" % (i["id"], i["text"], i["status"]))
        out.append("")
    return "\n".join(out)


# --------------------------------------------------------------- manifest
def resolve_stack(stack):
    s = (stack or "").strip().lower()
    s = STACK_ALIASES.get(s, s)
    if s not in STACKS:
        raise ValueError("unsupported stack %r; supported: %s (aliases: %s)" % (
            stack, ", ".join(sorted(STACKS)), ", ".join("%s->%s" % kv for kv in sorted(STACK_ALIASES.items()))))
    return s


def render(template, values):
    """Replace <<key>> placeholders; code braces in snippets need no escaping."""
    for k, v in values.items():
        template = template.replace("<<%s>>" % k, str(v))
    return template


def _pascal(name):
    return "".join(p.capitalize() for p in name.replace("_", "-").split("-") if p)


def _ident(name):
    return name.replace("-", "_").replace(" ", "_")


def build_manifest(stack, screens, devices=None, profile=None):
    """Capture instructions per screen x device. Raises ValueError on unsupported stack/device."""
    resolved = resolve_stack(stack)
    spec = STACKS[resolved]
    screens = [s.strip() for s in screens if s and s.strip()]
    if not screens:
        raise ValueError("at least one screen is required (--screens home,gameplay)")
    if devices:
        names = [d.strip() for d in devices if d and d.strip()]
        unknown = [d for d in names if d not in DEVICE_BY_NAME]
        if unknown:
            raise ValueError("unknown device(s) %s; known: %s" % (", ".join(unknown), ", ".join(DEVICE_BY_NAME)))
    else:
        names = list(spec["default_devices"])
        plats = set((profile or {}).get("product", {}).get("platforms") or []) if isinstance(profile, dict) else set()
        if "tablet" in plats and "tablet" not in names:
            names.append("tablet")
        if ({"web", "desktop"} & plats) and "desktop" not in names:
            names.append("desktop")
    entries = []
    for screen in screens:
        for dn in names:
            dev = DEVICE_BY_NAME[dn]
            w, h = dev["logical_size"]
            file_name = "%s_%s.png" % (screen, dn)
            fmt = dict(screen=screen, screen_id=_ident(screen), screen_pascal=_pascal(screen), device=dn, device_id=_ident(dn),
                       w=w, h=h, pw=w * dev["dpr"], ph=h * dev["dpr"], dpr=dev["dpr"], file=file_name,
                       file_stem=os.path.splitext(file_name)[0])
            masks = []
            if dev["status_bar_mask"]:
                masks.append({"region": dev["status_bar_mask"], "why": "status bar (clock/battery)"})
            masks.append({"region": None, "why": "add --ignore for FPS counters, live timers, ad slots and particle layers"})
            entries.append({
                "screen": screen, "device": dn, "logical_size": [w, h], "dpr": dev["dpr"],
                "file": file_name,
                "baseline": "baselines/%s/%s@%dx.png" % (screen, dn, dev["dpr"]),
                "sidecar": "baselines/%s/%s.json" % (screen, dn),
                "capture": {"tool": spec["tool"], "mechanism": spec["mechanism"], "snippet": render(spec["snippet"], fmt)},
                "settle": render(spec["settle"], fmt),
                "suggested_masks": masks,
                "compare": "python3 scripts/visual_qa.py diff baselines/%s/%s@%dx.png %s --threshold 0.5 --json" % (screen, dn, dev["dpr"], file_name),
                "executed": False,
                "status": "NOT RUN",
                "note": NOT_EXECUTED,
            })
    return {
        "schema": "visual-qa-manifest/1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "stack": stack, "resolved_stack": resolved,
        "note": "Capture instructions, not executed: visual_qa.py never launches the app or takes screenshots. "
                "Run the snippets with the project's own test tooling, then compare with `visual_qa.py diff`. "
                "Every entry stays NOT RUN until a capture exists; report BLOCKED when the tool is unavailable.",
        "naming": "<screen>_<device>.png",
        "devices": [DEVICE_BY_NAME[n] for n in names],
        "sidecar_fields": ["captured_with", "app_version", "locale", "theme", "dpr", "ignore_regions", "notes"],
        "entries": entries,
    }


def manifest_markdown(mf):
    out = ["# Capture manifest — %s (%s)" % (mf["stack"], mf["resolved_stack"]), mf["note"], "",
           "| screen | device | size | dpr | file | tool | status |", "|---|---|---|---|---|---|---|"]
    for e in mf["entries"]:
        out.append("| %s | %s | %dx%d | %d | %s | %s | %s (%s) |" % (
            e["screen"], e["device"], e["logical_size"][0], e["logical_size"][1], e["dpr"], e["file"], e["capture"]["tool"], e["status"], NOT_EXECUTED))
    return "\n".join(out) + "\n"


# -------------------------------------------------------------------- CLI
def _blocked(reason, as_json, extra=None):
    payload = {"status": "BLOCKED", "reason": reason}
    if extra:
        payload.update(extra)
    sys.stderr.write("BLOCKED: %s\n" % reason)
    sys.stdout.write(json.dumps(payload, indent=2) + "\n" if as_json else "BLOCKED: %s\n" % reason)
    return EXIT_BLOCKED


def cmd_diff(args):
    result = diff_images(args.a, args.b, args.threshold, args.tolerance, args.ignore or (), args.out)
    if result["status"] == "BLOCKED":
        extra = {k: v for k, v in result.items() if k not in ("status", "reason")}
        return _blocked(result["reason"], args.json, extra)
    if args.json:
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
    else:
        sys.stdout.write("%s  diff_ratio=%.6f (%.4f %%)  threshold=%s %%  tolerance=%d  bbox=%s  masked=%d px%s\n" % (
            result["status"], result["diff_ratio"], result["diff_percent"], args.threshold, args.tolerance, result["bbox"],
            result["masked_pixels"], ("  diff image: %s" % result["diff_image"]) if result.get("diff_image") else ""))
        for c in result["clusters"]:
            sys.stdout.write("  cluster bbox=%s changed=%d px\n" % (c["bbox"], c["changed_pixels"]))
    return EXIT_PASS if result["status"] == "PASS" else EXIT_FAIL


def _load_profile(path):
    if not os.path.isfile(path):
        sys.stderr.write("error: profile not found: %s\n" % path)
        return None, EXIT_USAGE
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), 0
    except (OSError, ValueError) as e:
        sys.stderr.write("error: profile is not valid JSON: %s (%s)\n" % (path, e))
        return None, EXIT_FAIL


def cmd_checklist(args):
    profile, rc = _load_profile(args.profile)
    if rc:
        return rc
    try:
        cl = build_checklist(profile, args.screen, page_screens(args.profile))
    except UnknownScreen as e:
        sys.stderr.write("error: %s\n" % e)
        return EXIT_USAGE
    except ValueError as e:
        sys.stderr.write("error: %s\n" % e)
        return EXIT_FAIL
    fmt = "json" if args.json else (args.format or "md")
    text = json.dumps(cl, indent=2, ensure_ascii=False) + "\n" if fmt == "json" else checklist_markdown(cl)
    if args.out:
        write_text(args.out, text)
    sys.stdout.write(text)
    return EXIT_PASS


def cmd_manifest(args):
    profile = None
    if args.profile:
        profile, rc = _load_profile(args.profile)
        if rc:
            return rc
    try:
        mf = build_manifest(args.stack, args.screens.split(","), args.devices.split(",") if args.devices else None, profile)
    except ValueError as e:
        sys.stderr.write("error: %s\n" % e)
        return EXIT_USAGE
    js = json.dumps(mf, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        write_text(args.out, js)
    sys.stdout.write(js if args.json else manifest_markdown(mf))
    return EXIT_PASS


def cmd_devices(args):
    if args.json:
        sys.stdout.write(json.dumps(DEVICES, indent=2) + "\n")
    else:
        sys.stdout.write("| name | logical size | dpr | represents | mandatory for |\n|---|---|---|---|---|\n")
        for d in DEVICES:
            sys.stdout.write("| %s | %dx%d | %d | %s | %s |\n" % (d["name"], d["logical_size"][0], d["logical_size"][1], d["dpr"], d["represents"], d["mandatory_for"]))
    return EXIT_PASS


def build_parser():
    p = argparse.ArgumentParser(prog="visual_qa.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    d = sub.add_parser("diff", help="pixel-diff two screenshots (exit 0 PASS / 1 FAIL / 3 BLOCKED / 2 usage)",
                       description="Compare a.png with b.png. --threshold is a PERCENT of compared pixels (default 0.5 = 0.5 percent). "
                                   "Pixels change when any channel differs by more than --tolerance (0..255, default 16). "
                                   "bbox = [x0, y0, x1, y1], exclusive max corner. Exit codes: 0 PASS, 1 FAIL, 3 BLOCKED "
                                   "(Pillow missing, unreadable image, size mismatch), 2 usage error.")
    d.add_argument("a")
    d.add_argument("b")
    d.add_argument("--threshold", type=non_negative_float, default=0.5, help="max changed pixels in PERCENT before FAIL (default 0.5 = 0.5 percent)")
    d.add_argument("--tolerance", type=non_negative_float, default=16, help="per-channel tolerance 0..255 (default 16; 0 = exact)")
    d.add_argument("--ignore", action="append", type=parse_rect, help="x0,y0,x1,y1 region to mask (repeatable; exclusive max)")
    d.add_argument("--out", help="write a side-by-side a | b | heat image")
    d.add_argument("--json", action="store_true", help="print the result as JSON")
    d.set_defaults(func=cmd_diff)
    c = sub.add_parser("checklist", help="QA checklist from a style-profile.json (exit 0 / 1 invalid / 2 missing)")
    c.add_argument("--profile", required=True)
    c.add_argument("--screen", help="screen id: %s, or the name of a pages/<name>.md next to the profile; anything else exits 2 (default: all screens)" % ", ".join(KNOWN_SCREENS))
    c.add_argument("--format", choices=["md", "json"], default="md")
    c.add_argument("--out")
    c.add_argument("--json", action="store_true", help="same as --format json")
    c.set_defaults(func=cmd_checklist)
    m = sub.add_parser("manifest", help="capture instructions per stack and device (never executed; exit 0 / 2)")
    m.add_argument("--stack", required=True, help="one of: %s" % ", ".join(sorted(STACKS)))
    m.add_argument("--screens", required=True, help="comma-separated screen names")
    m.add_argument("--devices", help="comma-separated device rows (default per stack); see `devices`")
    m.add_argument("--profile", help="style-profile.json to pick extra device rows from product.platforms")
    m.add_argument("--out", help="write the manifest JSON to this file")
    m.add_argument("--json", action="store_true", help="print JSON instead of the markdown table")
    m.set_defaults(func=cmd_manifest)
    v = sub.add_parser("devices", help="print the device matrix")
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_devices)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_usage(sys.stderr)
        return EXIT_USAGE
    try:
        return args.func(args)
    except Exception as e:  # never a traceback for the user: one error line, exit 2
        sys.stderr.write("error: %s: %s\n" % (e.__class__.__name__, e))
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
