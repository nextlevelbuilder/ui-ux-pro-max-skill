#!/usr/bin/env python3
"""
Background Image Fetcher
Fetches real images from Pexels for slide backgrounds.
Uses web scraping (no API key required) or WebFetch tool integration.
"""

import json
import csv
import re
import sys
from pathlib import Path

# Project root relative to this script
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
TOKENS_PATH = PROJECT_ROOT / 'assets' / 'design-tokens.json'
BACKGROUNDS_CSV = Path(__file__).parent.parent / 'data' / 'slide-backgrounds.csv'


def resolve_token_reference(ref: str, tokens: dict) -> str:
    """Resolve token reference like {primitive.color.ocean-blue.500} to hex value."""
    if not ref or not ref.startswith('{') or not ref.endswith('}'):
        return ref  # Already a value, not a reference

    # Parse reference: {primitive.color.ocean-blue.500}
    path = ref[1:-1].split('.')  # ['primitive', 'color', 'ocean-blue', '500']
    current = tokens
    for key in path:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None  # Invalid path
    # Return $value if it's a token object
    if isinstance(current, dict) and '$value' in current:
        return current['$value']
    return current


def load_brand_colors():
    """Load colors from assets/design-tokens.json for overlay gradients.

    Resolves semantic token references to actual hex values.
    """
    try:
        with open(TOKENS_PATH) as f:
            tokens = json.load(f)

        colors = tokens.get('primitive', {}).get('color', {})
        semantic = tokens.get('semantic', {}).get('color', {})

        # Try semantic tokens first (preferred) - resolve references
        if semantic:
            primary_ref = semantic.get('primary', {}).get('$value')
            secondary_ref = semantic.get('secondary', {}).get('$value')
            accent_ref = semantic.get('accent', {}).get('$value')
            background_ref = semantic.get('background', {}).get('$value')

            primary = resolve_token_reference(primary_ref, tokens)
            secondary = resolve_token_reference(secondary_ref, tokens)
            accent = resolve_token_reference(accent_ref, tokens)
            background = resolve_token_reference(background_ref, tokens)

            if primary and secondary:
                return {
                    'primary': primary,
                    'secondary': secondary,
                    'accent': accent or primary,
                    'background': background or '#0D0D0D',
                }

        # Fallback: find first color palette with 500 value (primary)
        primary_keys = ['ocean-blue', 'coral', 'blue', 'primary']
        secondary_keys = ['golden-amber', 'purple', 'amber', 'secondary']
        accent_keys = ['emerald', 'mint', 'green', 'accent']

        primary_color = None
        secondary_color = None
        accent_color = None

        for key in primary_keys:
            if key in colors and isinstance(colors[key], dict):
                primary_color = colors[key].get('500', {}).get('$value')
                if primary_color:
                    break

        for key in secondary_keys:
            if key in colors and isinstance(colors[key], dict):
                secondary_color = colors[key].get('500', {}).get('$value')
                if secondary_color:
                    break

        for key in accent_keys:
            if key in colors and isinstance(colors[key], dict):
                accent_color = colors[key].get('500', {}).get('$value')
                if accent_color:
                    break

        background = colors.get('dark', {}).get('800', {}).get('$value', '#0D0D0D')

        return {
            'primary': primary_color or '#3B82F6',
            'secondary': secondary_color or '#F59E0B',
            'accent': accent_color or '#10B981',
            'background': background,
        }
    except (FileNotFoundError, KeyError, TypeError):
        # Fallback defaults
        return {
            'primary': '#3B82F6',
            'secondary': '#F59E0B',
            'accent': '#10B981',
            'background': '#0D0D0D',
        }


