"""CSV data integrity for data/*.csv (ids, enums, seeds, contrast, cross-references). Read-only."""

import csv
import importlib.util
import re
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
DATA = SCRIPTS.parent / "data"
STYLE_ID, GENRE_ID, COMP_ID = "Style ID", "Genre ID", "Component ID"
GENRE_DEFAULT_STYLES = "Default Styles"
STYLE_SEED_COLORS = "Seed Colors"
ENUMS = {
    ("styles", "Radius Class"): {"none", "sm", "md", "lg", "xl", "pill"},
    ("styles", "Shading"): {"flat", "soft", "soft-cel", "cel", "painterly", "glossy", "clay", "pixel", "realistic"},
    ("styles", "Motion Class"): {"static", "snappy", "soft", "bouncy", "dramatic"},
    ("styles", "Status"): {"active", "experimental", "deprecated"},
    ("genres", "Kind"): {"game", "app"},
    ("components", "Applies To"): {"game", "app", "both"},
}
FILES = {"styles": "visual-styles.csv", "genres": "genre-profiles.csv", "components": "component-catalog.csv"}
ID_COLS = {"styles": STYLE_ID, "genres": GENRE_ID, "components": COMP_ID}
MIN_ROWS = {"styles": 12, "genres": 10, "components": 25}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COMPONENT_ID = re.compile(r"^[a-z][a-z0-9-]*\.[a-z0-9-]+$")  # QA Low: every id carries its group prefix
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
CATALOG_HEADER = ["Component ID", "Name", "Group", "Purpose", "Visual Rules", "Variants", "States", "Interaction",
                  "Platform Notes", "Anti Patterns", "QA Criteria", "Code Reuse Hint", "Applies To"]


def load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows_of(catalog):
    with (DATA / FILES[catalog]).open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return reader.fieldnames, list(reader)


