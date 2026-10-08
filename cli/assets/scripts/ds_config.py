#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design system generator: configuration constants and design-dial resolution.
"""

# ============ CONFIGURATION ============
REASONING_FILE = "ui-reasoning.csv"

SEARCH_CONFIG = {
    "product": {"max_results": 1},
    "style": {"max_results": 3},
    "color": {"max_results": 5},
    "landing": {"max_results": 2},
    "typography": {"max_results": 2}
}

SEMANTIC_COLOR_ENTRIES = (
    ("Primary", "primary", "--color-primary"),
    ("On Primary", "on_primary", "--color-on-primary"),
    ("Secondary", "secondary", "--color-secondary"),
    ("On Secondary", "on_secondary", "--color-on-secondary"),
    ("Accent/CTA", "accent", "--color-accent"),
    ("On Accent/CTA", "on_accent", "--color-on-accent"),
    ("Background", "background", "--color-background"),
    ("Foreground", "foreground", "--color-foreground"),
    ("Card", "card", "--color-card"),
    ("Card Foreground", "card_foreground", "--color-card-foreground"),
    ("Muted", "muted", "--color-muted"),
    ("Muted Foreground", "muted_foreground", "--color-muted-foreground"),
    ("Border", "border", "--color-border"),
    ("Destructive", "destructive", "--color-destructive"),
    ("On Destructive", "on_destructive", "--color-on-destructive"),
    ("Ring", "ring", "--color-ring"),
)

# ============ DESIGN DIALS (1-10) ============
# Inspired by taste-skill's DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY
# knobs: three optional 1-10 sliders that bias the existing query-based search
# instead of replacing it. Each dial buckets into a low/mid/high tier.
DIAL_TIERS = {
    "variance": [
        (1, 3, {"label": "Centered / Minimal", "style_keywords": ["Minimalism", "Exaggerated Minimalism", "centered", "symmetric", "grid-based"]}),
        (4, 7, {"label": "Balanced / Modern", "style_keywords": ["modern", "structured", "balanced"]}),
        (8, 10, {"label": "Bold / Asymmetric", "style_keywords": ["Brutalism", "Bento Grids", "asymmetric", "experimental"]}),
    ],
    "motion": [
        (1, 3, {"label": "Subtle", "tier": "Subtle"}),
        (4, 7, {"label": "Standard", "tier": "Standard"}),
        (8, 10, {"label": "Complex", "tier": "Complex"}),
    ],
    "density": [
        (1, 3, {"label": "Spacious", "spacing": {"xs": "4px", "sm": "8px", "md": "24px", "lg": "32px", "xl": "48px", "2xl": "64px", "3xl": "96px"}}),
        (4, 7, {"label": "Standard", "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px", "2xl": "48px", "3xl": "64px"}}),
        (8, 10, {"label": "Dense / Dashboard", "spacing": {"xs": "2px", "sm": "4px", "md": "8px", "lg": "12px", "xl": "16px", "2xl": "24px", "3xl": "32px"}}),
    ],
}


def _resolve_dial(dial_name: str, value) -> dict:
    """Bucket a 1-10 dial value into its tier config. Returns None if value is None."""
    if value is None:
        return None
    value = max(1, min(10, int(value)))
    for lo, hi, info in DIAL_TIERS[dial_name]:
        if lo <= value <= hi:
            return {**info, "value": value}
    return None
