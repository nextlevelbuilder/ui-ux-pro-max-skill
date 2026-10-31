#!/usr/bin/env python3
"""audit.py - static visual-drift scanner for the visual-audit skill.

Scans a project tree (Flutter/Dart, Unity USS/UXML/C#, web CSS/TSX/Vue/Svelte,
SwiftUI/Compose experimental) for hard-coded design literals, normalises them
and compares them with a design contract (tokens.json, style-profile.json).
Emits findings in the visual-audit/1 schema (integration contract section 4.4).

Commands
    scan <dir> [--contract tokens.json] [--profile style-profile.json]
               [--platform auto|flutter|unity|web|native|mixed]
               [--format json|md] [--out file] [--md report.md]
               [--fail-on critical|high|medium|low|none] [--tolerance N]
               [--near-threshold D] [--exclude GLOB]... [--primary GLOB]...
               [--max-files N] [--json]
    compare <before.json> <after.json> [--fail-on ...] [--json]
    rules [--json]

Exit codes
    scan     0 nothing at/above --fail-on (default high), 1 findings at/above
             threshold, 2 usage/IO error (dir missing, contract file missing,
             unknown platform), 1 also for a malformed contract/profile JSON.
    compare  0 no new findings at/above threshold, 1 new findings at/above
             threshold, 2 file missing/unparsable/wrong schema.

Stdlib only. Regex scanner, not a parser: computed values, theme extensions,
multi-line literals beyond one nesting level and sprite/texture UI are not seen.
"""
import argparse
import datetime
import fnmatch
import json
import math
import os
import re
import sys
from urllib.parse import unquote_plus

SCHEMA = "visual-audit/1"
SEVERITIES = ["critical", "high", "medium", "low", "info"]
SEV_RANK = {s: i for i, s in enumerate(SEVERITIES)}

MIN_RULE_IDS = [
    "color.off-palette", "color.near-duplicate", "radius.off-scale",
    "font-size.off-scale", "font-family.unlisted", "spacing.off-scale",
    "shadow.variant-explosion", "duration.off-scale", "icon.mixed-libraries",
    "component.duplicate-implementation", "touch.target-too-small",
    "text.contrast-risk",
]

# rule id -> (category, kind, default severity text, note)
RULE_TABLE = [
    ("color.off-palette", "color", "rule", "ladder (high: count>=3 or primary screen; else medium)", "exact"),
    ("color.near-duplicate", "color", "rule", "low (always)", "exact"),
    ("radius.off-scale", "radius", "rule", "ladder", "exact"),
    ("font-size.off-scale", "font-size", "rule", "ladder", "exact"),
    ("font-family.unlisted", "font-family", "rule", "ladder", "exact"),
    ("spacing.off-scale", "spacing", "rule", "low; medium when count>=3; never high", "exact"),
    ("duration.off-scale", "duration", "rule", "medium; high when count>=3 (primary ignored)", "exact"),
    ("shadow.variant-explosion", "shadow", "rule / recommendation (inventory)", "medium (one per project)", "exact"),
    ("shadow.unlisted", "shadow", "rule", "low per occurrence (extension id)", "exact"),
    ("icon.mixed-libraries", "icon", "rule", "medium; high when >=3 libraries in one group", "exact"),
    ("component.duplicate-implementation", "component", "recommendation", "medium", "heuristic"),
    ("touch.target-too-small", "touch", "recommendation", "medium (heuristic cap, CC-10h)", "heuristic"),
    ("text.contrast-risk", "text", "recommendation", "medium (heuristic cap)", "heuristic"),
    ("radius.variant-explosion", "radius", "recommendation", "medium (inventory mode, > 4 distinct)", "exact"),
    ("font-family.variant-explosion", "font-family", "recommendation", "medium (inventory mode, > 3 distinct)", "exact"),
    ("font-size.variant-explosion", "font-size", "recommendation", "medium (inventory mode, > 8 distinct)", "exact"),
    ("duration.variant-explosion", "duration", "recommendation", "medium (inventory mode, > 6 distinct)", "exact"),
    ("color.variant-explosion", "color", "recommendation", "medium (inventory mode, > 24 distinct opaque)", "exact"),
]

# ----------------------------------------------------------------- routing
SKIP_DIRS = {"build", ".dart_tool", "node_modules", "Library", "Temp", "Logs", "obj",
             "bin", ".git", "dist", ".next", "coverage", "__pycache__", ".idea", ".vs",
             "Pods", "DerivedData", ".gradle"}
SKIP_FILE_RE = re.compile(r"(\.g\.dart|\.freezed\.dart|\.gr\.dart|\.min\.(css|js)|\.map|\.lock)$")
EXT_PLATFORM = {
    ".dart": "flutter",
    ".cs": "unity", ".uss": "unity", ".uxml": "unity",
    ".css": "web", ".scss": "web", ".tsx": "web", ".jsx": "web", ".ts": "web", ".js": "web",
    ".vue": "web", ".svelte": "web", ".html": "web", ".cjs": "web", ".mjs": "web",
    ".swift": "native", ".kt": "native",
}
PLATFORM_CHOICES = ["auto", "flutter", "unity", "web", "native", "mixed"]
MARKERS = [
    (re.compile(r"(^|/)pubspec\.yaml$"), "flutter"),
    (re.compile(r"(^|/)ProjectSettings/ProjectVersion\.txt$"), "unity"),
    (re.compile(r"(^|/)[^/]+\.csproj$"), "unity"),
    (re.compile(r"(^|/)Assets/$"), "unity"),
    (re.compile(r"(^|/)package\.json$"), "web"),
    (re.compile(r"(^|/)Package\.swift$"), "native"),
    (re.compile(r"(^|/)build\.gradle(\.kts)?$"), "native"),
    (re.compile(r"\.xcodeproj/$"), "native"),
]
PRIMARY_SEGMENTS = {"screens", "pages", "app", "views", "routes"}
FAR_COLOR_DISTANCE = 30.0  # above this the nearest token is not a recommendation, only information
MAX_FILE_BYTES = 1024 * 1024
MAX_LINE_CHARS = 5000
GENERIC_FAMILIES = {"sans-serif", "serif", "monospace", "system-ui", "cursive", "fantasy",
                    "inherit", "initial", "unset", "ui-sans-serif", "ui-serif", "ui-monospace"}

# ------------------------------------------------------------------ regexes
HEX = r"#(?P<hex>[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3,4})\b"
RX = {
    # --- colours
    "dart.color_hex": re.compile(r"\bColor\(\s*0[xX](?P<argb>[0-9A-Fa-f]{8})\s*\)"),
    "dart.color_argb": re.compile(r"\bColor\.fromARGB\(\s*(?P<a>\d+)\s*,\s*(?P<r>\d+)\s*,\s*(?P<g>\d+)\s*,\s*(?P<b>\d+)\s*\)"),
    "dart.color_rgbo": re.compile(r"\bColor\.fromRGBO\(\s*(?P<r>\d+)\s*,\s*(?P<g>\d+)\s*,\s*(?P<b>\d+)\s*,\s*(?P<o>[\d.]+)\s*\)"),
    "dart.colors_named": re.compile(r"\bColors\.(?P<name>[a-z][A-Za-z]*)(?:\[(?P<shade>\d{2,3})\])?(?!\w)"),
    "cs.color_f": re.compile(r"\bnew\s+Color\(\s*(?P<r>[\d.]+)f?\s*,\s*(?P<g>[\d.]+)f?\s*,\s*(?P<b>[\d.]+)f?(?:\s*,\s*(?P<a>[\d.]+)f?)?\s*\)"),
    "cs.color32": re.compile(r"\bnew\s+Color32\(\s*(?P<r>\d+)\s*,\s*(?P<g>\d+)\s*,\s*(?P<b>\d+)\s*,\s*(?P<a>\d+)\s*\)"),
    "cs.html_string": re.compile(r"\bColorUtility\.TryParseHtmlString\(\s*\"" + HEX + r"\""),
    "css.hex": re.compile(r"(?<![\w&])" + HEX),
    "css.rgb": re.compile(r"\brgba?\(\s*(?P<r>\d{1,3})\s*[, ]\s*(?P<g>\d{1,3})\s*[, ]\s*(?P<b>\d{1,3})\s*(?:[,/]\s*(?P<a>[\d.]+%?))?\s*\)"),
    "css.hsl": re.compile(r"\bhsla?\(\s*(?P<h>[\d.]+)(?:deg)?\s*[, ]\s*(?P<s>[\d.]+)%\s*[, ]\s*(?P<l>[\d.]+)%\s*(?:[,/]\s*(?P<a>[\d.]+%?))?\s*\)"),
    "tw.color": re.compile(r"\b(?:bg|text|border|ring|fill|stroke|from|to|via|shadow|outline|accent|caret|decoration|divide|placeholder)-\[" + HEX + r"\]"),
    # --- radii
    "dart.radius": re.compile(r"\b(?:BorderRadius|Radius)\.circular\(\s*(?P<n>\d+(?:\.\d+)?)\s*\)"),
    "css.radius": re.compile(r"\bborder(?:-(?:top|bottom)-(?:left|right))?-radius\s*:\s*(?P<v>[^;}]+)"),
    "tw.radius": re.compile(r"\brounded(?:-[tblr]{1,2})?-\[(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem|em)\]"),
    "js.style_radius": re.compile(r"\bborderRadius\s*:\s*['\"]?(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem)?['\"]?"),
    # --- font sizes
    "dart.font_size": re.compile(r"\bfontSize\s*:\s*(?P<n>\d+(?:\.\d+)?)\b"),
    "css.font_size": re.compile(r"\bfont-size\s*:\s*(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem|em|pt)\b"),
    "tw.font_size": re.compile(r"\btext-\[(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem|em)\]"),
    "js.style_font_size": re.compile(r"\bfontSize\s*:\s*['\"]?(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem)?['\"]?"),
    # --- font families
    "dart.font_family": re.compile(r"\bfontFamily\s*:\s*(?P<q>['\"])(?P<name>[^'\"]+)(?P=q)"),
    "dart.google_fonts": re.compile(r"\bGoogleFonts\.(?P<name>[a-zA-Z0-9]+)\("),
    "css.font_family": re.compile(r"\bfont-family\s*:\s*(?P<v>[^;}]+)"),
    # --- shadows
    "dart.shadow": re.compile(r"\bBoxShadow\((?P<body>[^()]*(?:\([^()]*\)[^()]*)*)\)"),
    "css.shadow": re.compile(r"\bbox-shadow\s*:\s*(?P<v>[^;}]+)"),
    "css.shadow_num": re.compile(r"(?<![\w.#-])(?P<n>-?\d+(?:\.\d+)?)(?P<u>px|rem)?(?![\w.])"),
    "css.shadow_mask": re.compile(r"(?:\bbox-shadow|--[\w-]*shadow[\w-]*)\s*:[^;}]+"),
    # --- durations
    "dart.duration": re.compile(r"\bDuration\(\s*milliseconds\s*:\s*(?P<ms>\d+)\s*\)"),
    "dart.duration_s": re.compile(r"\bDuration\(\s*seconds\s*:\s*(?P<s>\d+)\s*\)"),
    "css.duration": re.compile(r"\b(?:transition|animation)(?:-duration)?\s*:\s*(?P<v>[^;}]+)"),
    "css.ms": re.compile(r"(?<![\w.])(?P<n>\d+(?:\.\d+)?)(?P<u>ms|s)\b"),
    "js.duration_str": re.compile(r"\b(?:transitionDuration|animationDuration)\s*:\s*['\"](?P<n>\d+(?:\.\d+)?)(?P<u>ms|s)['\"]"),
    "tw.duration": re.compile(r"\bduration-\[(?P<n>\d+)(?P<u>ms|s)\]"),
    "cs.dotween": re.compile(r"\.(?:DO[A-Z]\w*|SetDuration)\((?P<args>[^()]*(?:\([^()]*\)[^()]*)*)\)"),
    "cs.dotween_to": re.compile(r"\bDOTween\.To\((?P<args>[^()]*(?:\([^()]*\)[^()]*)*)\)"),
    "cs.last_float": re.compile(r"(?P<n>\d+(?:\.\d+)?)f?\s*$"),
    # --- icon libraries
    "dart.icon_import": re.compile(r"import\s+'package:(?P<pkg>font_awesome_flutter|phosphor_flutter|lucide_icons|lucide_flutter|cupertino_icons|flutter_feather_icons|ionicons|hugeicons|material_symbols_icons)/"),
    "dart.icon_use": re.compile(r"\b(?P<lib>Icons|CupertinoIcons|FontAwesomeIcons|PhosphorIcons|LucideIcons|FeatherIcons|Ionicons)\.[a-zA-Z0-9_]+"),
    "web.icon_import": re.compile(r"from\s+['\"](?P<pkg>lucide-react|lucide-vue-next|lucide-svelte|@heroicons/[\w-]+|react-icons(?:/\w+)?|@phosphor-icons/[\w-]+|@mui/icons-material|@fortawesome/[\w-]+|font-awesome|@tabler/icons-[\w-]+|@radix-ui/react-icons|@iconify/[\w-]+)"),
    "web.icon_cdn": re.compile(r"(?P<lib>font-?awesome|material-icons|material-symbols)[^\"']*\.css"),
    # --- touch targets
    "dart.sized_box": re.compile(r"\bSizedBox\((?P<args>[^()]*)\bchild\s*:\s*(?:const\s+)?(?P<widget>IconButton|InkWell|GestureDetector|TextButton|ElevatedButton|OutlinedButton|FilledButton)\b"),
    "dart.wh": re.compile(r"\b(?P<k>width|height)\s*:\s*(?P<n>\d+(?:\.\d+)?)"),
    "dart.min_size": re.compile(r"\bminimumSize\s*:\s*(?:const\s+)?Size\(\s*(?P<w>\d+(?:\.\d+)?)\s*,\s*(?P<h>\d+(?:\.\d+)?)\s*\)"),
    "css.rule": re.compile(r"(?P<sel>[^{}]+)\{(?P<body>[^{}]*)\}"),
    "css.button_sel": re.compile(r"(?:\bbutton\b|\[role=\"?button\"?\]|\.[\w-]*(?:btn|button|icon-btn|fab|chip|tap)[\w-]*)", re.I),
    "css.wh": re.compile(r"(?<![\w-])(?P<k>(?:min-)?(?:width|height))\s*:\s*(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem)\b"),
    # --- duplicate components
    "dart.class": re.compile(r"\bclass\s+(?P<name>\w+)\s+extends\s+(?:StatelessWidget|StatefulWidget|ConsumerWidget|HookWidget|State<\w+>)"),
    "ts.component": re.compile(r"\bexport\s+(?:default\s+)?(?:function\s+(?P<fn>[A-Z]\w*)|const\s+(?P<const>[A-Z]\w*)\s*(?::[^=]+)?=)"),
    "cs.class": re.compile(r"\bclass\s+(?P<name>\w+)\s*:\s*(?:MonoBehaviour|VisualElement|UIBehaviour)"),
    "component.name": re.compile(r"^(?:(?:Primary|Main|Cta|Secondary|Action|Icon|Big|Small)?Button\w*|\w*(?:Popup|Dialog|Modal|Sheet|Toast|Snackbar|Card|Badge|Chip))$"),
    "component.family": re.compile(r"(Button|Popup|Dialog|Modal|Sheet|Toast|Snackbar|Card|Badge|Chip)"),
    # --- CSS vars / spacing
    "css.var_def": re.compile(r"^\s*--[\w-]+\s*:", re.M),
    "css.var_decl": re.compile(r"(?<![\w-])--(?P<name>[\w-]+)\s*:\s*(?P<v>[^;}]+)"),
    "dart.edge_insets": re.compile(r"\bEdgeInsets\.(?:all|symmetric|only|fromLTRB)\((?P<args>[^()]*)\)"),
    "dart.edge_num": re.compile(r"(?<![\w.])(?P<n>\d+(?:\.\d+)?)\b"),
    "css.spacing": re.compile(r"(?<![\w-])(?P<prop>padding|margin|gap)(?:-(?:top|right|bottom|left|inline|block))?\s*:\s*(?P<v>[^;}]+)"),
    "css.px": re.compile(r"(?<![\w.-])(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem)\b"),
    "tw.spacing": re.compile(r"\b(?:[pm][trblxy]?|gap(?:-[xy])?|space-[xy])-\[(?P<n>\d+(?:\.\d+)?)(?P<u>px|rem)\]"),
    # --- contrast
    "css.fg": re.compile(r"(?<![\w-])color\s*:\s*(" + HEX + r")"),
    "css.bg": re.compile(r"\bbackground(?:-color)?\s*:\s*(" + HEX + r")"),
    # --- markup helpers
    "html.style_block": re.compile(r"<style\b[^>]*>(?P<css>.*?)</style>", re.S | re.I),
    "uxml.style_attr": re.compile(r"\bstyle\s*=\s*\"(?P<v>[^\"]*)\""),
    # HTML/Vue/Svelte inline style attribute (not Vue :style / v-bind:style bindings)
    "html.style_attr": re.compile(r"(?<![:\w-])style\s*=\s*(?P<q>[\"'])(?P<v>.*?)(?P=q)", re.S),
    # --- font families declared outside CSS
    # Tailwind theme: fontFamily: { heading: ['Poppins', 'sans-serif'], body: "Inter, sans-serif" }
    "tw.font_family_block": re.compile(r"\bfontFamily\s*:\s*\{"),
    "tw.font_family_entry": re.compile(
        r"(?P<key>['\"]?[\w-]+['\"]?)\s*:\s*(?:\[\s*(?P<q>['\"`])(?P<name>[^'\"`]+)(?P=q)[^\]]*\]|(?P<q2>['\"`])(?P<name2>[^'\"`]+)(?P=q2))"),
    # Google Fonts loader URL (<link href>, @import url(), JS strings): css2?family=A:wght@..&family=B, css?family=A|B
    "google.fonts_url": re.compile(r"fonts\.googleapis\.com/css2?\?(?P<qs>[^\"'\s)<>]+)"),
    # --- Swift / Kotlin (experimental, no fixture)
    "swift.color": re.compile(r"\bColor\(\s*red:\s*(?P<r>[\d.]+)\s*,\s*green:\s*(?P<g>[\d.]+)\s*,\s*blue:\s*(?P<b>[\d.]+)"),
    "swift.color_hex": re.compile(r"\bColor\(\s*hex:\s*['\"]?" + HEX),
    "swift.radius": re.compile(r"\.cornerRadius\(\s*(?P<n>\d+(?:\.\d+)?)\s*\)"),
    "swift.font_size": re.compile(r"\.font\(\s*\.system\(\s*size:\s*(?P<n>\d+(?:\.\d+)?)"),
    "kt.color": re.compile(r"\bColor\(\s*0[xX](?P<argb>[0-9A-Fa-f]{8})\s*\)"),
    "kt.radius": re.compile(r"\bRoundedCornerShape\(\s*(?P<n>\d+(?:\.\d+)?)\.dp\s*\)"),
    "kt.font_size": re.compile(r"\bfontSize\s*=\s*(?P<n>\d+(?:\.\d+)?)\.sp"),
    "kt.duration": re.compile(r"\btween\((?:durationMillis\s*=\s*)?(?P<n>\d+)"),
}

