#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIP Design Search CLI - Search corporate identity design guidelines
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from core import search, search_all, get_cip_brief, CSV_CONFIG

# --cip-brief prints emoji, which raises UnicodeEncodeError when stdout/stderr is
# a cp1252 pipe or file (Windows without PYTHONUTF8). Same intent as the guard in
# ui-ux-pro-max/scripts/search.py.
for _stream in (sys.stdout, sys.stderr):
    _encoding = getattr(_stream, "encoding", None)
    if _encoding and _encoding.lower().replace("-", "") != "utf8" and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors=_stream.errors)


def format_results(results, domain):
    """Format search results for display"""
    if not results:
        return "No results found."

    output = []
    for i, item in enumerate(results, 1):
        output.append(f"\n{'='*60}")
        output.append(f"Result {i}:")
        for key, value in item.items():
            if value:
                output.append(f"  {key}: {value}")
    return "\n".join(output)


def format_brief(brief):
    """Format CIP brief for display"""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"CIP DESIGN BRIEF: {brief['brand_name']}")
    output.append(f"{'='*60}")

    if brief.get("industry"):
        output.append(f"\n📊 INDUSTRY: {brief['industry'].get('Industry', 'N/A')}")
        output.append(f"   Style: {brief['industry'].get('CIP Style', 'N/A')}")
        output.append(f"   Mood: {brief['industry'].get('Mood', 'N/A')}")

    if brief.get("style"):
        output.append(f"\n🎨 DESIGN STYLE: {brief['style'].get('Style Name', 'N/A')}")
        output.append(f"   Description: {brief['style'].get('Description', 'N/A')}")
        output.append(f"   Materials: {brief['style'].get('Materials', 'N/A')}")
        output.append(f"   Finishes: {brief['style'].get('Finishes', 'N/A')}")

    if brief.get("color_system"):
        output.append(f"\n🎯 COLOR SYSTEM:")
        output.append(f"   Primary: {brief['color_system'].get('primary', 'N/A')}")
        output.append(f"   Secondary: {brief['color_system'].get('secondary', 'N/A')}")

    output.append(f"\n✏️ TYPOGRAPHY: {brief.get('typography', 'N/A')}")

    if brief.get("recommended_deliverables"):
        output.append(f"\n📦 RECOMMENDED DELIVERABLES:")
        for d in brief["recommended_deliverables"]:
            output.append(f"   • {d.get('Deliverable', 'N/A')}: {d.get('Description', '')[:60]}...")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search CIP design guidelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search deliverables
  python search.py "business card"

  # Search specific domain
  python search.py "luxury elegant" --domain style

  # Generate CIP brief
  python search.py "tech startup" --cip-brief -b "TechFlow"

  # Search all domains
  python search.py "corporate professional" --all

  # JSON output
  python search.py "vehicle branding" --json
        """
    )

    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()),
                        help="Search domain (auto-detected if not specified)")
    parser.add_argument("--max", "-m", type=int, default=3, help="Max results (default: 3)")
    parser.add_argument("--all", "-a", action="store_true", help="Search all domains")
    parser.add_argument("--cip-brief", "-c", action="store_true", help="Generate CIP brief")
    parser.add_argument("--brand", "-b", default="BrandName", help="Brand name for CIP brief")
    parser.add_argument("--style", "-s", help="Style override for CIP brief")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.cip_brief:
        brief = get_cip_brief(args.brand, args.query, args.style)
        if args.json:
            print(json.dumps(brief, indent=2))
        else:
            print(format_brief(brief))
    elif args.all:
        results = search_all(args.query, args.max)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for domain, items in results.items():
                print(f"\n{'#'*60}")
                print(f"# {domain.upper()}")
                print(format_results(items, domain))
    else:
        result = search(args.query, args.domain, args.max)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nDomain: {result['domain']}")
            print(f"Query: {result['query']}")
            print(f"Results: {result['count']}")
            print(format_results(result.get("results", []), result["domain"]))


if __name__ == "__main__":
    main()
