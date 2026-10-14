#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slide Search CLI - Search slide design databases for strategies, layouts, copy, and charts
"""

import sys
import json
import argparse
from slide_search_core import (
    search, search_all, AVAILABLE_DOMAINS,
    search_with_context, get_layout_for_goal, get_typography_for_slide,
    get_color_for_emotion, get_background_config
)


def format_result(result, domain):
    """Format a single search result for display"""
    output = []

    if domain == "strategy":
        output.append(f"**{result.get('strategy_name', 'N/A')}**")
        output.append(f"  Slides: {result.get('slide_count', 'N/A')}")
        output.append(f"  Structure: {result.get('structure', 'N/A')}")
        output.append(f"  Goal: {result.get('goal', 'N/A')}")
        output.append(f"  Audience: {result.get('audience', 'N/A')}")
        output.append(f"  Tone: {result.get('tone', 'N/A')}")
        output.append(f"  Arc: {result.get('narrative_arc', 'N/A')}")
        output.append(f"  Source: {result.get('sources', 'N/A')}")

    elif domain == "layout":
        output.append(f"**{result.get('layout_name', 'N/A')}**")
        output.append(f"  Use case: {result.get('use_case', 'N/A')}")
        output.append(f"  Zones: {result.get('content_zones', 'N/A')}")
        output.append(f"  Visual weight: {result.get('visual_weight', 'N/A')}")
        output.append(f"  CTA: {result.get('cta_placement', 'N/A')}")
        output.append(f"  Recommended: {result.get('recommended_for', 'N/A')}")
        output.append(f"  Avoid: {result.get('avoid_for', 'N/A')}")
        output.append(f"  CSS: {result.get('css_structure', 'N/A')}")

    elif domain == "copy":
        output.append(f"**{result.get('formula_name', 'N/A')}**")
        output.append(f"  Components: {result.get('components', 'N/A')}")
        output.append(f"  Use case: {result.get('use_case', 'N/A')}")
        output.append(f"  Template: {result.get('example_template', 'N/A')}")
        output.append(f"  Emotion: {result.get('emotion_trigger', 'N/A')}")
        output.append(f"  Slide type: {result.get('slide_type', 'N/A')}")
        output.append(f"  Source: {result.get('source', 'N/A')}")

    elif domain == "chart":
        output.append(f"**{result.get('chart_type', 'N/A')}**")
        output.append(f"  Best for: {result.get('best_for', 'N/A')}")
        output.append(f"  Data type: {result.get('data_type', 'N/A')}")
        output.append(f"  When to use: {result.get('when_to_use', 'N/A')}")
        output.append(f"  When to avoid: {result.get('when_to_avoid', 'N/A')}")
        output.append(f"  Max categories: {result.get('max_categories', 'N/A')}")
        output.append(f"  Slide context: {result.get('slide_context', 'N/A')}")
        output.append(f"  CSS: {result.get('css_implementation', 'N/A')}")
        output.append(f"  Accessibility: {result.get('accessibility_notes', 'N/A')}")

    return "\n".join(output)


def format_context(context):
    """Format contextual recommendations for display."""
    output = []
    output.append(f"\n=== CONTEXTUAL RECOMMENDATIONS ===")
    output.append(f"Inferred Goal: {context.get('inferred_goal', 'N/A')}")
    output.append(f"Position: Slide {context.get('slide_position')} of {context.get('total_slides')}")

    if context.get('recommended_layout'):
        output.append(f"\n📐 Layout: {context['recommended_layout']}")
        output.append(f"   Direction: {context.get('layout_direction', 'N/A')}")
        output.append(f"   Visual Weight: {context.get('visual_weight', 'N/A')}")

    if context.get('typography'):
        typo = context['typography']
        output.append(f"\n📝 Typography:")
        output.append(f"   Primary: {typo.get('primary_size', 'N/A')}")
        output.append(f"   Secondary: {typo.get('secondary_size', 'N/A')}")
        output.append(f"   Contrast: {typo.get('weight_contrast', 'N/A')}")

    if context.get('color_treatment'):
        color = context['color_treatment']
        output.append(f"\n🎨 Color Treatment:")
        output.append(f"   Background: {color.get('background', 'N/A')}")
        output.append(f"   Text: {color.get('text_color', 'N/A')}")
        output.append(f"   Accent: {color.get('accent_usage', 'N/A')}")

    if context.get('should_break_pattern'):
        output.append(f"\n⚡ Pattern Break: YES (use contrasting layout)")

    if context.get('should_use_full_bleed'):
        output.append(f"\n🖼️ Full Bleed: Recommended for emotional impact")

    if context.get('use_background_image') and context.get('background'):
        bg = context['background']
        output.append(f"\n📸 Background Image:")
        output.append(f"   Category: {bg.get('image_category', 'N/A')}")
        output.append(f"   Overlay: {bg.get('overlay_style', 'N/A')}")
        output.append(f"   Keywords: {bg.get('search_keywords', 'N/A')}")

    output.append(f"\n✨ Animation: {context.get('animation_class', 'animate-fade-up')}")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search slide design databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  search-slides.py "investor pitch"           # Auto-detect domain (strategy)
  search-slides.py "funnel conversion" -d chart
  search-slides.py "headline hook" -d copy
  search-slides.py "two column" -d layout
  search-slides.py "startup funding" --all    # Search all domains
  search-slides.py "metrics dashboard" --json # JSON output

Contextual Search (Premium System):
  search-slides.py "problem slide" --context --position 2 --total 9
  search-slides.py "cta" --context --position 9 --total 9 --prev-emotion frustration
        """
    )

    parser.add_argument("query", help="Search query")
    parser.add_argument("-d", "--domain", choices=AVAILABLE_DOMAINS,
                        help="Specific domain to search (auto-detected if not specified)")
    parser.add_argument("-n", "--max-results", type=int, default=3,
                        help="Maximum results to return (default: 3)")
    parser.add_argument("--all", action="store_true",
                        help="Search across all domains")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")

    # Contextual search options
    parser.add_argument("--context", action="store_true",
                        help="Use contextual search with layout/typography/color recommendations")
    parser.add_argument("--position", type=int, default=1,
                        help="Slide position in deck (1-based, default: 1)")
    parser.add_argument("--total", type=int, default=9,
                        help="Total slides in deck (default: 9)")
    parser.add_argument("--prev-emotion", type=str, default=None,
                        help="Previous slide's emotion for contrast calculation")

    args = parser.parse_args()

    # Contextual search mode
    if args.context:
        result = search_with_context(
            args.query,
            slide_position=args.position,
            total_slides=args.total,
            previous_emotion=args.prev_emotion
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_context(result['context']))

            # Also show base search results
            if result.get('base_results'):
                print("\n\n=== RELATED SEARCH RESULTS ===")
                for domain, data in result['base_results'].items():
                    print(f"\n--- {domain.upper()} ---")
                    for item in data['results']:
                        print(format_result(item, domain))
                        print()
        return

    if args.all:
        results = search_all(args.query, args.max_results)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print(f"No results found for: {args.query}")
                return

            for domain, data in results.items():
                print(f"\n=== {domain.upper()} ===")
                print(f"File: {data['file']}")
                print(f"Results: {data['count']}")
                print()
                for result in data['results']:
                    print(format_result(result, domain))
                    print()
    else:
        result = search(args.query, args.domain, args.max_results)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("error"):
                print(f"Error: {result['error']}")
                return

            print(f"Domain: {result['domain']}")
            print(f"Query: {result['query']}")
            print(f"File: {result['file']}")
            print(f"Results: {result['count']}")
            print()

            if result['count'] == 0:
                print("No matching results found.")
                return

            for i, item in enumerate(result['results'], 1):
                print(f"--- Result {i} ---")
                print(format_result(item, result['domain']))
                print()


if __name__ == "__main__":
    main()
