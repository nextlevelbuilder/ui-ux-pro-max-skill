#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visual Direction CLI: catalog search, profile builder, design-contract generator and validator.

Stdlib only, offline, deterministic. Commands (see SKILL.md and references/style-selection-workflow.md):

    vd.py styles "<query>" [-n 5] [--family <id>] [--json]
    vd.py genres "<query>" [-n 5] [--json]
    vd.py components "<query>" [--kind game|app] [-n 10] [--json]
    vd.py profile --style <id> | --genre <id> | --reference <analysis.json> [--seed-design-system <ds.json>]
                  --platform <p>[,<p>] [--stack <s>] [--audience <a>] [--project "<Name>"] [--out style-profile.json] [--json]
    vd.py init --profile style-profile.json --output-dir <project-root> [--force] [--json]
    vd.py page --dir design-system/<slug> --name <page> [--reason "..."] [--force] [--json]
    vd.py validate --dir design-system/<slug> [--json]

Exit codes: 0 ok · 1 validation failed / unknown id / malformed input · 2 usage or missing file.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_core  # noqa: E402
import vd_tokens  # noqa: E402

TOOL_VERSION = "1.0.0"
SCHEMA = "vdp/1"
REFERENCE_SCHEMA = "vdp-reference-analysis/1"
TEMPLATE_PATH = HERE.parent / "templates" / "master-template.md"
GENERATED_BY = "generated-by: visual-direction"
REFERENCE_CUSTOM_STYLE = "reference-derived-custom"

KINDS = ("game", "app")
PLATFORMS = ("mobile-ios", "mobile-android", "web", "desktop", "tablet")
STACKS = ("flutter", "flutter-flame", "unity-ugui", "unity-ui-toolkit", "react", "nextjs", "vue", "svelte",
          "html-tailwind", "swiftui", "jetpack-compose", "react-native", "other")
RADIUS_CLASSES = ("none", "sm", "md", "lg", "xl", "pill")
SHADINGS = ("flat", "soft", "soft-cel", "cel", "painterly", "glossy", "clay", "pixel", "realistic")
MOTION_CLASSES = ("static", "snappy", "soft", "bouncy", "dramatic")
CONFIDENCES = ("observed", "high", "assumption", "not-derivable")
SOURCE_TYPES = ("catalog", "genre", "reference-analysis", "design-system-seed", "research")
REFERENCE_ROLES = ("color", "shapes", "characters", "buttons", "hud", "popup", "icons", "typography", "layout", "motion")
REQUIRED_KEYS = ("schema", "project", "product", "style", "sources", "shape", "rendering", "typography",
                 "motion", "anti_patterns", "qa_criteria")
MASTER_H2 = ("Identity", "Visual Direction", "Token Summary", "Component Rules", "Page Override Logic",
             "Intentional Exceptions", "Anti-Patterns (Do NOT Use)", "QA Criteria", "Unknowns", "Change Log")
PAGE_SKELETON_H2 = ("Overrides", "Component remaps", "Intentional exceptions (page scope)", "Notes")
RESTATED_THRESHOLD = 3
COPY_LINE_RATIO = 0.8
TOOL_FILES = ("style-profile.json", "tokens.json", "component-catalog.md", "asset-guidelines.md",
              "interaction-guidelines.md", "visual-qa-checklist.md", "pages/README.md")
CHANGELOG_HEAD_RE = re.compile(r"^## \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z · .+ · \[(tool|manual)\]$")
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")
HEX_IN_TEXT_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")


class UsageError(Exception):
    """Exit 2: missing file / bad usage."""


class InputError(Exception):
    """Exit 1: malformed or invalid input."""


# ============================================================================ small helpers


def safe_slug(name, fallback="default"):
    """Same rule as the orchestrator's design_system.safe_slug: one safe path segment."""
    slug = re.sub(r"[^a-z0-9_-]+", "-", str(name).lower()).strip("-")
    return slug or fallback


def utc_now():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


