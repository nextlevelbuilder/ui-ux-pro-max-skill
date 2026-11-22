#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-contained HTML preview of a generated design system.

Writes preview.html with inline CSS (no JS framework, no Tailwind CDN).
Google Fonts are linked when the pairing provides a URL; system-font
fallbacks keep the page readable offline.
"""

from html import escape
import os
import re
import tempfile
from pathlib import Path

from design_system import (
    SEMANTIC_COLOR_ENTRIES,
    _button_outline_text_color,
    _contrast_ratio,
    _palette_is_dark,
    _write_persisted_file,
    safe_slug,
)

_SAFE_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_GOOGLE_FONTS_PREFIXES = (
    "https://fonts.googleapis.com/",
    "https://fonts.gstatic.com/",
)

# Surface / on-surface pairs used for WCAG contrast badges.
_CONTRAST_PAIRS = (
    ("primary", "on_primary"),
    ("secondary", "on_secondary"),
    ("accent", "on_accent"),
    ("background", "foreground"),
    ("card", "card_foreground"),
    ("muted", "muted_foreground"),
    ("destructive", "on_destructive"),
)

_ON_ROLE = {surface: on for surface, on in _CONTRAST_PAIRS}
_ON_ROLE.update({on: surface for surface, on in _CONTRAST_PAIRS})


def _text(value) -> str:
    if value is None:
        return ""
    return escape(str(value), quote=False)


def _attr(value) -> str:
    if value is None:
        return ""
    return escape(str(value), quote=True)


def _css_color(value, fallback=None) -> str:
    raw = (value or "").strip()
    if _SAFE_HEX.match(raw):
        return raw
    if fallback and _SAFE_HEX.match(fallback.strip()):
        return fallback.strip()
    return ""


def _css_font(name: str) -> str:
    cleaned = re.sub(r'["\\]', "", (name or "").strip())
    return cleaned or "sans-serif"


def _google_fonts_href(url: str) -> str:
    raw = (url or "").strip()
    if any(raw.startswith(prefix) for prefix in _GOOGLE_FONTS_PREFIXES):
        return _attr(raw)
    return ""


def _wcag_level(ratio) -> str:
    if ratio is None:
        return ""
    if ratio >= 7:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    return "Fail"


def _format_ratio(ratio) -> str:
    if ratio is None:
        return ""
    return f"{ratio:.2f}:1"


def _is_dark(design_system: dict) -> bool:
    if design_system.get("color_mode") == "dark":
        return True
    colors = design_system.get("colors") or {}
    return _palette_is_dark({"Background": colors.get("background", "")})


def _role_contrast(colors: dict, key: str):
    pair_key = _ON_ROLE.get(key)
    if not pair_key:
        return None
    return _contrast_ratio(colors.get(key, ""), colors.get(pair_key, ""))


def format_preview_html(design_system: dict) -> str:
    """Render a dependency-free HTML page for the generated design system."""
    project = design_system.get("project_name") or "Design system"
    # Detect RTL preview via explicit direction/lang metadata or Arabic script in project_name.
    is_arabic = bool(
        design_system.get("direction") == "rtl"
        or design_system.get("lang") == "ar"
        or re.search(r"[\u0600-\u06FF]", str(project))
    )
    html_lang = "ar" if is_arabic else "en"
    html_dir = ' dir="rtl"' if is_arabic else ""
    eyebrow_spacing = "0" if is_arabic else "0.08em"
    eyebrow_transform = "none" if is_arabic else "uppercase"
    badge_spacing = "0" if is_arabic else "0.04em"
    category = design_system.get("category") or ""
    style = design_system.get("style") or {}
    colors = design_system.get("colors") or {}
    typography = design_system.get("typography") or {}
    effects = design_system.get("key_effects") or ""
    anti_patterns = design_system.get("anti_patterns") or ""
    notes = colors.get("notes") or ""
    heading_font = typography.get("heading") or "sans-serif"
    body_font = typography.get("body") or "sans-serif"
    google_href = _google_fonts_href(typography.get("google_fonts_url") or "")
    dark = _is_dark(design_system)

    css_vars = []
    for _label, key, css_var in SEMANTIC_COLOR_ENTRIES:
        hex_val = _css_color(colors.get(key, ""))
        if hex_val:
            css_vars.append(f"    {css_var}: {hex_val};")

    background = _css_color(colors.get("background"), "#FFFFFF") or "#FFFFFF"
    foreground = _css_color(colors.get("foreground"), "#111111") or "#111111"
    card = _css_color(colors.get("card"), background) or background
    card_fg = _css_color(colors.get("card_foreground"), foreground) or foreground
    primary = _css_color(colors.get("primary"), "#2563EB") or "#2563EB"
    on_primary = _css_color(colors.get("on_primary")) or _css_color(
        colors.get("foreground"), "#FFFFFF"
    ) or "#FFFFFF"
    secondary = _css_color(colors.get("secondary"), primary) or primary
    on_secondary = _css_color(colors.get("on_secondary")) or on_primary
    accent = _css_color(colors.get("accent") or colors.get("cta"), primary) or primary
    on_accent = _css_color(colors.get("on_accent") or colors.get("on_cta")) or on_primary
    destructive = _css_color(colors.get("destructive"), "#DC2626") or "#DC2626"
    on_destructive = _css_color(colors.get("on_destructive")) or "#FFFFFF"
    muted = _css_color(colors.get("muted"), card) or card
    muted_fg = _css_color(colors.get("muted_foreground"), foreground) or foreground
    border = _css_color(colors.get("border"), foreground) or foreground
    ring = _css_color(colors.get("ring"), primary) or primary
    secondary_text = _css_color(_button_outline_text_color(colors), foreground) or foreground

    heading_stack = f'"{_css_font(heading_font)}", system-ui, -apple-system, "Segoe UI", sans-serif'
    body_stack = f'"{_css_font(body_font)}", system-ui, -apple-system, "Segoe UI", sans-serif'

    swatches = []
    for label, key, css_var in SEMANTIC_COLOR_ENTRIES:
        hex_val = _css_color(colors.get(key, ""))
        if not hex_val:
            continue
        ratio = _role_contrast(colors, key)
        pair_key = _ON_ROLE.get(key)
        pair_hex = _css_color(colors.get(pair_key, "")) if pair_key else ""
        level = _wcag_level(ratio)
        ratio_html = ""
        if ratio is not None:
            badge_class = "badge-aaa" if level == "AAA" else "badge-aa" if level == "AA" else "badge-fail"
            pair_label = next(
                (entry[0] for entry in SEMANTIC_COLOR_ENTRIES if entry[1] == pair_key),
                pair_key,
            )
            ratio_html = (
                f'<p class="swatch-contrast">vs {_text(pair_label)} '
                f'<code dir="ltr" style="unicode-bidi:isolate">{_text(pair_hex)}</code>: '
                f'<span dir="ltr" style="unicode-bidi:isolate">{_text(_format_ratio(ratio))}</span> '
                f'<span class="badge {badge_class}" dir="ltr" style="unicode-bidi:isolate">{_text(level)}</span></p>'
            )
        swatches.append(
            f'<li class="swatch">'
            f'<div class="swatch-chip" style="background:{hex_val}" aria-hidden="true"></div>'
            f'<div class="swatch-meta">'
            f'<p class="swatch-role">{_text(label)}</p>'
            f'<p><code dir="ltr" style="unicode-bidi:isolate">{_text(hex_val)}</code> '
            f'<code dir="ltr" style="unicode-bidi:isolate">{_text(css_var)}</code></p>'
            f'{ratio_html}'
            f'</div></li>'
        )

    anti_items = []
    for clause in (anti_patterns.split("+") if anti_patterns else []):
        clause = clause.strip()
        if clause:
            anti_items.append(f"<li>{_text(clause)}</li>")
    if not anti_items:
        anti_items.append("<li>None listed for this system.</li>")

    font_links = ""
    if google_href:
        font_links = (
            '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'  <link rel="stylesheet" href="{google_href}">\n'
        )

    color_scheme = "dark" if dark else "light"
    notes_html = (
        f'<p class="notes">{_text(notes)}</p>' if notes else ""
    )
    effects_html = _text(effects) if effects else "None listed for this system."
    css_vars_block = "\n".join(css_vars)
    swatches_html = "".join(swatches)
    anti_html = "".join(anti_items)

    return f"""<!DOCTYPE html>
