#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic Visual Direction Profile (vdp/1) -> tokens.json derivation.

Implements references/token-derivation.md (v1). Stdlib only. Same profile + same seeds
=> byte-identical output. Every ``$value`` is a string so the design-system generator
(``generate-tokens.cjs``) never sees a falsy numeric zero.

Usage (standalone):
    python3 scripts/vd_tokens.py --profile style-profile.json [--seeds seeds.json] --out tokens.json
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys

DERIVATION_VERSION = "token-derivation.md v1"
TOKENS_SCHEMA = "vdp-tokens/1"
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# --------------------------------------------------------------------------- colour maths


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return "#%02X%02X%02X" % (int(round(r)), int(round(g)), int(round(b)))


def hex_to_hsl(h):
    r, g, b = (c / 255.0 for c in hex_to_rgb(h))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, ss * 100, ll * 100


def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, max(0, min(100, l)) / 100.0, max(0, min(100, s)) / 100.0)
    return rgb_to_hex(r * 255, g * 255, b * 255)


def rel_lum(h):
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex_to_rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgba(h, alpha):
    r, g, b = hex_to_rgb(h)
    return "rgba(%d, %d, %d, %s)" % (r, g, b, alpha)


def is_hex(value):
    return isinstance(value, str) and bool(HEX_RE.match(value))


# --------------------------------------------------------------------------- ramps (§1.1)
LIGHT_F = {"50": 0.97, "100": 0.92, "200": 0.82, "300": 0.66, "400": 0.40}
DARK_G = {"600": 0.20, "700": 0.40, "800": 0.60, "900": 0.80}
L_WHITE, L_DARK = 99.0, 10.0
STEPS = ("50", "100", "200", "300", "400", "500", "600", "700", "800", "900")


def hsl_chroma(s, l):
    """HSL chroma (0..1) from S and L in 0..100."""
    return (s / 100.0) * (1 - abs(2 * l / 100.0 - 1))


def ramp(seed_hex):
    h, s, l = hex_to_hsl(seed_hex)
    neutral = s < 10
    out = {}
    for step, f in LIGHT_F.items():
        ls = l + (L_WHITE - l) * f
        ss = s if neutral else s * (1 - 0.30 * f)
        out[step] = hsl_to_hex(h, ss, ls)
    out["500"] = seed_hex.upper()
    # Darker steps preserve the seed's HSL chroma C = S·(1 − |2L − 1|) instead of its saturation, so a pastel seed
    # (high S, high L, low C) darkens into a muted shade rather than neon; S never exceeds the seed's S.
    chroma = hsl_chroma(s, l)
    for step, g in DARK_G.items():
        ls = l - (l - L_DARK) * g
        denom = 1 - abs(2 * ls / 100.0 - 1)
        ss = s if denom <= 0 else min(s, 100.0 * chroma / denom)
        out[step] = hsl_to_hex(h, ss, ls)
    return dict((k, out[k]) for k in STEPS)


def on_color(fill_hex, dark_hex):
    """§2.2: pick the higher-contrast of white / neutral.900 (dark_hex)."""
    if rel_lum(dark_hex) > 0.03:
        dark_hex = "#111111"
    cw, cd = contrast(fill_hex, "#FFFFFF"), contrast(fill_hex, dark_hex)
    return ("{primitive.color.white}", cw) if cw >= cd else ("{primitive.color.neutral.900}", cd)


def pick_fill(ramp_dict, default_step, dark_hex):
    """Legacy §2.2 walk (darken until white passes); kept for callers that want the old behaviour."""
    step = default_step
    while True:
        ref, ratio = on_color(ramp_dict[step], dark_hex)
        if ratio >= 4.5 or step == "900":
            return step, ref, ratio
        step = STEPS[STEPS.index(step) + 1]


def best_on_candidate(fill_hex, candidates):
    """(ref, hex, ratio) of the candidate with the highest contrast on ``fill_hex``."""
    best = None
    for ref, hx in candidates:
        ratio = contrast(fill_hex, hx)
        if best is None or ratio > best[2]:
            best = (ref, hx, ratio)
    return best


def pick_fill_and_on(ramp_dict, default_step, candidates, last_resort=()):
    """§2.2 (revised): keep the fill when any candidate on-colour (seed text, neutral.900, white) reaches 4.5:1 —
    the highest-contrast passing candidate wins; ``last_resort`` (black) is tried only when none passes. Otherwise
    walk the fill one ramp step toward the opposite luminance of the best candidate until a pair passes.
    Returns (step, on_ref, ratio, walked) where ``walked`` is None or (from_hex, to_hex)."""
    step = default_step
    start = ramp_dict[step]
    while True:
        ref, hx, ratio = best_on_candidate(ramp_dict[step], candidates)
        if ratio < 4.5 and last_resort:
            ref2, hx2, ratio2 = best_on_candidate(ramp_dict[step], last_resort)
            if ratio2 >= 4.5:
                ref, hx, ratio = ref2, hx2, ratio2
        if ratio >= 4.5:
            return step, ref, ratio, (None if ramp_dict[step] == start else (start, ramp_dict[step]))
        idx = STEPS.index(step)
        towards_dark = rel_lum(hx) > rel_lum(ramp_dict[step])  # light candidate -> darken the fill
        nxt = idx + 1 if towards_dark else idx - 1
        if nxt < 0 or nxt >= len(STEPS):
            return step, ref, ratio, (None if ramp_dict[step] == start else (start, ramp_dict[step]))
        step = STEPS[nxt]


# --------------------------------------------------------------------------- seeds (§0.2)
SEED_SLOTS = ("brand", "secondary", "accent", "neutral", "success", "danger", "warning", "reward")
DEFAULT_SEEDS = {"brand": "#2563EB", "secondary": "#64748B", "accent": "#0EA5E9", "neutral": "#6B7280",
                 "success": "#16A34A", "danger": "#DC2626"}
DEFAULT_WARNING = "#F5A524"
DEFAULT_REWARD = "#FFC83D"  # AD-7: unseeded reward is its own gold, not an alias of warning


def derive_neutral(text_hex):
    """CC-9: a neutral seed derived from the catalog text colour (keeps its warm/cool tint)."""
    h, s, _l = hex_to_hsl(text_hex)
    return hsl_to_hex(h, min(s, 8.0), 50.0)


def seeds_from_catalog(seed_colors_cell):
    """CC-9: ``primary;secondary;accent;background;surface;text`` -> brand/secondary/accent/neutral."""
    parts = [p.strip() for p in str(seed_colors_cell or "").split(";") if p.strip()]
    if len(parts) != 6 or not all(is_hex(p) for p in parts):
        return {}
    return {"brand": parts[0].upper(), "secondary": parts[1].upper(), "accent": parts[2].upper(),
            "neutral": derive_neutral(parts[5])}


def surfaces_from_catalog(seed_colors_cell):
    """CC-9 positions 4-6: ``…;background;surface;text`` -> palette.surfaces (authoritative, not approximated)."""
    parts = [p.strip() for p in str(seed_colors_cell or "").split(";") if p.strip()]
    if len(parts) != 6 or not all(is_hex(p) for p in parts):
        return {}
    return {"background": parts[3].upper(), "surface": parts[4].upper(), "text": parts[5].upper()}


def derive_outline_surface(surfaces, color_rule):
    """Outline colour for a surface set, per shape.outline.color_rule (None when the rule gives no colour)."""
    base = surfaces.get("surface") or surfaces.get("background")
    if not base or not is_hex(base):
        return None
    h, sat, l = hex_to_hsl(base)
    if color_rule == "darker-shade-of-fill":
        return hsl_to_hex(h, sat, max(l - 25, 5))
    if color_rule == "lighter-tint-of-fill":
        return hsl_to_hex(h, sat, min(l + 15, 97))
    if color_rule == "contrast-dark":
        return surfaces.get("text") if is_hex(surfaces.get("text", "")) else None
    return None


def seeds_from_design_system(ds):
    """§0.2 priority 2: output of ``search.py --design-system --json``."""
    if isinstance(ds, dict) and isinstance(ds.get("design_system"), dict):
        ds = ds["design_system"]
    colors = (ds or {}).get("colors") or {}
    mapping = {"primary": "brand", "secondary": "secondary", "accent": "accent",
               "muted_foreground": "neutral", "destructive": "danger", "success": "success"}
    out = {}
    for src, slot in mapping.items():
        value = colors.get(src)
        if is_hex(value):
            out[slot] = value.upper()
    return out


def seeds_from_palette_observed(palette_observed):
    """§0.2 priority 3: ``palette_observed`` of a reference analysis; highest share wins per role."""
    mapping = {"primary": "brand", "secondary": "secondary", "accent": "accent", "cta": "accent",
               "text": "neutral", "neutral": "neutral"}
    best = {}
    for entry in palette_observed or []:
        if not isinstance(entry, dict):
            continue
        slot = mapping.get(str(entry.get("role_guess", "")).lower())
        hx = entry.get("hex")
        if not slot or not is_hex(hx):
            continue
        share = float(entry.get("share") or 0)
        if slot not in best or share > best[slot][0]:
            best[slot] = (share, hx.upper())
    out = dict((slot, hx) for slot, (_s, hx) in best.items())
    if "neutral" in out:
        out["neutral"] = derive_neutral(out["neutral"])
    return out


