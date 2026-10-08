#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design system generator: color-mode resolution, WCAG contrast and dark-palette helpers.
"""

# ============ COLOR MODE RESOLUTION ============
# Style, palette and anti-patterns are resolved from separate CSVs. Without a
# shared notion of "which mode did we land on", a dark-primary style can be
# paired with a light palette and a "don't use dark mode" anti-pattern.

# Phrases in styles.csv "Light Mode ✓" / "Dark Mode ✓" that mark a style as
# dark-first rather than merely dark-capable ("✓ Full" means both work).
_DARK_PRIMARY_MARKERS = (
    "dark mode primary", "dark primary", "dark-only", "dark only",
    "dark preferred", "dark focused", "dark-first", "dark rich",
    "light mode only as exception",
)

# Query phrases that are an explicit request for a dark theme.
_DARK_QUERY_MARKERS = (
    "dark mode", "dark theme", "dark ui", "dark-mode", "darkmode",
    "night mode", "midnight", "oled",
)

# Anti-pattern clauses that contradict a resolved dark mode.
_DARK_ANTI_PATTERN_MARKERS = ("dark mode", "dark modes", "dark theme")

# Relative luminance below which a Background hex counts as a dark surface.
# #1F2937 (the lightest dark background in colors.csv) sits at ~0.026 and
# #E8ECF1 (the darkest light background) at ~0.79, so the gap is wide.
_DARK_BACKGROUND_MAX_LUMINANCE = 0.18


def _relative_luminance(hex_color: str):
    """WCAG relative luminance of a #RRGGBB string, or None if unparseable."""
    if not hex_color:
        return None
    value = hex_color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    if len(value) != 6:
        return None
    try:
        channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    except ValueError:
        return None
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _palette_is_dark(palette: dict) -> bool:
    """True when a colors.csv row's Background is a dark surface."""
    luminance = _relative_luminance((palette or {}).get("Background", ""))
    return luminance is not None and luminance < _DARK_BACKGROUND_MAX_LUMINANCE


def _contrast_ratio(first: str, second: str):
    """WCAG contrast ratio for two hex colors, or None if either is invalid."""
    first_luminance = _relative_luminance(first)
    second_luminance = _relative_luminance(second)
    if first_luminance is None or second_luminance is None:
        return None
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _style_is_dark_primary(style: dict) -> bool:
    """True when a styles.csv row describes itself as dark-first."""
    if not style:
        return False
    preferred_mode = style.get("Preferred Mode", "").strip().lower()
    if preferred_mode in {"dark", "light"}:
        return preferred_mode == "dark"
    if (style.get("Light Mode ✓") == "not-recommended"
            and style.get("Dark Mode ✓") == "supported"):
        return True
    declared = "{} {}".format(
        style.get("Light Mode ✓", ""), style.get("Dark Mode ✓", "")
    ).lower()
    return any(marker in declared for marker in _DARK_PRIMARY_MARKERS)


def _query_wants_dark(query: str) -> bool:
    """True when the query explicitly asks for a dark theme."""
    lowered = (query or "").lower()
    return any(marker in lowered for marker in _DARK_QUERY_MARKERS)


def _resolve_color_mode(query: str, style: dict) -> str:
    """Resolve the mode the rest of the output has to agree with."""
    if _query_wants_dark(query) or _style_is_dark_primary(style):
        return "dark"
    return "light"


def _derive_dark_palette(palette: dict) -> dict:
    """Keep product brand tokens while deriving accessible dark surfaces."""
    derived = dict(palette)
    background = "#0F172A"
    ring_candidates = (
        palette.get("Ring"), palette.get("Accent"), palette.get("Primary"),
        "#60A5FA",
    )
    ring = next(
        (candidate for candidate in ring_candidates
         if (_contrast_ratio(candidate, background) or 0) >= 3),
        "#60A5FA",
    )
    derived.update({
        "Background": background,
        "Foreground": "#F8FAFC",
        "Card": "#111827",
        "Card Foreground": "#F8FAFC",
        "Muted": "#1E293B",
        "Muted Foreground": "#CBD5E1",
        "Border": "#334155",
        "Ring": ring,
        "_mode_derivation": "derived-dark",
    })
    return derived


def _select_palette_for_mode(palettes: list, mode: str,
                             category: str = None) -> dict:
    """Pick the highest-ranked palette matching the resolved mode.

    Only the dark case filters. Light is left on the existing "top hit wins"
    behaviour so queries that never mention a mode keep their current palette.
    Falls back to the top hit when the data has no matching ramp.
    """
    if not palettes:
        return {}
    category_palette = next(
        (palette for palette in palettes
         if palette.get("Product Type") == category),
        None,
    )
    if category_palette:
        if mode == "dark" and not _palette_is_dark(category_palette):
            return _derive_dark_palette(category_palette)
        return category_palette
    if mode == "dark":
        for palette in palettes:
            if _palette_is_dark(palette):
                return palette
    return palettes[0]


def _filter_anti_patterns_for_mode(anti_patterns: str, mode: str) -> str:
    """Drop "avoid dark mode" advice once dark mode is the resolved answer."""
    if mode != "dark" or not anti_patterns:
        return anti_patterns
    kept = [
        clause for clause in anti_patterns.split("+")
        if not any(marker in clause.lower() for marker in _DARK_ANTI_PATTERN_MARKERS)
    ]
    return " + ".join(clause.strip() for clause in kept if clause.strip())