<html lang="{html_lang}"{html_dir}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="{color_scheme}">
  <title>{_attr(project)} design system preview</title>
{font_links}  <style>
    :root {{
{css_vars_block}
      --font-heading: {heading_stack};
      --font-body: {body_stack};
    }}
    *, *::before, *::after {{ box-sizing: border-box; }}
    html {{ font-size: 16px; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: var(--font-body);
      background: {background};
      color: {foreground};
      line-height: 1.5;
    }}
    a:focus-visible,
    button:focus-visible,
    input:focus-visible {{
      outline: 3px solid {ring};
      outline-offset: 2px;
    }}
    header, main {{
      width: min(1100px, calc(100% - 2rem));
      margin-inline: auto;
    }}
    header {{
      padding: 2.5rem 0 1.5rem;
      border-bottom: 1px solid {border};
    }}
    .eyebrow {{
      margin: 0 0 0.35rem;
      text-transform: {eyebrow_transform};
      letter-spacing: {eyebrow_spacing};
      font-size: 0.75rem;
      color: {muted_fg};
    }}
    h1, h2, h3, .specimen-heading {{
      font-family: var(--font-heading);
      line-height: 1.2;
      margin: 0 0 0.5rem;
    }}
    html[dir="rtl"] h1, html[dir="rtl"] h2, html[dir="rtl"] h3, html[dir="rtl"] .specimen-heading {{
      letter-spacing: 0;
    }}
    h1 {{ font-size: 2.25rem; }}
    h2 {{ font-size: 1.5rem; }}
    h3 {{ font-size: 1.2rem; }}
    main {{ padding: 2rem 0 4rem; display: grid; gap: 2.5rem; }}
    section {{
      background: {card};
      color: {card_fg};
      border: 1px solid {border};
      border-radius: 12px;
      padding: 1.5rem;
    }}
    .swatches {{
      list-style: none;
      margin: 1rem 0 0;
      padding: 0;
      display: grid;
      gap: 0.75rem;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    }}
    .swatch {{
      display: flex;
      gap: 0.75rem;
      align-items: flex-start;
    }}
    .swatch-chip {{
      width: 3rem;
      height: 3rem;
      border-radius: 8px;
      border: 1px solid {border};
      flex-shrink: 0;
    }}
    .swatch-meta p {{ margin: 0; font-size: 0.9rem; }}
    .swatch-role {{ font-weight: 600; }}
    .swatch-contrast {{ color: {muted_fg}; }}
    code {{ font-size: 0.85em; }}
    .badge {{
      display: inline-block;
      margin-inline-start: 0.35rem;
      padding: 0.05rem 0.4rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: {badge_spacing};
    }}
    .badge-aaa {{ background: {primary}; color: {on_primary}; }}
    .badge-aa {{ background: {muted}; color: {muted_fg}; }}
    .badge-fail {{ background: {destructive}; color: {on_destructive}; }}
    .type-scale {{ display: grid; gap: 0.75rem; }}
    .type-scale p {{ margin: 0; max-width: 42rem; }}
    .btn-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin: 0.75rem 0;
    }}
    .btn {{
      font-family: var(--font-body);
      font-weight: 600;
      font-size: 1rem;
      padding: 12px 24px;
      border-radius: 8px;
      border: 2px solid transparent;
      cursor: pointer;
      transition: opacity 200ms ease, transform 200ms ease, box-shadow 200ms ease;
    }}
    .btn-primary {{ background: {primary}; color: {on_primary}; }}
    .btn-secondary {{
      background: transparent;
      color: {secondary_text};
      border-color: {secondary};
    }}
    .btn-accent {{ background: {accent}; color: {on_accent}; }}
    .btn-destructive {{ background: {destructive}; color: {on_destructive}; }}
    .btn:hover, .btn.is-hover {{
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
      transform: translateY(-1px);
    }}
    .btn:focus-visible, .btn.is-focus {{
      outline: 3px solid {ring};
      outline-offset: 2px;
    }}
    .btn:disabled, .btn.is-disabled {{
      opacity: 0.45;
      cursor: not-allowed;
      transform: none;
    }}
    .state-label {{
      font-size: 0.8rem;
      color: {muted_fg};
      margin: 0.25rem 0 0;
    }}
    .preview-card {{
      background: {card};
      color: {card_fg};
      border: 1px solid {border};
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      max-width: 28rem;
    }}
    .field {{ display: grid; gap: 0.35rem; max-width: 28rem; }}
    .field + .field {{ margin-top: 1rem; }}
    label {{ font-weight: 600; }}
    input[type="text"], input[type="email"] {{
      font: inherit;
      padding: 12px 16px;
      border: 1px solid {border};
      border-radius: 8px;
      background: {background};
      color: {foreground};
    }}
    input[aria-invalid="true"] {{
      border-color: {destructive};
    }}
    .help {{ margin: 0; color: {muted_fg}; font-size: 0.9rem; }}
    .error {{
      margin: 0;
      color: {on_destructive};
      background: {destructive};
      font-size: 0.9rem;
      font-weight: 600;
      padding: 0.4rem 0.6rem;
      border-radius: 6px;
    }}
    .notes {{ color: {muted_fg}; }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
      }}
      .btn:hover, .btn.is-hover {{ transform: none; }}
    }}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">Design system preview</p>
    <h1>{_text(project)}</h1>
    <p>{_text(style.get("name") or "Unspecified style")}{_text(" · " + category if category else "")}</p>
  </header>
  <main>
    <section aria-labelledby="palette-heading">
      <h2 id="palette-heading">Palette</h2>
      {notes_html}
      <ul class="swatches">
        {swatches_html}
      </ul>
    </section>
    <section aria-labelledby="type-heading">
      <h2 id="type-heading">Typography</h2>
      <p class="help">Heading: {_text(heading_font)} · Body: {_text(body_font)}</p>
      <div class="type-scale">
        <p class="specimen-heading" style="font-size:2.5rem">Display · {_text(heading_font)}</p>
        <h3>Heading 2 · {_text(heading_font)}</h3>
        <p>Body copy in {_text(body_font)}. The generated pairing is shown at a readable scale so you can judge hierarchy, weight, and line length before building components. Pack my box with five dozen liquor jugs.</p>
      </div>
    </section>
    <section aria-labelledby="buttons-heading">
      <h2 id="buttons-heading">Buttons</h2>
      <p class="state-label">Default</p>
      <div class="btn-row">
        <button class="btn btn-primary" type="button">Primary</button>
        <button class="btn btn-secondary" type="button">Secondary</button>
        <button class="btn btn-accent" type="button">Accent</button>
        <button class="btn btn-destructive" type="button">Destructive</button>
      </div>
      <p class="state-label">Hover</p>
      <div class="btn-row">
        <button class="btn btn-primary is-hover" type="button">Primary</button>
        <button class="btn btn-secondary is-hover" type="button">Secondary</button>
        <button class="btn btn-accent is-hover" type="button">Accent</button>
        <button class="btn btn-destructive is-hover" type="button">Destructive</button>
      </div>
      <p class="state-label">Focus-visible</p>
      <div class="btn-row">
        <button class="btn btn-primary is-focus" type="button">Primary</button>
        <button class="btn btn-secondary is-focus" type="button">Secondary</button>
        <button class="btn btn-accent is-focus" type="button">Accent</button>
        <button class="btn btn-destructive is-focus" type="button">Destructive</button>
      </div>
      <p class="state-label">Disabled</p>
      <div class="btn-row">
        <button class="btn btn-primary" type="button" disabled>Primary</button>
        <button class="btn btn-secondary" type="button" disabled>Secondary</button>
        <button class="btn btn-accent" type="button" disabled>Accent</button>
        <button class="btn btn-destructive" type="button" disabled>Destructive</button>
      </div>
    </section>
    <section aria-labelledby="card-heading">
      <h2 id="card-heading">Card</h2>
      <article class="preview-card">
        <h3>{_text(project)}</h3>
        <p>A sample card using the generated card surface, border, and type pairing.</p>
        <button class="btn btn-primary" type="button">Continue</button>
      </article>
    </section>
    <section aria-labelledby="form-heading">
      <h2 id="form-heading">Form</h2>
      <form>
        <div class="field">
          <label for="preview-email">Email</label>
          <input id="preview-email" name="email" type="email" autocomplete="email" aria-describedby="preview-email-help">
          <p id="preview-email-help" class="help">Use your work address.</p>
        </div>
        <div class="field">
          <label for="preview-name">Display name</label>
          <input id="preview-name" name="name" type="text" value="Not a valid value" aria-invalid="true" aria-describedby="preview-name-error">
          <p id="preview-name-error" class="error">Enter a display name of at least two characters.</p>
        </div>
      </form>
    </section>
    <section aria-labelledby="style-heading">
      <h2 id="style-heading">Style, effects, anti-patterns</h2>
      <p><strong>Style:</strong> {_text(style.get("name") or "")}</p>
      <p><strong>Key effects:</strong> {effects_html}</p>
      <h3>Anti-patterns</h3>
      <ul>
        {anti_html}
      </ul>
    </section>
  </main>