def resolve_seeds(profile, extra=None):
    """Merge seed sources: profile.palette.seeds > ``extra`` (catalog / design-system) > constants."""
    seeds = dict(DEFAULT_SEEDS)
    for source in (extra or {}, ((profile.get("palette") or {}).get("seeds") or {})):
        for slot, value in source.items():
            if slot in SEED_SLOTS and is_hex(value):
                seeds[slot] = value.upper()
    seeds.setdefault("warning", DEFAULT_WARNING)
    return seeds


# --------------------------------------------------------------------------- platform unit (§0.3)
STACK_UNIT = {
    "flutter": "logical", "flutter-flame": "logical", "react-native": "logical",
    "swiftui": "pt", "jetpack-compose": "dp",
    "unity-ugui": "px", "unity-ui-toolkit": "px",
    "react": "px", "nextjs": "px", "vue": "px", "svelte": "px", "html-tailwind": "px",
}
TOUCH_MIN = {"mobile-ios": 44, "mobile-android": 48, "web": 24, "desktop": 24, "tablet": 44}
TOUCH_REC = {"mobile-ios": 44, "mobile-android": 48, "web": 44, "desktop": 32, "tablet": 44}


def platform_unit(profile):
    stack = (profile.get("product") or {}).get("stack")
    if stack in STACK_UNIT:
        return STACK_UNIT[stack]
    plats = set((profile.get("product") or {}).get("platforms") or [])
    if plats & {"web", "desktop"}:
        return "px"
    if plats == {"mobile-ios"}:
        return "pt"
    return "dp"


def dim(value, unit):
    if value == 0:
        return "0"
    return str(value) if unit == "logical" else "%s%s" % (value, unit)


# --------------------------------------------------------------------------- scales (§1.x)
SPACING = {"0": 0, "1": 4, "2": 8, "3": 12, "4": 16, "5": 20, "6": 24, "8": 32, "10": 40, "12": 48,
           "16": 64, "20": 80, "24": 96}
RADIUS = {"none": 0, "xs": 2, "sm": 4, "md": 8, "lg": 12, "xl": 16, "2xl": 24, "3xl": 32, "full": 9999}
RADIUS_CLASS = {  # control, container, popup, tile, chip (§2.3)
    "none": ("none", "none", "none", "none", "none"),
    "sm": ("sm", "md", "md", "xs", "sm"),
    "md": ("md", "lg", "lg", "sm", "md"),
    "lg": ("lg", "xl", "2xl", "md", "full"),
    "xl": ("xl", "2xl", "3xl", "lg", "full"),
    "pill": ("full", "2xl", "3xl", "lg", "full"),
}
OUTLINE = {"none": 0, "thin": 1, "regular": 2, "strong": 3, "heavy": 4}
FONT_APP = {"xs": 12, "sm": 14, "base": 16, "lg": 18, "xl": 20, "2xl": 24, "3xl": 30, "4xl": 36, "display": 48}
FONT_GAME = {"xs": 12, "sm": 14, "base": 16, "lg": 18, "xl": 22, "2xl": 28, "3xl": 36, "4xl": 48, "display": 64}
LINE_HEIGHT = {"tight": "1.1", "snug": "1.25", "normal": "1.5", "relaxed": "1.65"}
ICON_APP = {"sm": 16, "md": 24, "lg": 32, "xl": 48}
ICON_GAME = {"sm": 20, "md": 28, "lg": 40, "xl": 64}
# §1.10 + CC-8: reward = the "medium" reward beat, ambient = the ambient loop period (motion-direction.md §2)
DURATION = {
    "static": {"instant": 0, "fast": 0, "base": 0, "slow": 0, "reveal": 0, "reward": 0, "ambient": 0},
    "snappy": {"instant": 0, "fast": 80, "base": 140, "slow": 220, "reveal": 320, "reward": 600, "ambient": 4000},
    "soft": {"instant": 0, "fast": 150, "base": 250, "slow": 400, "reveal": 600, "reward": 650, "ambient": 3000},
    "bouncy": {"instant": 0, "fast": 120, "base": 200, "slow": 350, "reveal": 600, "reward": 750, "ambient": 2500},
    "dramatic": {"instant": 0, "fast": 200, "base": 400, "slow": 700, "reveal": 1000, "reward": 750, "ambient": 2000},
}
DURATION_KEYS = ("instant", "fast", "base", "slow", "reveal", "reward", "ambient")
EASING = {
    "static": {"standard": "linear", "enter": "linear", "exit": "linear", "emphasized": "linear"},
    "snappy": {"standard": "cubic-bezier(0.2, 0, 0, 1)", "enter": "cubic-bezier(0, 0, 0.2, 1)",
               "exit": "cubic-bezier(0.4, 0, 1, 1)", "emphasized": "cubic-bezier(0.2, 0, 0, 1)"},
    "soft": {"standard": "cubic-bezier(0.4, 0, 0.2, 1)", "enter": "cubic-bezier(0, 0, 0.2, 1)",
             "exit": "cubic-bezier(0.4, 0, 1, 1)", "emphasized": "cubic-bezier(0.25, 0.1, 0.25, 1)"},
    "bouncy": {"standard": "cubic-bezier(0.22, 1, 0.36, 1)", "enter": "cubic-bezier(0.34, 1.56, 0.64, 1)",
               "exit": "cubic-bezier(0.36, 0, 0.66, -0.56)", "emphasized": "cubic-bezier(0.68, -0.6, 0.32, 1.6)"},
    "dramatic": {"standard": "cubic-bezier(0.16, 1, 0.3, 1)", "enter": "cubic-bezier(0.16, 1, 0.3, 1)",
                 "exit": "cubic-bezier(0.7, 0, 0.84, 0)", "emphasized": "cubic-bezier(0.87, 0, 0.13, 1)"},
}
EASING_NAME = {"static": "linear", "snappy": "standard-decelerate", "soft": "ease-in-out-soft",
               "bouncy": "spring-soft", "dramatic": "expo-out"}
ZINDEX = {"base": "0", "raised": "10", "sticky": "50", "hud": "100", "overlay": "200", "popup": "300",
          "toast": "400", "tutorial": "500", "debug": "1000"}
OPACITY = {"disabled": "0.4", "hover": "0.92", "pressed": "0.85", "loading": "0.7", "scrim": "0.5",
           "scrimHeavy": "0.7", "muted": "0.7", "ghost": "0.12", "focusRing": "0.35"}
SHADOW_KINDS = ("none", "offset-soft", "soft-ambient", "hard-offset", "double-clay", "glow")
PRESSED_OFFSET = {"none": 0, "offset-soft": 1, "soft-ambient": 1, "hard-offset": 2, "double-clay": 4, "glow": 0}
DRIFT_BUDGET = {"color": 0, "fontFamily": 0, "radius": 1, "spacing": 2, "fontSize": 2, "shadow": 0,
                "duration": 1, "iconLibrary": 0}

REQUIRED_PRIMITIVE_GROUPS = ("color", "spacing", "radius", "outline", "shadow", "fontSize", "lineHeight",
                             "iconSize", "touchTarget", "duration", "easing", "zIndex", "opacity")
REQUIRED_SEMANTIC_COLORS = ("primary", "onPrimary", "secondary", "onSecondary", "accent", "onAccent",
                            "background", "surface", "surfaceElevated", "border", "overlay", "text",
                            "textMuted", "success", "warning", "danger", "reward")
REQUIRED_STATES = ("hover", "pressed", "focus", "disabled")


def normalize_shadow_kind(value):
    """Map a free-text ``rendering.shadow`` to one of the six derivation kinds."""
    v = str(value or "none").strip().lower()
    if v in SHADOW_KINDS:
        return v
    if v in ("", "no", "flat"):
        return "none"
    if "glow" in v:
        return "glow"
    if "clay" in v or ("hard" in v and "soft" in v):
        return "double-clay"
    if "hard" in v:
        return "hard-offset"
    if "ambient" in v or "subtle" in v or "minimal" in v:
        return "soft-ambient"
    if "soft" in v or "offset" in v or "blur" in v:
        return "offset-soft"
    return "none"


def shadow_set(kind, neutral900, brand500, tint=None):
    """Primitive shadows. AD-9: the soft/ambient/clay layers are tinted with ``tint`` (neutral.900 by default) instead of
    pure black, so elevation shares the outline/neutral family; pass "#000000" for styles that ask for black."""
    tint = tint or "#000000"
    r, g, b = hex_to_rgb(tint)
    out = _shadow_set_black(kind, neutral900, brand500)
    if tint.upper() == "#000000":
        return out
    return dict((k, v.replace("rgba(0, 0, 0,", "rgba(%d, %d, %d," % (r, g, b))) for k, v in out.items())