def load_backgrounds_config():
    """Load background configuration from CSV."""
    config = {}
    try:
        with open(BACKGROUNDS_CSV, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                config[row['slide_type']] = row
    except FileNotFoundError:
        print(f"Warning: {BACKGROUNDS_CSV} not found")
    return config


def get_overlay_css(style: str, brand_colors: dict) -> str:
    """Generate overlay CSS using brand colors from design-tokens.json."""
    overlays = {
        'gradient-dark': f"linear-gradient(135deg, {brand_colors['background']}E6, {brand_colors['background']}B3)",
        'gradient-brand': f"linear-gradient(135deg, {brand_colors['primary']}CC, {brand_colors['secondary']}99)",
        'gradient-accent': f"linear-gradient(135deg, {brand_colors['accent']}99, transparent)",
        'blur-dark': f"rgba(13,13,13,0.8)",
        'desaturate-dark': f"rgba(13,13,13,0.7)",
    }
    return overlays.get(style, overlays['gradient-dark'])


# Curated high-quality images from Pexels (free to use, pre-selected for brand aesthetic)
CURATED_IMAGES = {
    'hero': [
        'https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/1089438/pexels-photo-1089438.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'vision': [
        'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3182812/pexels-photo-3182812.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'team': [
        'https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3184338/pexels-photo-3184338.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3182773/pexels-photo-3182773.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'testimonial': [
        'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/1181622/pexels-photo-1181622.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'cta': [
        'https://images.pexels.com/photos/3184339/pexels-photo-3184339.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3184298/pexels-photo-3184298.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'problem': [
        'https://images.pexels.com/photos/3760529/pexels-photo-3760529.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/897817/pexels-photo-897817.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'solution': [
        'https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3184644/pexels-photo-3184644.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'hook': [
        'https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/1089438/pexels-photo-1089438.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'social': [
        'https://images.pexels.com/photos/3184360/pexels-photo-3184360.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3184287/pexels-photo-3184287.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
    'demo': [
        'https://images.pexels.com/photos/1181675/pexels-photo-1181675.jpeg?auto=compress&cs=tinysrgb&w=1920',
        'https://images.pexels.com/photos/3861958/pexels-photo-3861958.jpeg?auto=compress&cs=tinysrgb&w=1920',
    ],
}


def get_curated_images(slide_type: str) -> list:
    """Get curated images for slide type."""
    return CURATED_IMAGES.get(slide_type, CURATED_IMAGES.get('hero', []))


def get_pexels_search_url(keywords: str) -> str:
    """Generate Pexels search URL for manual lookup."""
    import urllib.parse
    return f"https://www.pexels.com/search/{urllib.parse.quote(keywords)}/"


def get_background_image(slide_type: str) -> dict:
    """
    Get curated image matching slide type and brand aesthetic.
    Uses pre-selected Pexels images (no API/scraping needed).
    """
    brand_colors = load_brand_colors()
    config = load_backgrounds_config()

    slide_config = config.get(slide_type)
    overlay_style = 'gradient-dark'
    keywords = slide_type

    if slide_config:
        keywords = slide_config.get('search_keywords', slide_config.get('image_category', slide_type))
        overlay_style = slide_config.get('overlay_style', 'gradient-dark')

    # Get curated images
    urls = get_curated_images(slide_type)
    if urls:
        return {
            'url': urls[0],
            'all_urls': urls,
            'overlay': get_overlay_css(overlay_style, brand_colors),
            'attribution': 'Photo from Pexels (free to use)',
            'source': 'pexels-curated',
            'search_url': get_pexels_search_url(keywords),
        }

    # Fallback: provide search URL for manual selection
    return {
        'url': None,
        'overlay': get_overlay_css(overlay_style, brand_colors),
        'keywords': keywords,
        'search_url': get_pexels_search_url(keywords),
        'available_types': list(CURATED_IMAGES.keys()),
    }


def generate_css_for_background(result: dict, slide_class: str = '.slide-with-bg') -> str:
    """Generate CSS for a background slide."""
    if not result.get('url'):
        search_url = result.get('search_url', '')
        return f"""/* No image scraped. Search manually: {search_url} */
/* Overlay ready: {result.get('overlay', 'gradient-dark')} */
"""

    return f"""{slide_class} {{
    background-image: url('{result['url']}');
    background-size: cover;
    background-position: center;
    position: relative;
}}

{slide_class}::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: {result['overlay']};
}}

{slide_class} .content {{
    position: relative;
    z-index: 1;
}}

/* {result.get('attribution', 'Pexels')} - {result.get('search_url', '')} */
"""


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Get background images for slides')
    parser.add_argument('slide_type', nargs='?', help='Slide type (hero, vision, team, etc.)')
    parser.add_argument('--list', action='store_true', help='List available slide types')
    parser.add_argument('--css', action='store_true', help='Output CSS for the background')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--colors', action='store_true', help='Show brand colors')
    parser.add_argument('--all', action='store_true', help='Show all curated URLs')

    args = parser.parse_args()

    if args.colors:
        colors = load_brand_colors()
        print("\nBrand Colors (from design-tokens.json):")
        for name, value in colors.items():
            print(f"  {name}: {value}")
        return

    if args.list:
        print("\nAvailable slide types (curated images):")
        for slide_type, urls in CURATED_IMAGES.items():
            print(f"  {slide_type}: {len(urls)} images")
        return

    if not args.slide_type:
        parser.print_help()
        return

    result = get_background_image(args.slide_type)

    if args.json:
        print(json.dumps(result, indent=2))
    elif args.css:
        print(generate_css_for_background(result))
    elif args.all:
        print(f"\nAll images for '{args.slide_type}':")
        for i, url in enumerate(result.get('all_urls', []), 1):
            print(f"  {i}. {url}")
    else:
        print(f"\nImage URL: {result['url']}")
        print(f"Alternatives: {len(result.get('all_urls', []))} available (use --all)")
        print(f"Overlay: {result['overlay']}")


if __name__ == '__main__':
    main()
