#!/usr/bin/env python3
import re, sys, os

filepath = os.path.join("src", "ui-ux-pro-max", "scripts", "search.py")

with open(filepath, encoding="utf-8") as f:
    content = f.read()

old_density = '    parser.add_argument("--density", type=int, choices=range(1, 11), metavar="1-10", help="VISUAL_DENSITY dial: 1=spacious, 10=dense/dashboard; overrides the spacing scale (only with --design-system)")'
new_density = old_density + '''
    parser.add_argument(
        "--rtl",
        nargs="?",
        const="all",
        choices=["all", "full", "partial", "caveats"],
        default=None,
        help="Filter by RTL level (style/product domain only). Usage: --rtl, --rtl=full, --rtl=partial, --rtl=caveats"
    )'''

rtl_fn = '''
def _apply_rtl_filter(result, rtl_level):
    if result.get("domain") not in ("style", "product"):
        print("note: --rtl only applies to --domain style or product", file=sys.stderr)
        return result
    if "results" not in result or not result["results"]:
        return result
    valid = ("full", "partial", "caveats")
    if rtl_level == "all":
        result["results"] = [r for r in result["results"] if r.get("rtl_level") in valid]
    else:
        result["results"] = [r for r in result["results"] if r.get("rtl_level") == rtl_level]
    result["count"] = len(result["results"])
    return result


'''

old_domain = '    # Domain search\n    else:\n        result = search(args.query, args.domain, args.max_results)\n        if args.json:'
new_domain = '    # Domain search\n    else:\n        result = search(args.query, args.domain, args.max_results)\n        if args.rtl is not None:\n            result = _apply_rtl_filter(result, args.rtl)\n        if args.json:'

if old_density in content:
    content = content.replace(old_density, new_density, 1)
    print("OK: --rtl argument added")
else:
    print("SKIP: already patched or not found")

if '_apply_rtl_filter' not in content:
    content = content.replace('if __name__ == "__main__":', rtl_fn + 'if __name__ == "__main__":')
    print("OK: RTL filter function added")

if old_domain in content:
    content = content.replace(old_domain, new_domain, 1)
    print("OK: RTL filter applied in search")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("DONE: search.py patched!")