def _shadow_set_black(kind, neutral900, brand500):
    if kind == "none":
        return {"none": "none", "sm": "none", "md": "none", "lg": "none", "inset": "none"}
    if kind == "offset-soft":
        return {"none": "none", "sm": "0 2px 4px rgba(0, 0, 0, 0.12)", "md": "0 4px 8px rgba(0, 0, 0, 0.14)",
                "lg": "0 8px 16px rgba(0, 0, 0, 0.16)", "inset": "inset 0 2px 4px rgba(0, 0, 0, 0.15)"}
    if kind == "soft-ambient":
        return {"none": "none", "sm": "0 1px 2px rgba(0, 0, 0, 0.05)", "md": "0 4px 12px rgba(0, 0, 0, 0.08)",
                "lg": "0 12px 32px rgba(0, 0, 0, 0.12)", "inset": "inset 0 1px 2px rgba(0, 0, 0, 0.06)"}
    if kind == "hard-offset":
        n = neutral900
        return {"none": "none", "sm": "2px 2px 0 %s" % n, "md": "4px 4px 0 %s" % n, "lg": "6px 6px 0 %s" % n,
                "inset": "inset 2px 2px 0 %s" % n}
    if kind == "double-clay":
        return {"none": "none", "sm": "0 2px 0 rgba(0, 0, 0, 0.25), 0 4px 6px rgba(0, 0, 0, 0.12)",
                "md": "0 4px 0 rgba(0, 0, 0, 0.25), 0 8px 12px rgba(0, 0, 0, 0.14)",
                "lg": "0 6px 0 rgba(0, 0, 0, 0.25), 0 12px 20px rgba(0, 0, 0, 0.18)",
                "inset": "inset 0 3px 0 rgba(0, 0, 0, 0.18)"}
    if kind == "glow":
        return {"none": "none", "sm": "0 0 6px %s" % rgba(brand500, 0.35), "md": "0 0 12px %s" % rgba(brand500, 0.45),
                "lg": "0 0 24px %s" % rgba(brand500, 0.55), "inset": "inset 0 0 8px %s" % rgba(brand500, 0.3)}
    raise ValueError("unknown rendering.shadow %r" % kind)


def bezier_overshoots(value):
    """True when a cubic-bezier's y control points leave [0, 1] (the curve passes its target)."""
    m = re.match(r"cubic-bezier\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)", str(value or ""))
    if not m:
        return False
    y1, y2 = float(m.group(2)), float(m.group(4))
    return not (0.0 <= y1 <= 1.0 and 0.0 <= y2 <= 1.0)


def interaction_steps(step):
    """(hover, pressed, edge) ramp steps for a filled control (AD-3). Normal fills go darker: hover +1, pressed +2,
    edge (outline / hard shadow) +3, so the pressed fill never equals the outline or the shadow. Fills at 700+ have no
    room for three darker steps: hover/pressed go lighter and the edge takes the darkest free step."""
    i = STEPS.index(step)
    if i + 3 < len(STEPS):
        return STEPS[i + 1], STEPS[i + 2], STEPS[i + 3]
    hover, pressed = STEPS[max(i - 1, 0)], STEPS[max(i - 2, 0)]
    edge = STEPS[-1] if i < len(STEPS) - 1 else STEPS[i - 3]
    return hover, pressed, edge


def clay_shadow(step, fill700, tint="#000000"):
    """Component-level double-clay shadow: hard layer in the fill's edge colour, soft layer in the shadow tint (AD-9)."""
    soft = rgba(tint, {"sm": 0.12, "md": 0.14, "lg": 0.18}[step])
    return {"sm": "0 2px 0 %s, 0 4px 6px %s", "md": "0 4px 0 %s, 0 8px 12px %s",
            "lg": "0 6px 0 %s, 0 12px 20px %s"}[step] % (fill700, soft)


def tok(value, typ, desc=None):
    t = {"$value": str(value), "$type": typ}
    if desc:
        t["$description"] = desc
    return t


# --------------------------------------------------------------------------- reference resolution
REF_RE = re.compile(r"^\{([A-Za-z0-9_.$-]+)\}$")


def is_reference(value):
    return isinstance(value, str) and bool(REF_RE.match(value))


def lookup(tokens, path):
    """Return the node at ``a.b.c`` or None."""
    node = tokens
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def resolve_ref(tokens, value, max_hops=10):
    """Resolve ``{a.b.c}`` chains to the final ``$value``; raise KeyError on a dangling or cyclic ref."""
    hops = 0
    seen = []
    while is_reference(value):
        path = REF_RE.match(value).group(1)
        if path in seen or hops >= max_hops:
            raise KeyError("token reference cycle at %s" % value)
        seen.append(path)
        node = lookup(tokens, path)
        if not isinstance(node, dict) or "$value" not in node:
            raise KeyError("unresolved token reference %s" % value)
        value = node["$value"]
        hops += 1
    return value


def iter_leaves(node, prefix=()):
    """Yield (path_tuple, leaf) for every ``{"$value": ...}`` leaf."""
    if isinstance(node, dict):
        if "$value" in node:
            yield prefix, node
            return
        for key, child in node.items():
            if key.startswith("$"):
                continue
            for item in iter_leaves(child, prefix + (key,)):
                yield item


# --------------------------------------------------------------------------- main derivation