DART_ICON_LIBS = {"Icons": "material", "CupertinoIcons": "cupertino_icons",
                  "FontAwesomeIcons": "font_awesome_flutter", "PhosphorIcons": "phosphor_flutter",
                  "LucideIcons": "lucide_icons", "FeatherIcons": "flutter_feather_icons",
                  "Ionicons": "ionicons"}

# Material swatch table (500 shade + white/black) for Colors.<name>
MATERIAL_500 = {
    "red": "#F44336", "pink": "#E91E63", "purple": "#9C27B0", "deepPurple": "#673AB7",
    "indigo": "#3F51B5", "blue": "#2196F3", "lightBlue": "#03A9F4", "cyan": "#00BCD4",
    "teal": "#009688", "green": "#4CAF50", "lightGreen": "#8BC34A", "lime": "#CDDC39",
    "yellow": "#FFEB3B", "amber": "#FFC107", "orange": "#FF9800", "deepOrange": "#FF5722",
    "brown": "#795548", "grey": "#9E9E9E", "blueGrey": "#607D8B",
    "white": "#FFFFFF", "black": "#000000",
}


class Blocked(Exception):
    pass


class ContractError(Exception):
    pass


# -------------------------------------------------------------- utilities
def strip_comments(src, line_comment=("//",), blocks=(("/*", "*/"),)):
    """Replace comments with spaces (newlines kept) so line numbers survive.
    String-aware: // inside '...' or "..." (e.g. https://) is not a comment.
    A newline ends an unterminated single/double-quoted string; backticks span lines."""
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in ("'", '"', "`"):
            q = c
            out.append(c)
            i += 1
            while i < n and src[i] != q:
                if src[i] == "\\" and i + 1 < n:
                    out.append(src[i:i + 2])
                    i += 2
                    continue
                if src[i] == "\n" and q != "`":
                    break
                out.append(src[i])
                i += 1
            if i < n:
                out.append(src[i])
                i += 1
            continue
        hit_block = False
        for bo, bc in blocks:
            if src.startswith(bo, i):
                j = src.find(bc, i + len(bo))
                j = n if j < 0 else j + len(bc)
                out.append("".join("\n" if ch == "\n" else " " for ch in src[i:j]))
                i = j
                hit_block = True
                break
        if hit_block:
            continue
        if line_comment and any(src.startswith(lc, i) for lc in line_comment):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        out.append(c)
        i += 1
    return "".join(out)


def comment_syntax(ext):
    if ext in (".css", ".uss"):
        return (), (("/*", "*/"),)
    if ext == ".uxml":
        return (), (("<!--", "-->"),)
    if ext in (".html", ".vue", ".svelte"):
        return ("//",), (("/*", "*/"), ("<!--", "-->"))
    return ("//",), (("/*", "*/"),)


def google_font_families(query, css2=True):
    """Family names from a Google Fonts query string. Returns [(family, raw_param)].
    `+`/%20 decode to spaces; `:wght@400;700`, `:ital,wght@…`, `:400,700` suffixes are stripped;
    css (v1) accepts several families per param separated by `|`."""
    out = []
    for part in re.split(r"&amp;|&#38;|&", query):
        if not part.lower().startswith("family="):
            continue
        raw = part[len("family="):]
        for fam_raw in (unquote_plus(raw).split("|") if not css2 else [unquote_plus(raw)]):
            name = fam_raw.split(":", 1)[0].strip()
            if name:
                out.append((name, raw if css2 else fam_raw.strip()))
    return out


def flatten_at_rules(text):
    """Remove the outer braces of @media/@supports/@container/@layer blocks so css.rule
    sees the nested rules; positions and line numbers are preserved (braces -> spaces)."""
    chars = list(text)
    for m in re.finditer(r"@(?:media|supports|container|layer|document)\b[^{;]*\{", text):
        open_pos = m.end() - 1
        depth = 0
        i = open_pos
        while i < len(chars):
            if chars[i] == "{":
                depth += 1
            elif chars[i] == "}":
                depth -= 1
                if depth == 0:
                    for k in range(m.start(), open_pos + 1):
                        if chars[k] != "\n":
                            chars[k] = " "
                    chars[i] = " "
                    break
            i += 1
    return "".join(chars)


def norm_hex(h):
    """Return (#RRGGBB upper, alpha 0..1 or None). Accepts 3,4,6,8-digit CSS hex."""
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    alpha = None
    if len(h) == 8:
        alpha = int(h[6:8], 16) / 255.0
        h = h[:6]
    return "#" + h.upper(), alpha


def norm_argb(argb):
    """Dart/Compose 0xAARRGGBB -> (#RRGGBB, alpha)."""
    return "#" + argb[2:].upper(), int(argb[:2], 16) / 255.0


def rgb_to_hex(r, g, b):
    return "#%02X%02X%02X" % (int(r), int(g), int(b))


def unity_f_to_hex(r, g, b):
    return rgb_to_hex(*(min(255, round(float(x) * 255)) for x in (r, g, b)))


def hsl_to_hex(h, s, l):
    h, s, l = float(h) % 360 / 360.0, float(s) / 100.0, float(l) / 100.0
    if s == 0:
        v = round(l * 255)
        return rgb_to_hex(v, v, v)
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q

    def hue(t):
        t %= 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p
    return rgb_to_hex(round(hue(h + 1 / 3) * 255), round(hue(h) * 255), round(hue(h - 1 / 3) * 255))


def to_px(n, unit, base=16.0):
    n = float(n)
    if unit in ("rem", "em"):
        return n * base
    if unit == "pt":
        return n * 4 / 3
    return n


def to_ms(n, unit):
    return float(n) * 1000 if unit == "s" else float(n)


def num(v):
    v = float(v)
    return int(v) if v.is_integer() else round(v, 2)


def alpha_of(a):
    if not a:
        return None
    a = a.strip()
    return float(a.rstrip("%")) / (100 if a.endswith("%") else 1)


NON_LITERAL = {"none", "inherit", "initial", "unset", "revert", "revert-layer", "auto", "transparent", "currentcolor"}
VAR_RE = re.compile(r"\b(?:var|env|theme)\((?:[^()]*|\([^()]*\))*\)")


def is_literal_value(v):
    """False for token/variable references and CSS keywords: var(--x), {token}, $sass, @less, none, inherit, ..."""
    sv = (v or "").strip().lower()
    if not sv or sv in NON_LITERAL:
        return False
    if "var(" in sv or "env(" in sv or "theme(" in sv or sv.startswith(("{", "$", "@")):
        return False
    return any(ch.isdigit() for ch in sv) or sv.startswith("#") or "rgb" in sv or "hsl" in sv or bool(re.search(r"[A-Za-z]", sv))


