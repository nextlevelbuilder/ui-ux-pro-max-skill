"""Unit + CLI tests for vd_tokens.py (deterministic VDP -> tokens.json). Offline; writes only to tmp_path."""

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
FIXTURES = SCRIPTS / "tests" / "fixtures"
SKILL_DIR = SCRIPTS.parent
GENERATOR = SKILL_DIR.parent / "design-system" / "scripts" / "generate-tokens.cjs"
REQUIRED_GROUPS = ("color", "spacing", "radius", "outline", "shadow", "fontSize", "lineHeight", "iconSize",
                   "touchTarget", "duration", "easing", "zIndex", "opacity")
REQUIRED_COLORS = ("primary", "onPrimary", "secondary", "onSecondary", "accent", "onAccent", "background", "surface",
                   "surfaceElevated", "border", "overlay", "text", "textMuted", "success", "warning", "danger", "reward")


def load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script)] + [str(a) for a in args],
                          capture_output=True, text=True, cwd=str(cwd), timeout=60)


@pytest.fixture(scope="module")
def vt():
    return load_module("vd_tokens.py", "vd_tokens_under_test")


@pytest.fixture
def profile():
    return json.loads((FIXTURES / "profile-valid.json").read_text(encoding="utf-8"))


def leaves(node, prefix=()):
    if isinstance(node, dict):
        if "$value" in node:
            yield prefix, node
            return
        for k, v in node.items():
            if not k.startswith("$"):
                for item in leaves(v, prefix + (k,)):
                    yield item


# ---------------------------------------------------------------- colour maths and ramps

def test_ramp_is_monotonic_and_keeps_seed(vt):
    r = vt.ramp("#f48fb1")
    assert r["500"] == "#F48FB1"
    lums = [vt.rel_lum(r[s]) for s in vt.STEPS]
    assert lums == sorted(lums, reverse=True)


def test_ramp_neutral_keeps_tint(vt):
    r = vt.ramp("#7D7470")
    h500 = vt.hex_to_hsl(r["500"])[0]
    h200 = vt.hex_to_hsl(r["200"])[0]
    assert abs(h500 - h200) < 2


def test_pick_fill_walks_darker_until_contrast(vt):
    ramp = vt.ramp("#F03131")
    step, ref, ratio = vt.pick_fill(ramp, "600", "#111111")
    assert ratio >= 4.5
    assert vt.STEPS.index(step) >= vt.STEPS.index("600")
    pastel = vt.pick_fill(vt.ramp("#F48FB1"), "500", "#2E2A32")
    assert pastel[1] == "{primitive.color.neutral.900}" and pastel[2] >= 4.5


@pytest.mark.parametrize("stack,platforms,unit", [
    ("flutter-flame", ["mobile-ios"], "logical"),
    ("react", ["mobile-ios"], "px"),
    ("swiftui", ["mobile-ios"], "pt"),
    ("jetpack-compose", ["mobile-android"], "dp"),
    (None, ["mobile-ios"], "pt"),
    (None, ["mobile-ios", "mobile-android"], "dp"),
    ("other", ["web"], "px"),
])
def test_platform_unit(vt, stack, platforms, unit):
    assert vt.platform_unit({"product": {"stack": stack, "platforms": platforms}}) == unit


def test_dim_formatting(vt):
    assert vt.dim(0, "px") == "0"
    assert vt.dim(16, "logical") == "16"
    assert vt.dim(16, "dp") == "16dp"


# ---------------------------------------------------------------- derivation

def test_vd_u33_layers_groups_colors_states(vt, profile):
    tokens = vt.derive_tokens(profile)
    assert set(k for k in tokens if not k.startswith("$")) == {"primitive", "semantic", "component"}
    assert set(REQUIRED_GROUPS) <= set(tokens["primitive"])
    assert set(REQUIRED_COLORS) <= set(tokens["semantic"]["color"])
    assert set(tokens["semantic"]["state"]) == {"hover", "pressed", "focus", "disabled"}
    for path, leaf in leaves(tokens):
        assert isinstance(leaf["$value"], str), path
        assert "$type" in leaf, path


def test_vd_u34_references_resolve_without_cycles(vt, profile):
    tokens = vt.derive_tokens(profile)
    for path, leaf in leaves(tokens):
        resolved = vt.resolve_ref(tokens, leaf["$value"])
        assert not vt.is_reference(resolved), path