def derive_tokens(profile, seeds=None):
    """Build the three-layer tokens dict. ``seeds`` overrides profile.palette.seeds + constants."""
    product = profile.get("product") or {}
    kind = product.get("kind", "app")
    game = kind == "game"
    unit = platform_unit(profile)
    plats = list(product.get("platforms") or ["mobile-android"])
    rendering = profile.get("rendering") or {}
    shading = rendering.get("shading", "flat")
    shadow_kind = normalize_shadow_kind(rendering.get("shadow", "none"))
    shape = profile.get("shape") or {}
    radius_class = shape.get("radius_class", "md")
    outline = shape.get("outline") or {}
    outline_w = outline.get("width") or 0
    outline_rule = outline.get("color_rule") or "none"
    motion = profile.get("motion") or {}
    motion_class = motion.get("class", "soft")
    strategy = str(profile.get("palette_strategy") or "").lower()
    style_id = (profile.get("style") or {}).get("id", "unknown")
    typography = profile.get("typography") or {}

    explicit = set(k for k, v in (seeds or {}).items() if k in SEED_SLOTS and is_hex(v))
    explicit |= set(k for k, v in (((profile.get("palette") or {}).get("seeds")) or {}).items() if k in SEED_SLOTS and is_hex(v))
    seeds = resolve_seeds(profile, seeds)
    seeds.setdefault("reward", DEFAULT_REWARD)
    ramps = dict((name, ramp(seeds[name])) for name in ("brand", "secondary", "accent", "neutral", "success", "warning", "danger", "reward"))
    n900 = ramps["neutral"]["900"]
    if rel_lum(n900) > 0.03:
        ramps["neutral"]["900"] = "#111111"
        n900 = "#111111"

    # ---- primitives
    color = dict((name, dict((step, tok(hx, "color")) for step, hx in r.items())) for name, r in ramps.items())
    color["white"] = tok("#FFFFFF", "color")
    color["black"] = tok("#000000", "color")

    fonts = FONT_GAME if game else FONT_APP
    icons = ICON_GAME if game else ICON_APP
    touch_min = max(TOUCH_MIN.get(p, 44) for p in plats)
    touch_rec = max(TOUCH_REC.get(p, 44) for p in plats)
    durations = dict(DURATION[motion_class])
    scale = motion.get("duration_scale")
    if isinstance(scale, dict):
        for key, value in scale.items():
            if key in DURATION_KEYS and isinstance(value, (int, float)) and not isinstance(value, bool):
                durations[key] = int(value)
    easing = EASING[motion_class]
    shadow_tint = "#000000" if str(rendering.get("shadow_tint") or "").lower() == "black" else n900
    shadows = shadow_set(shadow_kind, n900, ramps["brand"]["500"], shadow_tint)
    outline_key = min(OUTLINE, key=lambda k: (abs(OUTLINE[k] - outline_w), OUTLINE[k]))

    primitive = {
        "color": color,
        "spacing": dict((k, tok(dim(v, unit), "dimension")) for k, v in SPACING.items()),
        "radius": dict((k, tok(dim(v, unit), "dimension")) for k, v in RADIUS.items()),
        "outline": dict((k, tok(dim(v, unit), "dimension")) for k, v in OUTLINE.items()),
        "shadow": dict((k, tok(v, "shadow")) for k, v in shadows.items()),
        "fontSize": dict((k, tok(dim(v, unit), "dimension")) for k, v in fonts.items()),
        "lineHeight": dict((k, tok(v, "number")) for k, v in LINE_HEIGHT.items()),
        "iconSize": dict((k, tok(dim(v, unit), "dimension")) for k, v in icons.items()),
        "touchTarget": {"min": tok(dim(touch_min, unit), "dimension"), "recommended": tok(dim(touch_rec, unit), "dimension")},
        "duration": dict((k, tok("%sms" % durations[k], "duration")) for k in DURATION_KEYS),
        "easing": dict((k, tok(v, "cubicBezier", "%s (%s)" % (EASING_NAME[motion_class], k))) for k, v in easing.items()),
        "zIndex": dict((k, tok(v, "number")) for k, v in ZINDEX.items()),
        "opacity": dict((k, tok(v, "number")) for k, v in OPACITY.items()),
        "fontFamily": {
            "display": tok(typography.get("display") or "sans-serif", "fontFamily"),
            "body": tok(typography.get("body") or typography.get("display") or "sans-serif", "fontFamily"),
        },
    }

    # ---- semantic colour (§2)
    surfaces = (profile.get("palette") or {}).get("surfaces") or {}
    surfaces = dict((k, v.upper()) for k, v in surfaces.items() if k in ("background", "surface", "text", "outline") and is_hex(v))
    dark_first = "dark" in strategy and "supports-dark" not in strategy and not surfaces
    if dark_first:
        background, surface, surface_el, border = ("{primitive.color.neutral.900}", "{primitive.color.neutral.800}",
                                                   "{primitive.color.neutral.700}", "{primitive.color.neutral.700}")
        text, text_muted = "{primitive.color.neutral.50}", "{primitive.color.neutral.300}"
    else:
        background = "{primitive.color.brand.50}" if "pastel-base" in strategy else "{primitive.color.neutral.50}"
        surface = "{primitive.color.white}"
        surface_el = "{primitive.color.neutral.100}" if shading == "flat" else "{primitive.color.white}"
        border = "{primitive.color.neutral.300}" if game else "{primitive.color.neutral.200}"
        text, text_muted = "{primitive.color.neutral.900}", "{primitive.color.neutral.600}"

    if surfaces:
        bg_hex = surfaces.get("background") or surfaces.get("surface")
        dark_bg = bg_hex is not None and rel_lum(bg_hex) < 0.18
        if "background" in surfaces:
            background = surfaces["background"]
        if "surface" in surfaces:
            surface = surfaces["surface"]
            surface_el = surfaces["surface"] if shading != "flat" else surface_el
        if "outline" in surfaces:
            border = surfaces["outline"]
        elif outline_rule == "darker-shade-of-fill" and bg_hex:
            hh, ss, ll = hex_to_hsl(bg_hex)
            border = "{primitive.color.neutral.700}" if dark_bg else hsl_to_hex(hh, ss, max(ll - 12, 5))
        elif outline_rule == "lighter-tint-of-fill":
            border = "{primitive.color.brand.200}"
        elif outline_rule == "contrast-dark":
            border = surfaces["text"] if "text" in surfaces else "{primitive.color.neutral.900}"
        elif dark_bg:
            border = "{primitive.color.neutral.700}"
        if "text" in surfaces and bg_hex and contrast(surfaces["text"], bg_hex) >= 4.5:
            text = surfaces["text"]
        if dark_bg:
            text_muted = "{primitive.color.neutral.300}"
            if "surface" in surfaces:  # dark themes elevate by a lighter tint of the surface, flat shading included
                surface_el = hsl_to_hex(*(lambda hsl: (hsl[0], hsl[1], min(hsl[2] + 6, 95)))(hex_to_hsl(surfaces["surface"])))
            if "text" not in surfaces or contrast(surfaces.get("text", "#000000"), bg_hex) < 4.5:
                text = "{primitive.color.neutral.50}"
        elif bg_hex:
            for step in ("600", "700", "800", "900"):
                text_muted = "{primitive.color.neutral.%s}" % step
                if contrast(ramps["neutral"][step], bg_hex) >= 4.5:
                    break
    if not surfaces and not dark_first and outline_rule == "contrast-dark":
        border = "{primitive.color.neutral.900}"
    reward_name = "reward" if "reward" in ramps else "warning"
    on_candidates = []
    if is_hex(surfaces.get("text", "")):
        on_candidates.append((surfaces["text"], surfaces["text"]))
    on_candidates += [("{primitive.color.neutral.900}", n900), ("{primitive.color.white}", "#FFFFFF")]
    last_resort = [("{primitive.color.black}", "#000000")]
    contrast_notes = []

    def pick(role, name, default_step):
        step, ref, ratio, walked = pick_fill_and_on(ramps[name], default_step, on_candidates, last_resort)
        if walked:
            direction = "darkened" if rel_lum(walked[1]) < rel_lum(walked[0]) else "lightened"
            contrast_notes.append("%s: fill %s from %s to %s for contrast (%.2f:1 on %s)" % (role, direction, walked[0], walked[1], ratio, ref))
        if ref == "{primitive.color.black}":
            contrast_notes.append("%s: on-colour is #000000 because it is the only candidate reaching 4.5:1 on %s (seed text, neutral.900 and white fail); "
                                  "styles that forbid pure black should seed a darker text colour or adjust the fill" % (role, ramps[name][step]))
        return step, ref, ratio

    # Built-in status colours (not seeded by the style, reference, design-system seed or --seeds) use the same candidates
    # as every fill (seed text, neutral.900, white) but never #000000: only when none of them passes does the fill walk
    # darker one ramp step. Seeded fills keep the "never change the fill" rule above (black only as the last resort).
    status_candidates = list(on_candidates)

    def pick_status(role, name, default_step):
        if name in explicit:
            return pick(role, name, default_step)
        step = default_step
        start = ramps[name][step]
        while True:
            ref, hx, ratio = best_on_candidate(ramps[name][step], status_candidates)
            if ratio >= 4.5:
                break
            if step == STEPS[-1]:
                return pick(role, name, step)
            step = STEPS[STEPS.index(step) + 1]
        if ramps[name][step] != start:
            contrast_notes.append("%s: built-in status fill darkened from %s to %s for contrast (%.2f:1 on %s)" % (role, start, ramps[name][step], ratio, ref))
        return step, ref, ratio

    p_step, p_on, _ = pick("primary", "brand", "500")
    s_step, s_on, _ = pick("secondary", "secondary", "500")
    a_step, a_on, _ = pick("accent", "accent", "500")
    ok_step, ok_on, _ = pick_status("success", "success", "600")
    w_step, w_on, _ = pick_status("warning", "warning", "500")
    d_step, d_on, _ = pick_status("danger", "danger", "600")
    r_step, r_on, _ = pick_status("reward", "reward", "500")  # unseeded reward behaves like a built-in status colour

    p_hover, p_pressed, p_edge = interaction_steps(p_step)

    sem_color = {
        "primary": tok("{primitive.color.brand.%s}" % p_step, "color"),
        "onPrimary": tok(p_on, "color"),
        "primaryHover": tok("{primitive.color.brand.%s}" % p_hover, "color"),
        "primaryPressed": tok("{primitive.color.brand.%s}" % p_pressed, "color"),
        "secondary": tok("{primitive.color.secondary.%s}" % s_step, "color"),
        "onSecondary": tok(s_on, "color"),
        "accent": tok("{primitive.color.accent.%s}" % a_step, "color"),
        "onAccent": tok(a_on, "color"),
        "background": tok(background, "color"),
        "surface": tok(surface, "color"),
        "surfaceElevated": tok(surface_el, "color"),
        "border": tok(border, "color"),
        "overlay": tok(rgba(n900, OPACITY["scrim"]), "color"),
        "text": tok(text, "color"),
        "textMuted": tok(text_muted, "color"),
        "success": tok("{primitive.color.success.%s}" % ok_step, "color"),
        "onSuccess": tok(ok_on, "color"),
        "warning": tok("{primitive.color.warning.%s}" % w_step, "color"),
        "onWarning": tok(w_on, "color"),
        "danger": tok("{primitive.color.danger.%s}" % d_step, "color"),
        "onDanger": tok(d_on, "color"),
        "reward": tok("{primitive.color.%s.%s}" % (reward_name, r_step), "color"),
        "onReward": tok(r_on, "color"),
        "focusRing": tok("{primitive.color.brand.400}", "color"),
    }

    ctrl, cont, pop, tile, chip = RADIUS_CLASS[radius_class]
    sem_radius = dict((k, tok("{primitive.radius.%s}" % v, "dimension")) for k, v in
                      (("control", ctrl), ("container", cont), ("popup", pop), ("tile", tile), ("chip", chip)))

    if outline_rule == "darker-shade-of-fill":
        outline_color_rule = "fill+3"
    elif outline_rule == "lighter-tint-of-fill":
        outline_color_rule = "fill.200"
    elif outline_rule == "contrast-dark":
        outline_color_rule = "neutral.900"
    elif outline_rule == "border-token":
        outline_color_rule = "semantic.color.border"
    else:
        outline_color_rule = "none"

    elevated_by = {"flat": "tint", "soft": "shadow", "soft-cel": "shadow", "glossy": "shadow", "clay": "shadow",
                   "cel": "outline", "pixel": "outline", "painterly": "shadow", "realistic": "shadow"}[shading]
    elevated_shadow = "lg" if shading in ("painterly", "realistic") else ("none" if elevated_by != "shadow" else "md")

    pressed_off = PRESSED_OFFSET[shadow_kind]
    semantic = {
        "color": sem_color,
        "radius": sem_radius,
        "outline": {
            "control": tok("{primitive.outline.%s}" % outline_key, "dimension"),
            "colorRule": tok(outline_color_rule, "string"),
        },
        "elevation": {
            "method": tok(elevated_by, "string"),
            "raised": tok("{primitive.shadow.sm}" if elevated_by == "shadow" else "{primitive.shadow.none}", "shadow"),
            "elevated": tok("{primitive.shadow.%s}" % elevated_shadow, "shadow"),
            "floating": tok("{primitive.shadow.lg}" if elevated_by == "shadow" else "{primitive.shadow.md}", "shadow"),
        },
        "state": {
            "hover": {"opacity": tok("{primitive.opacity.hover}", "number"), "offsetY": tok(dim(0, unit), "dimension"),
                      "color": tok("{semantic.color.primaryHover}", "color")},
            "pressed": {"opacity": tok("{primitive.opacity.pressed}", "number"), "offsetY": tok(dim(pressed_off, unit), "dimension"),
                        "shadow": tok("{primitive.shadow.inset}" if shadow_kind in ("offset-soft", "soft-ambient") else "{primitive.shadow.none}", "shadow"),
                        "color": tok("{semantic.color.primaryPressed}", "color")},
            "focus": {"ringWidth": tok(dim(3, unit), "dimension"), "ringColor": tok("{semantic.color.focusRing}", "color"),
                      "ringOffset": tok(dim(2, unit), "dimension")},
            "disabled": {"opacity": tok("{primitive.opacity.disabled}", "number"), "offsetY": tok(dim(0, unit), "dimension"),
                         "shadow": tok("{primitive.shadow.none}", "shadow")},
        },
        "typography": {
            "display": {"fontFamily": tok("{primitive.fontFamily.display}", "fontFamily"), "fontSize": tok("{primitive.fontSize.display}", "dimension"),
                        "lineHeight": tok("{primitive.lineHeight.tight}", "number"), "fontWeight": tok("700", "fontWeight")},
            "title": {"fontFamily": tok("{primitive.fontFamily.display}", "fontFamily"), "fontSize": tok("{primitive.fontSize.2xl}", "dimension"),
                      "lineHeight": tok("{primitive.lineHeight.snug}", "number"), "fontWeight": tok("700", "fontWeight")},
            "body": {"fontFamily": tok("{primitive.fontFamily.body}", "fontFamily"), "fontSize": tok("{primitive.fontSize.base}", "dimension"),
                     "lineHeight": tok("{primitive.lineHeight.normal}", "number"), "fontWeight": tok("500" if game else "400", "fontWeight")},
            "label": {"fontFamily": tok("{primitive.fontFamily.body}", "fontFamily"), "fontSize": tok("{primitive.fontSize.sm}", "dimension"),
                      "lineHeight": tok("{primitive.lineHeight.snug}", "number"), "fontWeight": tok("600", "fontWeight")},
            "caption": {"fontFamily": tok("{primitive.fontFamily.body}", "fontFamily"), "fontSize": tok("{primitive.fontSize.xs}", "dimension"),
                        "lineHeight": tok("{primitive.lineHeight.snug}", "number"), "fontWeight": tok("500", "fontWeight")},
        },
        "spacing": {
            "inset": tok("{primitive.spacing.4}", "dimension"),
            "stack": tok("{primitive.spacing.3}", "dimension"),
            "inline": tok("{primitive.spacing.2}", "dimension"),
            "section": tok("{primitive.spacing.8}", "dimension"),
            "screenGutter": tok("{primitive.spacing.%s}" % ("4" if game else "5"), "dimension"),
        },
    }

    # ---- component layer (§3)
    # AD-2: one outline family per profile. Filled controls take their own ramp (edge step, see interaction_steps);
    # every surface-filled element (popup, tile, card, HUD chip, icon button, progress, secondary button) takes the
    # single surface-outline colour `semantic.color.border`. A brand/accent outline on a surface appears only when the
    # profile says so explicitly (shape.outline.secondary_button = "primary").
    surface_outline = "transparent" if outline_color_rule == "none" else "{semantic.color.border}"

    def filled_outline(fill_name, fill_step):
        edge = interaction_steps(fill_step)[2]
        return {"fill+3": "{primitive.color.%s.%s}" % (fill_name, edge), "fill.200": "{primitive.color.%s.200}" % fill_name,
                "neutral.900": "{semantic.color.border}", "semantic.color.border": "{semantic.color.border}",
                "none": "transparent"}[outline_color_rule]

    def comp_shadow(fill_name, step, edge_hex=None):
        if shadow_kind == "double-clay":
            return clay_shadow(step, edge_hex or ramps[fill_name]["700"], shadow_tint)
        if elevated_by == "shadow":
            return "{primitive.shadow.%s}" % step
        return "{primitive.shadow.none}"

    secondary_explicit = str((shape.get("outline") or {}).get("secondary_button") or "").lower() == "primary"
    secondary_outline = "{semantic.color.primary}" if secondary_explicit else (
        "{semantic.color.border}" if surface_outline == "transparent" else surface_outline)

    btn_h = 56 if game else 44
    btn_px = "6" if game else "5"
    component = {
        "button": {
            "primary": {
                "bg": tok("{semantic.color.primary}", "color"), "fg": tok("{semantic.color.onPrimary}", "color"),
                "bgHover": tok("{semantic.color.primaryHover}", "color"), "bgPressed": tok("{semantic.color.primaryPressed}", "color"),
                "outlineWidth": tok("{primitive.outline.none}" if outline_color_rule in ("none", "semantic.color.border") else "{semantic.outline.control}", "dimension"),
                "outlineColor": tok("transparent" if outline_color_rule in ("none", "semantic.color.border") else filled_outline("brand", p_step), "color"),
                "radius": tok("{semantic.radius.control}", "dimension"), "shadow": tok(comp_shadow("brand", "md", ramps["brand"][p_edge]), "shadow"),
                "height": tok(dim(btn_h, unit), "dimension"), "paddingX": tok("{primitive.spacing.%s}" % btn_px, "dimension"),
                "fontSize": tok("{primitive.fontSize.%s}" % ("xl" if game else "base"), "dimension"),
                "fontWeight": tok("700", "fontWeight"), "pressedOffsetY": tok("{semantic.state.pressed.offsetY}", "dimension"),
                "minWidth": tok(dim(160 if game else 96, unit), "dimension"),
            },
            "secondary": {
                "bg": tok("{semantic.color.surface}", "color"), "fg": tok("{semantic.color.primary}", "color"),
                "bgHover": tok("{primitive.color.brand.50}", "color"), "bgPressed": tok("{primitive.color.brand.100}", "color"),
                "outlineWidth": tok("{semantic.outline.control}" if outline_w else "{primitive.outline.regular}", "dimension"),
                "outlineColor": tok(secondary_outline, "color"),
                "radius": tok("{semantic.radius.control}", "dimension"),
                "shadow": tok("{primitive.shadow.none}" if shadow_kind != "double-clay" else comp_shadow("neutral", "sm"), "shadow"),
                "height": tok(dim(btn_h, unit), "dimension"), "paddingX": tok("{primitive.spacing.%s}" % btn_px, "dimension"),
                "fontSize": tok("{primitive.fontSize.%s}" % ("xl" if game else "base"), "dimension"),
                "fontWeight": tok("700" if game else "600", "fontWeight"),
            },
            "icon": {
                "size": tok("{primitive.touchTarget.recommended}", "dimension"), "iconSize": tok("{primitive.iconSize.md}", "dimension"),
                "bg": tok("{semantic.color.surface}" if game else "transparent", "color"), "fg": tok("{semantic.color.text}", "color"),
                "radius": tok("{primitive.radius.full}" if radius_class in ("lg", "xl", "pill") else "{semantic.radius.control}", "dimension"),
                "outlineWidth": tok("{semantic.outline.control}" if game else "{primitive.outline.none}", "dimension"),
                "outlineColor": tok(surface_outline if game else "transparent", "color"),
                "shadow": tok(comp_shadow("neutral", "sm") if game else "{primitive.shadow.none}", "shadow"),
            },
        },
        "card": {
            "bg": tok("{semantic.color.surface}", "color"), "fg": tok("{semantic.color.text}", "color"),
            "radius": tok("{semantic.radius.container}", "dimension"), "padding": tok("{primitive.spacing.%s}" % ("5" if game else "4"), "dimension"),
            "borderWidth": tok("{primitive.outline.thin}" if elevated_by != "shadow" or not game else "{semantic.outline.control}", "dimension"),
            "borderColor": tok("{semantic.color.border}", "color"), "shadow": tok("{semantic.elevation.raised}", "shadow"),
            "gap": tok("{primitive.spacing.3}", "dimension"),
        },
        "popup": {
            "bg": tok("{semantic.color.surfaceElevated}", "color"), "fg": tok("{semantic.color.text}", "color"),
            "radius": tok("{semantic.radius.popup}", "dimension"), "padding": tok("{primitive.spacing.%s}" % ("6" if game else "5"), "dimension"),
            "shadow": tok("{semantic.elevation.floating}", "shadow"), "scrim": tok("{semantic.color.overlay}", "color"),
            "outlineWidth": tok("{semantic.outline.control}" if game else "{primitive.outline.none}", "dimension"),
            "outlineColor": tok(surface_outline if game else "transparent", "color"),
            "maxWidth": tok(dim(360 if game else 480, unit), "dimension"), "zIndex": tok("{primitive.zIndex.popup}", "number"),
            "enterDuration": tok("{primitive.duration.base}", "duration"), "enterEasing": tok("{primitive.easing.enter}", "cubicBezier"),
        },
        "hud": {
            "chip": {
                "bg": tok("{semantic.color.surface}", "color"), "fg": tok("{semantic.color.text}", "color"),
                "radius": tok("{semantic.radius.chip}", "dimension"), "height": tok(dim(36 if game else 32, unit), "dimension"),
                "paddingX": tok("{primitive.spacing.3}", "dimension"), "fontSize": tok("{primitive.fontSize.%s}" % ("lg" if game else "sm"), "dimension"),
                "fontWeight": tok("700", "fontWeight"), "iconSize": tok("{primitive.iconSize.sm}", "dimension"),
                "outlineWidth": tok("{semantic.outline.control}" if game else "{primitive.outline.thin}", "dimension"),
                "outlineColor": tok(surface_outline if game else "{semantic.color.border}", "color"),
                "shadow": tok(comp_shadow("neutral", "sm") if game else "{primitive.shadow.none}", "shadow"),
                "zIndex": tok("{primitive.zIndex.hud}", "number"),
            },
        },
        "tile": {
            "bg": tok("{semantic.color.surface}", "color"), "bgSelected": tok("{primitive.color.brand.100}", "color"),
            "radius": tok("{semantic.radius.tile}", "dimension"), "outlineWidth": tok("{semantic.outline.control}", "dimension"),
            "outlineColor": tok(surface_outline, "color"), "outlineColorSelected": tok("{semantic.color.primary}", "color"),
            "shadow": tok(comp_shadow("neutral", "sm"), "shadow"), "gap": tok("{primitive.spacing.%s}" % ("1" if game else "2"), "dimension"),
            "minSize": tok("{primitive.touchTarget.min}", "dimension"),
        },
        "progress": {
            "track": tok("{primitive.color.neutral.200}", "color"), "fill": tok("{semantic.color.primary}", "color"),
            "fillReward": tok("{semantic.color.reward}", "color"), "height": tok(dim(16 if game else 8, unit), "dimension"),
            "radius": tok("{primitive.radius.full}", "dimension"),
            "outlineWidth": tok("{semantic.outline.control}" if game else "{primitive.outline.none}", "dimension"),
            "outlineColor": tok(surface_outline if game else "transparent", "color"),
            "fillDuration": tok("{primitive.duration.slow}", "duration"), "fillEasing": tok("{primitive.easing.standard}", "cubicBezier"),
        },
    }

    tokens = {
        "$schema": "https://design-tokens.org/schema.json",
        "$extensions": {
            "vdp": {
                "schema": TOKENS_SCHEMA,
                "platformUnit": unit,
                "minTouchTarget": touch_min,
                "motionClass": motion_class,
                "generatedFrom": style_id,
                "productKind": kind,
                "seeds": dict((k, seeds[k].upper()) for k in SEED_SLOTS if k in seeds),
                "derivation": DERIVATION_VERSION,
                "driftBudget": dict(DRIFT_BUDGET),
                "surfaces": surfaces,
                "contrastNotes": contrast_notes,
            }
        },
        "primitive": primitive,
        "semantic": semantic,
        "component": component,
    }

    harden_component_states(tokens, ramps, p_step, on_candidates, last_resort, contrast_notes,
                            explicit_secondary=secondary_explicit, fast_ms=durations["fast"])

    if "supports-dark" in strategy:
        tokens["dark"] = {"semantic": {"color": {
            "background": tok("{primitive.color.neutral.900}", "color"), "surface": tok("{primitive.color.neutral.800}", "color"),
            "surfaceElevated": tok("{primitive.color.neutral.700}", "color"), "border": tok("{primitive.color.neutral.700}", "color"),
            "text": tok("{primitive.color.neutral.50}", "color"), "textMuted": tok("{primitive.color.neutral.300}", "color"),
            "primary": tok("{primitive.color.brand.400}", "color"), "onPrimary": tok(pick_fill_and_on({"400": ramps["brand"]["400"]}, "400", on_candidates, last_resort)[1], "color"),
            "overlay": tok("rgba(0, 0, 0, 0.6)", "color"),
        }}}
    return tokens