def rel_lum(hx):
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hx[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((rel_lum(a), rel_lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@pytest.fixture(scope="module")
def core():
    return load_module("vd_core.py", "vd_core_data_under_test")


@pytest.fixture(scope="module")
def vd():
    return load_module("vd.py", "vd_data_under_test")


@pytest.mark.parametrize("catalog", sorted(FILES))
def test_csv_01_parses_cleanly(catalog):
    header, rows = rows_of(catalog)
    assert header and all(h.strip() for h in header) and len(set(header)) == len(header)
    for row in rows:
        assert None not in row and None not in row.values(), row.get(ID_COLS[catalog])


@pytest.mark.parametrize("catalog", sorted(FILES))
def test_csv_02_row_counts(catalog):
    assert len(rows_of(catalog)[1]) >= MIN_ROWS[catalog]


@pytest.mark.parametrize("catalog", sorted(FILES))
def test_csv_03_ids_unique_and_well_formed(catalog):
    ids = [r[ID_COLS[catalog]] for r in rows_of(catalog)[1]]
    assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
    pattern = COMPONENT_ID if catalog == "components" else KEBAB
    assert all(pattern.match(i) for i in ids), [i for i in ids if not pattern.match(i)]


def test_csv_04_required_cells_non_empty():
    for catalog, cols in (("styles", (STYLE_ID, "Style Name", "Keywords", "Family", STYLE_SEED_COLORS)),
                          ("genres", (GENRE_ID, "Genre Name", "Keywords", GENRE_DEFAULT_STYLES)),
                          ("components", (COMP_ID, "Name", "Group", "Purpose", "Visual Rules"))):
        for row in rows_of(catalog)[1]:
            for col in cols:
                assert row[col].strip(), (catalog, row[ID_COLS[catalog]], col)


def test_csv_05_enum_columns(core):
    offending = []
    for (catalog, column), allowed in ENUMS.items():
        for row in rows_of(catalog)[1]:
            for value in core.split_list(row[column], "|") or [""]:
                if value not in allowed:
                    offending.append((row[ID_COLS[catalog]], column, value))
    assert offending == []


def test_csv_06_genre_default_styles_resolve(core):
    style_ids = {r[STYLE_ID] for r in rows_of("styles")[1]}
    for row in rows_of("genres")[1]:
        defaults = core.split_list(row[GENRE_DEFAULT_STYLES], ";")
        assert defaults, row[GENRE_ID]
        assert len(defaults) == len(set(defaults)), row[GENRE_ID]
        assert set(defaults) <= style_ids, (row[GENRE_ID], set(defaults) - style_ids)


def test_csv_07_seed_colors_six_valid_hexes_with_contrast():
    for row in rows_of("styles")[1]:
        seeds = [s.strip() for s in row[STYLE_SEED_COLORS].split(";")]
        assert len(seeds) == 6 and all(HEX.match(s) for s in seeds), row[STYLE_ID]
        assert len(set(s.upper() for s in seeds)) > 1, row[STYLE_ID]
        background, text = seeds[3], seeds[5]
        assert contrast(text, background) >= 4.5, (row[STYLE_ID], contrast(text, background))


def test_csv_08_component_header_and_groups():
    header, rows = rows_of("components")
    assert header == CATALOG_HEADER
    assert {"hud", "board", "popup", "reward", "action", "feedback", "navigation"} <= {r["Group"] for r in rows}
    assert all(r["Group"] == "feedback" for r in rows if r[COMP_ID].startswith("progress.")), "CC-8: progress.* belong to feedback"


@pytest.mark.parametrize("catalog", sorted(FILES))
def test_csv_09_no_crlf_or_padding(catalog):
    raw = (DATA / FILES[catalog]).read_bytes()
    assert b"\r" not in raw
    for row in rows_of(catalog)[1]:
        assert row[ID_COLS[catalog]] == row[ID_COLS[catalog]].strip()


def test_csv_10_every_style_id_resolves_via_core(core):
    for row in rows_of("styles")[1]:
        sid = row[STYLE_ID]
        assert core.row_by_id("styles", sid) is not None
        assert core.search("styles", sid)["results"][0][STYLE_ID] == sid


def test_csv_11_every_style_and_genre_builds_a_valid_profile(vd):
    for row in rows_of("styles")[1]:
        profile = vd.build_profile_from_style(row, ["mobile-ios", "mobile-android"])
        assert vd.validate_profile(profile) == [], row[STYLE_ID]
        tokens = vd.derive_tokens(profile)
        assert vd.vd_tokens.validate_tokens(tokens, profile) == [], row[STYLE_ID]
    for row in rows_of("genres")[1]:
        profile = vd.build_profile_from_genre(row, ["web"])
        assert vd.validate_profile(profile) == [], row[GENRE_ID]
        assert profile["product"]["kind"] == row["Kind"]


def test_csv_12_hud_components_cover_genre_hud_elements(core):
    hud_ids = {r[COMP_ID] for r in rows_of("components")[1] if r[COMP_ID].startswith("hud.")}
    assert {"hud.score", "hud.timer", "hud.moves", "hud.currency", "hud.pause-button"} <= hud_ids
    for row in rows_of("genres")[1]:
        assert core.split_list(row["HUD Elements"], ";"), row[GENRE_ID]


def test_csv_13_catalog_source_refs_point_at_existing_ids(vd):
    style_ids = {r[STYLE_ID] for r in rows_of("styles")[1]}
    for row in rows_of("styles")[1]:
        profile = vd.build_profile_from_style(row, ["web"])
        for src in profile["sources"]:
            if src["type"] == "catalog":
                assert src["ref"].split("#", 1)[1] in style_ids


# ---------------------------------------------------------------- fix round 2: catalog surfaces + on-colour rule (all 20 styles)

def _resolved_colors(vd, row):
    profile = vd.build_profile_from_style(row, ["mobile-ios", "mobile-android"])
    tokens = vd.derive_tokens(profile)
    color = tokens["semantic"]["color"]
    return profile, tokens, dict((k, vd.vd_tokens.resolve_ref(tokens, v["$value"])) for k, v in color.items())


def test_fix2_1_catalog_surfaces_are_authoritative_for_every_style(vd):
    for row in rows_of("styles")[1]:
        seeds = [s.strip().upper() for s in row[STYLE_SEED_COLORS].split(";")]
        profile, tokens, resolved = _resolved_colors(vd, row)
        assert profile["palette"]["surfaces"]["background"] == seeds[3], row[STYLE_ID]
        assert resolved["background"] == seeds[3], (row[STYLE_ID], resolved["background"], seeds[3])
        assert resolved["surface"] == seeds[4], row[STYLE_ID]
        assert (rel_lum(resolved["background"]) < 0.18) == (rel_lum(seeds[3]) < 0.18), row[STYLE_ID]
        assert contrast(resolved["text"], resolved["background"]) >= 4.5, row[STYLE_ID]
        assert contrast(resolved["textMuted"], resolved["background"]) >= 4.5, row[STYLE_ID]
        assert tokens["$extensions"]["vdp"]["surfaces"]["text"] == seeds[5], row[STYLE_ID]
        assert vd.vd_tokens.validate_tokens(tokens, profile) == [], row[STYLE_ID]


def test_fix2_2_fills_kept_when_a_candidate_on_colour_passes(vd):
    for row in rows_of("styles")[1]:
        seeds = [s.strip().upper() for s in row[STYLE_SEED_COLORS].split(";")]
        profile, tokens, resolved = _resolved_colors(vd, row)
        neutral900 = tokens["primitive"]["color"]["neutral"]["900"]["$value"]
        candidates = (seeds[5], neutral900, "#FFFFFF", "#000000")
        for index, role in ((0, "primary"), (1, "secondary"), (2, "accent")):
            seed = seeds[index]
            if any(contrast(seed, c) >= 4.5 for c in candidates):
                assert resolved[role] == seed, (row[STYLE_ID], role, resolved[role], seed)
        for role in ("primary", "secondary", "accent", "success", "warning", "danger", "reward"):
            on = resolved["on" + role[0].upper() + role[1:]]
            assert contrast(resolved[role], on) >= 4.5, (row[STYLE_ID], role, resolved[role], on)


def test_status_colours_never_pure_black_when_unseeded(vd):
    """Coordinator decision: built-in success/warning/danger walk darker instead of taking #000000 text."""
    for row in rows_of("styles")[1]:
        profile, tokens, resolved = _resolved_colors(vd, row)
        color = tokens["semantic"]["color"]
        explicit = set((profile.get("palette") or {}).get("seeds") or {}) | set(vd.vd_tokens.seeds_from_catalog(row[STYLE_SEED_COLORS]))
        notes = tokens["$extensions"]["vdp"]["contrastNotes"]
        for role in ("success", "warning", "danger"):
            on_key = "on" + role[0].upper() + role[1:]
            if role not in explicit:
                assert color[on_key]["$value"] != "{primitive.color.black}", (row[STYLE_ID], role)
                start = tokens["primitive"]["color"][role][{"success": "600", "warning": "500", "danger": "600"}[role]]["$value"]
                if resolved[role] != start:
                    assert any(n.startswith("%s: built-in status fill darkened from %s to %s" % (role, start, resolved[role])) for n in notes), (row[STYLE_ID], role)
        for role in ("primary", "secondary", "accent", "success", "warning", "danger", "reward"):
            on = resolved["on" + role[0].upper() + role[1:]]
            assert contrast(resolved[role], on) >= 4.5, (row[STYLE_ID], role, resolved[role], on)


def test_component_ids_renamed_toast_and_tooltip():
    ids = {r[COMP_ID] for r in rows_of("components")[1]}
    assert {"feedback.toast-app", "overlay.tooltip", "feedback.toast"} <= ids
    assert not ({"toast", "tooltip"} & ids)


def test_darker_ramp_steps_preserve_seed_chroma_for_every_style(vd):
    """Pastel seeds darken into muted shades, not neon: the 600-900 steps never exceed the seed's HSL saturation or chroma."""
    vt = vd.vd_tokens
    for row in rows_of("styles")[1]:
        _profile, tokens, _resolved = _resolved_colors(vd, row)
        for ramp_name in ("brand", "secondary", "accent"):
            ramp = tokens["primitive"]["color"][ramp_name]
            seed = ramp["500"]["$value"]
            _h, seed_s, seed_l = vt.hex_to_hsl(seed)
            seed_c = vt.hsl_chroma(seed_s, seed_l)
            # saturation bound on the 700 step (the spec); 0.5 S-point tolerance = 8-bit hex rounding of the derived colour
            _h7, s700, _l7 = vt.hex_to_hsl(ramp["700"]["$value"])
            assert s700 <= seed_s + 0.5, (row[STYLE_ID], ramp_name, s700, seed_s)
            # chroma bound on every darker step (chroma is robust to rounding even at very low L)
            for step in ("600", "700", "800", "900"):
                _h2, s2, l2 = vt.hex_to_hsl(ramp[step]["$value"])
                assert vt.hsl_chroma(s2, l2) <= seed_c + 0.01, (row[STYLE_ID], ramp_name, step)
            assert seed.upper() == [c.upper() for c in row[STYLE_SEED_COLORS].split(";")][("brand", "secondary", "accent").index(ramp_name)]


def test_filled_button_has_no_outline_under_none_or_border_token(vd):
    for row in rows_of("styles")[1]:
        profile, tokens, _resolved = _resolved_colors(vd, row)
        button = tokens["component"]["button"]["primary"]
        rule = profile["shape"]["outline"]["color_rule"]
        if rule in ("none", "border-token"):
            assert button["outlineWidth"]["$value"] == "{primitive.outline.none}", row[STYLE_ID]
            assert button["outlineColor"]["$value"] == "transparent", row[STYLE_ID]
        else:
            assert button["outlineWidth"]["$value"] == "{semantic.outline.control}", row[STYLE_ID]
            assert button["outlineColor"]["$value"] != "transparent", row[STYLE_ID]


# ---------------------------------------------------------------- accessibility round (A-14 … AD-9), all 20 styles

def _all(vd):
    for row in rows_of("styles")[1]:
        profile, tokens, resolved = _resolved_colors(vd, row)
        yield row, profile, tokens, resolved, (lambda v, t=tokens: vd.vd_tokens.resolve_ref(t, v))


def test_a14_primary_label_passes_on_every_state(vd):
    for row, _p, tokens, _r, res in _all(vd):
        button = tokens["component"]["button"]["primary"]
        for bg_key, fg_key in (("bg", "fg"), ("bgHover", "fgHover"), ("bgPressed", "fgPressed")):
            fg = res((button.get(fg_key) or button["fg"])["$value"])
            assert contrast(fg, res(button[bg_key]["$value"])) >= 4.5, (row[STYLE_ID], bg_key, fg)


def test_a15_secondary_label_is_primary_family_and_passes(vd):
    for row, _p, tokens, _r, res in _all(vd):
        secondary = tokens["component"]["button"]["secondary"]
        fg_ref = secondary["fg"]["$value"]
        assert fg_ref == "{semantic.color.primary}" or fg_ref.startswith("{primitive.color.brand."), (row[STYLE_ID], fg_ref)
        for key in ("bg", "bgHover", "bgPressed"):
            assert contrast(res(fg_ref), res(secondary[key]["$value"])) >= 4.5, (row[STYLE_ID], key)


def test_a16_border_interactive_reaches_3_to_1(vd):
    for row, _p, tokens, resolved, _res in _all(vd):
        bi = resolved["borderInteractive"]
        assert contrast(bi, resolved["surface"]) >= 3 and contrast(bi, resolved["background"]) >= 3, (row[STYLE_ID], bi)
        assert tokens["component"]["card"]["borderColor"]["$value"] == "{semantic.color.border}", row[STYLE_ID]


def test_component_state_validator_is_clean_after_generation(vd):
    for row, profile, tokens, _r, _res in _all(vd):
        errors, warnings = vd.vd_tokens.component_state_findings(tokens)
        assert errors == [] and warnings == [], (row[STYLE_ID], errors, warnings)
        assert vd.vd_tokens.validate_tokens(tokens, profile) == [], row[STYLE_ID]


def test_ad6_press_feedback_within_100ms_every_motion_class(vd):
    row = rows_of("styles")[1][0]
    for cls in ("static", "snappy", "soft", "bouncy", "dramatic"):
        profile = vd.build_profile_from_style(row, ["web"])
        profile["motion"] = {"class": cls, "duration_scale": {"fast": 200}}
        tokens = vd.derive_tokens(profile)
        for variant in ("primary", "secondary", "icon"):
            value = vd.vd_tokens.resolve_ref(tokens, tokens["component"]["button"][variant]["pressDuration"]["$value"])
            assert int(value[:-2]) <= 100, (cls, variant, value)


def test_ad7_reward_and_warning_defaults(vd):
    for row, profile, _t, resolved, _res in _all(vd):
        assert "reward" not in (profile["palette"].get("seeds") or {}), row[STYLE_ID]
        assert resolved["reward"] == "#FFC83D" and resolved["warning"] == "#F5A524", row[STYLE_ID]
        assert contrast(resolved["reward"], resolved["onReward"]) >= 4.5 and contrast(resolved["warning"], resolved["onWarning"]) >= 4.5


def test_ad8_selected_tile_outline_and_light_fill(vd):
    for row, _p, tokens, _r, res in _all(vd):
        tile = tokens["component"]["tile"]
        assert tile["bgSelected"]["$value"] == "{primitive.color.brand.100}", row[STYLE_ID]
        assert tile["outlineColorSelected"]["$value"].startswith("{primitive.color.brand."), row[STYLE_ID]
        assert contrast(res(tile["outlineColorSelected"]["$value"]), res(tile["bg"]["$value"])) >= 3, row[STYLE_ID]


def test_ad9_shadows_tinted_unless_style_asks_for_black(vd):
    for row, profile, tokens, _r, res in _all(vd):
        black = profile["rendering"]["shadow_tint"] == "black"
        rule = row["Shadow Rule"].lower()
        if black:
            assert "never colo" in rule or "black" in rule, row[STYLE_ID]
        for path in (("card", "shadow"), ("popup", "shadow")):
            value = res(tokens["component"][path[0]][path[1]]["$value"])
            if not black:
                assert "rgba(0, 0, 0," not in value, (row[STYLE_ID], path, value)
        for key in ("sm", "md", "lg"):
            if not black:
                assert "rgba(0, 0, 0," not in tokens["primitive"]["shadow"][key]["$value"], (row[STYLE_ID], key)


# ---------------------------------------------------------------- QA pass 3 (N3-2, N3-3, tappable HUD capsules)

def test_n3_2_focus_ring_reaches_3_to_1_and_differs_from_states(vd):
    for row, _p, tokens, resolved, res in _all(vd):
        ring = res(tokens["semantic"]["state"]["focus"]["ringColor"]["$value"])
        assert ring == resolved["focusRing"], row[STYLE_ID]
        assert contrast(ring, resolved["background"]) >= 3 and contrast(ring, resolved["surface"]) >= 3, (row[STYLE_ID], ring)
        button = tokens["component"]["button"]["primary"]
        states = {res(button[k]["$value"]) for k in ("bg", "bgHover", "bgPressed")}
        assert ring not in states, (row[STYLE_ID], ring)
        if button["outlineColor"]["$value"] != "transparent":
            assert ring != res(button["outlineColor"]["$value"]), row[STYLE_ID]
        width = res(tokens["semantic"]["state"]["focus"]["ringWidth"]["$value"])
        assert float("".join(ch for ch in width if ch.isdigit() or ch == ".")) >= 2, (row[STYLE_ID], width)


def test_n3_3_filled_control_edge_on_dark_pages(vd):
    """Outlined filled controls on a dark page: edge >= 3:1 vs the page. Without an outline the control is
    identified by its label (>= 4.5:1 on every state, test_a14) — the documented rule."""
    dark_seen = 0
    for row, _p, tokens, resolved, res in _all(vd):
        if rel_lum(resolved["background"]) >= 0.18:
            continue
        dark_seen += 1
        button = tokens["component"]["button"]["primary"]
        if button["outlineColor"]["$value"] == "transparent":
            assert contrast(res(button["fg"]["$value"]), res(button["bg"]["$value"])) >= 4.5, row[STYLE_ID]
            continue
        edge = res(button["outlineColor"]["$value"])
        assert contrast(edge, resolved["background"]) >= 3, (row[STYLE_ID], edge)
        hard = re.match(r"^0 \d+px 0 (#[0-9A-Fa-f]{6}),", res(button["shadow"]["$value"]))
        if hard:  # the double-clay hard layer is an edge too: it must also reach 3:1 against the dark page
            assert contrast(hard.group(1), resolved["background"]) >= 3, (row[STYLE_ID], hard.group(1))
    assert dark_seen >= 5


def test_tappable_hud_capsule_uses_interactive_border(vd):
    for row, _p, tokens, resolved, res in _all(vd):
        hud = tokens["component"]["hud"]
        assert hud["chip"]["outlineColor"]["$value"] != "{semantic.color.borderInteractive}" or row is None
        chip = hud["chipInteractive"]
        assert chip["outlineColor"]["$value"] == "{semantic.color.borderInteractive}", row[STYLE_ID]
        assert chip["outlineWidth"]["$value"] != "{primitive.outline.none}", row[STYLE_ID]
        assert contrast(res(chip["outlineColor"]["$value"]), res(chip["bg"]["$value"])) >= 3, row[STYLE_ID]
