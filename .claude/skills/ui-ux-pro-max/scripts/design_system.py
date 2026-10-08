#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design System Generator - Aggregates search results and applies reasoning
to generate comprehensive design system recommendations.

Usage:
    from design_system import generate_design_system
    result = generate_design_system("SaaS dashboard", "My Project")
    print(result["text"])

    # With persistence (Master + Overrides pattern)
    result = generate_design_system("SaaS dashboard", "My Project", persist=True, output_dir="/path/to/project")
    result["persistence"]  # {"status": "success"|"skipped_exists", "created_files": [...], ...}
    result = generate_design_system("SaaS dashboard", "My Project", persist=True, page="dashboard", output_dir="/path/to/project")
"""

import io
import sys
from ds_config import (  # noqa: F401 - re-exported for existing importers
    DIAL_TIERS,
    REASONING_FILE,
    SEARCH_CONFIG,
    SEMANTIC_COLOR_ENTRIES,
    _resolve_dial,
)
from ds_color import (  # noqa: F401
    _contrast_ratio,
    _derive_dark_palette,
    _filter_anti_patterns_for_mode,
    _palette_is_dark,
    _query_wants_dark,
    _relative_luminance,
    _resolve_color_mode,
    _select_palette_for_mode,
    _style_is_dark_primary,
)
from ds_generator import DesignSystemGenerator
from ds_format_terminal import (  # noqa: F401
    BOX_WIDTH,
    ansi_ljust,
    format_ascii_box,
    format_markdown,
    hex_to_ansi,
    section_header,
)
from ds_persist import (  # noqa: F401
    _detect_page_type,
    _generate_intelligent_overrides,
    _write_persisted_file,
    format_master_md,
    format_page_override_md,
    persist_design_system,
    safe_slug,
)

# Force UTF-8 for stdout/stderr to handle emojis/box-drawing chars on Windows (cp1252 default)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ============ MAIN ENTRY POINT ============
def generate_design_system(query: str, project_name: str = None, output_format: str = "ascii",
                           persist: bool = False, page: str = None, output_dir: str = None,
                           variance: int = None, motion: int = None, density: int = None,
                           force: bool = False) -> dict:
    """
    Main entry point for design system generation.

    Args:
        query: Search query (e.g., "SaaS dashboard", "e-commerce luxury")
        project_name: Optional project name for output header
        output_format: "ascii" (default) or "markdown"
        persist: If True, save design system to design-system/ folder
        page: Optional page name for page-specific override file
        output_dir: Optional output directory (defaults to current working directory)
        variance: Optional 1-10 DESIGN_VARIANCE dial (1=centered/minimal, 10=bold/asymmetric)
        motion: Optional 1-10 MOTION_INTENSITY dial, pulls a matching GSAP snippet from motion.csv
        density: Optional 1-10 VISUAL_DENSITY dial, overrides the spacing scale (1=spacious, 10=dense)
        force: If True, overwrite an existing MASTER.md; otherwise persistence
               is skipped (with a status message) when one already exists

    Returns:
        dict with keys: "text" (formatted design system string), "design_system"
        (raw dict, useful for --json callers), and "persistence" (result of
        persist_design_system(), or None if persist=False)
    """
    generator = DesignSystemGenerator()
    design_system = generator.generate(query, project_name, variance=variance, motion=motion, density=density)

    persistence_result = None
    if persist:
        persistence_result = persist_design_system(design_system, page, output_dir, query, force=force)

    text = format_markdown(design_system) if output_format == "markdown" else format_ascii_box(design_system)

    return {
        "text": text,
        "design_system": design_system,
        "persistence": persistence_result,
    }


# ============ CLI SUPPORT ============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Design System")
    parser.add_argument("query", help="Search query (e.g., 'SaaS dashboard')")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format")

    args = parser.parse_args()

    result = generate_design_system(args.query, args.project_name, args.format)
    print(result["text"])