# --------------------------------------------------------------------------- component states (A-14 … AD-8)
TEXT_MIN, BOUNDARY_MIN = 4.5, 3.0
PRESS_FEEDBACK_MS = 90


def _hex_of(tokens, value):
    try:
        v = resolve_ref(tokens, value)
    except KeyError:
        return None
    return v.upper() if is_hex(v) else None


def step_away_until(hex_value, against, target):
    """Move ``hex_value``'s HSL lightness away from the ``against`` colours (darker on light surfaces, lighter on dark)
    until it reaches ``target`` contrast against all of them; returns the first passing hex (or the extreme)."""
    h, s, l = hex_to_hsl(hex_value)
    chroma = hsl_chroma(s, l)
    darker = sum(rel_lum(a) for a in against) / len(against) > 0.18
    current = hex_value.upper()
    for _ in range(60):
        if all(contrast(current, a) >= target for a in against):
            return current
        l = l - 2 if darker else l + 2
        if l < 2 or l > 98:
            break
        denom = 1 - abs(2 * l / 100.0 - 1)
        current = hsl_to_hex(h, s if denom <= 0 else min(s, 100.0 * chroma / denom), l)  # keep chroma: no neon edges
    return current


def best_label(states, candidates):
    """(ref, hex, min_ratio) of the candidate with the highest minimum contrast over ``states``."""
    best = None
    for ref, hx in candidates:
        ratio = min(contrast(hx, s) for s in states)
        if best is None or ratio > best[2]:
            best = (ref, hx, ratio)
    return best