def strip_vars(v):
    """Blank var()/env()/theme() references so calc(var(--r) + 2px) never yields a literal number."""
    return VAR_RE.sub(" ", v or "")


def shadow_signature_dart(body):
    """Signature for a Dart BoxShadow body, or None when the colour is not a literal Color(0x...)."""
    m_c = RX["dart.color_hex"].search(body)
    if not m_c:
        return None
    blur = re.search(r"blurRadius\s*:\s*([\d.]+)", body)
    off = re.search(r"Offset\(\s*([\d.-]+)\s*,\s*([\d.-]+)\s*\)", body)
    spread = re.search(r"spreadRadius\s*:\s*([\d.]+)", body)
    hexv, alpha = norm_argb(m_c.group("argb"))
    return "x=%s y=%s blur=%s spread=%s color=%s a=%s" % (
        num(off.group(1)) if off else 0, num(off.group(2)) if off else 0,
        num(blur.group(1)) if blur else 0, num(spread.group(1)) if spread else 0,
        hexv, round(alpha, 2))


def shadow_signature_css(v):
    v = v.strip()
    if v == "none":
        return "none"
    m = RX["css.rgb"].search(v)
    hexv, alpha = ("#000000", 1.0)
    if m:
        hexv = rgb_to_hex(m.group("r"), m.group("g"), m.group("b"))
        alpha = alpha_of(m.group("a")) if m.group("a") else 1.0
    else:
        mh = RX["css.hex"].search(v)
        if mh:
            hexv, a = norm_hex(mh.group("hex"))
            alpha = a if a is not None else 1.0
    cleaned = re.sub(r"rgba?\([^)]*\)|#[0-9A-Fa-f]{3,8}|\binset\b", "", v)
    nums = [num(to_px(n, u or "px")) for n, u in RX["css.shadow_num"].findall(cleaned)]
    nums += [0] * (4 - len(nums))
    return "x=%s y=%s blur=%s spread=%s color=%s a=%s" % (nums[0], nums[1], nums[2], nums[3], hexv, round(alpha, 2))


def shadow_signatures_css_multi(v):
    """One signature per comma-separated layer (commas inside rgba() are not separators).
    Non-literal layers (var(--shadow), none, inherit, {token}) are skipped, never counted."""
    layers = re.split(r",(?![^()]*\))", v or "")
    out = []
    for layer in layers:
        if not is_literal_value(layer) or not any(ch.isdigit() for ch in layer):
            continue
        sig = shadow_signature_css(layer)
        if sig != "none":
            out.append(sig)
    return out


def color_distance(h1, h2):
    """Luma-weighted RGB distance (0.299/0.587/0.114). <= 12 -> near-duplicate."""
    r1, g1, b1 = int(h1[1:3], 16), int(h1[3:5], 16), int(h1[5:7], 16)
    r2, g2, b2 = int(h2[1:3], 16), int(h2[3:5], 16), int(h2[5:7], 16)
    return math.sqrt(0.299 * (r1 - r2) ** 2 + 0.587 * (g1 - g2) ** 2 + 0.114 * (b1 - b2) ** 2)


def rel_lum(h):
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(int(h[1:3], 16)) + 0.7152 * ch(int(h[3:5], 16)) + 0.0722 * ch(int(h[5:7], 16))


def contrast(h1, h2):
    a, b = rel_lum(h1), rel_lum(h2)
    if a < b:
        a, b = b, a
    return (a + 0.05) / (b + 0.05)


def on_scale(value, scale, tolerance=None):
    """Integers must hit a step exactly; non-integers get +/-1 (conversion noise)."""
    if value == "pill":
        return any(s == "pill" or s >= 999 for s in scale)
    scale = [s for s in scale if s != "pill"]
    tol = tolerance if tolerance is not None else (0 if float(value).is_integer() else 1)
    return any(abs(value - s) <= tol for s in scale)


def nearest(value, scale):
    scale = [s for s in scale if s != "pill"]
    if not scale:
        return None
    return min(scale, key=lambda s: (abs(s - value), s))


def collapse(s, limit=120):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= limit else s[:limit - 1] + "…"


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def camel_to_title(name):
    return re.sub(r"(?<!^)(?=[A-Z0-9])", " ", name).title()


def balanced_block(text, pos, open_ch="{", close_ch="}"):
    """Return text from pos to the end of the first balanced block after pos."""
    start = text.find(open_ch, pos)
    if start < 0:
        return text[pos:pos + 400]
    depth = 0
    for i in range(start, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return text[pos:i + 1]
    return text[pos:]


def ts_block(text, pos):
    m = re.compile(r"\n(?=(?:export\s|function\s|class\s|const\s|let\s|var\s))").search(text, pos + 1)
    return text[pos:m.start()] if m else text[pos:]


# ----------------------------------------------------------- contract load
def resolve_ref(tokens, v, depth=0):
    if isinstance(v, str) and v.startswith("{") and v.endswith("}") and depth < 10:
        node = tokens
        for k in v[1:-1].split("."):
            node = node.get(k, {}) if isinstance(node, dict) else {}
        if not isinstance(node, dict) or "$value" not in node:
            raise ContractError("unresolved token reference %s" % v)
        return resolve_ref(tokens, node.get("$value"), depth + 1)
    return v


def leaves(node, path=()):
    if isinstance(node, dict):
        if "$value" in node:
            yield path, node
        else:
            for k, v in node.items():
                for item in leaves(v, path + (k,)):
                    yield item


LAYER_ORDER = ("semantic", "component", "primitive")  # naming preference when several paths share a value


def contract_layers(tokens):
    """Token layers in naming-preference order: semantic, component, primitive, then any other
    non-$ top-level layer (an optional `dark` theme, ...). Every layer contributes allowed values."""
    rest = [k for k in tokens if not k.startswith("$") and k not in LAYER_ORDER and isinstance(tokens.get(k), dict)]
    return [k for k in LAYER_ORDER if isinstance(tokens.get(k), dict)] + sorted(rest)


DIMENSION_GROUPS = (
    ("radius", ("radius", "corner")),
    ("fontSize", ("fontsize", "font-size", "textsize")),
    ("spacing", ("spacing", "padding", "gap", "margin", "inset", "gutter", "space")),
)


def dimension_group(path):
    """Scale a dimension leaf belongs to, from any segment of its path: primitive.radius.md,
    semantic.radius.control, component.button.primary.radius -> radius; ...paddingX, semantic.spacing.stack,
    component.hud.chip.gap -> spacing; ...fontSize -> fontSize. Heights, widths, outline/icon sizes -> None."""
    segs = [str(p).lower() for p in path]
    for group, keys in DIMENSION_GROUPS:
        if any(k in seg for seg in segs for k in keys):
            return group
    return None


def load_contract(tokens, profile=None):
    """Build allowed sets from a tokens.json dict (+ optional profile dict).
    Every literal $value in every layer (primitive, semantic, component, an optional dark layer),
    resolved through references, joins the allowed set for its $type.
    Returns dict with colors {hex: token path}, radius, fontSize, spacing, duration
    (sorted lists) + scale_paths {group: {value: path}}, fontFamily (lower-cased map), shadows {sig: path},
    minTouchTarget, iconLibrary, notes [..]."""
    if not isinstance(tokens, dict):
        raise ContractError("tokens.json root must be an object")
    if not any(k in tokens for k in ("primitive", "semantic", "component")):
        raise ContractError("tokens.json has none of the layers primitive/semantic/component")
    notes = []
    # value -> most specific token path. Every literal $value of every layer joins its type's allowed set
    # (generated contracts emit component literals such as pressDuration 90ms or tinted hard shadows).
    colors, families, shadows = {}, {}, {}
    scales = {"radius": {}, "fontSize": {}, "spacing": {}, "duration": {}}
    for layer in contract_layers(tokens):
        for path, leaf in leaves(tokens.get(layer, {})):
            name = layer + "." + ".".join(path)
            try:
                val = resolve_ref(tokens, leaf.get("$value"))
            except ContractError as e:
                notes.append("%s: %s (leaf ignored)" % (name, e))
                continue
            typ = leaf.get("$type")
            if typ == "color" and isinstance(val, str) and val.startswith("#"):
                try:
                    colors.setdefault(norm_hex(val)[0], name)
                except ValueError:
                    notes.append("%s: not a hex colour (%s)" % (name, val))
            elif typ == "dimension" and isinstance(val, (str, int, float)):
                m = re.match(r"^(\d+(?:\.\d+)?)(px|rem|em|pt|dp|sp)?$", str(val).strip())
                group = dimension_group(path)
                if not m or group is None:
                    continue
                scales[group].setdefault(num(to_px(m.group(1), m.group(2) or "px")), name)
            elif typ == "duration" and isinstance(val, (str, int, float)):
                m = re.match(r"^(\d+(?:\.\d+)?)(ms|s)?$", str(val).strip())
                if m:
                    scales["duration"].setdefault(num(to_ms(m.group(1), m.group(2) or "ms")), name)
            elif typ == "fontFamily" and isinstance(val, str):
                fam = val.split(",")[0].strip().strip("'\"")
                if fam and is_literal_value(fam):
                    families.setdefault(fam.lower(), fam)
            elif typ == "shadow" and isinstance(val, str) and val.strip() != "none":
                for sig in shadow_signatures_css_multi(val):
                    shadows.setdefault(sig, name)
    radius, font, spacing, duration = (scales[k] for k in ("radius", "fontSize", "spacing", "duration"))
    ext = tokens.get("$extensions", {}).get("vdp", {}) if isinstance(tokens.get("$extensions"), dict) else {}
    for fam in ext.get("fontFamilies", []) or []:
        if isinstance(fam, str):
            families.setdefault(fam.lower(), fam)
    min_touch = ext.get("minTouchTarget")
    if min_touch is None:
        leaf = tokens.get("primitive", {}).get("touchTarget", {}).get("min")
        if isinstance(leaf, dict):
            m = re.match(r"^(\d+(?:\.\d+)?)", str(leaf.get("$value", "")))
            min_touch = float(m.group(1)) if m else None
    try:
        min_touch = float(min_touch) if min_touch is not None else 44.0
    except (TypeError, ValueError):
        min_touch = 44.0
    icon_lib = ext.get("iconLibrary")
    if profile:
        for key in ("display", "body"):
            fam = (profile.get("typography") or {}).get(key)
            if isinstance(fam, str) and fam and " " not in fam.strip() or (isinstance(fam, str) and fam.istitle()):
                families.setdefault(fam.strip().lower(), fam.strip())
        if not duration:
            for v in ((profile.get("motion") or {}).get("duration_scale") or {}).values():
                if isinstance(v, (int, float)):
                    duration.setdefault(num(v), "profile.motion.duration_scale")
        if not icon_lib:
            hint = (profile.get("iconography") or {}).get("library_hint")
            if isinstance(hint, str) and hint:
                icon_lib = hint.split("|")[0].strip()
    required = ["color", "spacing", "radius", "outline", "shadow", "fontSize", "lineHeight",
                "iconSize", "touchTarget", "duration", "easing", "zIndex", "opacity"]
    missing = [g for g in required if g not in tokens.get("primitive", {})]
    if missing:
        notes.append("tokens.json primitive groups missing: %s (vd.py validate reports this; audit continues)" % ", ".join(missing))
    return {
        "colors": colors, "radius": sorted(radius), "fontSize": sorted(font), "spacing": sorted(spacing),
        "duration": sorted(duration), "fontFamily": families, "shadows": shadows,
        "scale_paths": {"radius": radius, "fontSize": font, "spacing": spacing, "duration": duration},
        "minTouchTarget": min_touch, "iconLibrary": icon_lib, "platformUnit": ext.get("platformUnit") or "px",
        "notes": notes,
    }


# ---------------------------------------------------------------- walking
def detect_platform(root, root_skip=()):
    found = set()
    for dp, dns, fns in os.walk(root):
        rel_dir = os.path.relpath(dp, root)
        depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1
        if depth > 2:
            dns[:] = []
            continue
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".") and not (depth == 0 and d in root_skip)]
        for name in fns + [d + "/" for d in dns]:
            rel = os.path.join(rel_dir, name).replace(os.sep, "/") if rel_dir != "." else name
            for rx, plat in MARKERS:
                if rx.search(rel):
                    found.add(plat)
    if not found:
        return "unknown"
    return found.pop() if len(found) == 1 else "mixed"


def _count_scannable(path):
    n = 0
    for dp, dns, fns in os.walk(path):
        for f in fns:
            if os.path.splitext(f)[1] in EXT_PLATFORM:
                n += 1
    return n


