#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Search - BM25 search engine for UI/UX style guides
Usage: python search.py "<query>" [--domain <domain>] [--stack <stack>] [--max-results 3]
       python search.py "<query>" --design-system [-p "Project Name"]
       python search.py "<query>" --config-path /path/to/config [--apply-brand] [--export-a2ui]

Domains: style, prompt, color, chart, landing, product, ux, typography
Stacks: html-tailwind, react, nextjs, vue, svelte, swiftui, react-native, flutter, shadcn, htmx-alpine-axum, tauri
External Config: Supports .ui-ux-pro-max-config/ directory for custom data and brand settings
"""

import argparse
import json
import sys
from pathlib import Path
from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack

# Import external configuration modules if available
try:
    from core import search_with_external_config, EXTERNAL_CONFIG_AVAILABLE
except ImportError:
    EXTERNAL_CONFIG_AVAILABLE = False
    search_with_external_config = None

try:
    from design_system import generate_design_system
except ImportError:
    generate_design_system = None

try:
    from a2ui_exporter import A2UIExporter
except ImportError:
    A2UIExporter = None


def format_output(result):
    """Format results for Claude consumption (token-optimized)"""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []

    # Handle external configuration results
    if result.get("external_config") or result.get("enhanced_results"):
        output.append(f"## UI Pro Max Enhanced Search Results")
        output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']}")

        # Check for external config status
        if result.get("external_config"):
            ext_config = result["external_config"]
            output.append(f"**External Config:** {'enabled' if ext_config.get('enabled') else 'disabled'}")
            if result.get('brand_applied'):
                output.append(f"**Brand Applied:** Yes")
            output.append(f"**Domains:** {ext_config.get('domains_loaded', 0)} | **Stacks:** {ext_config.get('stacks_loaded', 0)}")
        elif result.get("external_config_status"):
            output.append(f"**External Config:** {result['external_config_status'].get('enabled', 'disabled')}")
            if result['external_config_status'].get('brand_applied'):
                output.append(f"**Brand Applied:** Yes")

        output.append(f"**Source:** {'merged_data' if result.get('source') == 'merged_data' else 'Combined built-in + external'} | **Found:** {result['count']} results\n")

        results_list = result.get('enhanced_results') or result.get('results', [])
        for i, row in enumerate(results_list, 1):
            output.append(f"### Result {i}")

            # Show brand modifications if applied
            if row.get("brand_applied"):
                brand_info = row["brand_applied"]
                if brand_info.get("colors_replaced"):
                    output.append(f"- **Brand Colors Applied:** {len(brand_info['colors_replaced'])} replacements")
                if brand_info.get("fonts_applied"):
                    output.append(f"- **Brand Fonts Applied:** {', '.join(brand_info['fonts_applied'])}")
                if brand_info.get("modifications"):
                    output.append(f"- **Brand Modifications:** {len(brand_info['modifications'])} changes")
                output.append("")

            # Show regular result data (exclude internal fields from display)
            for key, value in row.items():
                if key in ["brand_applied", "score", "_source"]:
                    continue
                value_str = str(value)
                if len(value_str) > 300:
                    value_str = value_str[:300] + "..."
                output.append(f"- **{key}:** {value_str}")
            output.append("")

    elif result.get("stack"):
        output.append(f"## UI Pro Max Stack Guidelines")
        output.append(f"**Stack:** {result['stack']} | **Query:** {result['query']}")
        output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")

        for i, row in enumerate(result['results'], 1):
            output.append(f"### Result {i}")
            for key, value in row.items():
                value_str = str(value)
                if len(value_str) > 300:
                    value_str = value_str[:300] + "..."
                output.append(f"- **{key}:** {value_str}")
            output.append("")
    else:
        output.append(f"## UI Pro Max Search Results")
        output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']}")
        output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")

        for i, row in enumerate(result['results'], 1):
            output.append(f"### Result {i}")
            for key, value in row.items():
                value_str = str(value)
                if len(value_str) > 300:
                    value_str = value_str[:300] + "..."
                output.append(f"- **{key}:** {value_str}")
            output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UI Pro Max Search - AI-powered design intelligence toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search.py "glassmorphism buttons" --domain style
  python search.py "dashboard layout" --stack react --max-results 5
  python search.py "brand colors" --config-path ./my-config --apply-brand
  python search.py "card components" --export-a2ui --json
        """
    )

    # Core search arguments
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help="Stack-specific search")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Design system generation
    if generate_design_system:
        parser.add_argument("--design-system", "-ds", action="store_true", help="Generate complete design system recommendation")
        parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name for design system output")
        parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format for design system")

    # External configuration support
    if EXTERNAL_CONFIG_AVAILABLE:
        external_group = parser.add_argument_group('external configuration', 'Advanced customization options')
        external_group.add_argument("--config-path", "-c", type=str, default=None,
                                  help="Path to external configuration directory (default: .ui-ux-pro-max-config/)")
        external_group.add_argument("--apply-brand", "-b", action="store_true",
                                  help="Apply personal/company brand configuration to results")
        external_group.add_argument("--no-merge", action="store_true",
                                  help="Use only external configuration (don't merge with built-in data)")
        external_group.add_argument("--config-status", action="store_true",
                                  help="Show external configuration status and exit")

    # A2UI export support
    if A2UIExporter:
        export_group = parser.add_argument_group('export options', 'Cross-platform UI export')
        export_group.add_argument("--export-a2ui", "-a2ui", action="store_true",
                                help="Export results as A2UI protocol for cross-platform generation")
        export_group.add_argument("--export-targets", nargs="+",
                                choices=["react", "vue", "flutter", "html", "swiftui"],
                                default=["react", "html"],
                                help="Target platforms for A2UI export (default: react html)")
        export_group.add_argument("--export-options", type=str,
                                help="JSON string of export options")
        export_group.add_argument("--export-file", "-o", type=str,
                                help="Save A2UI export to file instead of stdout")

    args = parser.parse_args()

    # Handle config status check
    if EXTERNAL_CONFIG_AVAILABLE and hasattr(args, 'config_status') and args.config_status:
        from config_loader import ConfigLoader
        config_loader = ConfigLoader(args.config_path)
        external_config = config_loader.load_external_config()
        print(json.dumps(external_config, indent=2, ensure_ascii=False))
        sys.exit(0)

    # Initialize A2UI exporter if needed
    a2ui_exporter = None
    if A2UIExporter and hasattr(args, 'export_a2ui') and args.export_a2ui:
        export_options = {}
        if hasattr(args, 'export_options') and args.export_options:
            try:
                export_options = json.loads(args.export_options)
            except json.JSONDecodeError as e:
                print(f"Error parsing export options JSON: {e}", file=sys.stderr)
                sys.exit(1)

        if hasattr(args, 'export_targets'):
            export_options['targets'] = args.export_targets

        a2ui_exporter = A2UIExporter()

    # Design system takes priority
    if generate_design_system and hasattr(args, 'design_system') and args.design_system:
        result = generate_design_system(args.query, args.project_name, args.format)
        print(result)
        sys.exit(0)

    # Determine search function to use
    search_function = search
    search_kwargs = {
        'query': args.query,
        'max_results': args.max_results
    }

    # Use external configuration if available and requested
    if (EXTERNAL_CONFIG_AVAILABLE and
        (hasattr(args, 'config_path') and args.config_path or
         hasattr(args, 'apply_brand') and args.apply_brand or
         hasattr(args, 'no_merge') and args.no_merge)):

        search_function = search_with_external_config
        search_kwargs.update({
            'config_path': getattr(args, 'config_path', None),
            'apply_brand': getattr(args, 'apply_brand', True)
        })

        # Handle stack search with external config
        if args.stack:
            search_kwargs['stack'] = args.stack
        else:
            search_kwargs['domain'] = args.domain

    # Handle standard stack search
    elif args.stack:
        search_function = search_stack
        search_kwargs = {
            'query': args.query,
            'stack': args.stack,
            'max_results': args.max_results
        }
    # Handle standard domain search
    else:
        search_kwargs['domain'] = args.domain

    # Execute search
    try:
        result = search_function(**search_kwargs)
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle A2UI export
    if a2ui_exporter:
        try:
            # Extract results for A2UI export
            results_to_export = []
            if result.get("enhanced_results"):
                results_to_export = result["enhanced_results"]
            elif result.get("results"):
                results_to_export = result["results"]

            a2ui_result = a2ui_exporter.export_to_a2ui(results_to_export, export_options)

            # Save to file or print to stdout
            if hasattr(args, 'export_file') and args.export_file:
                output_path = Path(args.export_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(a2ui_result, f, indent=2, ensure_ascii=False)
                print(f"A2UI export saved to: {output_path}")
            else:
                print(json.dumps(a2ui_result, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"A2UI export error: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle regular output
    elif args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_output(result))