def profile_hash(profile):
    return hashlib.sha256(json.dumps(profile, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def load_json(path, what="file"):
    p = Path(path)
    if not p.is_file():
        raise UsageError("%s not found: %s" % (what, path))
    try:
        with p.open(encoding="utf-8") as fh:
            return json.load(fh)
    except ValueError as exc:
        raise InputError("%s is not valid JSON (%s): %s" % (what, path, exc))


def dump_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def first_clause(text, limit=90):
    """First ';'/'.' clause; when longer than ``limit`` it is cut to limit-1 characters plus '…' (same convention as
    the reference-analysis skill's to-profile, so the raw-analysis and fragment routes produce identical text)."""
    text = str(text or "").strip()
    part = re.split(r"[;.]", text, maxsplit=1)[0].strip() or text
    if len(part) <= limit:
        return part.rstrip(" ,")
    return part[:limit - 1].rstrip(" ,") + "\u2026"


def clauses(text):
    return [c.strip() for c in re.split(r"\s*;\s*", str(text or "")) if c.strip()]


def catalog_value(value, fallback=""):
    """Template rows (reference-derived-custom) say 'derived from …'; treat that as absent."""
    text = str(value or "").strip()
    return fallback if not text or text.lower().startswith("derived from") else text


def listify(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


# ============================================================================ catalog row parsing (style route)

_FAMILY_WORD = r"[A-Z][A-Za-z0-9+]*(?:\s+[A-Z0-9][A-Za-z0-9]*)*"


def _clean_family(name):
    name = re.sub(r"\s+(?:for JP|fallback|Extrabold|Black|Bold)\b.*$", "", name).strip()
    name = re.sub(r"\s+\d{3}(?:-\d{3})?$", "", name).strip()
    return name


def parse_typography(direction):
    """Return (display, body, case, weight_rule, classification, derivable)."""
    text = str(direction or "")
    classification = re.split(r"[(;,]", text, maxsplit=1)[0].strip().lower()
    classification = re.sub(r"\s+(display|first|at integer scale)$", "", classification).strip() or "sans-serif"
    if classification.startswith("derived from"):
        classification = "sans-serif"
    display = None
    m = re.search(r"\(([^)]*)\)", text)
    if m and "observations" not in m.group(1):
        first = m.group(1).split("/")[0].split(",")[0].strip()
        fam = re.match(_FAMILY_WORD, first)
        if fam:
            display = _clean_family(fam.group(0))
    body = None
    for pattern in (r"\bbody\s+(" + _FAMILY_WORD + ")",
                    r"(" + _FAMILY_WORD + r")\s+\d{3}(?:-\d{3})?\s+body\b",
                    r"\bwith\s+(" + _FAMILY_WORD + r")(?:\s+or\s+" + _FAMILY_WORD + r")?\s+body\b"):
        mb = re.search(pattern, text)
        if mb:
            body = _clean_family(mb.group(1))
            break
    derivable = display is not None
    if not derivable:
        display = classification
    if body is None:
        body = display
    low = text.lower()
    if "title case" in low:
        case = "title"
    elif "sentence case" in low:
        case = "sentence"
    elif "uppercase" in low or "all caps" in low:
        case = "upper"
    elif "small-caps" in low:
        case = "small-caps"
    else:
        case = "mixed"
    weights = re.findall(r"\b([4-9]00)\b", text)
    if len(weights) >= 2:
        weight_rule = "display %s / body %s" % (weights[0], weights[1])
    elif weights:
        weight_rule = "display %s / body 500" % weights[0]
    else:
        weight_rule = "display bold / body regular"
    return display, body, case, weight_rule, classification, derivable


def parse_outline(rule):
    """Return (width_px, color_rule) from a catalog Outline Rule."""
    text = str(rule or "")
    low = text.lower()
    if low.startswith("derived from"):
        return 2, "darker-shade-of-fill"
    no_ui = low.startswith("no ") or re.search(r"\bui(?: elements)?(?::| have| has)? no outline", low) or "no outlines on ui" in low
    border = re.search(r"(\d+(?:\.\d+)?)\s*px\s+(?!bottom)(?:[\w-]+\s+)?border\b", low)
    if no_ui:
        if border:
            return max(1, int(round(float(border.group(1))))), "border-token"
        return 0, "none"
    width = 0
    mpx = re.search(r"(\d+(?:\.\d+)?)(?:-\d+(?:\.\d+)?)?\s*px", low)
    mnative = re.search(r"(\d+)\s+native pixel", low)
    if mpx:
        width = max(1, int(round(float(mpx.group(1)))))
    elif mnative:
        width = int(mnative.group(1))
    if re.search(r"lighter tint|light tint|tint of", low) and not re.search(r"darker shade|darker-shade", low):
        rule_name = "lighter-tint-of-fill"
    elif re.search(r"darker shade|darker-shade|\bl -\d|own hue|fill hue|tonal|darker edge|darker gold|darker-gold", low):
        rule_name = "darker-shade-of-fill"
    elif re.search(r"navy|black|dark edge|darkest|near-black", low):
        rule_name = "contrast-dark"
    elif "border" in low:
        rule_name = "border-token"
    else:
        rule_name = "none" if width == 0 else "darker-shade-of-fill"
    return width, rule_name


def parse_shadow(rule):
    """Map a catalog Shadow Rule to one of: none, offset-soft, soft-ambient, hard-offset, double-clay, glow."""
    text = str(rule or "")
    low = text.lower()
    if low.startswith("derived from") or not low:
        return "none"
    if "glow carries depth" in low or "no conventional shadows" in low:
        return "glow"
    cleaned = "; ".join(c for c in clauses(low) if not c.startswith("character"))
    cleaned = re.sub(r"\bno (?:hard|soft|conventional)?\s*(?:blur|shadows?|soft shadows)\b[^;]*", "", cleaned)
    cleaned = re.sub(r"\bwith no blur\b", "", cleaned)
    cleaned = re.sub(r"\boptional\b.*$", "", cleaned)
    hard = bool(re.search(r"\bhard\b", cleaned) or re.search(r"\b\d+(?:px)?\s+-?\d+px\s+0\b", cleaned))
    soft = bool(re.search(r"\bsoft\b|\bblur\b|\bambient\b", cleaned) or re.search(r"\d+px\s+\d+px\s+\d+%", cleaned))
    if hard and soft:
        return "double-clay"
    if hard:
        return "hard-offset"
    pct = [int(p) for p in re.findall(r"(\d+)%", cleaned)]
    has_px = bool(re.search(r"\d+px", cleaned))
    if not has_px and (low.startswith("none") or low.startswith("no shadow")):
        return "none"
    if not has_px and not soft:
        return "none"
    if "ambient" in cleaned or "minimal" in cleaned or "subtle" in cleaned or (pct and max(pct) <= 12):
        return "soft-ambient"
    return "offset-soft"


def parse_highlight(rule):
    low = str(rule or "").lower()
    if low.startswith("derived from"):
        return "none"
    if low.startswith("none") or low.startswith("no gloss") or low.startswith("flat"):
        return "none"
    checks = (("top-left gloss", "top-left-gloss"), ("glow is the highlight", "glow"), ("radial specular", "radial-specular"),
              ("painted", "painted"), ("paper-fibre", "paper-edge-light"), ("bevel", "bevel-light"),
              ("inner stroke", "inner-stroke"), ("inner white line", "inner-stroke"), ("inner glow", "inner-glow"),
              ("glass gloss", "glass-gloss"), ("top-face light", "top-gloss"), ("top half", "top-gloss"),
              ("highlight band", "top-band"), ("gradient", "soft-gradient"), ("metallic highlight", "metallic-edge"),
              ("highlight dot", "highlight-dot"), ("cel highlights", "cel-band"))
    for needle, tag in checks:
        if needle in low:
            return tag
    return first_clause(rule, 60).lower()


def parse_texture(highlight_rule, shading, style_id):
    low = (str(highlight_rule or "") + " " + str(style_id or "")).lower()
    if "paper" in low:
        return "paper-grain"
    if "brush" in low or shading == "painterly":
        return "brush"
    if "grain" in low:
        return "grain"
    if shading == "pixel" or "crt" in low or "scanline" in low:
        return "pixel-grid"
    return "none"


def parse_silhouette(shape_language, radius_class):
    low = str(shape_language or "").lower()
    if low.startswith("derived from"):
        return "rounded-rect"
    checks = (("blob", "rounded-blob"), ("diagonal", "angular-cut"), ("parallelogram", "angular-cut"),
              ("chamfer", "chamfered"), ("pixel", "pixel-grid"), ("irregular", "organic"), ("wobble", "organic"),
              ("imperfect", "layered-paper"), ("bean", "chunky-rounded"), ("chunky", "chunky-rounded"),
              ("candy", "bubbly"), ("blobby", "rounded-blob"), ("cloud", "rounded-blob"), ("primitives", "geometric"),
              ("rounded", "rounded-rect"), ("rectang", "rectangular"))
    for needle, tag in checks:
        if needle in low:
            return tag
    return "rectangular-sharp" if radius_class == "none" else "rounded-rect"


def parse_iconography(icon_style):
    text = str(icon_style or "")
    low = text.lower()
    if low.startswith("derived from"):
        return {"style": "filled-rounded", "stroke": None, "library_hint": "custom"}
    stroke = None
    ms = re.search(r"(\d+(?:\.\d+)?)(?:-\d+(?:\.\d+)?)?\s*px\s+stroke", low)
    if ms:
        stroke = float(ms.group(1))
        stroke = int(stroke) if stroke == int(stroke) else stroke
    if "pixel" in low:
        style = "pixel"
    elif re.match(r"^(thin|hand-drawn)?\s*[\d.-]*\s*(px )?stroke", low) or (ms and "filled" not in low[:ms.start()]):
        style = "outline"
    elif re.search(r"filled rounded|rounded filled|filled chunky", low):
        style = "filled-rounded"
    elif "two-tone" in low or "duotone" in low:
        style = "filled-two-tone"
    elif "filled" in low or "glyph" in low:
        style = "filled-rounded" if "round" in low else "filled"
    elif "engraved" in low:
        style = "engraved-two-tone"
    elif "sticker" in low:
        style = "sticker"
    elif "cut-paper" in low:
        style = "paper-silhouette"
    else:
        style = "custom"
    libs = []
    for name, slug in (("lucide", "lucide"), ("sf symbols", "sf-symbols"), ("material symbols", "material-symbols"),
                       ("phosphor", "phosphor"), ("heroicons", "heroicons"), ("tabler", "tabler")):
        if name in low:
            libs.append(slug)
    return {"style": style, "stroke": stroke, "library_hint": "|".join(libs) if libs else "custom"}


def parse_illustration(illustration_style):
    text = str(illustration_style or "")
    low = text.lower()
    if low.startswith("derived from"):
        return {"character_style": "not-derivable", "asset_rendering": "not-derivable"}
    checks = (("chibi", "chibi"), ("bean-body", "bean-body"), ("anime", "anime"), ("pixel sprites", "pixel-sprite"),
              ("mascot", "mascot"), ("painted", "painted"), ("toy-like", "toy-3d"), ("sparse", "none"),
              ("abstract geometric", "none"), ("layered paper", "paper-cutout"), ("geometric people", "flat-geometric"),
              ("stylised hero", "stylised-hero"), ("realistic-proportion", "painterly-realistic"),
              ("head-only animal", "animal-icon"), ("candy and jelly", "candy-object"), ("rounded characters", "simple-rounded"),
              ("rendered characters", "soft-3d-render"))
    style = "custom"
    for needle, tag in checks:
        if needle in low:
            style = tag
            break
    parts = clauses(text)
    rendering = parts[-1] if len(parts) > 1 else first_clause(text, 120)
    return {"character_style": style, "asset_rendering": rendering[:160]}


APP_HINTS = {"app", "utility", "productivity", "finance", "wellness", "habit", "journal", "lifestyle", "learning",
             "education", "edtech", "ios", "android", "material", "system", "decor"}
GAME_HINTS = {"game", "puzzle", "match", "match-3", "arcade", "rpg", "gacha", "platformer", "merge", "onet", "tile",
              "roguelite", "runner", "sprite", "hero", "quest", "battle", "score", "saga", "blast", "word", "trivia",
              "quiz", "sorting", "stacking", "adventure", "card", "narrative", "stop-motion"}


def derive_kind_from_style(row):
    style_id = row.get("Style ID", "")
    if style_id.endswith("-app") or row.get("Family") == "minimal-app":
        return "app"
    keywords = set(vd_core.split_list(row.get("Keywords", ""), ","))
    if keywords & GAME_HINTS:
        return "game"
    if keywords & APP_HINTS:
        return "app"
    return "game"


def map_confidence(value):
    v = str(value or "").strip().lower()
    return v if v in CONFIDENCES else ("high" if v in ("high", "verified") else "assumption")


def catalog_rules(row):
    keys = (("shape_language", "Shape Language"), ("outline_rule", "Outline Rule"), ("highlight_rule", "Highlight Rule"),
            ("shadow_rule", "Shadow Rule"), ("typography_direction", "Typography Direction"), ("icon_style", "Icon Style"),
            ("illustration_style", "Illustration Style"), ("button_rule", "Button Rule"), ("panel_popup_rule", "Panel Popup Rule"),
            ("hud_rule", "HUD Rule"), ("reward_rule", "Reward Rule"), ("best_for", "Best For"), ("avoid_for", "Avoid For"),
            ("reference_notes", "Reference Notes"))
    return dict((k, row.get(col, "")) for k, col in keys if row.get(col, ""))


# ============================================================================ profile builders


def catalog_surfaces(row, color_rule=None):
    """palette.surfaces from the catalog Seed Colors (background;surface;text). The border colour is derived by
    vd_tokens from shape.outline.color_rule applied to the background (A-10), so no synthetic outline is stored."""
    return vd_tokens.surfaces_from_catalog(row.get("Seed Colors", ""))


def shadow_tint_from_row(row, shading):
    """AD-9: 'black' only when the style row asks for black/uncoloured shadows on a dark or flat style; else 'neutral'."""
    rule = str(row.get("Shadow Rule") or "").lower()
    seeds = [p.strip() for p in str(row.get("Seed Colors") or "").split(";")]
    dark = len(seeds) == 6 and vd_tokens.is_hex(seeds[3]) and vd_tokens.rel_lum(seeds[3]) < 0.18
    if re.search(r"never colou?red", rule):
        return "black"
    if (dark or shading == "flat") and re.search(r"\bblack\b", rule):
        return "black"
    return "neutral"


SECONDARY_PRIMARY_OUTLINE_RE = re.compile(r"secondary[^;.]*\bprimary\s+(?:outline|border|stroke)", re.I)


def build_profile_from_style(row, platforms, stack=None, audience=None, project=None, kind=None, genre_row=None):
    """Route A (catalog). ``row`` is a visual-styles.csv row; ``genre_row`` adds route-B context."""
    style_id = row.get("Style ID", "").strip()
    if not style_id:
        raise ValueError("style row has no Style ID")
    platforms = [p for p in listify(platforms) if p]
    if not platforms:
        raise ValueError("at least one platform is required")
    if kind is None:
        kind = genre_row.get("Kind", "").strip() if genre_row else derive_kind_from_style(row)
    if kind not in KINDS:
        kind = "game"
    name = project or (genre_row.get("Genre Name") if genre_row else None) or row.get("Style Name") or style_id
    display, body, case, weight_rule, classification, derivable = parse_typography(row.get("Typography Direction"))
    outline_w, outline_rule = parse_outline(row.get("Outline Rule"))
    radius_class = row.get("Radius Class", "md").strip() or "md"
    shading = row.get("Shading", "soft").strip() or "soft"
    motion_class = row.get("Motion Class", "soft").strip() or "soft"
    durations = vd_tokens.DURATION.get(motion_class, vd_tokens.DURATION["soft"])
    mobile_only = all(p in ("mobile-ios", "mobile-android", "tablet") for p in platforms)
    unknowns = []
    if not derivable:
        unknowns.append("typography family not identified; classification '%s' recorded (CC-4)" % classification)
    principles = [c for c in (first_clause(row.get("Palette Strategy"), 120), first_clause(row.get("Shape Language"), 120),
                              first_clause(row.get("Outline Rule"), 120), first_clause(row.get("Typography Direction"), 120))
                  if c and not c.lower().startswith("derived from")]
    anti = vd_core.split_list(row.get("Anti Patterns", ""), "|")
    if genre_row:
        anti += [a for a in vd_core.split_list(genre_row.get("Anti Patterns", ""), "|") if a not in anti]
    sources = []
    if genre_row:
        sources.append({"type": "genre", "ref": "genre-profiles.csv#%s" % genre_row.get("Genre ID", "")})
    sources.append({"type": "catalog", "ref": "visual-styles.csv#%s" % style_id})
    components = {}
    for key, col in (("button.primary", "Button Rule"), ("popup", "Panel Popup Rule"), ("hud", "HUD Rule"), ("reward", "Reward Rule")):
        if row.get(col) and not row.get(col, "").lower().startswith("derived from"):
            components[key] = row[col]
    profile = {
        "schema": SCHEMA,
        "project": {"name": name, "slug": safe_slug(name)},
        "product": {
            "kind": kind,
            "genre": genre_row.get("Genre ID", "") if genre_row else None,
            "platforms": platforms,
            "stack": stack or "other",
            "audience": audience or (genre_row.get("Audience") if genre_row else None) or catalog_value(row.get("Audience"), "general"),
            "orientation": "portrait" if mobile_only else "responsive",
        },
        "style": {
            "id": style_id,
            "name": row.get("Style Name", style_id),
            "family": row.get("Family", ""),
            "mood": vd_core.split_list(catalog_value(row.get("Mood")), ";"),
            "confidence": map_confidence(row.get("Confidence")),
        },
        "sources": sources,
        "principles": principles,
        "shape": {
            "radius_class": radius_class,
            "silhouette": parse_silhouette(row.get("Shape Language"), radius_class),
            "outline": dict({"width": outline_w, "color_rule": outline_rule},
                            **({"secondary_button": "primary"} if SECONDARY_PRIMARY_OUTLINE_RE.search(row.get("Button Rule", "")) else {})),
        },
        "rendering": {
            "shading": shading,
            "highlight": parse_highlight(row.get("Highlight Rule")),
            "shadow": parse_shadow(row.get("Shadow Rule")),
            "texture": parse_texture(row.get("Highlight Rule"), shading, style_id),
            "shadow_tint": shadow_tint_from_row(row, shading),
        },
        "typography": {"display": display, "body": body, "case": case, "weight_rule": weight_rule},
        "palette_strategy": catalog_value(row.get("Palette Strategy"), "neutral base + single accent"),
        "palette": {"seeds": vd_tokens.seeds_from_catalog(row.get("Seed Colors", "")),
                    "surfaces": catalog_surfaces(row, outline_rule)},
        "iconography": parse_iconography(row.get("Icon Style")),
        "illustration": parse_illustration(row.get("Illustration Style")),
        "motion": {
            "class": motion_class,
            "duration_scale": {"fast": durations["fast"], "base": durations["base"], "slow": durations["slow"]},
            "easing": vd_tokens.EASING_NAME.get(motion_class, "ease-in-out-soft"),
            "reduced_motion": "respect",
        },
        "components": components,
        "anti_patterns": anti,
        "qa_criteria": vd_core.split_list(row.get("QA Criteria", ""), "|"),
        "intentional_exceptions": [],
        "unknowns": unknowns,
        "catalog_rules": catalog_rules(row),
    }
    if genre_row:
        profile["genre_profile"] = {
            "name": genre_row.get("Genre Name", ""),
            "default_styles": vd_core.split_list(genre_row.get("Default Styles", ""), ";"),
            "core_screens": vd_core.split_list(genre_row.get("Core Screens", ""), ";"),
            "hud_elements": vd_core.split_list(genre_row.get("HUD Elements", ""), ";"),
            "key_interactions": vd_core.split_list(genre_row.get("Key Interactions", ""), ";"),
            "reward_loop": genre_row.get("Reward Loop", ""),
            "touch_rules": genre_row.get("Touch Rules", ""),
            "performance_notes": genre_row.get("Performance Notes", ""),
        }
    return profile


def build_profile_from_genre(genre_row, platforms, stack=None, audience=None, project=None, style_id=None):
    """Route B (genre): the first ``Default Styles`` id (or ``style_id`` if it is one of them) drives route A."""
    defaults = vd_core.split_list(genre_row.get("Default Styles", ""), ";")
    if not defaults:
        raise LookupError("genre %r lists no Default Styles" % genre_row.get("Genre ID"))
    chosen = style_id or defaults[0]
    row = vd_core.row_by_id("styles", chosen)
    if row is None:
        raise LookupError("default style %r of genre %r is not in visual-styles.csv" % (chosen, genre_row.get("Genre ID")))
    return build_profile_from_style(row, platforms, stack=stack, audience=audience, project=project, genre_row=genre_row)


RULE_TARGET_ROLE = {"palette": "color", "radius": "shapes", "outline": "shapes", "shading": "shapes", "shape": "shapes",
                    "hud": "hud", "popup": "popup", "icon": "icons", "typography": "typography",
                    "character": "characters", "motion": "motion", "layout": "layout", "card": "layout",
                    "tab-bar": "layout", "chip": "buttons"}
SHADING_WORDS = (("soft-cel", "soft-cel"), ("cel", "cel"), ("gloss", "glossy"), ("specular", "glossy"), ("clay", "clay"),
                 ("pixel", "pixel"), ("painterly", "painterly"), ("brush", "painterly"), ("realistic", "realistic"),
                 ("gradient", "soft"), ("flat", "flat"))


def _role_of_rule(target):
    target = str(target or "").lower()
    if target.startswith("button"):
        return "buttons"
    return RULE_TARGET_ROLE.get(target.split(".")[0], "layout")


# Vocabulary and clause rule identical to the reference-analysis skill's `to-profile`, so the raw-analysis and the
# fragment routes produce the same typography (QA F-03).
TYPO_ADJECTIVES = ("heavy", "bold", "light", "thin", "condensed", "wide", "rounded", "geometric", "humanist",
                   "grotesque", "handwritten", "hand-lettered", "brush", "stencil", "bubbly", "chunky")
TYPO_WEIGHTS = ("heavy", "bold", "light", "thin")
TYPO_BASES = (("sans-serif", "sans"), ("sans serif", "sans"), ("sans", "sans"), ("slab", "slab"), ("serif", "serif"),
              ("monospace", "monospace"), ("mono", "monospace"), ("script", "script"), ("pixel", "pixel"), ("bitmap", "pixel"))
BODY_WORDS = ("body", "caption", "sub-label", "sublabel", "subtitle", "paragraph", "regular weight", "regular",
              "humanist", "secondary text")
CLASSIFICATION_RE = re.compile(r"^[a-z][a-z -]*$")
RADIUS_PX_LADDER = ((2, "none"), (6, "sm"), (10, "md"), (16, "lg"), (32, "xl"))


def classify_typography(text):
    """CC-4: a classification string such as 'heavy rounded sans' (never a placeholder key name)."""
    low = str(text or "").lower()
    adjectives = [a for a in TYPO_ADJECTIVES if re.search(r"\b%s\b" % re.escape(a), low)]
    base = "sans"
    for needle, value in TYPO_BASES:
        if re.search(r"\b%s\b" % re.escape(needle), low):
            base = value
            break
    return " ".join(adjectives + [base])


CLASSIFICATION_BASES = ("sans", "serif", "slab", "mono", "monospace", "script", "pixel")


def normalise_classification(value):
    """'heavy-rounded-sans' (hyphenated fragment form) -> 'heavy rounded sans'; family names pass through unchanged."""
    v = str(value or "").strip()
    if not v or v != v.lower() or not CLASSIFICATION_RE.match(v) or "-" not in v:
        return v
    protected = v.replace("sans-serif", "sans\u0000serif")
    words = protected.replace("-", " ").replace("\u0000", "-").split()
    if words and (words[-1] in CLASSIFICATION_BASES or words[-1] == "sans-serif"):
        return " ".join(words)
    return v


def typography_classes(text):
    """(display, body, body_inferred): clauses naming body/caption/sub-label/regular/humanist classify the body,
    the rest classify display; without a body clause body = display minus its weight word (body_inferred=True)."""
    parts = [c.strip() for c in re.split(r"[;.,]|\bversus\b|\bvs\b", str(text or "")) if c.strip()]
    body_clauses = [c for c in parts if any(w in c.lower() for w in BODY_WORDS)]
    display_clauses = [c for c in parts if c not in body_clauses] or parts
    display = classify_typography(" ".join(display_clauses))
    if body_clauses:
        return display, classify_typography(" ".join(body_clauses)), False
    return display, " ".join(w for w in display.split() if w not in TYPO_WEIGHTS), True


def px_values(text):
    return [float(v) for v in re.findall(r"(\d+(?:\.\d+)?)\s*px\b", str(text or "").lower())]


def radius_class_from_px(values):
    """Median px -> class: <=2 none, <=6 sm, <=10 md, <=16 lg, <=32 xl, >32 pill."""
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0
    for limit, name in RADIUS_PX_LADDER:
        if median <= limit:
            return name
    return "pill"


def outline_color_rule_from_text(low):
    if re.search(r"light(?:er)? tint|lighter|tint of|light shade", low):
        return "lighter-tint-of-fill"
    if re.search(r"darker|own fill|tonal|same hue", low):
        return "darker-shade-of-fill"
    if re.search(r"\bblack\b|\bdark\b|navy|near-black", low):
        return "contrast-dark"
    if re.search(r"no outline|\bnone\b", low):
        return "none"
    return "darker-shade-of-fill"


def negations_from_rule(statement):
    """Anti-patterns are negations ('Do not …'), never the rule text itself."""
    out = []
    for clause in re.split(r"[;.]\s*", str(statement or "")):
        c = clause.strip().rstrip(".")
        if not c:
            continue
        m = re.match(r"^(?:no|never|not|nothing)\s+(.+)$", c, re.I)
        if m:
            rest = m.group(1).strip()
            text = "Do not use %s" % rest if not re.match(r"^(use|add|mix|rely|allow|place|animate|apply)\b", rest, re.I) else "Do not %s" % rest
        else:
            continue
        if len(text.split()) - 2 >= 4 and not re.search(r"\b(except|unless)\b", text, re.I):
            out.append(text)
    return out


def surfaces_from_palette_observed(palette_observed):
    """Observed background/surface/text/outline colours (highest share per role)."""
    best = {}
    for entry in palette_observed or []:
        if not isinstance(entry, dict):
            continue
        role = str(entry.get("role_guess", "")).lower()
        hx = entry.get("hex")
        if role not in ("background", "surface", "text", "outline") or not vd_tokens.is_hex(hx):
            continue
        share = float(entry.get("share") or 0)
        if role not in best or share > best[role][0]:
            best[role] = (share, hx.upper())
    return dict((role, hx) for role, (_s, hx) in best.items())


def apply_observed_palette(profile, observed, color_owned=True, owned_only=False, unknowns=None):
    """Seeds, surfaces and the derived accent from ``palette_observed`` — shared by the raw and the fragment route."""
    unknowns = unknowns if unknowns is not None else profile.setdefault("unknowns", [])
    seeds = vd_tokens.seeds_from_palette_observed(observed)
    if seeds and color_owned:
        palette = profile.setdefault("palette", {})
        palette.setdefault("seeds", {}).update(seeds)
        if "brand" in seeds and "accent" not in seeds and not owned_only:
            palette["seeds"]["accent"] = vd_tokens.ramp(seeds["brand"])["700"]
            unknowns.append("accent colour not observed; derived from the brand ramp (brand.700 = %s) — confirm or seed palette.seeds.accent" % palette["seeds"]["accent"])
    surfaces = surfaces_from_palette_observed(observed)
    if surfaces and color_owned:
        profile.setdefault("palette", {})["surfaces"] = surfaces
    if observed:
        profile.setdefault("palette", {})["observed"] = observed
    return profile


def build_profile_from_reference(analysis, ref_name, base, owned_only=False):
    """Route C/D. Overlay a vdp-reference-analysis/1 document on ``base`` (a complete profile).

    ``owned_only`` (CC-3, with --style/--genre): only rules whose role the references own may override the catalog.
    """
    if not isinstance(analysis, dict) or analysis.get("schema") != REFERENCE_SCHEMA:
        raise InputError("reference analysis must have schema %r (got %r)" % (REFERENCE_SCHEMA, (analysis or {}).get("schema")))
    profile = json.loads(json.dumps(base))
    refs = [r for r in analysis.get("references") or [] if isinstance(r, dict)]
    roles = []
    for r in refs:
        for role in r.get("roles") or []:
            if role not in roles:
                roles.append(role)
    observations = dict((o.get("id"), str(o.get("statement") or "")) for o in analysis.get("observations") or [] if isinstance(o, dict))
    rules = [r for r in analysis.get("rules") or [] if isinstance(r, dict)]
    strong = [r for r in rules if r.get("confidence") in ("observed", "high")]
    weak = [r for r in rules if r.get("confidence") not in ("observed", "high")]
    conflicts = [c for c in analysis.get("conflicts") or [] if isinstance(c, dict)]
    open_conflicts = [c for c in conflicts if c.get("status") == "open"]
    unknowns = list(profile.get("unknowns") or [])
    components = dict(profile.get("components") or {})
    exceptions = list(profile.get("intentional_exceptions") or [])
    qa = []
    principles = []
    anti = []

    def applies(rule):
        return (not owned_only) or (_role_of_rule(rule.get("target")) in roles)

    def evidence(rule):
        """Rule statement plus the statements of the observations it derives from."""
        return " ".join([str(rule.get("statement") or "")] + [observations.get(o, "") for o in rule.get("derived_from") or []])

    for rule in strong:
        target = str(rule.get("target") or "").lower()
        statement = str(rule.get("statement") or "").strip()
        scope = str(rule.get("scope") or "global")
        if scope.startswith("context:"):
            exceptions.append({"scope": scope.split(":", 1)[1], "rule": statement,
                               "reason": "observed in %s (%s)" % (", ".join(rule.get("derived_from") or []), rule.get("id"))})
            continue
        if not applies(rule):
            unknowns.append("%s rule not applied (role %s not owned by a reference): %s" % (rule.get("id"), _role_of_rule(target), statement[:80]))
            continue
        low = statement.lower()
        qa.append("%s: %s" % (target, statement))
        if len(principles) < 5:
            principles.append(first_clause(statement, 110))
        anti.extend(n for n in negations_from_rule(statement) if n not in anti)
        if target == "palette":
            profile["palette_strategy"] = statement
        elif target == "radius":
            px = px_values(evidence(rule))
            from_px = radius_class_from_px(px)
            found = [w for w in RADIUS_CLASSES if re.search(r"\b%s\b" % re.escape(w), low)]
            non_pill = [w for w in found if w != "pill"]
            if from_px:
                profile["shape"]["radius_class"] = from_px
            elif non_pill:
                profile["shape"]["radius_class"] = non_pill[-1]
            elif "pill" in found or re.search(r"fully rounded|circular", low):
                profile["shape"]["radius_class"] = "pill"
            if "pill" in found or re.search(r"fully rounded|circular", low):
                profile["shape"]["silhouette"] = "pill"
            components.setdefault("radius", statement)
        elif target == "outline":
            px = px_values(evidence(rule))
            width = max(1, int(round(px[0]))) if px else (3 if re.search(r"thick|heavy", low) else 2)
            if not px:
                unknowns.append("outline px value is an assumption from a %% estimate (%s)" % rule.get("id"))
            color_rule = outline_color_rule_from_text(low)
            if color_rule == "none":
                width = 0
            profile["shape"]["outline"] = {"width": width, "color_rule": color_rule}
        elif target == "shading":
            for word, value in SHADING_WORDS:
                if word in low:
                    profile["rendering"]["shading"] = value
                    break
            if "gloss" in low or "specular" in low:
                profile["rendering"]["highlight"] = "top-left-gloss"
            elif "band" in low:
                profile["rendering"]["highlight"] = "top-band"
            if "hard" in low and ("soft" in low or "blur" in low):
                profile["rendering"]["shadow"] = "double-clay"
            elif "hard" in low or "bottom edge" in low:
                profile["rendering"]["shadow"] = "hard-offset"
            elif "glow" in low:
                profile["rendering"]["shadow"] = "glow"
            elif "shadow" in low:
                profile["rendering"]["shadow"] = "offset-soft"
        elif target == "typography":
            fam = re.search(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:family|font)\b", statement)
            unknown_family = re.search(r"family (?:name )?(?:is )?(?:unknown|not (?:known|identified|derivable))", low)
            unknowns = [u for u in unknowns if not ("typography" in u and "not identified" in u)]
            if fam and not unknown_family:
                profile["typography"]["display"] = fam.group(1)
                profile["typography"]["body"] = fam.group(1)
            else:
                display, body, inferred = typography_classes(evidence(rule))
                profile["typography"]["display"] = display
                profile["typography"]["body"] = body
                unknowns.append("typography.display family not identified; classification '%s' from %s (CC-4)" % (display, ", ".join(rule.get("derived_from") or [rule.get("id", "")])))
                if inferred:
                    unknowns.append("typography.body classification '%s' inferred from the display family (no body text observed in %s); confirm" % (body, rule.get("id")))
            if "title case" in low:
                profile["typography"]["case"] = "title"
            elif "sentence case" in low:
                profile["typography"]["case"] = "sentence"
            elif "upper" in low:
                profile["typography"]["case"] = "upper"
            if "heavy" in low or "bold" in low:
                profile["typography"]["weight_rule"] = "display bold / body medium"
        elif target == "icon":
            if "outline" in low and "filled" not in low:
                style = "outline"
            elif "two-tone" in low:
                style = "filled-two-tone"
            elif "pixel" in low:
                style = "pixel"
            elif "filled" in low:
                style = "filled-rounded" if "round" in low else "filled"
            else:
                style = "mixed"
            profile["iconography"] = {"style": style, "stroke": None, "library_hint": "custom"}
        elif target == "character":
            profile["illustration"] = {"character_style": first_clause(statement, 60).lower(), "asset_rendering": statement[:160]}
        elif target == "motion":
            found = [w for w in MOTION_CLASSES if re.search(r"\b%s\b" % w, low)]
            if found:
                profile["motion"]["class"] = found[0]
                d = vd_tokens.DURATION[found[0]]
                profile["motion"]["duration_scale"] = {"fast": d["fast"], "base": d["base"], "slow": d["slow"]}
                profile["motion"]["easing"] = vd_tokens.EASING_NAME[found[0]]
        else:
            components[target] = statement
    for rule in weak:
        unknowns.append("assumption (%s, %s): %s" % (rule.get("id"), rule.get("confidence"), str(rule.get("statement") or "")[:120]))
    for item in analysis.get("not_derivable") or []:
        line = "not derivable from references: %s" % item
        if line not in unknowns:
            unknowns.append(line)
        if "motion" in str(item).lower() or "animation" in str(item).lower():
            unknowns.append("motion class not derivable from static references; catalog default '%s' kept" % profile["motion"]["class"])
    for c in open_conflicts:
        unknowns.append("open conflict on %s between %s" % (c.get("topic"), ", ".join(c.get("between") or [])))
    color_owned = (not owned_only) or ("color" in roles)
    apply_observed_palette(profile, analysis.get("palette_observed") or [], color_owned, owned_only, unknowns)
    global_strong = [r for r in strong if not str(r.get("scope") or "global").startswith("context:")]
    profile["style"]["confidence"] = "high" if len(global_strong) >= 5 and not open_conflicts else "assumption"
    profile["sources"] = [{"type": "reference-analysis", "ref": ref_name, "roles": roles}] + [
        s for s in profile.get("sources") or [] if s.get("type") != "reference-analysis"]
    if principles:
        profile["principles"] = principles
    if qa:
        profile["qa_criteria"] = qa + [q for q in profile.get("qa_criteria") or [] if q not in qa]
    if anti:
        profile["anti_patterns"] = anti + [a for a in profile.get("anti_patterns") or [] if a not in anti]
    profile["components"] = components
    profile["intentional_exceptions"] = exceptions
    seen = set()
    profile["unknowns"] = [u for u in unknowns if not (u in seen or seen.add(u))]
    return profile


FRAGMENT_SKIP = ("_partial", "_partial_note", "schema", "sources", "project", "product")


def fragment_kind(partial):
    kind = ((partial or {}).get("product") or {}).get("kind") if isinstance((partial or {}).get("product"), dict) else None
    return kind if kind in KINDS else None


def merge_partial_profile(partial, base, owned_only=False):
    """CC-3: complete a ``_partial`` vdp/1 fragment (``reference_analysis.py to-profile``) on ``base``.

    Fragment fields are honoured, never recomputed from catalog defaults; the palette is re-derived from the
    fragment's ``palette.observed`` with the same helper as the raw route so both routes agree.
    """
    profile = json.loads(json.dumps(base))
    unknowns = list(profile.get("unknowns") or [])
    for key, value in partial.items():
        if key in FRAGMENT_SKIP or value in (None, "", [], {}):
            continue
        if key == "style":
            if isinstance(value, dict) and value.get("confidence") in CONFIDENCES:
                profile["style"]["confidence"] = value["confidence"]
            continue
        if key == "palette":
            continue
        if key == "typography" and isinstance(value, dict):
            for sub, sub_value in value.items():
                if sub_value not in (None, "", [], {}):
                    profile["typography"][sub] = normalise_classification(sub_value) if sub in ("display", "body") else sub_value
            continue
        if key == "unknowns" and isinstance(value, list):
            unknowns = [u for u in value] + [u for u in unknowns if u not in value]
            continue
        if isinstance(value, dict) and isinstance(profile.get(key), dict):
            for sub, sub_value in value.items():
                if sub_value not in (None, "", [], {}):
                    profile[key][sub] = sub_value
        elif isinstance(value, list) and isinstance(profile.get(key), list):
            profile[key] = value + [v for v in profile[key] if v not in value]
        else:
            profile[key] = value
    palette = partial.get("palette") if isinstance(partial.get("palette"), dict) else {}
    observed = palette.get("observed") or []
    observed_seeds = vd_tokens.seeds_from_palette_observed(observed)
    observed_surfaces = surfaces_from_palette_observed(observed)
    unknowns = [u for u in unknowns if not u.startswith("accent colour not observed")]
    if observed:
        # same derivation as the raw route, so both routes agree on every slot the observations cover
        apply_observed_palette(profile, observed, True, owned_only, unknowns)
    seeds = profile.setdefault("palette", {}).setdefault("seeds", {})
    for slot, value in (palette.get("seeds") or {}).items():
        # an explicit fragment seed beats a catalog default or a derived fallback, never an observed role
        if slot in vd_tokens.SEED_SLOTS and vd_tokens.is_hex(value) and slot not in observed_seeds:
            seeds[slot] = value.upper()
            if slot == "accent":
                unknowns = [u for u in unknowns if not u.startswith("accent colour not observed")]
    surfaces = profile["palette"].setdefault("surfaces", {})
    for role, value in (palette.get("surfaces") or {}).items():
        if role in ("background", "surface", "text", "outline") and vd_tokens.is_hex(value) and role not in observed_surfaces:
            surfaces[role] = value.upper()
    if not surfaces:
        profile["palette"].pop("surfaces")
    ref_sources = [dict(src) for src in partial.get("sources") or [] if isinstance(src, dict) and src.get("type") == "reference-analysis"]
    if ref_sources:
        profile["sources"] = ref_sources + [src for src in profile.get("sources") or [] if src.get("type") != "reference-analysis"]
    seen = set()
    profile["unknowns"] = [u for u in unknowns if not (u in seen or seen.add(u))]
    return profile


def apply_seed(profile, seed):
    """Fill gaps from ``search.py --design-system --json`` output; never overrides an explicit style/reference value."""
    ds = seed.get("design_system") if isinstance(seed, dict) and isinstance(seed.get("design_system"), dict) else seed
    if not isinstance(ds, dict):
        raise InputError("design-system seed must be a JSON object")
    profile = json.loads(json.dumps(profile))
    seeds = profile.setdefault("palette", {}).setdefault("seeds", {})
    for slot, value in vd_tokens.seeds_from_design_system(ds).items():
        if slot not in seeds:
            seeds[slot] = value
    typo = profile.setdefault("typography", {})
    family_unknown = any("typography" in u and "not identified" in u for u in profile.get("unknowns") or [])
    ds_typo = ds.get("typography") or {}
    if (not typo.get("display") or family_unknown) and ds_typo.get("heading"):
        typo["display"] = ds_typo["heading"]
        typo["body"] = ds_typo.get("body") or ds_typo["heading"]
        profile["unknowns"] = [u for u in profile.get("unknowns") or [] if not ("typography" in u and "not identified" in u)]
        profile["unknowns"].append("typography families taken from the design-system seed (%s / %s); confirm with the user" % (typo["display"], typo["body"]))
    if not profile.get("palette_strategy"):
        colors = ds.get("colors") or {}
        if colors.get("notes"):
            profile["palette_strategy"] = str(colors["notes"])
    src = {"type": "design-system-seed", "ref": "search.py --design-system --json"}
    if src not in profile.get("sources", []):
        profile.setdefault("sources", []).append(src)
    return profile


# ============================================================================ profile validation


def validate_profile(profile):
    """Return a list of error strings (empty == valid) for a vdp/1 document."""
    errors = []
    if not isinstance(profile, dict):
        return ["profile: not a JSON object"]
    if profile.get("_partial"):
        errors.append("_partial: profile fragment must be completed by `vd.py profile --reference` first")
    for key in REQUIRED_KEYS:
        if key not in profile:
            errors.append("%s: required key missing" % key)
    if profile.get("schema") != SCHEMA:
        errors.append("schema: expected %r, got %r" % (SCHEMA, profile.get("schema")))
    project = profile.get("project")
    if isinstance(project, dict):
        if not str(project.get("name") or "").strip():
            errors.append("project.name: required")
    elif "project" in profile:
        errors.append("project: must be an object {name, slug}")
    product = profile.get("product")
    if isinstance(product, dict):
        if product.get("kind") not in KINDS:
            errors.append("product.kind: %r not in %s" % (product.get("kind"), list(KINDS)))
        plats = product.get("platforms")
        if not isinstance(plats, list) or not plats:
            errors.append("product.platforms: required non-empty list")
        else:
            bad = [p for p in plats if p not in PLATFORMS]
            if bad:
                errors.append("product.platforms: %s not in %s" % (bad, list(PLATFORMS)))
        if product.get("stack") not in (None, "") and product.get("stack") not in STACKS:
            errors.append("product.stack: %r not in %s" % (product.get("stack"), list(STACKS)))
    elif "product" in profile:
        errors.append("product: must be an object")
    style = profile.get("style")
    if isinstance(style, dict):
        if not str(style.get("id") or "").strip():
            errors.append("style.id: required")
        if style.get("confidence") not in (None,) and style.get("confidence") not in CONFIDENCES:
            errors.append("style.confidence: %r not in %s" % (style.get("confidence"), list(CONFIDENCES)))
    elif "style" in profile:
        errors.append("style: must be an object")
    sources = profile.get("sources")
    if isinstance(sources, list):
        for i, src in enumerate(sources):
            if not isinstance(src, dict):
                errors.append("sources[%d]: must be an object" % i)
                continue
            if src.get("type") not in SOURCE_TYPES:
                errors.append("sources[%d].type: %r not in %s" % (i, src.get("type"), list(SOURCE_TYPES)))
            if not str(src.get("ref") or "").strip():
                errors.append("sources[%d].ref: required" % i)
            for role in src.get("roles") or []:
                if role not in REFERENCE_ROLES:
                    errors.append("sources[%d].roles: %r not in %s" % (i, role, list(REFERENCE_ROLES)))
    elif "sources" in profile:
        errors.append("sources: must be a list")
    shape = profile.get("shape")
    if isinstance(shape, dict):
        if shape.get("radius_class") not in RADIUS_CLASSES:
            errors.append("shape.radius_class: %r not in %s" % (shape.get("radius_class"), list(RADIUS_CLASSES)))
        outline = shape.get("outline")
        if outline is not None and not isinstance(outline, dict):
            errors.append("shape.outline: must be an object {width, color_rule}")
        elif isinstance(outline, dict) and outline.get("width") is not None:
            width = outline.get("width")
            if isinstance(width, bool) or not isinstance(width, (int, float)):
                errors.append("shape.outline.width: must be a number")
            elif not math.isfinite(width) or width < 0:
                errors.append("shape.outline.width: must be a finite number >= 0 (got %r)" % width)
        if isinstance(outline, dict) and outline.get("secondary_button") not in (None, "primary", "surface"):
            errors.append("shape.outline.secondary_button: %r not in ['primary', 'surface']" % outline.get("secondary_button"))
    elif "shape" in profile:
        errors.append("shape: must be an object")
    rendering = profile.get("rendering")
    if isinstance(rendering, dict):
        if rendering.get("shading") not in SHADINGS:
            errors.append("rendering.shading: %r not in %s" % (rendering.get("shading"), list(SHADINGS)))
        if rendering.get("shadow_tint") not in (None, "neutral", "black"):
            errors.append("rendering.shadow_tint: %r not in ['neutral', 'black']" % rendering.get("shadow_tint"))
    elif "rendering" in profile:
        errors.append("rendering: must be an object")
    typo = profile.get("typography")
    if isinstance(typo, dict):
        if not str(typo.get("display") or "").strip():
            errors.append("typography.display: required (family or classification, CC-4)")
    elif "typography" in profile:
        errors.append("typography: must be an object")
    motion = profile.get("motion")
    if isinstance(motion, dict):
        if motion.get("class") not in MOTION_CLASSES:
            errors.append("motion.class: %r not in %s" % (motion.get("class"), list(MOTION_CLASSES)))
        scale = motion.get("duration_scale")
        if scale is not None:
            if not isinstance(scale, dict):
                errors.append("motion.duration_scale: must be an object or null")
            else:
                for k, v in scale.items():
                    if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                        errors.append("motion.duration_scale.%s: must be a non-negative number" % k)
    elif "motion" in profile:
        errors.append("motion: must be an object")
    for key in ("anti_patterns", "qa_criteria", "principles", "unknowns"):
        value = profile.get(key)
        if value is not None and (not isinstance(value, list) or any(not isinstance(v, str) for v in value)):
            errors.append("%s: must be a list of strings" % key)
    exceptions = profile.get("intentional_exceptions")
    if exceptions is not None:
        if not isinstance(exceptions, list):
            errors.append("intentional_exceptions: must be a list")
        else:
            for i, exc in enumerate(exceptions):
                if not isinstance(exc, dict) or not all(exc.get(k) for k in ("scope", "rule", "reason")):
                    errors.append("intentional_exceptions[%d]: needs scope, rule and reason" % i)
    surfaces = (profile.get("palette") or {}).get("surfaces") if isinstance(profile.get("palette"), dict) else None
    if surfaces is not None:
        if not isinstance(surfaces, dict):
            errors.append("palette.surfaces: must be an object")
        else:
            for role, value in surfaces.items():
                if role not in ("background", "surface", "text", "outline"):
                    errors.append("palette.surfaces.%s: unknown role (allowed background, surface, text, outline)" % role)
                elif not vd_tokens.is_hex(value):
                    errors.append("palette.surfaces.%s: %r is not #RRGGBB" % (role, value))
    seeds = (profile.get("palette") or {}).get("seeds") if isinstance(profile.get("palette"), dict) else None
    if seeds is not None:
        if not isinstance(seeds, dict):
            errors.append("palette.seeds: must be an object")
        else:
            for slot, value in seeds.items():
                if slot not in vd_tokens.SEED_SLOTS:
                    errors.append("palette.seeds.%s: unknown slot (allowed %s)" % (slot, list(vd_tokens.SEED_SLOTS)))
                elif not vd_tokens.is_hex(value):
                    errors.append("palette.seeds.%s: %r is not #RRGGBB" % (slot, value))
    return errors


# ============================================================================ tokens


def derive_tokens(profile):
    """tokens.json for a profile; seeds come from palette.seeds, then the catalog row, then constants."""
    extra = {}
    style_id = (profile.get("style") or {}).get("id")
    row = vd_core.row_by_id("styles", style_id) if style_id else None
    if row is not None:
        extra = vd_tokens.seeds_from_catalog(row.get("Seed Colors", ""))
        palette = profile.get("palette") if isinstance(profile.get("palette"), dict) else {}
        if not palette.get("surfaces"):
            color_rule = ((profile.get("shape") or {}).get("outline") or {}).get("color_rule") or "none"
            surfaces = catalog_surfaces(row, color_rule)
            if surfaces:
                profile = json.loads(json.dumps(profile))
                profile.setdefault("palette", {})["surfaces"] = surfaces
    return vd_tokens.derive_tokens(profile, extra)


# ============================================================================ template renderer

_BLOCK_RE = re.compile(r"\{\{#([A-Za-z0-9_]+)\}\}\n?(.*?)\{\{/\1\}\}\n?", re.S)
_VAR_RE = re.compile(r"\{\{([A-Za-z0-9_.]+)\}\}")


def render_template(template, ctx):
    """Tiny mustache subset: ``{{name}}``, ``{{#list}}…{{/list}}`` with ``{{.}}`` / ``{{key}}`` per item."""
    def render_block(match):
        name, body = match.group(1), match.group(2)
        items = ctx.get(name) or []
        out = []
        for item in items:
            if isinstance(item, dict):
                out.append(_VAR_RE.sub(lambda m: str(item.get(m.group(1), ctx.get(m.group(1), ""))), body))
            else:
                out.append(body.replace("{{.}}", str(item)))
        return "".join(out)
    text = _BLOCK_RE.sub(render_block, template)
    return _VAR_RE.sub(lambda m: str(ctx.get(m.group(1), "")), text)


def _row(group, unit_note=""):
    return " · ".join("%s=%s" % (k, v["$value"]) for k, v in group.items())


def master_context(profile, tokens, component_count, last_changelog_entry="(none)", generated_at=None):
    product = profile.get("product") or {}
    style = profile.get("style") or {}
    shape = profile.get("shape") or {}
    outline = shape.get("outline") or {}
    rendering = profile.get("rendering") or {}
    typo = profile.get("typography") or {}
    icon = profile.get("iconography") or {}
    illus = profile.get("illustration") or {}
    motion = profile.get("motion") or {}
    prim = tokens["primitive"]
    sem = tokens["semantic"]
    ext = tokens["$extensions"]["vdp"]
    unit = ext["platformUnit"]

    def resolved(ref):
        try:
            return vd_tokens.resolve_ref(tokens, ref)
        except KeyError:
            return ref

    colors = []
    for key, on_key in (("primary", "onPrimary"), ("secondary", "onSecondary"), ("accent", "onAccent"),
                        ("success", "onSuccess"), ("warning", "onWarning"), ("danger", "onDanger"), ("reward", "onReward"),
                        ("background", "text"), ("surface", "text"), ("surfaceElevated", "text"), ("border", None),
                        ("text", "background"), ("textMuted", "background"), ("overlay", None)):
        hx = resolved(sem["color"][key]["$value"])
        on_hex = resolved(sem["color"][on_key]["$value"]) if on_key and on_key in sem["color"] else "—"
        ratio = "%.2f:1" % vd_tokens.contrast(hx, on_hex) if vd_tokens.is_hex(hx) and vd_tokens.is_hex(on_hex) else "—"
        colors.append({"label": key, "key": key, "hex": hx, "on_hex": on_hex, "contrast": ratio})
    durations = prim["duration"]
    ctx = {
        "tool_version": TOOL_VERSION,
        "profile_hash": profile_hash(profile),
        "project_name": (profile.get("project") or {}).get("name", ""),
        "project_slug": safe_slug((profile.get("project") or {}).get("slug") or (profile.get("project") or {}).get("name", "")),
        "generated_at": generated_at or utc_now(),
        "derivation_version": ext.get("derivation", vd_tokens.DERIVATION_VERSION),
        "product_kind": product.get("kind", ""),
        "product_genre": product.get("genre") or "—",
        "platforms_csv": ", ".join(product.get("platforms") or []),
        "stack": product.get("stack") or "other",
        "platform_unit": unit,
        "style_name": style.get("name") or style.get("id", ""),
        "style_id": style.get("id", ""),
        "style_family": style.get("family") or "—",
        "style_confidence": style.get("confidence") or "assumption",
        "mood_csv": ", ".join(style.get("mood") or []) or "—",
        "audience": product.get("audience") or "—",
        "orientation": product.get("orientation") or "—",
        "principles": profile.get("principles") or ["(none recorded)"],
        "sources_csv": "; ".join("%s:%s" % (s.get("type"), s.get("ref")) for s in profile.get("sources") or []),
        "radius_class": shape.get("radius_class", ""),
        "silhouette": shape.get("silhouette") or "—",
        "outline_width": "%s%s" % (outline.get("width", 0), "" if unit == "logical" else unit) if outline.get("width") else "none",
        "outline_color_rule": outline.get("color_rule") or "none",
        "shading": rendering.get("shading", ""),
        "highlight": rendering.get("highlight") or "none",
        "shadow": rendering.get("shadow") or "none",
        "texture": rendering.get("texture") or "none",
        "font_display": typo.get("display", ""),
        "font_body": typo.get("body", ""),
        "type_case": typo.get("case") or "mixed",
        "weight_rule": typo.get("weight_rule") or "—",
        "palette_strategy": profile.get("palette_strategy") or "—",
        "icon_style": icon.get("style") or "—",
        "icon_stroke": icon.get("stroke") if icon.get("stroke") is not None else "none",
        "icon_library_hint": icon.get("library_hint") or "custom",
        "character_style": illus.get("character_style") or "none",
        "asset_rendering": illus.get("asset_rendering") or "none",
        "motion_class": motion.get("class", ""),
        "duration_fast": durations["fast"]["$value"].rstrip("ms"),
        "duration_base": durations["base"]["$value"].rstrip("ms"),
        "duration_slow": durations["slow"]["$value"].rstrip("ms"),
        "duration_reward": durations["reward"]["$value"].rstrip("ms"),
        "duration_ambient": durations["ambient"]["$value"].rstrip("ms"),
        "easing_name": motion.get("easing") or vd_tokens.EASING_NAME.get(motion.get("class", ""), ""),
        "reduced_motion": motion.get("reduced_motion") or "respect",
        "semantic_colors": colors,
        "spacing_row": _row(prim["spacing"]),
        "radius_row": _row(prim["radius"]),
        "radius_control": resolved(sem["radius"]["control"]["$value"]),
        "radius_container": resolved(sem["radius"]["container"]["$value"]),
        "radius_popup": resolved(sem["radius"]["popup"]["$value"]),
        "radius_tile": resolved(sem["radius"]["tile"]["$value"]),
        "radius_chip": resolved(sem["radius"]["chip"]["$value"]),
        "outline_row": _row(prim["outline"]),
        "outline_control": resolved(sem["outline"]["control"]["$value"]),
        "font_size_row": _row(prim["fontSize"]),
        "line_height_row": _row(prim["lineHeight"]),
        "icon_size_row": _row(prim["iconSize"]),
        "touch_min": prim["touchTarget"]["min"]["$value"],
        "touch_recommended": prim["touchTarget"]["recommended"]["$value"],
        "duration_row": _row(prim["duration"]),
        "easing_row": _row(prim["easing"]),
        "z_index_row": _row(prim["zIndex"]),
        "opacity_row": _row(prim["opacity"]),
        "shadow_row": _row(prim["shadow"]),
        "elevation_method": sem["elevation"]["method"]["$value"],
        "elevation_raised": sem["elevation"]["raised"]["$value"],
        "elevation_elevated": sem["elevation"]["elevated"]["$value"],
        "elevation_floating": sem["elevation"]["floating"]["$value"],
        "typography_roles": [{"role": role, "family": resolved(spec["fontFamily"]["$value"]), "size": resolved(spec["fontSize"]["$value"]),
                              "line_height": resolved(spec["lineHeight"]["$value"]), "weight": spec["fontWeight"]["$value"]}
                             for role, spec in sem["typography"].items()],
        "component_count": component_count,
        "component_notes": [{"id": k, "note": v} for k, v in (profile.get("components") or {}).items()] or [{"id": "—", "note": "no component notes in the profile"}],
        "drift_restated_threshold": RESTATED_THRESHOLD,
        "budget_radius": ext.get("driftBudget", vd_tokens.DRIFT_BUDGET).get("radius", 1),
        "budget_spacing": ext.get("driftBudget", vd_tokens.DRIFT_BUDGET).get("spacing", 2),
        "budget_duration": ext.get("driftBudget", vd_tokens.DRIFT_BUDGET).get("duration", 1),
        "intentional_exceptions": [{"scope": e.get("scope", ""), "rule": e.get("rule", ""), "reason": e.get("reason", ""),
                                    "status": e.get("status", "active")} for e in profile.get("intentional_exceptions") or []]
                                  or [{"scope": "—", "rule": "none declared", "reason": "—", "status": "—"}],
        "anti_patterns": profile.get("anti_patterns") or ["(none recorded)"],
        "qa_criteria": profile.get("qa_criteria") or [],
        "unknowns": (list(profile.get("unknowns") or []) + [n for n in ext.get("contrastNotes") or [] if n not in (profile.get("unknowns") or [])]) or ["(none recorded)"],
        "last_changelog_entry": last_changelog_entry,
    }
    return ctx


def render_master(profile, tokens, component_count=0, last_changelog_entry="(none)", generated_at=None, template=None):
    template = template if template is not None else TEMPLATE_PATH.read_text(encoding="utf-8")
    return render_template(template, master_context(profile, tokens, component_count, last_changelog_entry, generated_at))


def render_master_snippet(master_text):
    """The paste block for a foreign MASTER.md: Visual Direction, Token Summary, Page Override Logic, Intentional Exceptions."""
    sections = split_h2(master_text)
    wanted = ("Visual Direction", "Token Summary", "Page Override Logic", "Intentional Exceptions")
    lines = ["---", "", "## Visual Direction",
             "<!-- %s vd.py %s; paste below \"## Global Rules\" of MASTER.md -->" % (GENERATED_BY, TOOL_VERSION)]
    for name in wanted:
        body = sections.get(name, "").rstrip()
        if name != "Visual Direction":
            lines.append("")
            lines.append("### %s" % name)
        if body:
            lines.append(body.replace("\n### ", "\n#### "))
    return "\n".join(lines) + "\n"


def split_h2(text):
    """{heading: body} for every ``## `` section of a markdown document."""
    sections = {}
    current = None
    buf = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf).strip("\n")
            current = line[3:].strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip("\n")
    return sections


def generated_header(profile, extra=""):
    return "<!-- %s vd.py %s;%s profile-hash: %s -->" % (GENERATED_BY, TOOL_VERSION, (" " + extra + ";") if extra else "", profile_hash(profile))


# ============================================================================ companion documents


def catalog_rows_for(profile):
    kind = (profile.get("product") or {}).get("kind", "app")
    rows = [r for r in vd_core.load_rows("components") if r.get("Applies To", "").strip().lower() in (kind, "both")]
    return rows


def _style_modifier(component_id, style_row, profile_components):
    cid = component_id.lower()
    notes = []
    if style_row:
        mapping = (("button.", "Button Rule"), ("popup.", "Panel Popup Rule"), ("dialog.", "Panel Popup Rule"),
                   ("sheet.", "Panel Popup Rule"), ("panel.", "Panel Popup Rule"), ("hud.", "HUD Rule"), ("reward.", "Reward Rule"))
        for prefix, col in mapping:
            if cid.startswith(prefix) and style_row.get(col) and not style_row[col].lower().startswith("derived from"):
                notes.append(style_row[col])
                break
    for key, note in (profile_components or {}).items():
        k = key.lower()
        if cid == k or cid.startswith(k + ".") or cid.split(".")[0] == k:
            if note not in notes:
                notes.append(note)
    return notes


COMPONENT_TOKEN_GROUP = (("button.primary", ("button", "primary")), ("button.secondary", ("button", "secondary")),
                         ("button.icon", ("button", "icon")), ("button.", ("button", "primary")), ("card", ("card",)),
                         ("panel.", ("card",)), ("popup.", ("popup",)), ("dialog.", ("popup",)), ("sheet.", ("popup",)),
                         ("hud.", ("hud", "chip")), ("board.tile", ("tile",)), ("board.", ("tile",)), ("progress.", ("progress",)),
                         ("chip.", ("hud", "chip")), ("nav.", ("card",)), ("reward.", ("card",)), ("commerce.", ("card",)))
STACK_NOTE_KEYS = {"flutter": ("flutter",), "flutter-flame": ("flutter", "flame"), "unity-ugui": ("unity",), "unity-ui-toolkit": ("unity",),
                   "react": ("web",), "nextjs": ("web",), "vue": ("web",), "svelte": ("web",), "html-tailwind": ("web",),
                   "swiftui": ("ios", "swiftui"), "jetpack-compose": ("android", "compose"), "react-native": ("ios", "android", "react native")}
AUTHORITATIVE_KEYS = ("radius", "height", "outlineWidth", "outlineColor", "borderWidth", "shadow", "padding", "paddingX",
                      "fontSize", "minWidth", "size", "maxWidth", "gap", "minSize")


def _component_tokens(component_id, tokens):
    """Resolved token values that are authoritative for this component (CC-11, prose never wins)."""
    if not isinstance(tokens, dict):
        return None, []
    cid = component_id.lower()
    for prefix, path in COMPONENT_TOKEN_GROUP:
        if cid == prefix or cid.startswith(prefix):
            node = tokens.get("component") or {}
            for part in path:
                node = node.get(part) if isinstance(node, dict) else None
            if not isinstance(node, dict):
                return None, []
            pairs = []
            for key in AUTHORITATIVE_KEYS:
                leaf = node.get(key)
                if isinstance(leaf, dict) and "$value" in leaf:
                    try:
                        pairs.append("%s=%s" % (key, vd_tokens.resolve_ref(tokens, leaf["$value"])))
                    except KeyError:
                        pairs.append("%s=%s" % (key, leaf["$value"]))
            return "component." + ".".join(path), pairs
    return None, []


def _platform_notes(text, stack):
    keys = STACK_NOTE_KEYS.get(stack or "")
    if not keys:
        return "(set product.stack to render the notes for one stack; all stacks are in data/component-catalog.csv)"
    kept = [c for c in clauses(text) if any(c.lower().startswith(k) or (" %s:" % k) in c.lower() or c.lower().startswith(k + ":") for k in keys)]
    return "; ".join(kept) if kept else text


def render_component_catalog(profile, rows=None, style_row=None, tokens=None):
    rows = catalog_rows_for(profile) if rows is None else rows
    style = profile.get("style") or {}
    if style_row is None and style.get("id"):
        style_row = vd_core.row_by_id("styles", style["id"])
    kind = (profile.get("product") or {}).get("kind", "app")
    stack = (profile.get("product") or {}).get("stack")
    out = [generated_header(profile), "# Component Catalog — %s" % (profile.get("project") or {}).get("name", ""), "",
           "Filtered for `product.kind = %s` (rows whose Applies To is `%s` or `both`; %d components) and style `%s`." % (kind, kind, len(rows), style.get("id", "")),
           "Order of authority per component: **Tokens (authoritative)** from `tokens.json` → catalog rule (structure, variants, states) → "
           "**Style modifier (reference)**, the catalog/style prose. Where prose and tokens disagree (e.g. a pill vs a 16 radius, 2px vs 3px outline), the token value wins; "
           "record a deliberate deviation as an intentional exception, never by editing the prose (CC-11).",
           "Rows specific to this product kind are rendered in full; shared rows (`Applies To = both`) are rendered compact — their full "
           "visual rules, variants, interaction, platform notes, anti-patterns and QA live in `data/component-catalog.csv` of the `visual-direction` skill. "
           "Style modifiers are printed once per group, naming the components they apply to.", ""]
    if stack:
        out.append("Platform notes are filtered for stack `%s`." % stack)
        out.append("")
    groups = {}
    for r in rows:
        groups.setdefault(r.get("Group", "other"), []).append(r)
    for group in sorted(groups):
        out.append("## %s" % group)
        out.append("")
        printed = []
        for r in groups[group]:
            for note in _style_modifier(r["Component ID"], style_row, profile.get("components")):
                if note not in printed:
                    printed.append(note)
                    ids = [x["Component ID"] for x in groups[group] if note in _style_modifier(x["Component ID"], style_row, profile.get("components"))]
                    out.append("- **Style modifier (reference) for %s:** %s" % (", ".join("`%s`" % i for i in ids), note))
        if printed:
            out.append("")
        for r in groups[group]:
            out.append("### `%s` — %s" % (r["Component ID"], r.get("Name", "")))
            out.append("")
            path, pairs = _component_tokens(r["Component ID"], tokens)
            if pairs:
                out.append("- **Tokens (authoritative, `%s`):** %s" % (path, " · ".join(pairs)))
            out.append("- **Purpose:** %s" % r.get("Purpose", ""))
            compact = r.get("Applies To", "").strip().lower() == "both"
            if compact:
                out.append("- **States:** %s" % r.get("States", ""))
                out.append("- **Code reuse hint:** %s" % first_clause(r.get("Code Reuse Hint", ""), 120))
                out.append("- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#%s`" % r["Component ID"])
            else:
                out.append("- **Visual rules:** %s" % r.get("Visual Rules", ""))
                out.append("- **Variants:** %s" % r.get("Variants", ""))
                out.append("- **States:** %s" % r.get("States", ""))
                out.append("- **Interaction:** %s" % r.get("Interaction", ""))
                out.append("- **Platform notes:** %s" % _platform_notes(r.get("Platform Notes", ""), stack))
                out.append("- **Anti-patterns:** %s" % r.get("Anti Patterns", ""))
                out.append("- **QA:** %s" % r.get("QA Criteria", ""))
                out.append("- **Code reuse hint:** %s" % r.get("Code Reuse Hint", ""))
            out.append("")
    return "\n".join(out)


def render_asset_guidelines(profile, tokens):
    style = profile.get("style") or {}
    typo = profile.get("typography") or {}
    icon = profile.get("iconography") or {}
    illus = profile.get("illustration") or {}
    rules = profile.get("catalog_rules") or {}
    seeds = tokens["$extensions"]["vdp"].get("seeds", {})
    out = [generated_header(profile), "# Asset Guidelines — %s" % (profile.get("project") or {}).get("name", ""), "",
           "Style `%s` (%s). Every asset produced or sourced for this project must follow the rules below and be "
           "recorded in the Provenance section." % (style.get("id", ""), style.get("family", "")), "",
           "## Illustration", "",
           "- Character style: `%s`" % illus.get("character_style", "none"),
           "- Asset rendering: %s" % illus.get("asset_rendering", "none"),
           "- Shading: `%s` · highlight `%s` · shadow `%s` · texture `%s`" % tuple((profile.get("rendering") or {}).get(k, "none") for k in ("shading", "highlight", "shadow", "texture")),
           "- Outline: %s%s (%s)" % (((profile.get("shape") or {}).get("outline") or {}).get("width", 0), "px", ((profile.get("shape") or {}).get("outline") or {}).get("color_rule", "none")),
           ]
    if rules.get("illustration_style"):
        out.append("- Catalog rule: %s" % rules["illustration_style"])
    out += ["", "## Iconography", "",
            "- Style: `%s` · stroke: %s · library hint: `%s`" % (icon.get("style", ""), icon.get("stroke") if icon.get("stroke") is not None else "none", icon.get("library_hint", "custom")),
            "- Sizes: " + _row(tokens["primitive"]["iconSize"]),
            "- One icon library per project; mixing libraries is a `visual-audit` finding (`icon.mixed-libraries`)."]
    if rules.get("icon_style"):
        out.append("- Catalog rule: %s" % rules["icon_style"])
    out += ["", "## Typography", "",
            "- Display: **%s** · Body: **%s** · case: %s · %s" % (typo.get("display", ""), typo.get("body", ""), typo.get("case", "mixed"), typo.get("weight_rule", "")),
            "- Sizes: " + _row(tokens["primitive"]["fontSize"]),
            "- Bundle font files with their licence text; record each family under Provenance."]
    if rules.get("typography_direction"):
        out.append("- Catalog rule: %s" % rules["typography_direction"])
    out += ["", "## Palette seeds", "", "| Slot | Hex |", "|---|---|"]
    for slot, hx in seeds.items():
        out.append("| %s | `%s` |" % (slot, hx))
    out += ["", "Strategy: %s" % (profile.get("palette_strategy") or "—"), "",
            "## Provenance", "",
            "Every externally sourced rule, font, icon set or reference gets one record (JSON object) plus one markdown line. "
            "`status` is `checked` only for pages actually opened in the session; otherwise `NOT RUN`. URLs are copied, never typed from memory.", "",
            "```json", "[]", "```", "",
            "- (no records yet — format: `- [use] **asset** — source, licence, tier, status date — note`)", "",
            "Field rules: `licence_class` ∈ CC0 · OFL · MIT · Apache-2.0 · BSD · CC-BY · CC-BY-SA · CC-BY-NC · CC-BY-ND · marketplace · "
            "proprietary/unknown · trademark · ai-generated; `use` ∈ inspiration · rule · embedded; `tier` T1–T7. "
            "A `sources[]` entry of type `research` in `style-profile.json` points here as `asset-guidelines.md#provenance:<asset>`.", ""]
    return "\n".join(out)


def render_interaction_guidelines(profile, tokens):
    motion = profile.get("motion") or {}
    prim = tokens["primitive"]
    sem = tokens["semantic"]
    kind = (profile.get("product") or {}).get("kind", "app")
    unit = tokens["$extensions"]["vdp"]["platformUnit"]
    out = [generated_header(profile), "# Interaction Guidelines — %s" % (profile.get("project") or {}).get("name", ""), "",
           "Motion class `%s` · easing `%s` · reduced motion: %s · unit `%s`." % (motion.get("class", ""), motion.get("easing", ""), motion.get("reduced_motion", "respect"), unit), "",
           "## Durations (tokens.json#primitive.duration)", "", "| Token | Value | Use |", "|---|---|---|"]
    uses = {"instant": "state swap, no animation", "fast": "T0 input feedback (press, select, hover)",
            "base": "T1 transitions (open/close, move)", "slow": "T2 reveals and progress fills",
            "reveal": "screen / popup entrance", "reward": "T3 medium reward beat (small ≈ ×0.67, jackpot ≈ ×1.2)",
            "ambient": "T4 idle loop period (breathing, shimmer)"}
    for key, leaf in prim["duration"].items():
        out.append("| `primitive.duration.%s` | %s | %s |" % (key, leaf["$value"], uses.get(key, "")))
    out += ["", "## Easing (tokens.json#primitive.easing)", "", "| Role | Curve |", "|---|---|"]
    for key, leaf in prim["easing"].items():
        out.append("| `%s` | `%s` |" % (key, leaf["$value"]))
    out += ["", "## Touch and pointer", "",
            "- Minimum target `%s`, recommended `%s` (max across platforms %s)." % (prim["touchTarget"]["min"]["$value"], prim["touchTarget"]["recommended"]["$value"], ", ".join((profile.get("product") or {}).get("platforms") or [])),
            "- Press feedback within `primitive.duration.fast`; release inside bounds fires the action.",
            "- Hover is a no-op on touch platforms; focus ring %s / offset %s in `semantic.color.focusRing`." % (sem["state"]["focus"]["ringWidth"]["$value"], sem["state"]["focus"]["ringOffset"]["$value"]),
            "", "## States (tokens.json#semantic.state)", "", "| State | Opacity | Offset Y | Shadow |", "|---|---|---|---|"]
    for state, spec in sem["state"].items():
        out.append("| %s | %s | %s | %s |" % (state, spec.get("opacity", {}).get("$value", "—"), spec.get("offsetY", {}).get("$value", "—"), spec.get("shadow", {}).get("$value", "—")))
    out += ["", "## Reduced motion", "",
            "- `prefers-reduced-motion` / platform accessibility setting → T3/T4 beats become instant state swaps with a ≤150 ms fade; T0/T1 keep opacity and colour changes only.",
            "- Never flash more than 3 times per second; never require motion to understand state."]
    gp = profile.get("genre_profile") or {}
    if kind == "game":
        out += ["", "## Game-specific", "",
                "- Gameplay input feedback (T0) never exceeds 150 ms in any motion class.",
                "- Reward tiers by magnitude, not mechanic: small / medium / jackpot; captions and particle caps are fixed per project.",
                "- HUD stays readable during board motion: no shadows on HUD plates, numerals ≥ 16 %s." % ("logical px" if unit == "logical" else unit)]
        if gp.get("touch_rules"):
            out.append("- Genre touch rules (%s): %s" % (gp.get("name", ""), gp["touch_rules"]))
        if gp.get("key_interactions"):
            out.append("- Key interactions: %s" % ", ".join(gp["key_interactions"]))
        if gp.get("reward_loop"):
            out.append("- Reward loop: %s" % gp["reward_loop"])
        out.append("- Full rules: `motion-direction.md` and `game-ui-patterns.md` in the `visual-direction` skill references.")
    else:
        out += ["", "## App-specific", "",
                "- Motion confirms, never decorates: every T2/T3 animation must change a state the user asked for.",
                "- Lists and sheets use `primitive.easing.enter` / `exit`; page transitions ≤ `primitive.duration.reveal`.",
                "- Full rules: `motion-direction.md` in the `visual-direction` skill references."]
    return "\n".join(out) + "\n"


def render_qa_checklist(profile, tokens):
    kind = (profile.get("product") or {}).get("kind", "app")
    prim = tokens["primitive"]
    unit = tokens["$extensions"]["vdp"]["platformUnit"]
    out = [generated_header(profile), "# Visual QA Checklist — %s" % (profile.get("project") or {}).get("name", ""), "",
           "Tick every item per screen before sign-off. Items come from `style-profile.json#qa_criteria` plus generic per-screen checks. "
           "Automated checks: `audit.py scan --contract tokens.json` (code) and `visual_qa.py checklist --profile style-profile.json` (screenshots) from the `visual-audit` skill.", "",
           "## Profile criteria (every screen)", ""]
    for item in profile.get("qa_criteria") or []:
        out.append("- [ ] %s" % item)
    out += ["- [ ] Every `onX` text passes 4.5:1 on its `X`",
            "- [ ] All interactive targets ≥ %s %s" % (prim["touchTarget"]["min"]["$value"], "" if unit != "logical" else "logical px"),
            "- [ ] No colour, font family, radius, spacing or duration outside `tokens.json` without an intentional exception", ""]
    screens = {
        "game": (("home", ["Primary CTA is the single most saturated element", "HUD chips readable over the hero art", "Bottom navigation inside the thumb zone"]),
                 ("gameplay", ["Board owns ≥ 60 % of the height; HUD ≤ 12 %", "Tiles ≥ touch minimum; selection feedback within 1 frame", "Timer/moves readable during motion; no shadows on HUD plates"]),
                 ("popup", ["Scrim uses `semantic.color.overlay`; panel uses `component.popup.*`", "Close control ≥ touch minimum, top-right", "Entrance uses `primitive.duration.base` + `primitive.easing.enter`"]),
                 ("shop", ["Price tags share one component; currency icons from one set", "Offer cards never louder than the primary CTA", "Purchase confirmation uses the confirm popup, not a toast"]),
                 ("reward", ["Reward colour is `semantic.color.reward` only", "Beat length within `primitive.duration.reward` ± 20 %", "Skippable at 1.2 s; reduced-motion swap exists"])),
        "app": (("home", ["One primary action per view", "Hierarchy by weight and spacing, not boxes", "Navigation inside the thumb zone on mobile"]),
                ("list", ["Row height from tokens; dividers use `semantic.color.border`", "Empty, loading and error states present", "Tap target ≥ touch minimum per row"]),
                ("detail", ["Title uses `semantic.typography.title`; body uses `.body`", "Secondary actions subordinate to the primary", "Back navigation consistent with the platform"]),
                ("form", ["Inputs use `component.*` tokens; focus ring visible", "Validation messages use `semantic.color.danger` + icon/text", "Disabled state readable (opacity token), not focusable"]),
                ("settings", ["Grouped lists with consistent spacing tokens", "Destructive actions styled with `button.destructive` + confirm", "Theme switch keeps contrast ≥ 4.5:1 in both modes"])),
    }
    for screen, items in screens[kind]:
        out.append("## Screen: %s" % screen)
        out.append("")
        for item in items:
            out.append("- [ ] %s" % item)
        out.append("")
    return "\n".join(out)


def render_pages_readme(profile):
    return "\n".join([
        generated_header(profile), "# Page overrides", "",
        "Each `pages/<page>.md` holds **deviations only** for one screen. Create one with:", "",
        "    python3 scripts/vd.py page --dir design-system/%s --name <page> --reason \"why this screen differs\"" % safe_slug((profile.get("project") or {}).get("slug") or (profile.get("project") or {}).get("name", "")),
        "", "Rules enforced by `vd.py validate`:", "",
        "1. Every row in `## Overrides` needs a non-empty reason.",
        "2. A page restating ≥ %d MASTER.md values unchanged, or copying ≥ 80 %% of its lines, is rejected (`page.copies-master`)." % RESTATED_THRESHOLD,
        "3. `Token / rule` must be a path that exists in `tokens.json` or a component id from the catalog.",
        "4. Pages never remap `semantic.color.*` meanings or `$extensions.vdp.platformUnit`.",
        "5. Rows count against the drift budget written in MASTER.md § Page Override Logic.",
        "6. Page-scoped intentional exceptions need an `Expires` date (or `never`).", "",
    ])


def render_page_skeleton(name, reason=None, project_name="", profile=None, created=None):
    slug = safe_slug(name)
    title = " ".join(w.capitalize() for w in slug.replace("_", "-").split("-"))
    header = ("<!-- %s vd.py %s; page: %s; profile-hash: %s -->" % (GENERATED_BY, TOOL_VERSION, slug, profile_hash(profile) if profile else "none"))
    return "\n".join([
        header,
        "# %s Page Overrides" % title, "",
        "> **PROJECT:** %s · **Page type:** %s · **Created:** %s" % (project_name or "—", reason or "(describe the screen)", created or today()),
        "> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.",
        "> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.",
        "", "**Reason for this page file:** %s" % (reason or "(fill in)"), "",
        "## Overrides", "",
        "| Token / rule | Master value | Page value | Reason |",
        "|---|---|---|---|",
        "<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->",
        "", "## Component remaps", "",
        "- (component id) → (catalog variant or another component), reason", "",
        "## Intentional exceptions (page scope)", "",
        "| Scope | Rule | Reason | Expires |", "|---|---|---|---|",
        "<!-- Expires: an ISO date (YYYY-MM-DD) or the word never; expired rows are a validate warning -->", "",
        "## Notes", "",
        "- Overrides that remap a token to another existing token (`{a.b}` → `{c.d}`) are not drift; only literal values (hex, px, ms) count against the drift budget.", "",
    ])


def changelog_entry(actor, bullets, when=None):
    lines = ["## %s · %s · [tool]" % (when or utc_now(), actor)]
    lines += ["- %s" % b for b in bullets]
    return "\n".join(lines) + "\n"


def append_changelog(path, entry):
    existing = path.read_text(encoding="utf-8") if path.is_file() else "# Changelog\n\nAppend-only. `vd.py` writes `[tool]` entries; humans write `[manual]` entries (format: `## <ISO UTC> · <actor> · [manual]`).\n"
    if not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + "\n" + entry, encoding="utf-8")


# ============================================================================ init


BODY_HASH_RE = re.compile(r"; body-hash: ([0-9a-f]{12}) -->")


def _body_hash(text):
    body = text.split("\n", 1)[1] if "\n" in text else ""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def stamp_body_hash(text):
    """Record the hash of everything below the header line so `init --force` can detect hand edits."""
    first, _sep, rest = text.partition("\n")
    return first.replace(" -->", "; body-hash: %s -->" % _body_hash(text), 1) + "\n" + rest


def master_hand_edited(path):
    """True when a tool-written MASTER.md was edited after generation (or carries no body hash to prove otherwise)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    m = BODY_HASH_RE.search(text.split("\n", 1)[0])
    return m is None or m.group(1) != _body_hash(text)


def master_state(path):
    if not path.is_file():
        return "absent"
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
    return "tool-owned" if first and GENERATED_BY in first[0] else "foreign"


def init_design_system(profile, output_dir, force=False, when=None):
    """Create design-system/<slug>/… ; returns a result dict. Raises InputError on an invalid profile."""
    errors = validate_profile(profile)
    if errors:
        raise InputError("profile invalid:\n  " + "\n  ".join(errors))
    project = profile.get("project") or {}
    slug = safe_slug(project.get("slug") or project.get("name", ""))
    root = Path(output_dir).resolve() / "design-system" / slug
    tokens = derive_tokens(profile)
    rows = catalog_rows_for(profile)
    when = when or utc_now()
    files = {
        "style-profile.json": dump_json(profile),
        "tokens.json": vd_tokens.dumps(tokens),
        "component-catalog.md": render_component_catalog(profile, rows, tokens=tokens),
        "asset-guidelines.md": render_asset_guidelines(profile, tokens),
        "interaction-guidelines.md": render_interaction_guidelines(profile, tokens),
        "visual-qa-checklist.md": render_qa_checklist(profile, tokens),
        "pages/README.md": render_pages_readme(profile),
    }
    master_text = stamp_body_hash(render_master(profile, tokens, len(rows), "%s · vd.py init · [tool]" % when, generated_at=when))
    state = master_state(root / "MASTER.md")
    created, skipped, overwritten, backups = [], [], [], []
    root.mkdir(parents=True, exist_ok=True)
    (root / "pages").mkdir(exist_ok=True)
    master_result = {"absent": "created", "tool-owned": "kept-tool-owned", "foreign": "kept"}[state]
    snippet = None
    if state == "absent":
        files["MASTER.md"] = master_text
    elif state == "tool-owned" and force:
        files["MASTER.md"] = master_text
        master_result = "rewritten"
        if master_hand_edited(root / "MASTER.md"):
            backup = root / ("MASTER.md.bak-%s" % (when or utc_now()).replace("-", "").replace(":", ""))
            (root / "MASTER.md").replace(backup)
            backups.append(backup.name)
            master_result = "rewritten (hand-edited copy saved as %s)" % backup.name
    elif state == "foreign":
        snippet = render_master_snippet(master_text)
        files["MASTER.visual-direction.md"] = snippet
    for rel, text in files.items():
        target = root / rel
        if target.exists():
            if (force and rel != "MASTER.md") or (rel == "MASTER.md" and master_result == "rewritten"):
                target.write_text(text, encoding="utf-8")
                overwritten.append(rel)
            else:
                skipped.append(rel)
        else:
            target.write_text(text, encoding="utf-8")
            created.append(rel)
    changelog_existed = (root / "CHANGELOG.md").is_file()
    if state == "tool-owned" and not force:
        skipped.append("MASTER.md")
    elif state == "foreign":
        skipped.append("MASTER.md")
    sem_count = len(tokens["semantic"]["color"])
    bullets = ["profile: style-profile.json (sha256 %s) · style: %s · derivation: %s" % (profile_hash(profile), (profile.get("style") or {}).get("id"), vd_tokens.DERIVATION_VERSION),
               "created: %s" % (", ".join(created) or "—"),
               "skipped (exists): %s" % (", ".join(skipped) or "—")]
    if overwritten:
        bullets.append("overwritten (--force): %s" % ", ".join(overwritten))
    if backups:
        bullets.append("backup (hand-edited MASTER.md): %s" % ", ".join(backups))
    bullets.append("master: %s" % master_result)
    bullets.append("tokens: %d semantic colours, %d primitive groups, %d components · unit %s · touch min %s" % (
        sem_count, len(tokens["primitive"]), len(tokens["component"]), tokens["$extensions"]["vdp"]["platformUnit"], tokens["$extensions"]["vdp"]["minTouchTarget"]))
    append_changelog(root / "CHANGELOG.md", changelog_entry("vd.py init%s" % (" --force" if force else ""), bullets, when))
    if not changelog_existed:
        created.append("CHANGELOG.md")
    return {"status": "ok", "design_system_dir": str(root), "slug": slug, "created_files": created,
            "skipped_files": skipped, "overwritten_files": overwritten, "master": master_result,
            "master_snippet": snippet, "changelog": "appended", "backups": backups}


# ============================================================================ validate


def page_copies_master(page_text, master_text):
    """True when a page restates MASTER.md instead of overriding it (≥3 master-only H2s or ≥80 % identical lines)."""
    master_h2 = set(split_h2(master_text))
    page_h2 = set(split_h2(page_text))
    master_only = master_h2 - set(PAGE_SKELETON_H2)
    if len(page_h2 & master_only) >= RESTATED_THRESHOLD:
        return True
    strip = lambda t: [l.strip() for l in t.splitlines() if l.strip() and not l.strip().startswith("<!--")]
    page_lines = strip(page_text)
    master_lines = set(strip(master_text))
    if len(page_lines) >= 10:
        shared = sum(1 for l in page_lines if l in master_lines)
        if shared / float(len(page_lines)) >= COPY_LINE_RATIO:
            return True
    return False


def parse_override_rows(page_text):
    """Rows of the ``## Overrides`` table as dicts (token, master, page, reason)."""
    body = split_h2(page_text).get("Overrides", "")
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or line.lower().startswith("| token"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        rows.append({"token": cells[0].strip("`"), "master": cells[1], "page": cells[2], "reason": cells[3]})
    return rows


LITERAL_VALUE_RE = re.compile(r"^(#[0-9A-Fa-f]{3,8}|rgba?\(.*\)|hsla?\(.*\)|-?\d+(\.\d+)?\s*(px|dp|pt|ms|s|rem|em|%)?|none|transparent)$", re.I)


def is_literal_value(value, tokens=None):
    """True for a raw value (hex, px, ms, …); False for a `{token}` reference or an existing token path."""
    v = str(value or "").strip().strip("`")
    if not v:
        return False
    if v.startswith("{") and v.endswith("}"):
        return False
    if isinstance(tokens, dict) and vd_tokens.lookup(tokens, v) is not None:
        return False
    return bool(LITERAL_VALUE_RE.match(v)) or vd_tokens.is_hex(v)


def _budget_group(token_path, tokens):
    leaf = vd_tokens.lookup(tokens, token_path)
    typ = leaf.get("$type") if isinstance(leaf, dict) else None
    low = token_path.lower()
    if typ == "color" or ".color." in low:
        return "color"
    if typ == "fontFamily":
        return "fontFamily"
    if typ == "shadow":
        return "shadow"
    if typ == "duration":
        return "duration"
    if "radius" in low:
        return "radius"
    if "fontsize" in low:
        return "fontSize"
    if typ == "dimension":
        return "spacing"
    return None


def validate_dir(dir_path, today_str=None):
    """Validate design-system/<slug>/ ; returns a list of findings {level, rule, file, message}."""
    root = Path(dir_path)
    if not root.is_dir():
        raise UsageError("design-system directory not found: %s" % dir_path)
    findings = []

    def add(level, rule, file, message):
        findings.append({"level": level, "rule": rule, "file": file, "message": message})

    profile = tokens = None
    for name in ("style-profile.json", "tokens.json", "CHANGELOG.md"):
        if not (root / name).is_file():
            add("error", "missing-file", name, "missing-file: %s" % name)
    master_path = root / "MASTER.md"
    if not master_path.is_file():
        add("error", "missing-file", "MASTER.md", "missing-file: MASTER.md")
    if (root / "style-profile.json").is_file():
        try:
            profile = json.loads((root / "style-profile.json").read_text(encoding="utf-8"))
        except ValueError as exc:
            add("error", "profile.malformed", "style-profile.json", "not valid JSON: %s" % exc)
        else:
            for err in validate_profile(profile):
                add("error", "profile." + err.split(":")[0].strip(), "style-profile.json", err)
    if (root / "tokens.json").is_file():
        try:
            tokens = json.loads((root / "tokens.json").read_text(encoding="utf-8"))
        except ValueError as exc:
            add("error", "tokens.malformed", "tokens.json", "not valid JSON: %s" % exc)
        else:
            for err in vd_tokens.validate_tokens(tokens, profile if isinstance(profile, dict) else None):
                add("error", err.split(":")[0].strip(), "tokens.json", err)
            try:
                for warn in vd_tokens.component_state_findings(tokens)[1]:
                    add("warning", "contrast.interactive-boundary", "tokens.json", warn)
            except (KeyError, TypeError, AttributeError):
                pass
    expected_hash = profile_hash(profile) if isinstance(profile, dict) else None
    master_text = ""
    if master_path.is_file():
        master_text = master_path.read_text(encoding="utf-8", errors="replace")
        state = master_state(master_path)
        if state == "tool-owned":
            h2 = split_h2(master_text)
            for heading in MASTER_H2:
                if heading not in h2:
                    add("error", "master.missing-section", "MASTER.md", "mandatory section missing: ## %s" % heading)
            if PLACEHOLDER_RE.search(master_text):
                add("error", "master.unresolved-placeholder", "MASTER.md", "unresolved template placeholder: %s" % PLACEHOLDER_RE.search(master_text).group(0))
            m = re.search(r"profile-hash: ([0-9a-f]{12})", master_text.splitlines()[0])
            if expected_hash and m and m.group(1) != expected_hash:
                add("warning", "master.stale", "MASTER.md", "profile-hash mismatch (run vd.py init --force to regenerate)")
        else:
            if not (root / "MASTER.visual-direction.md").is_file():
                add("warning", "master.foreign", "MASTER.md", "MASTER.md is not tool-owned and MASTER.visual-direction.md is absent; run vd.py init to produce the paste block")
            if isinstance(tokens, dict):
                known = set()
                for _p, leaf in vd_tokens.iter_leaves(dict((k, v) for k, v in tokens.items() if not k.startswith("$"))):
                    try:
                        value = vd_tokens.resolve_ref(tokens, leaf.get("$value"))
                    except KeyError:
                        continue
                    if isinstance(value, str):
                        known.update(h.upper() for h in HEX_IN_TEXT_RE.findall(value))
                for hx in sorted(set(h.upper() for h in HEX_IN_TEXT_RE.findall(master_text))):
                    if hx not in known:
                        add("warning", "master.colour-not-in-tokens", "MASTER.md", "MASTER.md colour %s not in tokens.json" % hx)
    # pages
    pages_dir = root / "pages"
    component_ids = set()
    groups = set()
    try:
        for r in vd_core.load_rows("components"):
            component_ids.add(r.get("Component ID", "").lower())
            groups.add(r.get("Group", "").lower())
    except FileNotFoundError:
        pass
    budget = dict(vd_tokens.DRIFT_BUDGET)
    if isinstance(tokens, dict):
        budget.update(((tokens.get("$extensions") or {}).get("vdp") or {}).get("driftBudget") or {})
    today_str = today_str or today()
    if pages_dir.is_dir():
        for page in sorted(pages_dir.glob("*.md")):
            if page.name.lower() == "readme.md":
                continue
            rel = "pages/%s" % page.name
            text = page.read_text(encoding="utf-8", errors="replace")
            if master_text and page_copies_master(text, master_text):
                add("error", "page.copies-master", rel, "page restates MASTER.md instead of overriding it")
            rows = parse_override_rows(text)
            restated = [r for r in rows if r["page"] and r["page"] == r["master"]]
            if len(restated) >= RESTATED_THRESHOLD:
                add("error", "page.copies-master", rel, "page restates %d master values: %s" % (len(restated), ", ".join(r["token"] for r in restated)))
            elif restated:
                add("warning", "page.restates-master", rel, "page restates %d master value(s): %s" % (len(restated), ", ".join(r["token"] for r in restated)))
            counts = {}
            for r in rows:
                token = r["token"]
                if not r["reason"]:
                    add("error", "page.missing-reason", rel, "override %s has no reason" % token)
                if token.startswith("semantic.color.") or token == "$extensions.vdp.platformUnit":
                    add("error", "page.semantic-remap", rel, "pages may not change %s" % token)
                low = token.lower()
                is_component = low in component_ids or low.split(".")[0] in groups
                if isinstance(tokens, dict) and not is_component:
                    if vd_tokens.lookup(tokens, token) is None:
                        add("error", "page.unknown-path", rel, "unknown token path or component id: %s" % token)
                    elif is_literal_value(r["page"], tokens):
                        group = _budget_group(token, tokens)
                        if group:
                            counts[group] = counts.get(group, 0) + 1
            for group, n in sorted(counts.items()):
                limit = budget.get(group)
                if limit is not None and n > limit:
                    add("error", "page.drift-budget", rel, "drift budget exceeded (%s: %d/%d)" % (group, n, limit))
            exc_body = split_h2(text).get("Intentional exceptions (page scope)", "")
            for line in exc_body.splitlines():
                cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else []
                if len(cells) >= 4 and cells[0] and not cells[0].startswith("---") and cells[0].lower() != "scope":
                    expires = cells[3]
                    if expires.lower() != "never" and re.match(r"^\d{4}-\d{2}-\d{2}$", expires) and expires < today_str:
                        add("warning", "page.exception-expired", rel, "intentional exception '%s' expired on %s" % (cells[0], expires))
                    elif expires.lower() != "never" and not re.match(r"^\d{4}-\d{2}-\d{2}$", expires):
                        add("warning", "page.exception-expires", rel, "intentional exception '%s' needs an ISO Expires date or 'never'" % cells[0])
    # changelog
    cl = root / "CHANGELOG.md"
    if cl.is_file():
        for n, line in enumerate(cl.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.startswith("## ") and not CHANGELOG_HEAD_RE.match(line):
                add("error", "changelog.malformed", "CHANGELOG.md", "line %d: expected '## <ISO-8601 UTC> · <actor> · [tool|manual]'" % n)
    # tool-owned companions: stale hash
    if expected_hash:
        for name in ("component-catalog.md", "asset-guidelines.md", "interaction-guidelines.md", "visual-qa-checklist.md"):
            p = root / name
            if p.is_file():
                first = p.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
                m = re.search(r"profile-hash: ([0-9a-f]{12})", first[0]) if first else None
                if m and m.group(1) != expected_hash:
                    add("warning", "stale", name, "profile-hash mismatch (run vd.py init --force to regenerate)")
    return findings


# ============================================================================ CLI


def _print_results(result, catalog):
    if result["count"] == 0:
        print("No results for '%s' in %s." % (result["query"], catalog))
        if result.get("suggestions"):
            print("Did you mean: %s" % ", ".join(result["suggestions"]))
        return
    for i, row in enumerate(result["results"], 1):
        score = "exact" if row.get("_score") == float("inf") else "%.2f" % row.get("_score", 0)
        if catalog == "styles":
            print("%d. %s — %s  [family: %s · radius: %s · shading: %s · motion: %s] (%s)" % (
                i, row["Style ID"], row.get("Style Name", ""), row.get("Family", ""), row.get("Radius Class", ""),
                row.get("Shading", ""), row.get("Motion Class", ""), score))
            print("   best for: %s" % first_clause(row.get("Best For", ""), 140))
        elif catalog == "genres":
            print("%d. %s — %s  [%s] (%s)" % (i, row["Genre ID"], row.get("Genre Name", ""), row.get("Kind", ""), score))
            print("   default styles: %s" % row.get("Default Styles", "").replace(";", ", "))
        else:
            print("%d. %s — %s  [group: %s · applies: %s] (%s)" % (i, row["Component ID"], row.get("Name", ""),
                                                                   row.get("Group", ""), row.get("Applies To", ""), score))
            print("   %s" % first_clause(row.get("Purpose", ""), 140))


def _json_results(result):
    out = dict(result)
    out["results"] = []
    for row in result["results"]:
        copy = dict(row)
        copy["_score"] = "exact" if row.get("_score") == float("inf") else row.get("_score")
        out["results"].append(copy)
    return out


def cmd_search(args, catalog):
    filters = {}
    if catalog == "styles" and getattr(args, "family", None):
        filters["Family"] = args.family
    if catalog == "components" and getattr(args, "kind", None):
        rows = vd_core.load_rows("components")
        result = vd_core.search(catalog, args.query, max_results=len(rows) or 1)
        result["results"] = [r for r in result["results"] if r.get("Applies To", "").strip().lower() in (args.kind, "both")][:args.n]
        result["count"] = len(result["results"])
        result["kind"] = args.kind
    else:
        result = vd_core.search(catalog, args.query, max_results=args.n, filters=filters or None)
    if args.json:
        print(json.dumps(_json_results(result), indent=2, ensure_ascii=False))
    else:
        _print_results(result, catalog)
    return 0


def _unknown_id(catalog, identifier, label):
    close = vd_core.closest_ids(catalog, identifier)
    if close:
        print("error: unknown %s id %r. Closest ids: %s" % (label, identifier, ", ".join(close)), file=sys.stderr)
    else:
        print("error: unknown %s id %r and no close match in the catalog (run `vd.py %s \"<query>\"`)." % (label, identifier, catalog), file=sys.stderr)
    return 1


def cmd_profile(args, parser):
    if not (args.style or args.genre or args.reference):
        parser.error("one of --style, --genre or --reference is required")
    platforms = list(dict.fromkeys(p.strip() for p in args.platform.split(",") if p.strip()))
    bad = [p for p in platforms if p not in PLATFORMS]
    if bad or not platforms:
        parser.error("--platform: %s not in %s" % (bad or ["(empty)"], ", ".join(PLATFORMS)))
    analysis = None
    partial = None
    ref_name = None
    if args.reference:
        doc = load_json(args.reference, "reference analysis")
        ref_name = Path(args.reference).name
        if isinstance(doc, dict) and doc.get("_partial") and doc.get("schema") == SCHEMA:
            partial = doc
        elif isinstance(doc, dict) and doc.get("schema") == REFERENCE_SCHEMA:
            analysis = doc
        else:
            raise InputError("%s: expected schema %r (or a _partial %r fragment), got %r" % (
                args.reference, REFERENCE_SCHEMA, SCHEMA, (doc or {}).get("schema") if isinstance(doc, dict) else type(doc).__name__))
    if args.genre:
        genre_row = vd_core.row_by_id("genres", args.genre)
        if genre_row is None:
            return _unknown_id("genres", args.genre, "genre")
        if args.style and vd_core.row_by_id("styles", args.style) is None:
            return _unknown_id("styles", args.style, "style")
        profile = build_profile_from_genre(genre_row, platforms, stack=args.stack, audience=args.audience, project=args.project, style_id=args.style)
    else:
        style_id = args.style or REFERENCE_CUSTOM_STYLE
        row = vd_core.row_by_id("styles", style_id)
        if row is None:
            return _unknown_id("styles", style_id, "style")
        kind = fragment_kind(partial) if partial is not None else None
        if analysis and not args.style:
            screen_types = set(str(r.get("screen_type", "")) for r in analysis.get("references") or [] if isinstance(r, dict))
            roles = set(role for r in analysis.get("references") or [] if isinstance(r, dict) for role in r.get("roles") or [])
            kind = "game" if (screen_types & {"gameplay", "shop"} or roles & {"hud", "characters"}) else "app"
        profile = build_profile_from_style(row, platforms, stack=args.stack, audience=args.audience, project=args.project, kind=kind)
    if analysis is not None:
        profile = build_profile_from_reference(analysis, ref_name, profile, owned_only=bool(args.style or args.genre))
    elif partial is not None:
        profile = merge_partial_profile(partial, profile, owned_only=bool(args.style or args.genre))
        if not any(s.get("type") == "reference-analysis" for s in profile.get("sources") or []):
            profile["sources"].insert(0, {"type": "reference-analysis", "ref": ref_name, "roles": []})
    if args.seed_design_system:
        profile = apply_seed(profile, load_json(args.seed_design_system, "design-system seed"))
    if args.project:
        profile["project"] = {"name": args.project, "slug": safe_slug(args.project)}
    errors = validate_profile(profile)
    if errors:
        print("error: built profile failed validation:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 1
    # every contrast walk (a changed fill hue) must be visible in the profile, not only in tokens.json
    notes = derive_tokens(profile)["$extensions"]["vdp"].get("contrastNotes") or []
    if notes:
        profile["unknowns"] = list(profile.get("unknowns") or []) + [n for n in notes if n not in (profile.get("unknowns") or [])]
    text = dump_json(profile)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        if args.json:
            sys.stdout.write(text)
        else:
            print("wrote %s (style %s, kind %s, platforms %s, stack %s)" % (
                args.out, profile["style"]["id"], profile["product"]["kind"], ",".join(platforms), profile["product"]["stack"]))
    else:
        sys.stdout.write(text)
    return 0


def cmd_init(args):
    profile = load_json(args.profile, "profile")
    if not isinstance(profile, dict):
        raise InputError("%s: profile must be a JSON object" % args.profile)
    out_dir = Path(args.output_dir)
    if out_dir.exists() and not out_dir.is_dir():
        raise UsageError("--output-dir exists and is not a directory: %s" % args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = init_design_system(profile, args.output_dir, force=args.force)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("design system: %s" % result["design_system_dir"])
        print("created: %s" % (", ".join(result["created_files"]) or "—"))
        print("skipped: %s" % (", ".join(result["skipped_files"]) or "—"))
        if result["overwritten_files"]:
            print("overwritten: %s" % ", ".join(result["overwritten_files"]))
        print("MASTER.md: %s" % result["master"])
        for name in result.get("backups") or []:
            print("backup: hand edits to the tool-written MASTER.md were kept in %s" % name)
        if result["master_snippet"]:
            print("\nMASTER.md already exists and is not tool-owned. Paste this block below \"## Global Rules\" "
                  "(also saved as MASTER.visual-direction.md):\n")
            print(result["master_snippet"])
    return 0


def cmd_page(args):
    root = Path(args.dir)
    if not root.is_dir():
        raise UsageError("--dir not found: %s" % args.dir)
    slug = safe_slug(args.name)
    target = root / "pages" / ("%s.md" % slug)
    profile = None
    if (root / "style-profile.json").is_file():
        try:
            profile = json.loads((root / "style-profile.json").read_text(encoding="utf-8"))
        except ValueError:
            profile = None
    project_name = (profile or {}).get("project", {}).get("name", "") if isinstance(profile, dict) else ""
    if target.exists() and not args.force:
        msg = "skipped: %s already exists (edit it, pick another --name, or pass --force)" % target
        if args.json:
            print(json.dumps({"status": "skipped", "page": str(target), "created": False, "message": msg}))
        else:
            print(msg)
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_page_skeleton(args.name, args.reason, project_name, profile if isinstance(profile, dict) else None), encoding="utf-8")
    bullets = ["profile: style-profile.json (sha256 %s)" % (profile_hash(profile) if isinstance(profile, dict) else "n/a"),
               "%s: pages/%s.md" % ("overwritten (--force)" if args.force else "created", slug),
               "reason: %s" % (args.reason or "—")]
    append_changelog(root / "CHANGELOG.md", changelog_entry("vd.py page %s" % slug, bullets))
    if args.json:
        print(json.dumps({"status": "ok", "page": str(target), "created": True, "slug": slug}))
    else:
        print("created %s" % target)
    return 0


def cmd_validate(args):
    findings = validate_dir(args.dir)
    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]
    if args.json:
        print(json.dumps({"status": "ok" if not errors else "error", "dir": str(args.dir), "errors": len(errors),
                          "warnings": len(warnings), "findings": findings}, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            print("%s: %s: %s" % (f["level"].upper(), f["file"], f["message"]))
        print("%s — %d error(s), %d warning(s)" % ("OK" if not errors else "FAILED", len(errors), len(warnings)))
    return 1 if errors else 0


def build_parser():
    p = argparse.ArgumentParser(prog="vd.py", description="Visual Direction: style catalog search, profile builder, design-contract generator.")
    sub = p.add_subparsers(dest="command")

    def add_search(name, help_text, default_n):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("query")
        sp.add_argument("-n", type=int, default=default_n, help="max results (default %d)" % default_n)
        sp.add_argument("--json", action="store_true", help="print JSON instead of text")
        return sp

    s_styles = add_search("styles", "search visual-styles.csv", 5)
    s_styles.add_argument("--family", help="filter by Family id (e.g. cute-cartoon)")
    add_search("genres", "search genre-profiles.csv", 5)
    s_comp = add_search("components", "search component-catalog.csv", 10)
    s_comp.add_argument("--kind", choices=KINDS, help="only components that apply to game or app (plus 'both')")

    pr = sub.add_parser("profile", help="build a Visual Direction Profile (vdp/1)")
    pr.add_argument("--style", help="style id from visual-styles.csv (route A; combinable with --genre and/or --reference)")
    pr.add_argument("--genre", help="genre id from genre-profiles.csv (route B: product kind/genre/screens/HUD/touch rules; combinable with --style and/or --reference)")
    pr.add_argument("--reference", help="reference-analysis.json (schema vdp-reference-analysis/1) or a _partial vdp/1 fragment (routes C/D)")
    pr.add_argument("--seed-design-system", help="JSON from `search.py \"<query>\" --design-system --json`; fills gaps only")
    pr.add_argument("--platform", required=True, help="comma-separated: %s" % ",".join(PLATFORMS))
    pr.add_argument("--stack", choices=STACKS, help="implementation stack")
    pr.add_argument("--audience", help="free text, e.g. casual-all-ages")
    pr.add_argument("--project", help="project name (slugged for design-system/<slug>)")
    pr.add_argument("--out", help="write the profile here (default: stdout)")
    pr.add_argument("--json", action="store_true", help="print the profile JSON to stdout even with --out")

    ini = sub.add_parser("init", help="write design-system/<slug>/ from a profile")
    ini.add_argument("--profile", required=True, help="style-profile.json")
    ini.add_argument("--output-dir", required=True, help="project root (design-system/<slug>/ is created inside)")
    ini.add_argument("--force", action="store_true", help="overwrite tool-owned files (never a foreign MASTER.md, never pages/*.md, never CHANGELOG.md)")
    ini.add_argument("--json", action="store_true", help="print {status, design_system_dir, created_files, skipped_files, ...}")

    pg = sub.add_parser("page", help="create pages/<page>.md override skeleton")
    pg.add_argument("--dir", required=True, help="design-system/<slug>")
    pg.add_argument("--name", required=True, help="page name (slugged)")
    pg.add_argument("--reason", help="why this page needs overrides")
    pg.add_argument("--force", action="store_true", help="overwrite an existing page skeleton")
    pg.add_argument("--json", action="store_true", help="print JSON result")

    va = sub.add_parser("validate", help="validate design-system/<slug>/ (profile, tokens, MASTER, pages, CHANGELOG)")
    va.add_argument("--dir", required=True, help="design-system/<slug>")
    va.add_argument("--json", action="store_true", help="print {status, findings} JSON")
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_usage(sys.stderr)
        print("vd.py: error: a subcommand is required (styles, genres, components, profile, init, page, validate)", file=sys.stderr)
        return 2
    try:
        if args.command in ("styles", "genres", "components"):
            return cmd_search(args, args.command)
        if args.command == "profile":
            return cmd_profile(args, parser)
        if args.command == "init":
            return cmd_init(args)
        if args.command == "page":
            return cmd_page(args)
        if args.command == "validate":
            return cmd_validate(args)
    except UsageError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    except InputError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    except (LookupError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
