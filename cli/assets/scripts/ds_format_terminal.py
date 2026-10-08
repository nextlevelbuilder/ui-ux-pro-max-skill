#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design system generator: ASCII-box and Markdown output formatters.
"""

import os
import re
from ds_config import SEMANTIC_COLOR_ENTRIES


# ============ OUTPUT FORMATTERS ============
BOX_WIDTH = 90  # Wider box for more content


def hex_to_ansi(hex_color: str) -> str:
    """Convert hex color to ANSI True Color swatch (██) with fallback."""
    if not hex_color or not hex_color.startswith('#'):
        return ""
    colorterm = os.environ.get('COLORTERM', '')
    if colorterm not in ('truecolor', '24bit'):
        return ""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return ""
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m██\033[0m "


def ansi_ljust(s: str, width: int) -> str:
    """Like str.ljust but accounts for zero-width ANSI escape sequences."""
    import re
    visible_len = len(re.sub(r'\033\[[0-9;]*m', '', s))
    pad = width - visible_len
    return s + (" " * max(0, pad))


def section_header(name: str, width: int) -> str:
    """Create a Unicode section separator: ├─── NAME ───...┤"""
    label = f"─── {name} "
    fill = "─" * (width - len(label) - 1)
    return f"├{label}{fill}┤"


def format_ascii_box(design_system: dict) -> str:
    """Format design system as Unicode box with ANSI color swatches."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")
    dials = design_system.get("dials", {})
    motion_snippet = design_system.get("motion_snippet", {})

    def wrap_text(text: str, prefix: str, width: int) -> list:
        """Wrap long text into multiple lines."""
        if not text:
            return []
        words = text.split()
        lines = []
        current_line = prefix
        for word in words:
            if len(current_line) + len(word) + 1 <= width - 2:
                current_line += (" " if current_line != prefix else "") + word
            else:
                if current_line != prefix:
                    lines.append(current_line)
                current_line = prefix + word
        if current_line != prefix:
            lines.append(current_line)
        return lines

    # Build sections from pattern
    sections = pattern.get("sections", "").split(" > ")
    sections = [s.strip() for s in sections if s.strip()]

    # Build output lines
    lines = []
    w = BOX_WIDTH - 1

    # Header with double-line box
    lines.append("╔" + "═" * w + "╗")
    lines.append(ansi_ljust(f"║  TARGET: {project} - RECOMMENDED DESIGN SYSTEM", BOX_WIDTH) + "║")
    lines.append("╚" + "═" * w + "╝")
    lines.append("┌" + "─" * w + "┐")

    # Design Dials section (only if at least one dial was set)
    if any(dials.get(k) is not None for k in ("variance", "motion", "density")):
        lines.append(section_header("DESIGN DIALS", BOX_WIDTH + 1))
        if dials.get("variance") is not None:
            lines.append(f"│  Variance: {dials['variance']}/10 — {dials['variance_label']}".ljust(BOX_WIDTH) + "│")
        if dials.get("motion") is not None:
            lines.append(f"│  Motion:   {dials['motion']}/10 — {dials['motion_label']}".ljust(BOX_WIDTH) + "│")
        if dials.get("density") is not None:
            lines.append(f"│  Density:  {dials['density']}/10 — {dials['density_label']}".ljust(BOX_WIDTH) + "│")

    # Pattern section
    lines.append(section_header("PATTERN", BOX_WIDTH + 1))
    lines.append(f"│  Name: {pattern.get('name', '')}".ljust(BOX_WIDTH) + "│")
    if pattern.get('conversion'):
        lines.append(f"│     Conversion: {pattern.get('conversion', '')}".ljust(BOX_WIDTH) + "│")
    if pattern.get('cta_placement'):
        lines.append(f"│     CTA: {pattern.get('cta_placement', '')}".ljust(BOX_WIDTH) + "│")
    lines.append("│     Sections:".ljust(BOX_WIDTH) + "│")
    for i, section in enumerate(sections, 1):
        lines.append(f"│       {i}. {section}".ljust(BOX_WIDTH) + "│")

    # Style section
    lines.append(section_header("STYLE", BOX_WIDTH + 1))
    lines.append(f"│  Name: {style.get('name', '')}".ljust(BOX_WIDTH) + "│")
    light = style.get("light_mode", "")
    dark = style.get("dark_mode", "")
    if light or dark:
        lines.append(f"│     Mode Support: Light {light}  Dark {dark}".ljust(BOX_WIDTH) + "│")
    if style.get("keywords"):
        for line in wrap_text(f"Keywords: {style.get('keywords', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if style.get("best_for"):
        for line in wrap_text(f"Best For: {style.get('best_for', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if style.get("performance") or style.get("accessibility"):
        perf_a11y = f"Performance: {style.get('performance', '')} | Accessibility: {style.get('accessibility', '')}"
        lines.append(f"│     {perf_a11y}".ljust(BOX_WIDTH) + "│")

    # Colors section (extended palette with ANSI swatches)
    lines.append(section_header("COLORS", BOX_WIDTH + 1))
    for label, key, css_var in SEMANTIC_COLOR_ENTRIES:
        hex_val = colors.get(key, "")
        if not hex_val:
            continue
        swatch = hex_to_ansi(hex_val)
        content = f"│     {swatch}{label + ':':14s} {hex_val:10s} ({css_var})"
        lines.append(ansi_ljust(content, BOX_WIDTH) + "│")
    if colors.get("notes"):
        for line in wrap_text(f"Notes: {colors.get('notes', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")

    # Typography section
    lines.append(section_header("TYPOGRAPHY", BOX_WIDTH + 1))
    lines.append(f"│  {typography.get('heading', '')} / {typography.get('body', '')}".ljust(BOX_WIDTH) + "│")
    if typography.get("mood"):
        for line in wrap_text(f"Mood: {typography.get('mood', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if typography.get("best_for"):
        for line in wrap_text(f"Best For: {typography.get('best_for', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if typography.get("google_fonts_url"):
        lines.append(f"│     Google Fonts: {typography.get('google_fonts_url', '')}".ljust(BOX_WIDTH) + "│")
    if typography.get("css_import"):
        lines.append(f"│     CSS Import: {typography.get('css_import', '')[:70]}...".ljust(BOX_WIDTH) + "│")

    # Key Effects section
    if effects:
        lines.append(section_header("KEY EFFECTS", BOX_WIDTH + 1))
        for line in wrap_text(effects, "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")

    # Motion section (GSAP skeleton, only if --motion dial was set)
    if motion_snippet:
        lines.append(section_header("MOTION", BOX_WIDTH + 1))
        lines.append(f"│  {motion_snippet.get('Category', '')} ({motion_snippet.get('Intensity Tier', '')})".ljust(BOX_WIDTH) + "│")
        lines.append(f"│     Trigger: {motion_snippet.get('Trigger', '')} | Duration: {motion_snippet.get('Duration', '')} | Easing: {motion_snippet.get('Easing', '')}".ljust(BOX_WIDTH) + "│")
        for line in wrap_text(f"GSAP: {motion_snippet.get('GSAP Snippet', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
        if motion_snippet.get("Framework Notes"):
            for line in wrap_text(f"Framework: {motion_snippet.get('Framework Notes', '')}", "│     ", BOX_WIDTH):
                lines.append(line.ljust(BOX_WIDTH) + "│")

    # Anti-patterns section
    if anti_patterns:
        lines.append(section_header("AVOID", BOX_WIDTH + 1))
        for line in wrap_text(anti_patterns, "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")

    # Pre-Delivery Checklist section
    lines.append(section_header("PRE-DELIVERY CHECKLIST", BOX_WIDTH + 1))
    checklist_items = [
        "[ ] No emojis as icons (use SVG: Heroicons/Lucide)",
        "[ ] cursor-pointer on all clickable elements",
        "[ ] Hover states with smooth transitions (150-300ms)",
        "[ ] Light mode: text contrast 4.5:1 minimum",
        "[ ] Focus states visible for keyboard nav",
        "[ ] prefers-reduced-motion respected",
        "[ ] Responsive: 375px, 768px, 1024px, 1440px"
    ]
    for item in checklist_items:
        lines.append(f"│     {item}".ljust(BOX_WIDTH) + "│")

    lines.append("└" + "─" * w + "┘")

    return "\n".join(lines)


def format_markdown(design_system: dict) -> str:
    """Format design system as markdown."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")
    dials = design_system.get("dials", {})
    motion_snippet = design_system.get("motion_snippet", {})

    lines = []
    lines.append(f"## Design System: {project}")
    lines.append("")

    # Design Dials section (only if at least one dial was set)
    if any(dials.get(k) is not None for k in ("variance", "motion", "density")):
        lines.append("### Design Dials")
        if dials.get("variance") is not None:
            lines.append(f"- **Variance:** {dials['variance']}/10 — {dials['variance_label']}")
        if dials.get("motion") is not None:
            lines.append(f"- **Motion:** {dials['motion']}/10 — {dials['motion_label']}")
        if dials.get("density") is not None:
            lines.append(f"- **Density:** {dials['density']}/10 — {dials['density_label']}")
        lines.append("")

    # Pattern section
    lines.append("### Pattern")
    lines.append(f"- **Name:** {pattern.get('name', '')}")
    if pattern.get('conversion'):
        lines.append(f"- **Conversion Focus:** {pattern.get('conversion', '')}")
    if pattern.get('cta_placement'):
        lines.append(f"- **CTA Placement:** {pattern.get('cta_placement', '')}")
    if pattern.get('color_strategy'):
        lines.append(f"- **Color Strategy:** {pattern.get('color_strategy', '')}")
    lines.append(f"- **Sections:** {pattern.get('sections', '')}")
    lines.append("")

    # Style section
    lines.append("### Style")
    lines.append(f"- **Name:** {style.get('name', '')}")
    light = style.get("light_mode", "")
    dark = style.get("dark_mode", "")
    if light or dark:
        lines.append(f"- **Mode Support:** Light {light} | Dark {dark}")
    if style.get('keywords'):
        lines.append(f"- **Keywords:** {style.get('keywords', '')}")
    if style.get('best_for'):
        lines.append(f"- **Best For:** {style.get('best_for', '')}")
    if style.get('performance') or style.get('accessibility'):
        lines.append(f"- **Performance:** {style.get('performance', '')} | **Accessibility:** {style.get('accessibility', '')}")
    lines.append("")

    # Colors section (extended palette)
    lines.append("### Colors")
    lines.append("| Role | Hex | CSS Variable |")
    lines.append("|------|-----|--------------|")
    for label, key, css_var in SEMANTIC_COLOR_ENTRIES:
        hex_val = colors.get(key, "")
        if hex_val:
            lines.append(f"| {label} | `{hex_val}` | `{css_var}` |")
    if colors.get("notes"):
        lines.append(f"\n*Notes: {colors.get('notes', '')}*")
    lines.append("")

    # Typography section
    lines.append("### Typography")
    lines.append(f"- **Heading:** {typography.get('heading', '')}")
    lines.append(f"- **Body:** {typography.get('body', '')}")
    if typography.get("mood"):
        lines.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("best_for"):
        lines.append(f"- **Best For:** {typography.get('best_for', '')}")
    if typography.get("google_fonts_url"):
        lines.append(f"- **Google Fonts:** {typography.get('google_fonts_url', '')}")
    if typography.get("css_import"):
        lines.append(f"- **CSS Import:**")
        lines.append(f"```css")
        lines.append(f"{typography.get('css_import', '')}")
        lines.append(f"```")
    lines.append("")

    # Key Effects section
    if effects:
        lines.append("### Key Effects")
        lines.append(f"{effects}")
        lines.append("")

    # Motion section (GSAP skeleton, only if --motion dial was set)
    if motion_snippet:
        lines.append("### Motion")
        lines.append(f"**{motion_snippet.get('Category', '')}** ({motion_snippet.get('Intensity Tier', '')}) — Trigger: {motion_snippet.get('Trigger', '')} | Duration: {motion_snippet.get('Duration', '')} | Easing: `{motion_snippet.get('Easing', '')}`")
        lines.append("```js")
        lines.append(motion_snippet.get("GSAP Snippet", ""))
        lines.append("```")
        if motion_snippet.get("Framework Notes"):
            lines.append(f"*Framework notes: {motion_snippet.get('Framework Notes', '')}*")
        motion_do = motion_snippet.get("Do", "")
        motion_dont = motion_snippet.get("Don't", "")
        if motion_do:
            lines.append(f"- ✅ {motion_do}")
        if motion_dont:
            lines.append(f"- ❌ {motion_dont}")
        lines.append("")

    # Anti-patterns section
    if anti_patterns:
        lines.append("### Avoid (Anti-patterns)")
        newline_bullet = '\n- '
        lines.append(f"- {anti_patterns.replace(' + ', newline_bullet)}")
        lines.append("")

    # Pre-Delivery Checklist section
    lines.append("### Pre-Delivery Checklist")
    lines.append("- [ ] No emojis as icons (use SVG: Heroicons/Lucide)")
    lines.append("- [ ] cursor-pointer on all clickable elements")
    lines.append("- [ ] Hover states with smooth transitions (150-300ms)")
    lines.append("- [ ] Light mode: text contrast 4.5:1 minimum")
    lines.append("- [ ] Focus states visible for keyboard nav")
    lines.append("- [ ] prefers-reduced-motion respected")
    lines.append("- [ ] Responsive: 375px, 768px, 1024px, 1440px")
    lines.append("")

    return "\n".join(lines)