def walk(root, excludes=(), allowed_platforms=None, root_skip=()):
    """Return ([(relpath, platform)] sorted, skipped_count). root_skip = root-level dirs to prune."""
    files, skipped = [], 0
    for dp, dns, fns in os.walk(root):
        keep = []
        for d in sorted(dns):
            if d in SKIP_DIRS or d.startswith(".") or (dp == root and d in root_skip):
                skipped += _count_scannable(os.path.join(dp, d))
            else:
                keep.append(d)
        dns[:] = keep
        for f in sorted(fns):
            ext = os.path.splitext(f)[1]
            if ext not in EXT_PLATFORM:
                continue
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/")
            if SKIP_FILE_RE.search(f) or any(fnmatch.fnmatch(rel, g) for g in excludes):
                skipped += 1
                continue
            if allowed_platforms is not None and EXT_PLATFORM[ext] not in allowed_platforms:
                skipped += 1
                continue
            files.append((rel, EXT_PLATFORM[ext]))
    files.sort()
    return files, skipped


def read_source(path):
    """Return text or None when the file must be skipped (binary / huge / minified)."""
    try:
        if os.path.getsize(path) > MAX_FILE_BYTES:
            return None
        with open(path, "rb") as fh:
            head = fh.read(4096)
            if b"\x00" in head:
                return None
            data = head + fh.read()
    except OSError:
        return None
    text = data.decode("utf-8", errors="replace")
    if any(len(line) > MAX_LINE_CHARS for line in text.split("\n")):
        return None
    return text


FLUTTER_SCAFFOLD_DIRS = ("android", "ios", "macos", "linux", "windows")


def flutter_scaffold_dirs(root):
    """Root-level folders of a stock `flutter create` app that hold platform glue, not the UI:
    android/ ios/ macos/ linux/ windows/ always; web/ only when it is the Flutter web shell
    (index.html or manifest.json and no package.json). Empty when there is no pubspec.yaml."""
    if not os.path.isfile(os.path.join(root, "pubspec.yaml")):
        return set()
    skip = {d for d in FLUTTER_SCAFFOLD_DIRS if os.path.isdir(os.path.join(root, d))}
    web = os.path.join(root, "web")
    if os.path.isdir(web) and not os.path.isfile(os.path.join(web, "package.json")) and (
            os.path.isfile(os.path.join(web, "index.html")) or os.path.isfile(os.path.join(web, "manifest.json"))):
        skip.add("web")
    return skip