def test_vd_u35_extensions(vt, profile):
    ext = vt.derive_tokens(profile)["$extensions"]["vdp"]
    assert {"platformUnit", "minTouchTarget", "motionClass", "generatedFrom"} <= set(ext)
    assert ext["generatedFrom"] == profile["style"]["id"]
    assert ext["platformUnit"] == "logical" and ext["minTouchTarget"] == 48 and ext["motionClass"] == "bouncy"


def test_vd_u37_duration_by_class_with_reward_and_ambient(vt, profile):
    values = {}
    for cls in ("static", "snappy", "soft", "bouncy", "dramatic"):
        p = json.loads(json.dumps(profile))
        p["motion"] = {"class": cls, "duration_scale": None}
        d = vt.derive_tokens(p)["primitive"]["duration"]
        assert set(d) == {"instant", "fast", "base", "slow", "reveal", "reward", "ambient"}
        values[cls] = dict((k, int(v["$value"][:-2])) for k, v in d.items())
    assert all(v == 0 for v in values["static"].values())
    assert values["snappy"]["base"] < values["bouncy"]["base"] < values["dramatic"]["base"]
    assert values["bouncy"]["reward"] == 750 and values["bouncy"]["ambient"] == 2500


def test_duration_scale_overrides_class_row(vt, profile):
    profile["motion"]["duration_scale"] = {"fast": 99}
    d = vt.derive_tokens(profile)["primitive"]["duration"]
    assert d["fast"]["$value"] == "99ms" and d["base"]["$value"] == "200ms"


def test_derivation_is_deterministic(vt, profile):
    assert vt.dumps(vt.derive_tokens(profile)) == vt.dumps(vt.derive_tokens(profile))


def test_supports_dark_adds_dark_layer_and_dark_first_background(vt, profile):
    profile["palette_strategy"] = "neutral base, supports-dark"
    tokens = vt.derive_tokens(profile)
    assert "dark" in tokens and "background" in tokens["dark"]["semantic"]["color"]
    profile["palette_strategy"] = "dark moody base"
    tokens = vt.derive_tokens(profile)
    assert tokens["semantic"]["color"]["background"]["$value"] == "{primitive.color.neutral.900}"
    assert "dark" not in tokens


def test_double_clay_component_shadow_uses_fill_edge_step(vt, profile):
    """AD-3: the hard shadow uses the fill's edge step (+3), never the pressed step (+2)."""
    tokens = vt.derive_tokens(profile)
    brand = tokens["primitive"]["color"]["brand"]
    shadow = tokens["component"]["button"]["primary"]["shadow"]["$value"]
    assert brand["800"]["$value"] in shadow and brand["700"]["$value"] not in shadow
    profile["rendering"]["shadow"] = "glow"
    assert "rgba" in vt.derive_tokens(profile)["primitive"]["shadow"]["md"]["$value"]


@pytest.mark.parametrize("text,kind", [
    ("none", "none"), ("hard offset plus soft blur", "double-clay"), ("1px hard offset", "hard-offset"),
    ("subtle ambient", "soft-ambient"), ("neon glow", "glow"), ("whatever", "none"), ("offset-soft", "offset-soft"),
])
def test_normalize_shadow_kind(vt, text, kind):
    assert vt.normalize_shadow_kind(text) == kind


# ---------------------------------------------------------------- seeds

def test_seeds_from_catalog_and_design_system_and_palette(vt):
    cat = vt.seeds_from_catalog("#FF8FAB;#7ED6C4;#FFD23F;#FFF6E9;#FFFFFF;#4A3B5C")
    assert cat["brand"] == "#FF8FAB" and cat["accent"] == "#FFD23F" and vt.is_hex(cat["neutral"])
    assert vt.seeds_from_catalog("#FF8FAB;#7ED6C4") == {}
    ds = json.loads((FIXTURES / "seed-design-system.json").read_text(encoding="utf-8"))
    got = vt.seeds_from_design_system(ds)
    assert got["brand"] == ds["design_system"]["colors"]["primary"].upper() and "danger" in got
    pal = vt.seeds_from_palette_observed([
        {"hex": "#111111", "share": 0.1, "role_guess": "primary"},
        {"hex": "#222222", "share": 0.3, "role_guess": "primary"},
        {"hex": "#FF8A3D", "share": 0.2, "role_guess": "cta"},
    ])
    assert pal["brand"] == "#222222" and pal["accent"] == "#FF8A3D"


