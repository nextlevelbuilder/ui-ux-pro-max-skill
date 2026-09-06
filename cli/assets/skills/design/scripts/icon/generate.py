#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon Generation Script using Gemini 3.1 Pro Preview API
Generates SVG icons via text generation (SVG is XML text format)

Model: gemini-3.1-pro-preview - best thinking, token efficiency, factual consistency

Usage:
    python generate.py --prompt "settings gear icon" --style outlined
    python generate.py --prompt "shopping cart" --style filled --color "#6366F1"
    python generate.py --name "dashboard" --category navigation --style duotone
    python generate.py --prompt "cloud upload" --batch 4 --output-dir ./icons
    python generate.py --prompt "user profile" --sizes "16,24,32,48"
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime


def load_env():
    """Load .env files in priority order"""
    env_paths = [
        Path(__file__).parent.parent.parent / ".env",
        Path.home() / ".claude" / "skills" / ".env",
        Path.home() / ".claude" / ".env"
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key not in os.environ:
                            os.environ[key] = value.strip('"\'')

load_env()

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed.")
    print("Install with: pip install google-genai")
    sys.exit(1)


# ============ CONFIGURATION ============
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3.1-pro-preview"

# Icon styles with SVG-specific instructions
ICON_STYLES = {
    "outlined": "outlined stroke icons, 2px stroke width, no fill, clean open paths",
    "filled": "solid filled icons, no stroke, flat color fills, bold shapes",
    "duotone": "duotone style with primary color at full opacity and secondary color at 30% opacity, layered shapes",
    "thin": "thin line icons, 1px or 1.5px stroke width, delicate minimalist lines",
    "bold": "bold thick line icons, 3px stroke width, heavy weight, impactful",
    "rounded": "rounded icons with round line caps and joins, soft corners, friendly feel",
    "sharp": "sharp angular icons, square line caps and mitered joins, precise edges",
    "flat": "flat design icons, solid fills, no gradients or shadows, geometric simplicity",
    "gradient": "linear or radial gradient fills, modern vibrant color transitions",
    "glassmorphism": "glassmorphism style with semi-transparent fills, blur backdrop effect simulation, frosted glass",
    "pixel": "pixel art style icons on a grid, retro 8-bit aesthetic, crisp edges",
    "hand-drawn": "hand-drawn sketch style, slightly irregular strokes, organic feel, imperfect lines",
    "isometric": "isometric 3D projection, 30-degree angles, dimensional depth",
    "glyph": "simple glyph style, single solid shape, minimal detail, pictogram",
    "animated-ready": "animated-ready SVG with named groups and IDs for CSS/JS animation targets",
}

ICON_CATEGORIES = {
    "navigation": "arrows, menus, hamburger, chevrons, home, back, forward, breadcrumb",
    "action": "edit, delete, save, download, upload, share, copy, paste, print, search",
    "communication": "email, chat, phone, video call, notification, bell, message bubble",
    "media": "play, pause, stop, skip, volume, microphone, camera, image, gallery",
    "file": "document, folder, archive, attachment, cloud, database, storage",
    "user": "person, group, avatar, profile, settings, lock, key, shield",
    "commerce": "cart, bag, wallet, credit card, receipt, tag, gift, store",
    "data": "chart, graph, analytics, dashboard, table, filter, sort, calendar",
    "development": "code, terminal, bug, git, API, server, database, deploy",
    "social": "heart, star, thumbs up, bookmark, flag, trophy, badge, crown",
    "weather": "sun, moon, cloud, rain, snow, wind, thunder, temperature",
    "map": "pin, location, compass, globe, route, directions, map marker",
}

# SVG generation prompt template
SVG_PROMPT_TEMPLATE = """Generate a clean, production-ready SVG icon.

Requirements:
- Output ONLY valid SVG code, nothing else
- ViewBox: "0 0 {viewbox} {viewbox}"
- Use currentColor for strokes/fills (inherits CSS color)
- No embedded fonts or text elements unless specifically requested
- No raster images or external references
- Optimized paths with minimal nodes
- Accessible: include <title> element with icon description
{style_instructions}
{color_instructions}
{size_instructions}

Icon to generate: {prompt}

Output the SVG code only, wrapped in ```svg``` code block."""

SVG_BATCH_PROMPT_TEMPLATE = """Generate {count} distinct SVG icon variations for: {prompt}

Requirements for EACH icon:
- Output ONLY valid SVG code
- ViewBox: "0 0 {viewbox} {viewbox}"
- Use currentColor for strokes/fills (inherits CSS color)
- No embedded fonts, raster images, or external references
- Optimized paths with minimal nodes
- Include <title> element with icon description
{style_instructions}
{color_instructions}

Generate {count} different visual interpretations. Output each SVG in a separate ```svg``` code block.
Label each variation (e.g., "Variation 1: [brief description]")."""


def extract_svgs(text):
    """Extract SVG code blocks from model response"""
    svgs = []

    # Try ```svg code blocks first
    pattern = r'```svg\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        svgs.extend(matches)

    # Fallback: try ```xml code blocks
    if not svgs:
        pattern = r'```xml\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        svgs.extend(matches)

    # Fallback: try bare <svg> tags
    if not svgs:
        pattern = r'(<svg[^>]*>.*?</svg>)'
        matches = re.findall(pattern, text, re.DOTALL)
        svgs.extend(matches)

    # Clean up extracted SVGs
    cleaned = []
    for svg in svgs:
        svg = svg.strip()
        if not svg.startswith('<svg'):
            # Try to find <svg> within the extracted text
            match = re.search(r'(<svg[^>]*>.*?</svg>)', svg, re.DOTALL)
            if match:
                svg = match.group(1)
            else:
                continue
        cleaned.append(svg)

    return cleaned


def apply_color(svg_code, color):
    """Replace currentColor with specific color if provided"""
    if color:
        # Replace currentColor with the specified color
        svg_code = svg_code.replace('currentColor', color)
        # If no currentColor was present, add fill/stroke color
        if color not in svg_code:
            svg_code = svg_code.replace('<svg', f'<svg color="{color}"', 1)
    return svg_code


def apply_viewbox_size(svg_code, size):
    """Adjust SVG viewBox to target size"""
    if size:
        # Update width/height attributes if present
        svg_code = re.sub(r'width="[^"]*"', f'width="{size}"', svg_code)
        svg_code = re.sub(r'height="[^"]*"', f'height="{size}"', svg_code)
        # Add width/height if not present
        if 'width=' not in svg_code:
            svg_code = svg_code.replace('<svg', f'<svg width="{size}" height="{size}"', 1)
    return svg_code


def generate_icon(prompt, style=None, category=None, name=None,
                  color=None, size=24, output_path=None, viewbox=24):
    """Generate a single SVG icon using Gemini 3.1 Pro Preview"""

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set")
        print("Set it with: export GEMINI_API_KEY='your-key'")
        return None

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Build style instructions
    style_instructions = ""
    if style and style in ICON_STYLES:
        style_instructions = f"- Style: {ICON_STYLES[style]}"

    # Build color instructions
    color_instructions = "- Use currentColor for all strokes and fills"
    if color:
        color_instructions = f"- Use color: {color} for primary elements, currentColor for secondary"

    # Build size instructions
    size_instructions = f"- Design for {size}px display size, optimize detail level accordingly"

    # Build final prompt
    icon_prompt = prompt
    if category and category in ICON_CATEGORIES:
        icon_prompt = f"{prompt} (category: {ICON_CATEGORIES[category]})"
    if name:
        icon_prompt = f"'{name}' icon: {icon_prompt}"

    full_prompt = SVG_PROMPT_TEMPLATE.format(
        prompt=icon_prompt,
        viewbox=viewbox,
        style_instructions=style_instructions,
        color_instructions=color_instructions,
        size_instructions=size_instructions
    )

    print(f"Generating icon with {MODEL}...")
    print(f"Prompt: {prompt}")
    if style:
        print(f"Style: {style}")
    print()

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4096,
            )
        )

        # Extract SVG from response
        response_text = response.text if hasattr(response, 'text') else ""
        if not response_text:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text

        svgs = extract_svgs(response_text)

        if not svgs:
            print("No valid SVG generated. Model response:")
            print(response_text[:500])
            return None

        svg_code = svgs[0]

        # Apply color if specified
        svg_code = apply_color(svg_code, color)

        # Apply size
        svg_code = apply_viewbox_size(svg_code, size)

        # Determine output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            slug = name or prompt.split()[0] if prompt else "icon"
            slug = re.sub(r'[^a-zA-Z0-9_-]', '_', slug.lower())
            style_suffix = f"_{style}" if style else ""
            output_path = f"{slug}{style_suffix}_{timestamp}.svg"

        # Save SVG
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_code)

        print(f"Icon saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating icon: {e}")
        return None