def write_text(path, text):
    """Write a report file, creating parent directories (qa-logs/… on first run)."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


DECORATION_ELEMENTS = {"svg", "img", "path", "i", "span", "b", "em", "small", "use", "picture", "figure", "label", "p"}


def is_touch_selector(sel):
    """True when the LAST compound of the selector is the control itself (button, [role=button],
    .btn/.icon-btn/.fab/.chip/.tap classes); decorative descendants (`.icon-btn svg`, `button > span`,
    `.btn::before`) are never touch targets."""
    if sel.startswith("--"):
        return False
    last = re.split(r"\s*[>+~]\s*|\s+", sel.strip())[-1]
    if "::before" in last or "::after" in last or re.search(r"(?<!:):(?:before|after)\b", last):
        return False
    base = re.sub(r"::?[\w-]+(?:\([^)]*\))?", "", last)  # strip pseudo-classes/elements
    elem = re.match(r"^[a-zA-Z][\w-]*", base)
    if elem and elem.group(0).lower() in DECORATION_ELEMENTS and not re.search(r"[.#\[]", base):
        return False
    return RX["css.button_sel"].search(base) is not None


def is_primary(rel, primary_globs=()):
    parts = rel.lower().split("/")
    if any(p in PRIMARY_SEGMENTS for p in parts[:-1]):
        return True
    low = rel.lower()
    if "hud" in low or "gameplay" in low:
        return True
    return any(fnmatch.fnmatch(rel, g) for g in primary_globs)


# --------------------------------------------------------------- scanning
class Hit(object):
    __slots__ = ("cat", "file", "line", "value", "extra", "evidence", "platform", "confidence")

    def __init__(self, cat, file, line, value, evidence, extra=None, platform="web", confidence="exact"):
        self.cat, self.file, self.line, self.value = cat, file, line, value
        self.evidence, self.extra, self.platform, self.confidence = evidence, extra, platform, confidence

    def as_tuple(self):
        return (self.cat, self.file, self.line, self.value, self.extra, self.evidence)


class Scanner(object):
    def __init__(self, rem_base=16.0):
        self.rem_base = rem_base
        self.hits = []
        self.icon_libs = {}      # platform -> {lib: [(file, line, evidence)]}
        self.components = {}     # platform -> {name: [(file, line, evidence, body)]}
        self.shadows = []        # (sig, file, line, evidence, platform)
        self.named_colors = {}   # name -> count
        self.experimental = set()

    # -- helpers
    def add(self, cat, rel, line, value, evidence, extra=None, platform="web", confidence="exact"):
        self.hits.append(Hit(cat, rel, line, value, collapse(evidence), extra, platform, confidence))

    def add_icon(self, platform, lib, rel, line, evidence):
        self.icon_libs.setdefault(platform, {}).setdefault(lib, []).append((rel, line, collapse(evidence)))

    def add_component(self, platform, name, rel, line, evidence, body):
        self.components.setdefault(platform, {}).setdefault(name, []).append((rel, line, collapse(evidence), re.sub(r"\s+", " ", body).strip()))

    def add_shadow(self, sig, rel, line, evidence, platform):
        if sig and sig != "none":
            self.shadows.append((sig, rel, line, collapse(evidence), platform))

    # -- entry
    def scan_file(self, rel, text, platform):
        ext = os.path.splitext(rel)[1]
        lc, blocks = comment_syntax(ext)
        text = strip_comments(text, lc, blocks)
        if ext in (".css", ".scss", ".uss", ".html", ".vue", ".svelte", ".tsx", ".jsx", ".ts", ".js", ".cjs", ".mjs"):
            self.scan_google_fonts(rel, text, "unity" if ext == ".uss" else "web")
        if ext == ".dart":
            self.scan_dart(rel, text)
        elif ext in (".css", ".scss", ".uss"):
            self.scan_css(rel, text, "unity" if ext == ".uss" else "web")
        elif ext == ".uxml":
            self.scan_uxml(rel, text)
        elif ext in (".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".html", ".cjs", ".mjs"):
            self.scan_markup(rel, text, ext)
        elif ext == ".cs":
            self.scan_cs(rel, text)
        elif ext == ".swift":
            self.scan_swift(rel, text)
        elif ext == ".kt":
            self.scan_kotlin(rel, text)

    # -- dart
    def scan_dart(self, rel, text):
        P = "flutter"
        shadow_spans = []
        for m in RX["dart.shadow"].finditer(text):
            shadow_spans.append((m.start(), m.end()))
            self.add_shadow(shadow_signature_dart(m.group("body")), rel, lineno(text, m.start()), m.group(0), P)

        def in_shadow(pos):
            return any(a <= pos < b for a, b in shadow_spans)
        for m in RX["dart.color_hex"].finditer(text):
            if in_shadow(m.start()):
                continue
            hexv, a = norm_argb(m.group("argb"))
            self.add("color", rel, lineno(text, m.start()), hexv, m.group(0), a, P)
        for m in RX["dart.color_argb"].finditer(text):
            self.add("color", rel, lineno(text, m.start()), rgb_to_hex(m.group("r"), m.group("g"), m.group("b")),
                     m.group(0), int(m.group("a")) / 255.0, P)
        for m in RX["dart.color_rgbo"].finditer(text):
            self.add("color", rel, lineno(text, m.start()), rgb_to_hex(m.group("r"), m.group("g"), m.group("b")),
                     m.group(0), float(m.group("o")), P)
        for m in RX["dart.colors_named"].finditer(text):
            name, shade = m.group("name"), m.group("shade")
            key = name + ("[%s]" % shade if shade else "")
            self.named_colors[key] = self.named_colors.get(key, 0) + 1
            if name == "transparent":
                continue
            if name in MATERIAL_500 and (shade is None or shade == "500"):
                self.add("color", rel, lineno(text, m.start()), MATERIAL_500[name], m.group(0), None, P)
        for m in RX["dart.radius"].finditer(text):
            v = num(m.group("n"))
            self.add("radius", rel, lineno(text, m.start()), "pill" if v >= 999 else v, m.group(0), None, P)
        for m in RX["dart.font_size"].finditer(text):
            self.add("fontSize", rel, lineno(text, m.start()), num(m.group("n")), m.group(0), None, P)
        for m in RX["dart.font_family"].finditer(text):
            self.add("fontFamily", rel, lineno(text, m.start()), m.group("name").strip(), m.group(0), None, P)
        for m in RX["dart.google_fonts"].finditer(text):
            self.add("fontFamily", rel, lineno(text, m.start()), camel_to_title(m.group("name")), m.group(0), None, P)
        for m in RX["dart.duration"].finditer(text):
            v = int(m.group("ms"))
            if v:
                self.add("duration", rel, lineno(text, m.start()), v, m.group(0), None, P)
        for m in RX["dart.duration_s"].finditer(text):
            v = int(m.group("s")) * 1000
            if v:
                self.add("duration", rel, lineno(text, m.start()), v, m.group(0), None, P)
        for m in RX["dart.icon_import"].finditer(text):
            self.add_icon(P, m.group("pkg"), rel, lineno(text, m.start()), m.group(0).rstrip("/") + "/...'")
        for m in RX["dart.icon_use"].finditer(text):
            self.add_icon(P, DART_ICON_LIBS[m.group("lib")], rel, lineno(text, m.start()), m.group(0))
        for m in RX["dart.sized_box"].finditer(text):
            dims = {k: float(n) for k, n in RX["dart.wh"].findall(m.group("args"))}
            if dims:
                w, h = dims.get("width"), dims.get("height")
                self.add("touch", rel, lineno(text, m.start()), (w, h), m.group(0), m.group("widget"), P, "heuristic")
        for m in RX["dart.min_size"].finditer(text):
            self.add("touch", rel, lineno(text, m.start()), (float(m.group("w")), float(m.group("h"))), m.group(0), "minimumSize", P, "heuristic")
        for m in RX["dart.class"].finditer(text):
            if RX["component.name"].match(m.group("name")):
                self.add_component(P, m.group("name"), rel, lineno(text, m.start()), m.group(0), balanced_block(text, m.start()))
        for m in RX["dart.edge_insets"].finditer(text):
            nums = RX["dart.edge_num"].findall(m.group("args"))
            for n in nums:
                ev = m.group(0) + (" → %s" % num(n) if len(nums) > 1 else "")
                self.add("spacing", rel, lineno(text, m.start()), num(n), ev, None, P)

    # -- css-like (css / scss / uss / style blocks / uxml inline styles)
    def scan_css(self, rel, text, platform, base=0, full_text=None):
        full = full_text if full_text is not None else text
        text = flatten_at_rules(text)
        for m in RX["css.rule"].finditer(text):
            # a preceding at-statement (`@import url(...);`, `@charset "x";`) is not part of the selector
            raw_sel = m.group("sel")
            cut = raw_sel.rfind(";") + 1
            sel_raw = raw_sel[cut:]
            sel, body = sel_raw.strip(), m.group("body")
            if not sel or sel.startswith("@"):
                continue
            sel_line = lineno(full, base + m.start("sel") + cut + (len(sel_raw) - len(sel_raw.lstrip())))
            self.scan_css_body(rel, sel, body, base + m.start("body"), full, platform, sel_line)

    def scan_css_body(self, rel, sel, body, base, full, platform, sel_line=None):
        P = platform
        masked = RX["css.shadow_mask"].sub(lambda s: " " * len(s.group(0)), body)
        for mm in RX["css.hex"].finditer(masked):
            hexv, a = norm_hex(mm.group("hex"))
            self.add("color", rel, lineno(full, base + mm.start()), hexv, mm.group(0), a, P)
        for mm in RX["css.rgb"].finditer(masked):
            self.add("color", rel, lineno(full, base + mm.start()), rgb_to_hex(mm.group("r"), mm.group("g"), mm.group("b")),
                     mm.group(0), alpha_of(mm.group("a")), P)
        for mm in RX["css.hsl"].finditer(masked):
            self.add("color", rel, lineno(full, base + mm.start()), hsl_to_hex(mm.group("h"), mm.group("s"), mm.group("l")),
                     mm.group(0), alpha_of(mm.group("a")), P)
        for mm in RX["css.radius"].finditer(body):
            if not is_literal_value(mm.group("v")):
                continue
            vals = RX["css.px"].findall(strip_vars(mm.group("v")))
            for n, u in vals:
                v = num(to_px(n, u, self.rem_base))
                ev = collapse(mm.group(0)) + (" → %s" % v if len(vals) > 1 else "")
                self.add("radius", rel, lineno(full, base + mm.start()), "pill" if v >= 999 else v, ev, None, P)
        for mm in RX["css.font_size"].finditer(body):
            self.add("fontSize", rel, lineno(full, base + mm.start()), num(to_px(mm.group("n"), mm.group("u"), self.rem_base)), mm.group(0), None, P)
        for mm in RX["css.font_family"].finditer(body):
            v = mm.group("v").strip()
            if is_literal_value(v) and not v.lower().startswith(("var(", "inherit", "initial", "unset")):
                fam = v.split(",")[0].strip().strip("'\"")
                if fam:
                    self.add("fontFamily", rel, lineno(full, base + mm.start()), fam, mm.group(0), None, P)
        for mm in RX["css.var_decl"].finditer(body):
            name, v, ln = mm.group("name").lower(), mm.group("v").strip(), lineno(full, base + mm.start())
            ev = collapse(mm.group(0))
            if not is_literal_value(v):
                continue
            v = strip_vars(v)
            if "radius" in name:
                for n, u in RX["css.px"].findall(v):
                    px = num(to_px(n, u, self.rem_base))
                    self.add("radius", rel, ln, "pill" if px >= 999 else px, ev, None, P)
            elif "font-size" in name or name.startswith("text-"):
                for n, u in RX["css.px"].findall(v):
                    self.add("fontSize", rel, ln, num(to_px(n, u, self.rem_base)), ev, None, P)
            elif "font" in name:
                fam = v.split(",")[0].strip().strip("'\"")
                if fam and not fam.startswith("var("):
                    self.add("fontFamily", rel, ln, fam, ev, None, P)
            elif "shadow" in name:
                for sig in shadow_signatures_css_multi(v):
                    self.add_shadow(sig, rel, ln, ev, P)
            elif any(k in name for k in ("duration", "motion", "transition")):
                for n, u in RX["css.ms"].findall(v):
                    ms = num(to_ms(n, u))
                    if ms:
                        self.add("duration", rel, ln, ms, ev, None, P)
            elif any(k in name for k in ("space", "spacing", "gap")):
                for n, u in RX["css.px"].findall(v):
                    self.add("spacing", rel, ln, num(to_px(n, u, self.rem_base)), ev, None, P)
        for mm in RX["css.shadow"].finditer(body):
            for sig in shadow_signatures_css_multi(mm.group("v")):  # var()/none layers are skipped inside
                self.add_shadow(sig, rel, lineno(full, base + mm.start()), mm.group(0), P)
        for mm in RX["css.duration"].finditer(body):
            if not is_literal_value(mm.group("v")):
                continue
            for n, u in RX["css.ms"].findall(strip_vars(mm.group("v"))):
                ms = num(to_ms(n, u))
                if ms:
                    self.add("duration", rel, lineno(full, base + mm.start()), ms, mm.group(0), None, P)
        for mm in RX["css.spacing"].finditer(body):
            if not is_literal_value(mm.group("v")):
                continue
            vals = RX["css.px"].findall(strip_vars(mm.group("v")))
            for n, u in vals:
                v = num(to_px(n, u, self.rem_base))
                ev = collapse(mm.group(0)) + (" → %s" % v if len(vals) > 1 else "")
                self.add("spacing", rel, lineno(full, base + mm.start()), v, ev, None, P)
        if sel and sel_line is not None and is_touch_selector(sel):
            dims = {k: to_px(n, u, self.rem_base) for k, n, u in RX["css.wh"].findall(body)}
            w = dims.get("width", dims.get("min-width"))
            h = dims.get("height", dims.get("min-height"))
            if w is not None and h is not None:
                self.add("touch", rel, sel_line, (w, h), "%s { width: %s; height: %s }" % (sel, num(w), num(h)), sel, P, "heuristic")
        if sel and sel_line is not None:
            fg = RX["css.fg"].search(body)
            bg = RX["css.bg"].search(body)
            if fg and bg:
                f, b = norm_hex(fg.group("hex"))[0], norm_hex(bg.group("hex"))[0]
                ratio = round(contrast(f, b), 2)
                self.add("contrast", rel, lineno(full, base + fg.start()), ratio, "%s { color: %s; background: %s }" % (sel, f, b), (sel, f, b), P, "heuristic")

    def scan_google_fonts(self, rel, text, platform):
        """Families requested from fonts.googleapis.com (<link href>, CSS @import url(), JS strings)."""
        for m in RX["google.fonts_url"].finditer(text):
            css2 = text[m.start():m.start("qs")].rstrip("?").endswith("css2")
            ln = lineno(text, m.start())
            for name, raw in google_font_families(m.group("qs"), css2):
                self.add("fontFamily", rel, ln, name, "fonts.googleapis.com family=%s" % raw, None, platform)

    def scan_tailwind_font_families(self, rel, text):
        """Tailwind theme `fontFamily: { key: ['Family', ...] }` in tailwind.config.* or an inline
        `tailwind.config = {...}` <script>. First (primary) family of each entry; var()/generic skipped."""
        for m in RX["tw.font_family_block"].finditer(text):
            block = balanced_block(text, m.start())
            base = m.start()
            inner_start = block.find("{") + 1
            for e in RX["tw.font_family_entry"].finditer(block, inner_start):
                name = (e.group("name") or (e.group("name2") or "").split(",")[0]).strip().strip("'\"")
                if not name or not is_literal_value(name) or name.lower() in GENERIC_FAMILIES:
                    continue
                self.add("fontFamily", rel, lineno(text, base + e.start()), name, e.group(0), None, "web")

    def scan_uxml(self, rel, text):
        for m in RX["uxml.style_attr"].finditer(text):
            self.scan_css_body(rel, "", m.group("v"), m.start("v"), text, "unity", None)

    # -- web markup
    def scan_markup(self, rel, text, ext):
        P = "web"
        if ext in (".vue", ".svelte", ".html"):
            for m in RX["html.style_block"].finditer(text):
                self.scan_css(rel, m.group("css"), P, base=m.start("css"), full_text=text)
            text = RX["html.style_block"].sub(lambda s: "".join("\n" if c == "\n" else " " for c in s.group(0)), text)
            # inline style="..." attributes go through the full CSS declaration extractors, then are blanked
            # so the markup-level hex/rgb pass below does not count their colours twice
            for m in RX["html.style_attr"].finditer(text):
                self.scan_css_body(rel, "", m.group("v"), m.start("v"), text, P, None)
            text = RX["html.style_attr"].sub(
                lambda s: s.group(0)[:s.start("v") - s.start()] + "".join("\n" if c == "\n" else " " for c in s.group("v")) + s.group("q"), text)
            for m in RX["web.icon_cdn"].finditer(text):
                lib = "font-awesome" if "awesome" in m.group("lib") else m.group("lib")
                self.add_icon(P, lib, rel, lineno(text, m.start()), m.group(0))
        self.scan_tailwind_font_families(rel, text)
        for m in RX["tw.color"].finditer(text):
            hexv, a = norm_hex(m.group("hex"))
            self.add("color", rel, lineno(text, m.start()), hexv, m.group(0), a, P)
        masked = RX["tw.color"].sub(lambda s: " " * len(s.group(0)), text)
        for m in RX["css.hex"].finditer(masked):
            hexv, a = norm_hex(m.group("hex"))
            self.add("color", rel, lineno(text, m.start()), hexv, m.group(0), a, P)
        for m in RX["css.rgb"].finditer(masked):
            self.add("color", rel, lineno(text, m.start()), rgb_to_hex(m.group("r"), m.group("g"), m.group("b")), m.group(0), alpha_of(m.group("a")), P)
        for m in RX["tw.radius"].finditer(text):
            v = num(to_px(m.group("n"), m.group("u"), self.rem_base))
            self.add("radius", rel, lineno(text, m.start()), "pill" if v >= 999 else v, m.group(0), None, P)
        for m in RX["js.style_radius"].finditer(text):
            v = num(to_px(m.group("n"), m.group("u") or "px", self.rem_base))
            self.add("radius", rel, lineno(text, m.start()), "pill" if v >= 999 else v, m.group(0), None, P)
        for m in RX["tw.font_size"].finditer(text):
            self.add("fontSize", rel, lineno(text, m.start()), num(to_px(m.group("n"), m.group("u"), self.rem_base)), m.group(0), None, P)
        for m in RX["js.style_font_size"].finditer(text):
            self.add("fontSize", rel, lineno(text, m.start()), num(to_px(m.group("n"), m.group("u") or "px", self.rem_base)), m.group(0), None, P)
        for m in RX["tw.spacing"].finditer(text):
            self.add("spacing", rel, lineno(text, m.start()), num(to_px(m.group("n"), m.group("u"), self.rem_base)), m.group(0), None, P)
        for m in RX["js.duration_str"].finditer(text):
            ms = num(to_ms(m.group("n"), m.group("u")))
            if ms:
                self.add("duration", rel, lineno(text, m.start()), ms, m.group(0), None, P)
        for m in RX["tw.duration"].finditer(text):
            ms = num(to_ms(m.group("n"), m.group("u")))
            if ms:
                self.add("duration", rel, lineno(text, m.start()), ms, m.group(0), None, P)
        for m in RX["web.icon_import"].finditer(text):
            pkg = m.group("pkg")
            lib = "/".join(pkg.split("/")[:2]) if pkg.startswith("@") else pkg.split("/")[0]
            self.add_icon(P, lib, rel, lineno(text, m.start()), m.group(0))
        for m in RX["ts.component"].finditer(text):
            name = m.group("fn") or m.group("const")
            if RX["component.name"].match(name):
                ev = "export const %s" % name if m.group("const") else "export function %s" % name
                self.add_component(P, name, rel, lineno(text, m.start()), ev, ts_block(text, m.start()))

    # -- unity c#
    def scan_cs(self, rel, text):
        P = "unity"
        for m in RX["cs.color_f"].finditer(text):
            self.add("color", rel, lineno(text, m.start()), unity_f_to_hex(m.group("r"), m.group("g"), m.group("b")),
                     m.group(0), float(m.group("a")) if m.group("a") else None, P)
        for m in RX["cs.color32"].finditer(text):
            self.add("color", rel, lineno(text, m.start()), rgb_to_hex(m.group("r"), m.group("g"), m.group("b")), m.group(0), int(m.group("a")) / 255.0, P)
        for m in RX["cs.html_string"].finditer(text):
            hexv, a = norm_hex(m.group("hex"))
            self.add("color", rel, lineno(text, m.start()), hexv, m.group(0) + ")", a, P)
        for key in ("cs.dotween", "cs.dotween_to"):
            for m in RX[key].finditer(text):
                last = m.group("args").split(",")[-1].strip()
                mm = RX["cs.last_float"].search(last)
                if mm:
                    ms = num(float(mm.group("n")) * 1000)
                    if ms:
                        self.add("duration", rel, lineno(text, m.start()), ms, m.group(0), None, P)
        for m in RX["cs.class"].finditer(text):
            if RX["component.name"].match(m.group("name")):
                self.add_component(P, m.group("name"), rel, lineno(text, m.start()), m.group(0), balanced_block(text, m.start()))

    # -- swift / kotlin (experimental)
    def scan_swift(self, rel, text):
        P = "native"
        self.experimental.add("swift")
        for m in RX["swift.color"].finditer(text):
            self.add("color", rel, lineno(text, m.start()), unity_f_to_hex(m.group("r"), m.group("g"), m.group("b")), m.group(0), None, P)
        for m in RX["swift.color_hex"].finditer(text):
            hexv, a = norm_hex(m.group("hex"))
            self.add("color", rel, lineno(text, m.start()), hexv, m.group(0), a, P)
        for m in RX["swift.radius"].finditer(text):
            v = num(m.group("n"))
            self.add("radius", rel, lineno(text, m.start()), "pill" if v >= 999 else v, m.group(0), None, P)
        for m in RX["swift.font_size"].finditer(text):
            self.add("fontSize", rel, lineno(text, m.start()), num(m.group("n")), m.group(0), None, P)

    def scan_kotlin(self, rel, text):
        P = "native"
        self.experimental.add("kotlin")
        for m in RX["kt.color"].finditer(text):
            hexv, a = norm_argb(m.group("argb"))
            self.add("color", rel, lineno(text, m.start()), hexv, m.group(0), a, P)
        for m in RX["kt.radius"].finditer(text):
            v = num(m.group("n"))
            self.add("radius", rel, lineno(text, m.start()), "pill" if v >= 999 else v, m.group(0), None, P)
        for m in RX["kt.font_size"].finditer(text):
            self.add("fontSize", rel, lineno(text, m.start()), num(m.group("n")), m.group(0), None, P)
        for m in RX["kt.duration"].finditer(text):
            ms = int(m.group("n"))
            if ms:
                self.add("duration", rel, lineno(text, m.start()), ms, m.group(0), None, P)


# --------------------------------------------------------------- findings
def _scale_text(scale):
    return ", ".join(str(s) for s in scale) if scale else "(empty)"


def _stem(rel):
    return os.path.splitext(os.path.basename(rel))[0]


def page_slug(rel):
    """Screen slug for pages/<slug>.md: strip Screen/Panel/Page/View/Widget suffixes, kebab-case.
    shop_screen.dart -> shop, ShopPanel.cs -> shop, CtaButton.tsx -> cta-button."""
    stem = _stem(rel)
    stem = re.sub(r"\.(g|freezed|gr|module|styles?)$", "", stem)
    stem = re.sub(r"(?i)[_-]?(screen|panel|page|view|widget|component|styles?|sheet)$", "", stem) or stem
    kebab = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", stem).replace("_", "-").replace(" ", "-").lower()
    kebab = re.sub(r"-+", "-", kebab).strip("-")
    return kebab or "default"


def _page_hint(rel):
    return "pages/%s.md" % page_slug(rel)


class Finder(object):
    """Turn scanner hits into contract findings (contract mode) or variant-explosion
    findings (inventory mode). All thresholds live here."""

    def __init__(self, scanner, contract=None, profile=None, tolerance=None, near_threshold=12.0, primary_globs=()):
        self.s = scanner
        self.c = contract
        self.p = profile or {}
        self.tol = tolerance
        self.near = near_threshold
        self.primary_globs = primary_globs
        self.findings = []
        self.min_touch = contract["minTouchTarget"] if contract else 44.0

    # -- severity helpers
    def ladder(self, rel, count):
        return "high" if count >= 3 or is_primary(rel, self.primary_globs) else "medium"

    def emit(self, rule, sev, hit_file, line, evidence, message, violates, nearest_txt, impact, fix,
             files=None, kind="rule", confidence="exact"):
        self.findings.append({
            "id": None, "rule": rule, "severity": sev, "category": rule.split(".")[0],
            "file": hit_file, "line": int(line), "evidence": evidence, "message": message,
            "violates": violates, "nearest": nearest_txt, "impact": impact, "fix": fix,
            "files_to_change": files or [hit_file], "verify": "", "kind": kind, "confidence": confidence,
        })

    def anti_pattern_text(self, category):
        words = {"color": ("colour", "color", "palette"), "radius": ("radius", "corner", "rounded"),
                 "font-size": ("font", "type", "text size"), "font-family": ("font", "family", "typeface"),
                 "spacing": ("spacing", "padding", "gap"), "shadow": ("shadow",), "duration": ("motion", "animation", "duration"),
                 "icon": ("icon",), "component": ("component", "button"), "touch": ("touch", "tap", "target"), "text": ("contrast", "readab")}
        out = []
        for ap in self.p.get("anti_patterns") or []:
            if isinstance(ap, str) and any(w in ap.lower() for w in words.get(category, ())):
                out.append(ap)
        return out

    def violates_text(self, token_path, category):
        extra = self.anti_pattern_text(category)
        return token_path + ("; profile anti_patterns: " + " | ".join(extra) if extra else "")

    def fix_suffix(self, rel):
        return "; if intentional, add to `%s` intentional_exceptions" % _page_hint(rel)

    # -- grouping
    def hits(self, cat):
        return [h for h in self.s.hits if h.cat == cat]

    def run(self):
        if self.c:
            self.colors()
            self.scale("radius", "radius.off-scale", self.c["radius"], "tokens radius values (all layers)", "corner radius")
            self.scale("fontSize", "font-size.off-scale", self.c["fontSize"], "tokens fontSize values (all layers)", "font size")
            self.scale("spacing", "spacing.off-scale", self.c["spacing"], "tokens spacing values (all layers)", "spacing")
            self.scale("duration", "duration.off-scale", self.c["duration"], "tokens duration values (all layers)", "duration (ms)")
            self.families()
            self.shadows_contract()
        else:
            self.variant_explosions()
        self.icons()
        self.duplicates()
        self.touch()
        self.contrast_risk()
        self.apply_exceptions()
        self.finalise()
        return self.findings

    # -- colours
    def colors(self):
        allowed = self.c["colors"]
        if not allowed:
            return
        hits = self.hits("color")
        offs = []
        for h in hits:
            if h.value in allowed:
                continue
            if h.value in ("#000000", "#FFFFFF") and h.extra is not None and h.extra < 1:
                continue
            offs.append(h)
        counts = {}
        for h in offs:
            counts[h.value] = counts.get(h.value, 0) + 1
        for h in offs:
            near_hex = min(allowed, key=lambda c: (color_distance(h.value, c), c))
            d = color_distance(h.value, near_hex)
            near_txt = "%s %s (distance %.1f)" % (allowed[near_hex], near_hex, d)
            stem = _stem(h.file)
            if d <= self.near:
                self.emit("color.near-duplicate", "low", h.file, h.line, h.evidence,
                          "Colour %s is a near-duplicate of a contract colour (distance %.1f <= %.0f)" % (h.value, d, self.near),
                          self.violates_text("tokens colour values, all layers (allowed set)", "color"), near_txt,
                          "`%s` renders %s next to %s elsewhere; the two read as the same colour with a slight mismatch" % (stem, h.value, near_hex),
                          "Replace with the %s token (%s)%s" % (allowed[near_hex], near_hex, self.fix_suffix(h.file)))
            else:
                if d > FAR_COLOR_DISTANCE:
                    fix = ("No close token (nearest %s %s is %.1f away) \u2014 pick the semantic role (primary/accent/surface/text/success/danger/reward) "
                           "that matches the element's purpose and use its token%s" % (allowed[near_hex], near_hex, d, self.fix_suffix(h.file)))
                    impact = "`%s` renders %s, a colour the contract has no counterpart for; it reads as foreign to the palette" % (stem, h.value)
                else:
                    fix = "Replace with the nearest token %s (%s) or a semantic colour that fits the role%s" % (allowed[near_hex], near_hex, self.fix_suffix(h.file))
                    impact = "`%s` renders %s where the contract expects %s; adjacent screens will not match" % (stem, h.value, allowed[near_hex])
                self.emit("color.off-palette", self.ladder(h.file, counts[h.value]), h.file, h.line, h.evidence,
                          "Hard-coded colour %s not in tokens.json palette" % h.value,
                          self.violates_text("tokens colour values, all layers (allowed set)", "color"), near_txt, impact, fix)

    # -- numeric scales
    def scale(self, cat, rule, scale, token_path, label):
        if not scale:
            return
        hits = self.hits(cat)
        offs = [h for h in hits if h.value != 0 and not on_scale(h.value, scale, self.tol)]
        counts = {}
        for h in offs:
            counts[h.value] = counts.get(h.value, 0) + 1
        for h in offs:
            cnt = counts[h.value]
            if rule == "spacing.off-scale":
                sev = "medium" if cnt >= 3 else "low"
            elif rule == "duration.off-scale":
                sev = "high" if cnt >= 3 else "medium"
            else:
                sev = self.ladder(h.file, cnt)
            near_v = nearest(h.value, scale)
            near_path = self.c.get("scale_paths", {}).get(cat, {}).get(near_v, cat)
            near_txt = "%s %s (scale %s)" % (near_path, near_v, _scale_text(scale))
            stem = _stem(h.file)
            impact = {
                "radius": "`%s` uses corner radius %s while the scale is %s; shapes read as a different component family" % (stem, h.value, _scale_text(scale)),
                "fontSize": "`%s` sets text at %s outside the type scale %s; the type rhythm breaks between screens" % (stem, h.value, _scale_text(scale)),
                "spacing": "`%s` pads with %s; off-grid spacing makes groups look misaligned next to on-grid screens" % (stem, h.value),
                "duration": "`%s` animates in %s ms instead of a contract step (%s); motion feels inconsistent between screens" % (stem, h.value, _scale_text(scale)),
            }[cat]
            self.emit(rule, sev, h.file, h.line, h.evidence,
                      "%s %s is not on the contract scale (%s); nearest step %s (%d occurrence%s project-wide)" % (
                          label.capitalize(), h.value, _scale_text(scale), near_v, cnt, "" if cnt == 1 else "s"),
                      self.violates_text("%s (allowed set %s)" % (token_path, _scale_text(scale)), rule.split(".")[0]), near_txt, impact,
                      "Use the %s step %s (%s)%s" % (label, near_v, near_path, self.fix_suffix(h.file)))

    # -- families
    def families(self):
        allowed = self.c["fontFamily"]
        if not allowed:
            return
        hits = [h for h in self.hits("fontFamily") if h.value.lower() not in GENERIC_FAMILIES]
        offs = [h for h in hits if h.value.lower() not in allowed]
        counts = {}
        for h in offs:
            counts[h.value.lower()] = counts.get(h.value.lower(), 0) + 1
        listed = ", ".join(sorted(allowed.values()))
        for h in offs:
            self.emit("font-family.unlisted", self.ladder(h.file, counts[h.value.lower()]), h.file, h.line, h.evidence,
                      "Font family '%s' is not a contract family (%s)" % (h.value, listed),
                      self.violates_text("tokens fontFamily values, all layers + $extensions.vdp.fontFamilies (allowed: %s)" % listed, "font-family"),
                      "contract families: %s" % listed,
                      "`%s` sets family '%s'; the contract typography is %s, so this text reads as foreign" % (_stem(h.file), h.value, listed),
                      "Use the display or body family (%s)%s" % (listed, self.fix_suffix(h.file)))

    # -- shadows (contract mode)
    def shadows_contract(self):
        allowed = self.c["shadows"]
        sigs = {}
        for sig, rel, line, ev, plat in self.s.shadows:
            sigs.setdefault(sig, []).append((rel, line, ev))
        unlisted = [sig for sig in sorted(sigs, key=lambda s: min(sigs[s])) if sig not in allowed]
        for sig in unlisted:
            for rel, line, ev in sorted(sigs[sig]):
                self.emit("shadow.unlisted", "low", rel, line, ev,
                          "Shadow signature not in any tokens.json shadow ($type shadow, all layers): %s" % sig,
                          self.violates_text("tokens shadow values, all layers (%d allowed signature%s)" % (len(allowed), "" if len(allowed) == 1 else "s"), "shadow"),
                          "allowed: " + "; ".join("%s = %s" % (p, s) for s, p in sorted(allowed.items(), key=lambda kv: kv[1])) if allowed else None,
                          "`%s` casts a shadow no other screen uses; elevation reads differently on this screen" % _stem(rel),
                          "Use one of the contract shadows (%s)%s" % (", ".join(sorted(allowed.values())) or "none defined", self.fix_suffix(rel)))
        if len(sigs) > len(allowed) and unlisted:
            first = min(sigs[unlisted[0]])
            self.emit("shadow.variant-explosion", "medium", first[0], first[1], unlisted[0],
                      "distinct=%d allowed=%d shadow signatures project-wide: %s" % (
                          len(sigs), len(allowed), "; ".join("%s x%d" % (s, len(v)) for s, v in sorted(sigs.items()))),
                      self.violates_text("tokens shadow values, all layers (allowed distinct count %d)" % len(allowed), "shadow"),
                      "allowed signatures: %s" % ("; ".join(sorted(allowed)) or "none"),
                      "%d elevation styles compete across screens; cards and buttons do not share one depth language" % len(sigs),
                      "Map every shadow to a shadow token (primitive.shadow / semantic.elevation / component.*.shadow); delete the extra signatures" + self.fix_suffix(first[0]),
                      files=sorted({r for v in sigs.values() for r, _, _ in v}))

    # -- inventory mode
    def variant_explosions(self):
        inv = build_inventory(self.s)
        checks = [
            ("radius.variant-explosion", "radius", {k: v for k, v in inv["radii"].items() if k not in ("0", "9999", "pill")}, 4),
            ("font-family.variant-explosion", "fontFamily", {f: c for f, c in inv["_family_counts"].items() if f.lower() not in GENERIC_FAMILIES}, 3),
            ("font-size.variant-explosion", "fontSize", inv["font_sizes"], 8),
            ("duration.variant-explosion", "duration", inv["durations"], 6),
            ("color.variant-explosion", "color", inv["colors"], 24),
        ]
        for rule, cat, values, limit in checks:
            if len(values) <= limit:
                continue
            stray = min(values, key=lambda k: (values[k], str(k)))
            hit = None
            for h in sorted(self.hits(cat), key=lambda h: (h.file, h.line)):
                if str(h.value) == str(stray) or (cat == "fontFamily" and h.value == stray):
                    hit = h
            # evidence = value with the fewest occurrences; ties -> later sorted file (max over sorted order)
            if hit is None:
                continue
            self.emit(rule, "medium", hit.file, hit.line, hit.evidence,
                      "%d distinct %s values project-wide (> %d): %s" % (
                          len(values), cat, limit, ", ".join("%s x%d" % (k, values[k]) for k in sorted(values, key=lambda k: (-values[k], str(k))))),
                      "no contract loaded (inventory mode); recommendation threshold > %d distinct" % limit,
                      None,
                      "Too many %s variants means no scale is being followed; screens drift independently" % cat,
                      "Define a scale in tokens.json (`vd.py init` from the visual-direction skill) and re-run with --contract",
                      kind="recommendation")
        sigs = {}
        for sig, rel, line, ev, plat in self.s.shadows:
            sigs.setdefault(sig, []).append((rel, line, ev))
        if len(sigs) > 6:
            stray = min(sigs, key=lambda s: (len(sigs[s]), [-ord(c) for c in min(sigs[s])[0]]))
            first = max(sigs[stray]) if len(sigs[stray]) > 1 else sigs[stray][0]
            self.emit("shadow.variant-explosion", "medium", first[0], first[1], stray,
                      "distinct=%d (> 6) shadow signatures project-wide: %s" % (len(sigs), "; ".join("%s x%d" % (s, len(v)) for s, v in sorted(sigs.items()))),
                      "no contract loaded (inventory mode); recommendation threshold > 6 distinct", None,
                      "%d elevation styles compete across screens" % len(sigs),
                      "Define primitive.shadow in tokens.json (`vd.py init`) and re-run with --contract", kind="recommendation")

    # -- icons
    def icons(self):
        contract_lib = (self.c or {}).get("iconLibrary")
        for plat in sorted(self.s.icon_libs):
            libs = self.s.icon_libs[plat]
            if len(libs) < 2:
                continue
            names = sorted(libs)
            files_per = {l: len({r for r, _, _ in libs[l]}) for l in names}
            uses_per = {l: len(libs[l]) for l in names}
            top = max(files_per[l] for l in names)
            tied = [l for l in names if files_per[l] == top]
            if len(tied) > 1 and contract_lib in tied:
                preferred = contract_lib
            else:
                preferred = tied[0]  # alphabetical first among the most-used
            others = [l for l in names if l != preferred]
            # point the finding at the non-preferred library with the fewest files (ties -> later sorted file)
            replace = min(others, key=lambda l: (files_per[l], [-ord(c) for c in max(libs[l])[0]]))
            rel, line, ev = min(libs[replace])
            sev = "high" if len(libs) >= 3 else "medium"
            why = ("declared in the contract" if preferred == contract_lib and contract_lib in libs else
                   "most used in the %s group" % plat if len(tied) == 1 else "tie broken alphabetically")
            self.emit("icon.mixed-libraries", sev, rel, line, ev,
                      "%s group uses %d icon libraries: %s; keep %s, replace %s" % (
                          plat, len(libs), ", ".join("%s (%d file%s, %d use%s)" % (l, files_per[l], "" if files_per[l] == 1 else "s", uses_per[l], "" if uses_per[l] == 1 else "s") for l in names),
                          preferred, ", ".join(others)),
                      self.violates_text("tokens.$extensions.vdp.iconLibrary / profile iconography.library_hint (one library per platform)", "icon"),
                      "preferred for %s: %s (%s)" % (plat, preferred, why),
                      "Two icon languages (%s) on one platform read as two products; stroke weight and corner style will not match" % ", ".join(names),
                      "Keep %s and replace the %s icons with %s equivalents; if a second library is required, declare it in the profile" % (
                          preferred, ", ".join(others), preferred),
                      files=sorted({r for l in names for r, _, _ in libs[l]}))

    # -- duplicate components
    def duplicates(self):
        canon_dirs = ("widgets/", "components/", "ui/", "shared/", "design_system/")
        for plat in sorted(self.s.components):
            fams = {}
            for name, defs in self.s.components[plat].items():
                fam = RX["component.family"].search(name)
                fam = fam.group(1) if fam else name
                for rel, line, ev, body in defs:
                    fams.setdefault(fam, []).append((rel, line, ev, body, name))
            for fam, defs in sorted(fams.items()):
                defs = sorted(defs)
                files = sorted({d[0] for d in defs})
                if len(files) < 2:
                    continue
                canon = [d for d in defs if any(c in d[0].lower() for c in canon_dirs)]
                canonical = canon[0] if canon else defs[0]
                for d in defs:
                    if d[0] == canonical[0]:
                        continue
                    same = d[3] == canonical[3]
                    self.emit("component.duplicate-implementation", "medium", d[0], d[1], d[2],
                              "%s of %s: `%s` in %s:%d vs `%s` in %s:%d" % (
                                  "copy-paste duplicate" if same else "divergent re-implementation", fam, d[4], d[0], d[1], canonical[4], canonical[0], canonical[1]),
                              self.violates_text("component-catalog: one implementation per component family (%s)" % fam, "component"),
                              "canonical: %s (%s)" % (canonical[0], canonical[4]),
                              "Two implementations of %s drift independently; a fix in one does not reach the other" % fam,
                              "Reuse `%s` from %s and delete `%s`; if the variant is intentional, make it a prop/variant of the canonical component" % (canonical[4], canonical[0], d[4]),
                              files=[d[0], canonical[0]], kind="recommendation", confidence="heuristic")

    # -- touch targets
    def touch(self):
        mn = self.min_touch
        for h in self.hits("touch"):
            w, hgt = h.value
            dims = [d for d in (w, hgt) if d is not None]
            if not dims or min(dims) >= mn:
                continue
            smallest = min(dims)
            sev = "medium"  # heuristic: capped at medium (CC-10h); the human confirms the rendered hit rect
            size = "%sx%s" % (num(w) if w is not None else "?", num(hgt) if hgt is not None else "?")
            self.emit("touch.target-too-small", sev, h.file, h.line, h.evidence,
                      "[heuristic] Tappable control %s is below the minimum touch target %s (%s)%s" % (size, num(mn), h.extra, "; smallest dimension < 24 - confirm on device, may be critical" if smallest < 24 else ""),
                      self.violates_text("tokens.$extensions.vdp.minTouchTarget / primitive.touchTarget.min = %s" % num(mn), "touch"),
                      "minimum %s" % num(mn),
                      "A %s hit area mis-taps on touch devices, especially for the thumb zone on phones" % size,
                      "Grow the control (or its padding / hit-test area) to at least %sx%s; confirm the rendered hit area on device" % (num(mn), num(mn)),
                      kind="recommendation", confidence="heuristic")

    # -- contrast
    def contrast_risk(self):
        for h in self.hits("contrast"):
            if h.value >= 4.5:
                continue
            sel, f, b = h.extra
            sev = "medium"  # heuristic: capped at medium; rendered contrast must be measured by hand
            self.emit("text.contrast-risk", sev, h.file, h.line, h.evidence,
                      "[heuristic] Text %s on %s has contrast %.2f:1 (< 4.5:1) in `%s`" % (f, b, h.value, sel),
                      self.violates_text("WCAG 2.x 1.4.3 (4.5:1 body text) / tokens.semantic.color text-on-surface pairs", "text"),
                      "needs >= 4.5:1 (3:1 for large text)",
                      "Text in `%s` is hard to read for low-vision users and in sunlight; %.2f:1 is far below AA" % (sel, h.value),
                      "Pair the text with a darker/lighter semantic colour (text / onPrimary / onAccent) or add a plate behind it; verify on the rendered background",
                      kind="recommendation", confidence="heuristic")

    # -- profile exceptions
    def apply_exceptions(self):
        exc = self.p.get("intentional_exceptions") or []
        if not exc:
            return
        for f in self.findings:
            for e in exc:
                if not isinstance(e, dict):
                    continue
                rule_txt = str(e.get("rule", "")).lower()
                scope = str(e.get("scope", "")).lower().replace("_", "-")
                path = f["file"].lower().replace("_", "-")
                cat_word = f["category"].split("-")[0]
                if (f["rule"] in rule_txt or cat_word in rule_txt) and scope and scope in path:
                    f["kind"] = "intentional-exception"
                    f["severity"] = "info"
                    f["message"] = "[intentional: %s] " % e.get("reason", "no reason given") + f["message"]
                    f["violates"] = "intentional_exceptions[scope=%s, rule=%s]" % (e.get("scope"), e.get("rule"))
                    break

    def finalise(self):
        self.findings.sort(key=lambda f: (SEV_RANK[f["severity"]], f["file"], f["line"], f["rule"], f["evidence"]))
        for i, f in enumerate(self.findings, 1):
            f["id"] = "VA-%04d" % i
            f["verify"] = "re-run `audit.py scan`; %s must be absent (`audit.py compare` lists it under resolved)" % f["id"]


# -------------------------------------------------------------- inventory
def build_inventory(s):
    colors, colors_alpha, radii, fonts, spacing, durations, fams = {}, {}, {}, {}, {}, {}, {}
    for h in s.hits:
        if h.cat == "color":
            if h.extra is not None and h.extra < 1:
                key = "%s@%.2f" % (h.value, h.extra)
                colors_alpha[key] = colors_alpha.get(key, 0) + 1
            else:
                colors[h.value] = colors.get(h.value, 0) + 1
        elif h.cat == "radius":
            k = "9999" if h.value == "pill" else str(h.value)
            radii[k] = radii.get(k, 0) + 1
        elif h.cat == "fontSize":
            fonts[str(h.value)] = fonts.get(str(h.value), 0) + 1
        elif h.cat == "spacing":
            spacing[str(h.value)] = spacing.get(str(h.value), 0) + 1
        elif h.cat == "duration":
            durations[str(h.value)] = durations.get(str(h.value), 0) + 1
        elif h.cat == "fontFamily":
            fams[h.value] = fams.get(h.value, 0) + 1
    libs = sorted({l for plat in s.icon_libs.values() for l in plat})
    components = {}
    for plat in s.components.values():
        for name, defs in plat.items():
            components[name] = sorted({d[0] for d in defs})
    return {
        "colors": dict(sorted(colors.items())),
        "colors_with_alpha": dict(sorted(colors_alpha.items())),
        "named_colors": dict(sorted(s.named_colors.items())),
        "radii": dict(sorted(radii.items(), key=lambda kv: float(kv[0]))),
        "font_sizes": dict(sorted(fonts.items(), key=lambda kv: float(kv[0]))),
        "spacing": dict(sorted(spacing.items(), key=lambda kv: float(kv[0]))),
        "shadows": len({sig for sig, _, _, _, _ in s.shadows}),
        "durations": dict(sorted(durations.items(), key=lambda kv: float(kv[0]))),
        "icon_libraries": libs,
        "icon_libraries_by_platform": {p: sorted(v) for p, v in sorted(s.icon_libs.items())},
        "font_families": sorted(fams),
        "components": dict(sorted(components.items())),
        "_family_counts": fams,
    }


# ------------------------------------------------------------------- scan
def scan_dir(root, tokens=None, profile=None, platform="auto", tolerance=None, near_threshold=12.0,
             excludes=(), primary_globs=(), max_files=20000, tokens_path=None, profile_path=None, warn=None):
    """Scan a directory; returns the visual-audit/1 report dict. tokens/profile are dicts."""
    warn = warn or (lambda msg: None)
    notes = []
    root_skip = flutter_scaffold_dirs(root) if platform != "native" else set()
    if root_skip:
        notes.append("flutter scaffold folders skipped (platform glue, not UI): %s; pass --platform native to scan them" % ", ".join(sorted(root_skip)))
    detected = detect_platform(root, root_skip)
    if platform == "auto":
        plat = detected
        allowed_plats = None
        if plat == "unknown":
            warn("platform unknown (no pubspec.yaml / package.json / Unity / native markers found): generic patterns applied to every supported extension")
            notes.append("platform unknown: generic patterns applied")
    elif platform == "mixed":
        plat, allowed_plats = "mixed", None
    else:
        plat = platform
        allowed_plats = {platform}
    files, skipped = walk(root, excludes, allowed_plats, root_skip)
    if len(files) > max_files:
        notes.append("file cap %d reached; %d files not scanned" % (max_files, len(files) - max_files))
        skipped += len(files) - max_files
        files = files[:max_files]
    if not files:
        warn("no source files found under %s (0 scanned, %d skipped)" % (root, skipped) + (
            " - 0 %s files" % plat if allowed_plats else ""))
        notes.append("no source files scanned")
    contract = load_contract(tokens, profile) if tokens is not None else None
    if contract:
        notes.extend(contract["notes"])
    scanner = Scanner()
    platforms = {}
    scanned = 0
    for rel, fplat in files:
        text = read_source(os.path.join(root, rel))
        if text is None:
            skipped += 1
            notes.append("skipped (binary/minified/too large): %s" % rel)
            continue
        scanned += 1
        platforms[fplat] = platforms.get(fplat, 0) + 1
        scanner.scan_file(rel, text, fplat)
    if scanner.experimental:
        notes.append("experimental extractors used (no fixture coverage): %s" % ", ".join(sorted(scanner.experimental)))
    finder = Finder(scanner, contract, profile, tolerance, near_threshold, primary_globs)
    findings = finder.run()
    if contract is None:
        notes.append("inventory-only rules: no --contract given, only variant-explosion / icon / duplicate / touch / contrast rules evaluated")
    summary = {s: 0 for s in SEVERITIES}
    for f in findings:
        summary[f["severity"]] += 1
    inventory = build_inventory(scanner)
    inventory.pop("_family_counts", None)
    return {
        "schema": SCHEMA,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "root": root,
        "platform": plat,
        "platform_detected": detected,
        "contract": {"tokens": tokens_path, "profile": profile_path},
        "scanned_files": scanned,
        "skipped_files": skipped,
        "summary": summary,
        "inventory": inventory,
        "findings": findings,
        "platforms": dict(sorted(platforms.items())),
        "notes": notes,
    }


# ---------------------------------------------------------------- outputs
def to_markdown(report):
    out = []
    out.append("# Visual audit — %s" % report["root"])
    out.append("platform: %s · contract: %s%s · scanned %d files · skipped %d · generated %s" % (
        report["platform"], report["contract"].get("tokens") or "none (inventory mode)",
        (" + " + report["contract"]["profile"]) if report["contract"].get("profile") else "",
        report["scanned_files"], report["skipped_files"], report["generated_at"]))
    out.append("")
    s = report["summary"]
    out.append("| critical | high | medium | low | info |")
    out.append("|---|---|---|---|---|")
    out.append("| %d | %d | %d | %d | %d |" % (s["critical"], s["high"], s["medium"], s["low"], s["info"]))
    out.append("")
    out.append("## Findings (by severity)")
    if not report["findings"]:
        out.append("")
        out.append("No findings.")
    for sev in SEVERITIES:
        group = [f for f in report["findings"] if f["severity"] == sev]
        if not group:
            continue
        out.append("")
        out.append("### %s%s" % (sev.upper(), " (intentional exceptions)" if sev == "info" else ""))
        for f in group:
            out.append("- **%s** `%s` [%s] — %s:%d — `%s`" % (f["id"], f["rule"], f["kind"], f["file"], f["line"], f["evidence"]))
            out.append("  %s%s" % (f["message"], (" Nearest: %s" % f["nearest"]) if f.get("nearest") else ""))
            out.append("  Fix: %s · Verify: %s" % (f["fix"], f["verify"]))
    inv = report["inventory"]
    out.append("")
    out.append("## Inventory")

    def fmt(d, limit=12):
        items = sorted(d.items(), key=lambda kv: (-kv[1], str(kv[0])))
        txt = " ".join("%s×%d" % (k, v) for k, v in items[:limit])
        return txt + (" …" if len(items) > limit else "") if items else "none"
    out.append("colours (opaque, distinct %d): %s" % (len(inv["colors"]), fmt(inv["colors"])))
    out.append("colours with alpha: %s" % fmt(inv["colors_with_alpha"]))
    out.append("radii: %s | font sizes: %s | spacing: %s" % (fmt(inv["radii"]), fmt(inv["font_sizes"]), fmt(inv["spacing"])))
    out.append("families: %s | shadows: %d distinct | durations: %s" % (", ".join(inv["font_families"]) or "none", inv["shadows"], fmt(inv["durations"])))
    out.append("icon libraries: %s" % (", ".join("%s {%s}" % (p, ", ".join(l)) for p, l in inv["icon_libraries_by_platform"].items()) or "none"))
    if inv["components"]:
        out.append("components: %s" % ", ".join("%s (%s)" % (n, ", ".join(fs)) for n, fs in inv["components"].items()))
    out.append("")
    out.append("## Notes")
    for n in report.get("notes") or []:
        out.append("- %s" % n)
    if not report.get("notes"):
        out.append("- none")
    return "\n".join(out) + "\n"


def threshold_hit(findings, fail_on):
    if fail_on == "none":
        return False
    rank = SEV_RANK[fail_on]
    return any(SEV_RANK[f["severity"]] <= rank and f["kind"] != "intentional-exception" and f["severity"] != "info" for f in findings)


# ---------------------------------------------------------------- compare
def compare_key(f):
    return (f.get("rule"), f.get("file"), re.sub(r"\s+", " ", str(f.get("evidence", ""))).strip().lower())


def compare_reports(before, after):
    """Multiset comparison on (rule, file, evidence-normalised); lines ignored."""
    def index(rep):
        idx = {}
        for f in rep.get("findings", []):
            idx.setdefault(compare_key(f), []).append(f)
        return idx
    b, a = index(before), index(after)
    resolved, new, unchanged, changed = [], [], [], []
    for key in sorted(set(b) | set(a), key=lambda k: (k[1], k[0], k[2])):
        bl, al = b.get(key, []), a.get(key, [])
        n = min(len(bl), len(al))
        for i in range(n):
            unchanged.append({"before": bl[i]["id"], "after": al[i]["id"], "rule": key[0], "file": key[1], "evidence": key[2]})
            if bl[i].get("severity") != al[i].get("severity"):
                changed.append({"before": bl[i]["id"], "after": al[i]["id"], "rule": key[0], "file": key[1],
                                "from": bl[i].get("severity"), "to": al[i].get("severity")})
        for f in bl[n:]:
            resolved.append({"id": f["id"], "rule": key[0], "file": key[1], "line": f.get("line"), "severity": f.get("severity"), "evidence": f.get("evidence")})
        for f in al[n:]:
            new.append({"id": f["id"], "rule": key[0], "file": key[1], "line": f.get("line"), "severity": f.get("severity"),
                        "kind": f.get("kind", "rule"), "evidence": f.get("evidence")})
    return {"schema": "visual-audit-compare/1", "resolved": resolved, "new": new, "unchanged": unchanged,
            "changed_severity": changed,
            "note": "severity is recomputed from project-wide occurrence counts after fixes; changed_severity entries are unchanged findings, not regressions",
            "counts": {"resolved": len(resolved), "new": len(new), "unchanged": len(unchanged), "changed_severity": len(changed)}}


def compare_markdown(result):
    c = result["counts"]
    out = ["resolved: %d  new: %d  unchanged: %d  changed_severity: %d" % (c["resolved"], c["new"], c["unchanged"], c["changed_severity"])]
    if c["changed_severity"]:
        out.append("note: severity recomputed from project-wide occurrence counts after fixes; changed_severity entries are unchanged findings, not regressions")
    if result["resolved"]:
        out.append("## Resolved")
        out.extend("- %s `%s` %s — `%s`" % (f["id"], f["rule"], f["file"], f["evidence"]) for f in result["resolved"])
    if result["new"]:
        out.append("## New")
        out.extend("- %s `%s` [%s] %s:%s — `%s`" % (f["id"], f["rule"], f["severity"], f["file"], f["line"], f["evidence"]) for f in result["new"])
    if result["changed_severity"]:
        out.append("## Changed severity")
        out.extend("- %s → %s `%s` %s: %s → %s" % (f["before"], f["after"], f["rule"], f["file"], f["from"], f["to"]) for f in result["changed_severity"])
    return "\n".join(out) + "\n"


# -------------------------------------------------------------------- CLI
def _load_json_file(path, what):
    """Return (data, exit_code, message). Missing -> 2, malformed -> 1."""
    if not os.path.isfile(path):
        return None, 2, "%s file not found: %s" % (what, path)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), 0, ""
    except (OSError, ValueError) as e:
        return None, 1, "%s is not valid JSON: %s (%s)" % (what, path, e)


def cmd_scan(args):
    root = args.dir
    if not os.path.isdir(root):
        sys.stderr.write("error: %s is not a directory\n" % root)
        return 2
    tokens = profile = None
    if args.contract:
        tokens, rc, msg = _load_json_file(args.contract, "contract tokens.json")
        if rc:
            sys.stderr.write("error: %s\n" % msg)
            return rc
    if args.profile:
        profile, rc, msg = _load_json_file(args.profile, "style-profile.json")
        if rc:
            sys.stderr.write("error: %s\n" % msg)
            return rc
        if not isinstance(profile, dict):
            sys.stderr.write("error: style-profile.json root must be an object\n")
            return 1
    try:
        report = scan_dir(os.path.normpath(root), tokens, profile, args.platform, args.tolerance, args.near_threshold,
                          tuple(args.exclude or ()), tuple(args.primary or ()), args.max_files,
                          args.contract, args.profile, warn=lambda m: sys.stderr.write("warning: %s\n" % m))
    except ContractError as e:
        sys.stderr.write("error: contract: %s\n" % e)
        return 1
    js = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    md = to_markdown(report)
    written = []
    if args.out:
        fmt = args.format or ("md" if args.out.lower().endswith(".md") else "json")
        write_text(args.out, md if fmt == "md" else js)
        written.append(args.out)
    if args.md:
        write_text(args.md, md)
        written.append(args.md)
    if written:
        sm = report["summary"]
        if args.json:
            line = {"findings": len(report["findings"]), "summary": sm, "scanned_files": report["scanned_files"],
                    "skipped_files": report["skipped_files"], "platform": report["platform"], "out": written}
            sys.stdout.write(json.dumps(line) + "\n")
        else:
            sys.stdout.write("visual audit: %d findings (critical %d, high %d, medium %d, low %d, info %d) \u00b7 platform %s \u00b7 scanned %d \u00b7 skipped %d \u2192 %s\n" % (
                len(report["findings"]), sm["critical"], sm["high"], sm["medium"], sm["low"], sm["info"],
                report["platform"], report["scanned_files"], report["skipped_files"], ", ".join(written)))
    else:
        sys.stdout.write(js if args.json else md)
    return 1 if threshold_hit(report["findings"], args.fail_on) else 0


def cmd_compare(args):
    reps = []
    for path in (args.before, args.after):
        data, rc, msg = _load_json_file(path, "findings")
        if rc:
            sys.stderr.write("error: %s\n" % msg)
            return 2
        if not isinstance(data, dict) or data.get("schema") != SCHEMA:
            sys.stderr.write("error: %s is not a %s report\n" % (path, SCHEMA))
            return 2
        reps.append(data)
    result = compare_reports(reps[0], reps[1])
    if getattr(args, "out", None):
        write_text(args.out, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n" if args.json else compare_markdown(result))
    return 1 if threshold_hit(result["new"], args.fail_on) else 0


def cmd_rules(args):
    rows = [{"rule": r, "category": c, "kind": k, "severity": s, "confidence": conf} for r, c, k, s, conf in RULE_TABLE]
    if args.json:
        sys.stdout.write(json.dumps(rows, indent=2) + "\n")
    else:
        sys.stdout.write("| rule | category | kind | severity | confidence |\n|---|---|---|---|---|\n")
        for r in rows:
            sys.stdout.write("| %s | %s | %s | %s | %s |\n" % (r["rule"], r["category"], r["kind"], r["severity"], r["confidence"]))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="audit.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("scan", help="scan a project tree for design drift (exit 0/1/2)")
    s.add_argument("dir")
    s.add_argument("--contract", help="tokens.json (missing file -> exit 2, malformed -> exit 1); omitted = inventory mode")
    s.add_argument("--profile", help="style-profile.json (intentional_exceptions, anti_patterns, fallbacks)")
    s.add_argument("--platform", choices=PLATFORM_CHOICES, default="auto", help="auto-detect (default) or force one platform group")
    s.add_argument("--format", choices=["json", "md"], help="format of --out (default: by extension, json)")
    s.add_argument("--out", help="write the report to this file")
    s.add_argument("--md", help="also write the markdown report to this file")
    s.add_argument("--fail-on", choices=["critical", "high", "medium", "low", "none"], default="high", help="exit 1 when findings at/above this severity exist (default high)")
    s.add_argument("--tolerance", type=float, default=None, help="global numeric tolerance for scale matching (default: integers exact, non-integers +/-1)")
    s.add_argument("--near-threshold", type=float, default=12.0, help="colour distance at/below which a colour is a near-duplicate (default 12)")
    s.add_argument("--exclude", action="append", help="fnmatch glob on the relative path to skip (repeatable)")
    s.add_argument("--primary", action="append", help="fnmatch glob marking primary screens (repeatable)")
    s.add_argument("--max-files", type=int, default=20000, help="stop after this many scannable files (default 20000)")
    s.add_argument("--json", action="store_true", help="print JSON to stdout instead of markdown")
    s.set_defaults(func=cmd_scan)
    c = sub.add_parser("compare", help="compare two findings.json files (exit 0/1/2)")
    c.add_argument("before")
    c.add_argument("after")
    c.add_argument("--fail-on", choices=["critical", "high", "medium", "low", "none"], default="high")
    c.add_argument("--out", help="also write the comparison JSON to this file (parent dirs created)")
    c.add_argument("--json", action="store_true", help="print the comparison as JSON")
    c.set_defaults(func=cmd_compare)
    r = sub.add_parser("rules", help="print the rule table")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_rules)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_usage(sys.stderr)
        return 2
    try:
        return args.func(args)
    except Exception as e:  # never a traceback for the user: one error line, exit 2
        sys.stderr.write("error: %s: %s\n" % (e.__class__.__name__, e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