def test_resolve_seeds_precedence(vt):
    profile = {"palette": {"seeds": {"brand": "#ABCDEF", "bogus": "#000000"}}}
    seeds = vt.resolve_seeds(profile, {"brand": "#111111", "accent": "#222222"})
    assert seeds["brand"] == "#ABCDEF" and seeds["accent"] == "#222222"
    assert seeds["warning"] == vt.DEFAULT_WARNING and "bogus" not in seeds


# ---------------------------------------------------------------- validation

def test_validate_tokens_accepts_derived_and_flags_damage(vt, profile):
    tokens = vt.derive_tokens(profile)
    assert vt.validate_tokens(tokens, profile) == []
    broken = json.loads(json.dumps(tokens))
    broken["semantic"]["color"]["primary"]["$value"] = "{primitive.color.nope}"
    assert any("primitive.color.nope" in e for e in vt.validate_tokens(broken, profile))
    broken = json.loads(json.dumps(tokens))
    del broken["semantic"]["color"]["reward"]
    assert any(e.startswith("tokens.semantic.color.reward") for e in vt.validate_tokens(broken, profile))
    broken = json.loads(json.dumps(tokens))
    broken["primitive"]["spacing"]["0"]["$value"] = 0
    assert any("must be a string" in e for e in vt.validate_tokens(broken, profile))
    broken = json.loads(json.dumps(tokens))
    broken["$extensions"]["vdp"]["generatedFrom"] = "other-style"
    assert any("generatedFrom" in e for e in vt.validate_tokens(broken, profile))


# ---------------------------------------------------------------- generator compatibility (contract §4.2)