def generate_batch(prompt, count, output_dir, style=None, color=None,
                   viewbox=24, name=None):
    """Generate multiple icon variations"""

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set")
        return []

    client = genai.Client(api_key=GEMINI_API_KEY)
    os.makedirs(output_dir, exist_ok=True)

    # Build instructions
    style_instructions = ""
    if style and style in ICON_STYLES:
        style_instructions = f"- Style: {ICON_STYLES[style]}"

    color_instructions = "- Use currentColor for all strokes and fills"
    if color:
        color_instructions = f"- Use color: {color} for primary elements"

    full_prompt = SVG_BATCH_PROMPT_TEMPLATE.format(
        prompt=prompt,
        count=count,
        viewbox=viewbox,
        style_instructions=style_instructions,
        color_instructions=color_instructions
    )

    print(f"\n{'='*60}")
    print(f"  BATCH ICON GENERATION")
    print(f"  Model: {MODEL}")
    print(f"  Prompt: {prompt}")
    print(f"  Variants: {count}")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}\n")

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=16384,
            )
        )

        response_text = response.text if hasattr(response, 'text') else ""
        if not response_text:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text

        svgs = extract_svgs(response_text)

        if not svgs:
            print("No valid SVGs generated.")
            print(response_text[:500])
            return []

        results = []
        slug = name or re.sub(r'[^a-zA-Z0-9_-]', '_', prompt.split()[0].lower())
        style_suffix = f"_{style}" if style else ""

        for i, svg_code in enumerate(svgs[:count]):
            svg_code = apply_color(svg_code, color)
            filename = f"{slug}{style_suffix}_{i+1:02d}.svg"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(svg_code)

            results.append(filepath)
            print(f"  [{i+1}/{len(svgs[:count])}] Saved: {filename}")

        print(f"\n{'='*60}")
        print(f"  BATCH COMPLETE: {len(results)}/{count} icons generated")
        print(f"{'='*60}\n")

        return results

    except Exception as e:
        print(f"Error generating icons: {e}")
        return []