</body>
</html>
"""


def preview_destination(design_system: dict, persist: bool = False,
                        output_dir: str = None) -> Path:
    """Resolve where preview.html should be written (not used for temp files)."""
    project_name = design_system.get("project_name") or "default"
    slug = safe_slug(project_name)
    if persist:
        base_dir = Path(output_dir) if output_dir else Path.cwd()
        return base_dir / "design-system" / slug / "preview.html"
    if output_dir:
        return Path(output_dir) / "preview.html"
    raise ValueError("preview_destination requires persist or output_dir")


def write_preview_html(design_system: dict, persist: bool = False,
                       output_dir: str = None, force: bool = False) -> dict:
    """Write preview.html. Follows persist path rules and --force semantics.

    With persist: design-system/<slug>/preview.html under output_dir or cwd.
    Without persist: --output-dir/preview.html, or a temp file when output_dir
    is omitted. Existing files are left untouched unless force is True.
    """
    html = format_preview_html(design_system)

    if not persist and not output_dir:
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".html",
            prefix="design-system-preview-", delete=False,
        )
        try:
            handle.write(html)
            handle.flush()
            os.fsync(handle.fileno())
        finally:
            handle.close()
        return {
            "status": "success",
            "preview_file": handle.name,
            "created_files": [handle.name],
        }

    path = preview_destination(design_system, persist=persist, output_dir=output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        _write_persisted_file(path, html, force)
    except FileExistsError:
        return {
            "status": "skipped_exists",
            "preview_file": str(path),
            "created_files": [],
            "message": (
                f"{path} already exists and was not modified. "
                "Re-run with force=True / --force to overwrite."
            ),
        }
    return {
        "status": "success",
        "preview_file": str(path),
        "created_files": [str(path)],
    }