def test_vd_u36_tokens_consumable_by_generate_tokens_cjs(vt, profile, tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    if not GENERATOR.is_file():
        pytest.skip("design-system sibling not installed: %s" % GENERATOR)
    (tmp_path / "tokens.json").write_text(vt.dumps(vt.derive_tokens(profile)), encoding="utf-8")
    proc = subprocess.run([node, str(GENERATOR), "--config", "tokens.json", "-o", "out.css"],
                          capture_output=True, text=True, cwd=str(tmp_path), timeout=60)
    assert proc.returncode == 0, proc.stderr
    css = (tmp_path / "out.css").read_text(encoding="utf-8")
    assert "--primitive-color-brand-500:" in css and "--primitive-duration-reward:" in css
    assert "[object Object]" not in css and "undefined" not in css


# ---------------------------------------------------------------- CLI

def test_cli_writes_tokens(tmp_path):
    proc = run_cli("vd_tokens.py", "--profile", FIXTURES / "profile-valid.json", "--out", "tokens.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / "tokens.json").read_text(encoding="utf-8"))
    assert "primitive" in data and "semantic" in data and "component" in data


def test_cli_missing_profile_exits_2_and_malformed_exits_1(tmp_path):
    assert run_cli("vd_tokens.py", "--profile", "nope.json", "--out", "t.json", cwd=tmp_path).returncode == 2
    proc = run_cli("vd_tokens.py", "--profile", FIXTURES / "profile-not-json.json", "--out", "t.json", cwd=tmp_path)
    assert proc.returncode == 1 and "JSON" in proc.stderr


def test_fix3c_surfaces_textmuted_contrast_and_dark_background(vt, profile):
    profile["palette"]["surfaces"] = {"background": "#FFD5E5", "surface": "#FFF3E0", "text": "#5B3A29", "outline": "#C98FA6"}
    tokens = vt.derive_tokens(profile)
    color = tokens["semantic"]["color"]
    assert color["border"]["$value"] == "#C98FA6" and color["background"]["$value"] == "#FFD5E5"
    muted = vt.resolve_ref(tokens, color["textMuted"]["$value"])
    assert vt.contrast(muted, "#FFD5E5") >= 4.5 and vt.validate_tokens(tokens, profile) == []
    assert tokens["$extensions"]["vdp"]["surfaces"]["text"] == "#5B3A29"
    profile["palette"]["surfaces"] = {"background": "#101418", "text": "#F5F5F5"}
    dark = vt.derive_tokens(profile)["semantic"]["color"]
    assert dark["text"]["$value"] == "#F5F5F5" and dark["textMuted"]["$value"] == "{primitive.color.neutral.300}"


def test_fix2_2_pick_fill_and_on_rule(vt):
    ramp = vt.ramp("#FF6B6B")
    candidates = [("#2F4A3A", "#2F4A3A"), ("{primitive.color.neutral.900}", "#111111"), ("{primitive.color.white}", "#FFFFFF")]
    step, ref, ratio, walked = vt.pick_fill_and_on(ramp, "500", candidates, [("{primitive.color.black}", "#000000")])
    assert step == "500" and walked is None and ratio >= 4.5 and ref != "{primitive.color.black}"
    # black only as a last resort: #2F6BFF fails for the seed text, neutral.900 and white
    ramp = vt.ramp("#2F6BFF")
    step, ref, ratio, walked = vt.pick_fill_and_on(ramp, "500", [("#111827", "#111827"), ("{primitive.color.white}", "#FFFFFF")], [("{primitive.color.black}", "#000000")])
    assert step == "500" and ref == "{primitive.color.black}" and walked is None
    # nothing passes and no last resort -> the fill walks toward the opposite luminance and the walk is reported
    step, ref, ratio, walked = vt.pick_fill_and_on(ramp, "500", [("{primitive.color.white}", "#FFFFFF")])
    assert walked is not None and walked[0] == "#2F6BFF" and vt.rel_lum(walked[1]) < vt.rel_lum("#2F6BFF") and ratio >= 4.5


def test_fix2_2_contrast_notes_surface_in_tokens_and_master(vt, profile):
    profile["palette"]["seeds"]["brand"] = "#2F6BFF"
    profile["palette"]["surfaces"] = {"background": "#FFFFFF", "surface": "#F5F7FA", "text": "#777777"}
    tokens = vt.derive_tokens(profile)
    assert tokens["semantic"]["color"]["onPrimary"]["$value"] == "{primitive.color.black}"
    notes = tokens["$extensions"]["vdp"]["contrastNotes"]
    assert any(n.startswith("primary: on-colour is #000000 because it is the only candidate") for n in notes)
    assert not any(n.startswith("primary: fill") for n in notes)
    assert vt.surfaces_from_catalog("#FF8FAB;#7ED6C4;#FFD23F;#FFF6E9;#FFFFFF;#4A3B5C") == {"background": "#FFF6E9", "surface": "#FFFFFF", "text": "#4A3B5C"}
    assert vt.derive_outline_surface({"surface": "#FFFFFF", "text": "#4A3B5C"}, "contrast-dark") == "#4A3B5C"
    assert vt.derive_outline_surface({"surface": "#FFFFFF"}, "none") is None


def test_seeded_status_colour_keeps_fill_unseeded_walks(vt, profile):
    profile["palette"]["surfaces"] = {"background": "#FFFFFF", "surface": "#FFFFFF", "text": "#4A3B5C"}
    profile["palette"]["seeds"].pop("success", None)
    walked = vt.derive_tokens(profile)
    assert walked["semantic"]["color"]["success"]["$value"] != "{primitive.color.success.600}"
    assert walked["semantic"]["color"]["onSuccess"]["$value"] != "{primitive.color.black}"
    assert any(n.startswith("success: built-in status fill darkened") for n in walked["$extensions"]["vdp"]["contrastNotes"])
    profile["palette"]["seeds"]["success"] = "#16A34A"
    seeded = vt.derive_tokens(profile)
    assert seeded["semantic"]["color"]["success"]["$value"] == "{primitive.color.success.600}"
    assert not any(n.startswith("success: built-in") for n in seeded["$extensions"]["vdp"]["contrastNotes"])
    via_cli_seeds = vt.derive_tokens({k: v for k, v in profile.items() if k != "palette"}, {"success": "#16A34A"})
    assert via_cli_seeds["semantic"]["color"]["success"]["$value"] == "{primitive.color.success.600}"



def test_pastel_seed_darkens_muted_not_neon(vt):
    """#FF8FAB (S 100, L 78, C 0.44): the old saturation-keeping ramp gave neon #FF0443 at 700; chroma-preserving gives a muted rose."""
    r = vt.ramp("#FF8FAB")
    assert r["500"] == "#FF8FAB"
    assert r["700"] == "#BA4A66" and r["700"] != "#FF0443"
    _h, s700, _l = vt.hex_to_hsl(r["700"])
    assert s700 < 60
    assert vt.ramp("#FF8FAB")["300"] == vt.ramp("#FF8FAB")["300"]  # deterministic; lighter steps unchanged by this rule