def generate_sizes(prompt, sizes, style=None, color=None, output_dir=None, name=None):
    """Generate same icon at multiple sizes"""
    if output_dir is None:
        output_dir = "."
    os.makedirs(output_dir, exist_ok=True)

    results = []
    slug = name or re.sub(r'[^a-zA-Z0-9_-]', '_', prompt.split()[0].lower())
    style_suffix = f"_{style}" if style else ""

    for size in sizes:
        print(f"Generating {size}px variant...")
        filename = f"{slug}{style_suffix}_{size}px.svg"
        filepath = os.path.join(output_dir, filename)

        result = generate_icon(
            prompt=prompt,
            style=style,
            color=color,
            size=size,
            output_path=filepath,
            viewbox=size
        )

        if result:
            results.append(result)

        time.sleep(1)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate SVG icons using Gemini 3.1 Pro Preview"
    )
    parser.add_argument("--prompt", "-p", type=str, help="Icon description")
    parser.add_argument("--name", "-n", type=str, help="Icon name (for filename)")
    parser.add_argument("--style", "-s", choices=list(ICON_STYLES.keys()),
                        help="Icon style")
    parser.add_argument("--category", "-c", choices=list(ICON_CATEGORIES.keys()),
                        help="Icon category for context")
    parser.add_argument("--color", type=str,
                        help="Primary color (hex, e.g. #6366F1). Default: currentColor")
    parser.add_argument("--size", type=int, default=24,
                        help="Icon size in px (default: 24)")
    parser.add_argument("--viewbox", type=int, default=24,
                        help="SVG viewBox size (default: 24)")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument("--output-dir", type=str, help="Output directory for batch")
    parser.add_argument("--batch", type=int,
                        help="Number of icon variants to generate")
    parser.add_argument("--sizes", type=str,
                        help="Comma-separated sizes (e.g. '16,24,32,48')")
    parser.add_argument("--list-styles", action="store_true",
                        help="List available icon styles")
    parser.add_argument("--list-categories", action="store_true",
                        help="List available icon categories")

    args = parser.parse_args()

    if args.list_styles:
        print("Available icon styles:")
        for style, desc in ICON_STYLES.items():
            print(f"  {style}: {desc[:70]}...")
        return

    if args.list_categories:
        print("Available icon categories:")
        for cat, desc in ICON_CATEGORIES.items():
            print(f"  {cat}: {desc}")
        return

    if not args.prompt and not args.name:
        parser.error("Either --prompt or --name is required")

    prompt = args.prompt or args.name

    # Multi-size mode
    if args.sizes:
        sizes = [int(s.strip()) for s in args.sizes.split(",")]
        generate_sizes(
            prompt=prompt,
            sizes=sizes,
            style=args.style,
            color=args.color,
            output_dir=args.output_dir or "./icons",
            name=args.name
        )
    # Batch mode
    elif args.batch:
        output_dir = args.output_dir or "./icons"
        generate_batch(
            prompt=prompt,
            count=args.batch,
            output_dir=output_dir,
            style=args.style,
            color=args.color,
            viewbox=args.viewbox,
            name=args.name
        )
    # Single icon
    else:
        generate_icon(
            prompt=prompt,
            style=args.style,
            category=args.category,
            name=args.name,
            color=args.color,
            size=args.size,
            output_path=args.output,
            viewbox=args.viewbox
        )


if __name__ == "__main__":
    main()