def harden_component_states(tokens, ramps, p_step, on_candidates, last_resort, notes, explicit_secondary=False, fast_ms=0):
    """Guarantee component-state contrast after the tree exists (needs resolved hexes):
    A-14 primary label >= 4.5 on bg/hover/pressed (one fg if possible, else per-state fg);
    A-15 secondary label = primary-family step reaching 4.5 on its states; explicit primary outline >= 3:1;
    A-16 semantic.color.borderInteractive >= 3:1 vs surface and background for interactive outlines;
    AD-6 pressDuration <= 90 ms; AD-8 tile selection outline >= 3:1 against the tile."""
    comp, sem = tokens["component"], tokens["semantic"]["color"]
    surface = _hex_of(tokens, sem["surface"]["$value"])
    background = _hex_of(tokens, sem["background"]["$value"])
    brand_ref = lambda step: "{primitive.color.brand.%s}" % step

    # A-16: interactive border
    border = _hex_of(tokens, sem["border"]["$value"]) or ramps["neutral"]["300"]
    interactive = step_away_until(border, [surface, background], BOUNDARY_MIN)
    sem["borderInteractive"] = tok("{semantic.color.border}" if interactive == border else interactive, "color",
                                   "border family stepped to >= 3:1 against surface and background (WCAG 1.4.11)")
    for path in (("tile",), ("button", "icon")):
        node = comp
        for part in path:
            node = node[part]
        if node.get("outlineColor", {}).get("$value") not in (None, "transparent"):
            node["outlineColor"] = tok("{semantic.color.borderInteractive}", "color")

    # A-14: primary button label on every state
    primary = comp["button"]["primary"]
    states = dict((k, _hex_of(tokens, primary[k]["$value"])) for k in ("bg", "bgHover", "bgPressed"))
    on_primary = _hex_of(tokens, sem["onPrimary"]["$value"])

    # Hover keeps the DEFAULT label: step the hover fill one ramp step lighter when that label is dark, darker when it
    # is light (falling back to the other direction), never onto the fill, the pressed fill or the outline colour.
    edge = _hex_of(tokens, primary["outlineColor"]["$value"]) if primary["outlineColor"]["$value"] != "transparent" else None
    directions = (-1, 1) if rel_lum(on_primary) < 0.18 else (1, -1)
    for direction in directions:
        index = STEPS.index(p_step) + direction
        if not 0 <= index < len(STEPS):
            continue
        candidate = ramps["brand"][STEPS[index]]
        if candidate in (states["bg"], states["bgPressed"], edge) or contrast(on_primary, candidate) < TEXT_MIN:
            continue
        if candidate != states["bgHover"]:
            sem["primaryHover"] = tok(brand_ref(STEPS[index]), "color")
            primary["bgHover"] = tok("{semantic.color.primaryHover}", "color")
            states["bgHover"] = candidate
        break
    ref, hx, ratio = best_label(states.values(), on_candidates)
    if ratio >= TEXT_MIN:
        primary["fg"] = tok("{semantic.color.onPrimary}" if hx == on_primary else ref, "color")
    else:
        # no single non-black label passes everywhere: keep the default label (onPrimary) and choose per state;
        # #000000 is considered per state only, and only when seed text, neutral.900 and white all fail there
        primary["fg"] = tok("{semantic.color.onPrimary}", "color")
        for key, fg_key in (("bgHover", "fgHover"), ("bgPressed", "fgPressed")):
            if contrast(on_primary, states[key]) >= TEXT_MIN:
                continue
            step = primary[key]["$value"].strip("{}").split(".")[-1] if primary[key]["$value"].startswith("{primitive.color.brand.") else None
            sref, shx, sratio = best_label([states[key]], on_candidates)
            if sratio < TEXT_MIN:
                sref, shx, sratio = best_label([states[key]], list(on_candidates) + list(last_resort))
                if sratio >= TEXT_MIN and sref == "{primitive.color.black}":
                    notes.append("button.primary.%s: label is #000000 on %s because it is the only candidate reaching 4.5:1" % (fg_key, states[key]))
            while sratio < TEXT_MIN and step and STEPS.index(step) < len(STEPS) - 1:
                old = ramps["brand"][step]
                step = STEPS[STEPS.index(step) + 1]
                primary[key] = tok(brand_ref(step), "color")
                states[key] = ramps["brand"][step]
                sref, shx, sratio = best_label([states[key]], on_candidates)
                notes.append("button.primary.%s: fill moved from %s to %s so its label reaches 4.5:1" % (key, old, states[key]))
            primary[fg_key] = tok(sref, "color")

    # N3-3: on a dark page the filled control's edge (outline and the double-clay hard layer, each checked on its own)
    # steps LIGHTER in the brand ramp — never onto fill/hover/pressed — until it reaches 3:1 against the page
    dark_page = rel_lum(background) < 0.18
    if dark_page:
        used = {states["bg"], states["bgHover"], states["bgPressed"]}

        def lighter_edge():
            for step in reversed(STEPS[:STEPS.index(p_step)]):
                candidate = ramps["brand"][step]
                if candidate not in used and contrast(candidate, background) >= BOUNDARY_MIN:
                    return brand_ref(step), candidate
            return "{semantic.color.borderInteractive}", _hex_of(tokens, sem["borderInteractive"]["$value"])

        outline_value = primary["outlineColor"]["$value"]
        old_edge = _hex_of(tokens, outline_value) if outline_value != "transparent" else None
        if old_edge and contrast(old_edge, background) < BOUNDARY_MIN:
            new_ref, new_hex = lighter_edge()
            primary["outlineColor"] = tok(new_ref, "color")
            notes.append("button.primary edge: %s is %.2f:1 on the dark page %s; stepped lighter to %s (%.2f:1)"
                         % (old_edge, contrast(old_edge, background), background, new_hex, contrast(new_hex, background)))
        shadow = primary["shadow"]["$value"]
        hard = re.match(r"^0 \d+px 0 (#[0-9A-Fa-f]{6}),", shadow)
        if hard and contrast(hard.group(1), background) < BOUNDARY_MIN:
            _ref, new_hex = lighter_edge()
            primary["shadow"] = tok(shadow.replace(hard.group(1), new_hex, 1), "shadow")
            notes.append("button.primary hard shadow: %s is %.2f:1 on the dark page %s; stepped lighter to %s"
                         % (hard.group(1), contrast(hard.group(1), background), background, new_hex))

    # N3-2: focus ring = brand-family step reaching 3:1 against background AND surface, not the fill/hover/pressed colour
    taken = {states["bg"], states["bgHover"], states["bgPressed"]}
    if primary["outlineColor"]["$value"] != "transparent":
        taken.add(_hex_of(tokens, primary["outlineColor"]["$value"]))  # focus must look different from the resting edge
    light_page = not dark_page
    start = STEPS.index(p_step)
    away = list(range(start + 1, len(STEPS))) if light_page else list(range(start - 1, -1, -1))
    back = list(range(start - 1, -1, -1)) if light_page else list(range(start + 1, len(STEPS)))
    focus_ref = None
    for index in away + back:
        candidate = ramps["brand"][STEPS[index]]
        if candidate in taken:
            continue
        if contrast(candidate, background) >= BOUNDARY_MIN and contrast(candidate, surface) >= BOUNDARY_MIN:
            focus_ref = brand_ref(STEPS[index])
            break
    if focus_ref is None:
        focus_ref = step_away_until(ramps["brand"][p_step], [background, surface], BOUNDARY_MIN)
    sem["focusRing"] = tok(focus_ref, "color", "brand-family focus indicator >= 3:1 against background and surface (WCAG 1.4.11)")

    # A-15: secondary label (and explicit primary outline) in the primary family
    secondary = comp["button"]["secondary"]
    sec_bg = _hex_of(tokens, secondary["bg"]["$value"])
    dark_surface = rel_lum(sec_bg) < 0.18
    if dark_surface:
        # brand.50/100 are near-white on a dark theme: hover/press with dark brand tints instead (900 -> 800)
        secondary["bgHover"] = tok(brand_ref("900"), "color")
        secondary["bgPressed"] = tok(brand_ref("800"), "color")
    sec_states = [_hex_of(tokens, secondary[k]["$value"]) for k in ("bg", "bgHover", "bgPressed")]
    away = STEPS[STEPS.index(p_step):] if not dark_surface else list(reversed(STEPS[:STEPS.index(p_step) + 1]))
    label_step = None
    for step in away:
        if min(contrast(ramps["brand"][step], s) for s in sec_states) >= TEXT_MIN:
            label_step = step
            break
    if label_step is None:
        ref, _hx, _r = best_label(sec_states, list(on_candidates) + list(last_resort))
        secondary["fg"] = tok(ref, "color")
    else:
        secondary["fg"] = tok("{semantic.color.primary}" if label_step == p_step else brand_ref(label_step), "color")
        if label_step != p_step:
            notes.append("button.secondary.fg: primary-family label stepped from %s to brand.%s (%s) to reach 4.5:1 on the secondary states"
                         % (ramps["brand"][p_step], label_step, ramps["brand"][label_step]))
    if explicit_secondary:
        for step in away:
            if contrast(ramps["brand"][step], surface) >= BOUNDARY_MIN and contrast(ramps["brand"][step], background) >= BOUNDARY_MIN:
                secondary["outlineColor"] = tok("{semantic.color.primary}" if step == p_step else brand_ref(step), "color")
                break
    elif secondary.get("outlineColor", {}).get("$value") not in (None, "transparent"):
        secondary["outlineColor"] = tok("{semantic.color.borderInteractive}", "color")

    # text on panels: keep semantic.color.text when it passes on the panel fill, else the best candidate for that fill
    for path in (("card",), ("popup",), ("hud", "chip"), ("button", "icon")):
        node = comp
        for part in path:
            node = node[part]
        bg_value = node["bg"]["$value"]
        panel = background if bg_value == "transparent" else _hex_of(tokens, bg_value)
        fg = _hex_of(tokens, node["fg"]["$value"])
        if panel and fg and contrast(fg, panel) < TEXT_MIN:
            ref, _hx, ratio = best_label([panel], on_candidates)
            if ratio < TEXT_MIN:
                ref, _hx, ratio = best_label([panel], list(on_candidates) + list(last_resort))
            node["fg"] = tok(ref, "color")
            notes.append("component.%s.fg: %s fails on its fill %s; label set to %s (%.2f:1)" % (".".join(path), fg, panel, ref, ratio))

    # AD-8: selected tile stays light; its outline reaches 3:1 against the tile (brand.700 family first)
    tile = comp["tile"]
    tile_bg = _hex_of(tokens, tile["bg"]["$value"])
    order = sorted(STEPS, key=lambda s: (abs(STEPS.index(s) - STEPS.index("700")), -STEPS.index(s)))
    for step in order:
        if contrast(ramps["brand"][step], tile_bg) >= BOUNDARY_MIN:
            tile["outlineColorSelected"] = tok(brand_ref(step), "color")
            break

    # tappable HUD capsules (wallet/currency '+' opens the shop) get an interactive edge; hud.chip stays decorative
    chip = comp["hud"]["chip"]
    interactive_chip = dict((k, dict(v)) for k, v in chip.items())
    interactive_chip["outlineColor"] = tok("{semantic.color.borderInteractive}", "color")
    if chip["outlineWidth"]["$value"] in ("{primitive.outline.none}",):
        interactive_chip["outlineWidth"] = tok("{primitive.outline.thin}", "dimension")
    comp["hud"]["chipInteractive"] = interactive_chip

    # AD-6: press feedback within 100 ms in every motion class
    press = "{primitive.duration.fast}" if fast_ms <= PRESS_FEEDBACK_MS else "%dms" % PRESS_FEEDBACK_MS
    for variant in ("primary", "secondary", "icon"):
        comp["button"][variant]["pressDuration"] = tok(press, "duration")


def component_state_findings(tokens):
    """(errors, warnings): text fg < 4.5:1 on any of its state backgrounds is an error; an interactive boundary
    < 3:1 against its own fill or the screen background is a warning."""
    errors, warnings = [], []
    comp = tokens.get("component") or {}
    sem = (tokens.get("semantic") or {}).get("color") or {}
    background = _hex_of(tokens, (sem.get("background") or {}).get("$value", ""))

    def leaf(node, key):
        return (node.get(key) or {}).get("$value") if isinstance(node, dict) else None

    def text_pairs(path, node):
        bg_value = leaf(node, "bg")
        if bg_value is None or leaf(node, "fg") is None:
            return
        for bg_key, fg_key in (("bg", "fg"), ("bgHover", "fgHover"), ("bgPressed", "fgPressed")):
            if leaf(node, bg_key) is None:
                continue
            bg_hex = background if leaf(node, bg_key) == "transparent" else _hex_of(tokens, leaf(node, bg_key))
            fg_hex = _hex_of(tokens, leaf(node, fg_key) or leaf(node, "fg"))
            if bg_hex and fg_hex and contrast(fg_hex, bg_hex) < TEXT_MIN:
                errors.append("tokens.component.%s.%s: label %s on %s %s is %.2f:1 (< 4.5)"
                              % (path, fg_key if leaf(node, fg_key) else "fg", fg_hex, bg_key, bg_hex, contrast(fg_hex, bg_hex)))

    for path in ("button.primary", "button.secondary", "button.icon", "card", "popup", "hud.chip", "hud.chipInteractive"):
        node = comp
        for part in path.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if isinstance(node, dict):
            text_pairs(path, node)

    def boundary(path, node, key, against_keys):
        value = leaf(node, key)
        if value in (None, "transparent"):
            return
        line = _hex_of(tokens, value)
        for against in against_keys:
            other = background if against == "background" else (background if leaf(node, against) == "transparent" else _hex_of(tokens, leaf(node, against) or ""))
            if line and other and contrast(line, other) < BOUNDARY_MIN:
                warnings.append("tokens.component.%s.%s: interactive boundary %s vs %s %s is %.2f:1 (< 3)"
                                % (path, key, line, against, other, contrast(line, other)))

    # N3-2: focus indicator must reach 3:1 against the page and the surface (error, not a warning)
    surface = _hex_of(tokens, (sem.get("surface") or {}).get("$value", ""))
    focus_value = ((((tokens.get("semantic") or {}).get("state") or {}).get("focus") or {}).get("ringColor") or {}).get("$value") \
        or (sem.get("focusRing") or {}).get("$value")
    focus = _hex_of(tokens, focus_value) if focus_value else None
    if focus:
        for name, other in (("background", background), ("surface", surface)):
            if other and contrast(focus, other) < BOUNDARY_MIN:
                errors.append("tokens.semantic.color.focusRing: focus ring %s vs %s %s is %.2f:1 (< 3)" % (focus, name, other, contrast(focus, other)))

    # N3-3: a filled control with an outline on a dark page needs an edge (outline or fill) of 3:1 against the page;
    # controls without an outline are identified by their label (>= 4.5:1, checked above)
    primary = (comp.get("button") or {}).get("primary") or {}
    if background and rel_lum(background) < 0.18 and leaf(primary, "outlineColor") not in (None, "transparent"):
        line, fill = _hex_of(tokens, leaf(primary, "outlineColor")), _hex_of(tokens, leaf(primary, "bg") or "")
        if line and fill and max(contrast(line, background), contrast(fill, background)) < BOUNDARY_MIN:
            warnings.append("tokens.component.button.primary.outlineColor: edge %s (fill %s) vs dark background %s is %.2f:1 (< 3)"
                            % (line, fill, background, max(contrast(line, background), contrast(fill, background))))

    tile = comp.get("tile") or {}
    boundary("tile", tile, "outlineColor", ("bg", "background"))
    boundary("hud.chipInteractive", (comp.get("hud") or {}).get("chipInteractive") or {}, "outlineColor", ("bg", "background"))
    boundary("tile", tile, "outlineColorSelected", ("bg",))
    button = comp.get("button") or {}
    boundary("button.icon", button.get("icon") or {}, "outlineColor", ("bg", "background"))
    boundary("button.secondary", button.get("secondary") or {}, "outlineColor", ("bg", "background"))
    return errors, warnings


# --------------------------------------------------------------------------- validation (§6)


def validate_tokens(tokens, profile=None):
    """Return a list of error strings for a tokens.json dict (empty list == valid)."""
    errors = []
    if not isinstance(tokens, dict):
        return ["tokens: not a JSON object"]
    for layer in ("primitive", "semantic", "component"):
        if not isinstance(tokens.get(layer), dict):
            errors.append("tokens.%s: missing layer" % layer)
    primitive = tokens.get("primitive") or {}
    for group in REQUIRED_PRIMITIVE_GROUPS:
        if not isinstance(primitive.get(group), dict):
            errors.append("tokens.primitive.%s: missing group" % group)
    sem_color = (tokens.get("semantic") or {}).get("color") or {}
    for name in REQUIRED_SEMANTIC_COLORS:
        if name not in sem_color:
            errors.append("tokens.semantic.color.%s: missing" % name)
    states = (tokens.get("semantic") or {}).get("state") or {}
    for name in REQUIRED_STATES:
        if name not in states:
            errors.append("tokens.semantic.state.%s: missing" % name)
    ext = (tokens.get("$extensions") or {}).get("vdp") or {}
    for key in ("platformUnit", "minTouchTarget", "motionClass", "generatedFrom"):
        if key not in ext:
            errors.append("tokens.$extensions.vdp.%s: missing" % key)
    unit = ext.get("platformUnit")
    for path, leaf in iter_leaves(dict((k, v) for k, v in tokens.items() if not k.startswith("$"))):
        dotted = ".".join(path)
        value = leaf.get("$value")
        if not isinstance(value, str):
            errors.append("tokens.%s: $value must be a string (got %s)" % (dotted, type(value).__name__))
            continue
        try:
            resolved = resolve_ref(tokens, value)
        except KeyError as exc:
            errors.append("tokens.%s: %s" % (dotted, exc))
            continue
        if leaf.get("$type") == "dimension" and unit in ("px", "dp", "pt") and isinstance(resolved, str):
            if resolved not in ("0",) and not resolved.endswith(unit):
                errors.append("tokens.%s: dimension %r does not carry platform unit %s" % (dotted, resolved, unit))
    # contrast: onX vs X >= 4.5
    for name in ("primary", "secondary", "accent", "success", "warning", "danger", "reward"):
        on_name = "on" + name[0].upper() + name[1:]
        if name in sem_color and on_name in sem_color:
            try:
                fill = resolve_ref(tokens, sem_color[name]["$value"])
                on = resolve_ref(tokens, sem_color[on_name]["$value"])
            except (KeyError, TypeError):
                continue
            if is_hex(fill) and is_hex(on) and contrast(fill, on) < 4.5:
                errors.append("tokens.semantic.color.%s: %s on %s is %.2f:1 (< 4.5)" % (on_name, on, fill, contrast(fill, on)))
    if "textMuted" in sem_color and "background" in sem_color:
        try:
            tm = resolve_ref(tokens, sem_color["textMuted"]["$value"])
            bg = resolve_ref(tokens, sem_color["background"]["$value"])
            if is_hex(tm) and is_hex(bg) and contrast(tm, bg) < 4.5:
                errors.append("tokens.semantic.color.textMuted: %s on %s is %.2f:1 (< 4.5)" % (tm, bg, contrast(tm, bg)))
        except (KeyError, TypeError):
            pass
    errors.extend(component_state_findings(tokens)[0])
    if profile is not None:
        style_id = (profile.get("style") or {}).get("id")
        if style_id and ext.get("generatedFrom") != style_id:
            errors.append("tokens.$extensions.vdp.generatedFrom: %r != style-profile.json#style.id %r" % (ext.get("generatedFrom"), style_id))
    return errors


def dumps(tokens):
    return json.dumps(tokens, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive tokens.json from a Visual Direction Profile (vdp/1).")
    ap.add_argument("--profile", required=True, help="style-profile.json (schema vdp/1)")
    ap.add_argument("--seeds", help="optional JSON object {brand, secondary, accent, neutral, success, danger, warning?, reward?}")
    ap.add_argument("--out", help="write tokens.json here (default: stdout)")
    args = ap.parse_args(argv)
    try:
        with open(args.profile, encoding="utf-8") as fh:
            profile = json.load(fh)
        seeds = None
        if args.seeds:
            with open(args.seeds, encoding="utf-8") as fh:
                seeds = json.load(fh)
    except (OSError, IOError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    except ValueError as exc:
        print("error: malformed JSON: %s" % exc, file=sys.stderr)
        return 1
    try:
        tokens = derive_tokens(profile, seeds)
    except (KeyError, ValueError) as exc:
        print("error: cannot derive tokens: %s" % exc, file=sys.stderr)
        return 1
    text = dumps(tokens)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
