"""Unit + CLI tests for vd.py (profile builder, init, page, validate). Offline; every write goes to tmp_path."""

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
FIXTURES = SCRIPTS / "tests" / "fixtures"
VALID = FIXTURES / "profile-valid.json"
REFERENCE = FIXTURES / "reference-analysis-valid.json"
SEED = FIXTURES / "seed-design-system.json"
STYLE = "japanese-cute-puzzle"
EXPECTED_FILES = {"MASTER.md", "style-profile.json", "tokens.json", "component-catalog.md", "asset-guidelines.md",
                  "interaction-guidelines.md", "visual-qa-checklist.md", "CHANGELOG.md", "pages"}


def load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(*args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / "vd.py")] + [str(a) for a in args],
                          capture_output=True, text=True, cwd=str(cwd), timeout=90)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def vd():
    return load_module("vd.py", "vd_under_test")


@pytest.fixture
def profile():
    return json.loads(VALID.read_text(encoding="utf-8"))


@pytest.fixture
def initialised(tmp_path):
    """A fresh design-system folder built from the valid fixture; returns (project_root, ds_dir)."""
    proc = run_cli("init", "--profile", VALID, "--output-dir", ".", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    return tmp_path, tmp_path / "design-system" / "onet-garden"


# ============================================================================ unit

@pytest.mark.parametrize("name,expected", [("Onet Garden", "onet-garden"), ("../../etc", "etc"), ("!!!", "default"), ("A_b-C 9", "a_b-c-9")])
def test_vd_u20_safe_slug_matches_orchestrator(vd, name, expected):
    assert vd.safe_slug(name) == expected
    repo = next((p for p in SCRIPTS.parents if (p / "src" / "ui-ux-pro-max" / "scripts" / "design_system.py").is_file()), None)
    if repo is None:
        pytest.skip("orchestrator source not present (installed copy)")
    import ast
    import re as _re
    tree = ast.parse((repo / "src" / "ui-ux-pro-max" / "scripts" / "design_system.py").read_text(encoding="utf-8"))
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "safe_slug")
    namespace = {"re": _re}
    exec(compile(ast.Module(body=[func], type_ignores=[]), "design_system.safe_slug", "exec"), namespace)
    assert namespace["safe_slug"](name) == vd.safe_slug(name)


def test_vd_u21_style_route_builds_valid_profile(vd):
    row = vd.vd_core.row_by_id("styles", STYLE)
    p = vd.build_profile_from_style(row, ["mobile-ios"])
    assert vd.validate_profile(p) == []
    assert p["schema"] == "vdp/1" and p["style"]["id"] == STYLE
    assert p["sources"][0] == {"type": "catalog", "ref": "visual-styles.csv#%s" % STYLE}
    assert p["product"]["kind"] == "game" and p["typography"]["display"] == "Fredoka"
    assert set(p["palette"]["seeds"]) >= {"brand", "secondary", "accent", "neutral"}


def test_vd_u22_genre_route_uses_default_styles(vd):
    genre = vd.vd_core.row_by_id("genres", "onet-animal-puzzle")
    p = vd.build_profile_from_genre(genre, ["mobile-android"])
    first = vd.vd_core.split_list(genre["Default Styles"], ";")[0]
    assert p["style"]["id"] == first and p["product"]["kind"] == "game" and p["product"]["genre"] == "onet-animal-puzzle"
    assert {s["type"] for s in p["sources"]} == {"genre", "catalog"}
    assert vd.validate_profile(p) == []


def test_vd_u23_genre_with_unknown_default_style_raises(vd):
    with pytest.raises(LookupError) as exc:
        vd.build_profile_from_genre({"Genre ID": "x", "Default Styles": "nope", "Kind": "game"}, ["web"])
    assert "nope" in str(exc.value)


def test_vd_u24_reference_route_sources_confidence_unknowns(vd):
    analysis = json.loads(REFERENCE.read_text(encoding="utf-8"))
    base = vd.build_profile_from_style(vd.vd_core.row_by_id("styles", "reference-derived-custom"), ["mobile-android"], kind="game")
    p = vd.build_profile_from_reference(analysis, "reference-analysis.json", base)
    assert p["sources"][0]["type"] == "reference-analysis" and p["sources"][0]["ref"] == "reference-analysis.json"
    assert set(p["sources"][0]["roles"]) == {"color", "shapes", "buttons", "hud", "typography", "layout", "icons"}
    assert p["style"]["confidence"] == "high"
    for item in analysis["not_derivable"]:
        assert any(item in u for u in p["unknowns"])
    assert vd.validate_profile(p) == []


def test_vd_u25_reference_rule_targets_map(vd):
    analysis = json.loads(REFERENCE.read_text(encoding="utf-8"))
    base = vd.build_profile_from_style(vd.vd_core.row_by_id("styles", "reference-derived-custom"), ["mobile-android"], kind="game")
    p = vd.build_profile_from_reference(analysis, "ra.json", base)
    assert p["shape"]["radius_class"] == "xl" and p["shape"]["silhouette"] == "pill"
    assert "button.primary" in p["components"] and p["palette_strategy"].startswith("Pastel")
    assert p["typography"]["display"] == "heavy rounded sans"
    assert any("family not identified" in u for u in p["unknowns"])
    assert p["palette"]["seeds"]["brand"] == "#7ED3B2" and p["palette"]["seeds"]["accent"] == "#FF8A3D"
    assert p["intentional_exceptions"][0]["scope"] == "home"


def test_reference_with_style_overrides_only_owned_roles(vd):
    analysis = json.loads(REFERENCE.read_text(encoding="utf-8"))
    analysis["references"][0]["roles"] = ["color"]
    base = vd.build_profile_from_style(vd.vd_core.row_by_id("styles", STYLE), ["mobile-ios"])
    p = vd.build_profile_from_reference(analysis, "ra.json", base, owned_only=True)
    assert p["shape"]["radius_class"] == base["shape"]["radius_class"]
    assert p["palette_strategy"] != base["palette_strategy"]
    assert any("not applied" in u for u in p["unknowns"])


def test_reference_wrong_schema_raises_input_error(vd, profile):
    with pytest.raises(vd.InputError) as exc:
        vd.build_profile_from_reference({"schema": "vdp/1"}, "x.json", profile)
    assert "vdp-reference-analysis/1" in str(exc.value)


def test_vd_u26_seed_fills_gaps_only(vd):
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    styled = vd.build_profile_from_style(vd.vd_core.row_by_id("styles", STYLE), ["mobile-ios"])
    merged = vd.apply_seed(styled, seed)
    assert merged["typography"]["display"] == "Fredoka"
    assert merged["palette"]["seeds"]["brand"] == styled["palette"]["seeds"]["brand"]
    assert merged["palette"]["seeds"]["danger"] == seed["design_system"]["colors"]["destructive"].upper()
    assert {"type": "design-system-seed", "ref": "search.py --design-system --json"} in merged["sources"]
    assert merged["shape"] == styled["shape"] and merged["rendering"] == styled["rendering"]
    custom = vd.build_profile_from_style(vd.vd_core.row_by_id("styles", "reference-derived-custom"), ["web"])
    assert vd.apply_seed(custom, seed)["typography"]["display"] == seed["design_system"]["typography"]["heading"]


def test_vd_u27_validate_required_keys(vd):
    msgs = vd.validate_profile(json.loads((FIXTURES / "profile-missing-required.json").read_text()))
    assert any(m.startswith("shape") for m in msgs)
    p = json.loads(VALID.read_text())
    del p["product"]["platforms"]
    assert any("product.platforms" in m for m in vd.validate_profile(p))


def test_vd_u28_validate_enums(vd):
    msgs = vd.validate_profile(json.loads((FIXTURES / "profile-bad-enum.json").read_text()))
    assert any(m.startswith("shape.radius_class") and "pill" in m for m in msgs)
    assert any(m.startswith("motion.class") and "bouncy" in m for m in msgs)


def test_vd_u29_validate_platform_subset(vd):
    msgs = vd.validate_profile(json.loads((FIXTURES / "profile-bad-platform.json").read_text()))
    assert any("watch" in m for m in msgs)


def test_vd_u30_u31_validate_sources_and_confidence(vd, profile):
    profile["sources"] = [{"type": "research", "ref": "asset-guidelines.md#provenance:Button state model"}]
    assert vd.validate_profile(profile) == []
    profile["sources"] = [{"type": "web", "ref": "x"}]
    assert any("sources[0].type" in m for m in vd.validate_profile(profile))
    profile = json.loads(VALID.read_text())
    profile["style"]["confidence"] = "medium"
    assert any("style.confidence" in m for m in vd.validate_profile(profile))
    profile["_partial"] = True
    assert any("_partial" in m for m in vd.validate_profile(profile))


def test_vd_u32_fixture_validates(vd, profile):
    assert vd.validate_profile(profile) == []


def test_vd_u38_render_master_has_sections_and_no_placeholders(vd, profile):
    tokens = vd.derive_tokens(profile)
    text = vd.render_master(profile, tokens, component_count=3)
    assert text.splitlines()[0].startswith("<!-- generated-by: visual-direction")
    assert "**LOGIC:**" in text and STYLE in text
    for heading in vd.MASTER_H2:
        assert "## %s" % heading in text, heading
    assert "{{" not in text and "}}" not in text


def test_vd_u39_render_page_skeleton(vd):
    text = vd.render_page_skeleton("shop", "promo layout", "Onet Garden")
    assert "Shop Page Overrides" in text and "promo layout" in text and "## Overrides" in text
    for heading in ("Identity", "Token Summary", "QA Criteria", "Anti-Patterns (Do NOT Use)"):
        assert "## %s" % heading not in text


def test_vd_u40_page_copies_master(vd, profile):
    master = vd.render_master(profile, vd.derive_tokens(profile), 3)
    assert vd.page_copies_master(master, master) is True
    lines = master.splitlines()
    lines[12] = "changed line one"
    lines[20] = "changed line two"
    assert vd.page_copies_master("\n".join(lines), master) is True
    skeleton = vd.render_page_skeleton("shop", "promo") + "\n".join(
        "| component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | reason %d |" % i for i in range(5))
    assert vd.page_copies_master(skeleton, master) is False


def test_render_template_blocks_and_vars(vd):
    tpl = "Hi {{name}}\n{{#items}}- {{.}}\n{{/items}}{{#rows}}| {{a}} | {{b}} |\n{{/rows}}"
    out = vd.render_template(tpl, {"name": "X", "items": ["p", "q"], "rows": [{"a": 1, "b": 2}]})
    assert out == "Hi X\n- p\n- q\n| 1 | 2 |\n"


def test_vd_u41_changelog_append_only(vd, profile, tmp_path):
    vd.init_design_system(profile, tmp_path)
    vd.init_design_system(profile, tmp_path, force=True)
    text = (tmp_path / "design-system" / "onet-garden" / "CHANGELOG.md").read_text(encoding="utf-8")
    heads = [l for l in text.splitlines() if l.startswith("## ")]
    assert len(heads) == 2 and all(vd.CHANGELOG_HEAD_RE.match(h) for h in heads)
    assert "--force" in heads[1]


def test_init_invalid_profile_writes_nothing(vd, tmp_path):
    bad = json.loads((FIXTURES / "profile-bad-enum.json").read_text())
    with pytest.raises(vd.InputError):
        vd.init_design_system(bad, tmp_path)
    assert not (tmp_path / "design-system").exists()


def test_catalog_rows_filtered_by_kind_and_style_modifier(vd, profile):
    rows = vd.catalog_rows_for(profile)
    assert rows and all(r["Applies To"] in ("game", "both") for r in rows)
    text = vd.render_component_catalog(profile, rows)
    assert "### `button.primary`" in text and "Style modifier (reference)" in text and "### `nav.tabs`" not in text


# ============================================================================ CLI: search

def test_vd_c01_c02_styles_text_and_json(tmp_path):
    proc = run_cli("styles", "japanese cute puzzle", cwd=tmp_path)
    assert proc.returncode == 0 and STYLE in proc.stdout and "Japanese Cute Puzzle" in proc.stdout
    proc = run_cli("styles", "japanese cute puzzle", "--json", cwd=tmp_path)
    data = json.loads(proc.stdout)
    assert data["count"] >= 1 and data["results"][0]["Style ID"] == STYLE and "_score" in data["results"][0]


def test_vd_c03_styles_no_match_exits_0(tmp_path):
    proc = run_cli("styles", "qqqq zzzz", cwd=tmp_path)
    assert proc.returncode == 0 and "No results" in proc.stdout
    data = json.loads(run_cli("styles", "qqqq zzzz", "--json", cwd=tmp_path).stdout)
    assert data["count"] == 0 and data["results"] == []


def test_vd_c04_styles_n_and_family(tmp_path):
    data = json.loads(run_cli("styles", "cute casual game", "-n", "2", "--json", cwd=tmp_path).stdout)
    assert len(data["results"]) <= 2
    data = json.loads(run_cli("styles", "game", "--family", "anime", "--json", cwd=tmp_path).stdout)
    assert data["results"] and all(r["Family"] == "anime" for r in data["results"])


def test_vd_c05_genres(tmp_path):
    proc = run_cli("genres", "onet animal", cwd=tmp_path)
    assert proc.returncode == 0 and "onet-animal-puzzle" in proc.stdout
    data = json.loads(run_cli("genres", "onet animal", "--json", cwd=tmp_path).stdout)
    assert data["results"][0]["Genre ID"] == "onet-animal-puzzle"


def test_vd_c06_c07_components_kind(tmp_path):
    data = json.loads(run_cli("components", "button", "--kind", "game", "--json", cwd=tmp_path).stdout)
    assert data["count"] >= 1 and all(r["Applies To"] in ("game", "both") for r in data["results"])
    proc = run_cli("components", "button", "--kind", "cobol", cwd=tmp_path)
    assert proc.returncode == 2 and "--kind" in proc.stderr


# ============================================================================ CLI: profile

def test_vd_c08_profile_style(tmp_path):
    proc = run_cli("profile", "--style", STYLE, "--platform", "mobile-ios,mobile-android", "--out", "p.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    p = json.loads((tmp_path / "p.json").read_text())
    assert p["schema"] == "vdp/1" and p["product"]["platforms"] == ["mobile-ios", "mobile-android"]


def test_vd_c09_c10_c11_unknown_ids(tmp_path):
    proc = run_cli("profile", "--style", "japanese-cute-puzzel", "--platform", "mobile-ios", "--out", "p.json", cwd=tmp_path)
    assert proc.returncode == 1 and STYLE in proc.stderr and not (tmp_path / "p.json").exists() and proc.stdout == ""
    proc = run_cli("profile", "--style", "zzzzzz", "--platform", "mobile-ios", "--out", "p.json", cwd=tmp_path)
    assert proc.returncode == 1 and "no close match" in proc.stderr and not (tmp_path / "p.json").exists()
    proc = run_cli("profile", "--genre", "onet-animal-puzzl", "--platform", "mobile-ios", "--out", "p.json", cwd=tmp_path)
    assert proc.returncode == 1 and "onet-animal-puzzle" in proc.stderr and not (tmp_path / "p.json").exists()


def test_vd_c12_c13_c14_reference_file_errors(tmp_path):
    proc = run_cli("profile", "--reference", "missing.json", "--platform", "web", cwd=tmp_path)
    assert proc.returncode == 2 and "missing.json" in proc.stderr
    proc = run_cli("profile", "--reference", FIXTURES / "profile-not-json.json", "--platform", "web", cwd=tmp_path)
    assert proc.returncode == 1 and "Expecting" in proc.stderr
    proc = run_cli("profile", "--reference", VALID, "--platform", "web", cwd=tmp_path)
    assert proc.returncode == 1 and "vdp-reference-analysis/1" in proc.stderr


def test_vd_c15_c16_c17_c18_usage_errors(tmp_path):
    assert run_cli("profile", "--platform", "web", cwd=tmp_path).returncode == 2
    proc = run_cli("profile", "--style", STYLE, "--platform", "watch", cwd=tmp_path)
    assert proc.returncode == 2 and "mobile-ios" in proc.stderr
    proc = run_cli("profile", "--style", STYLE, "--platform", "web", "--stack", "cobol", cwd=tmp_path)
    assert proc.returncode == 2 and "flutter" in proc.stderr


def test_vd_c19_profile_with_seed(tmp_path):
    proc = run_cli("profile", "--reference", REFERENCE, "--seed-design-system", SEED, "--platform", "mobile-android", "--out", "p.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    p = json.loads((tmp_path / "p.json").read_text())
    assert any(s["type"] == "design-system-seed" for s in p["sources"])
    assert p["typography"]["display"] == "Kalam" and p["style"]["id"] == "reference-derived-custom"


def test_vd_c20_c43_profile_stdout_and_determinism(tmp_path):
    a = run_cli("profile", "--style", STYLE, "--platform", "mobile-ios", cwd=tmp_path)
    b = run_cli("profile", "--style", STYLE, "--platform", "mobile-ios", cwd=tmp_path)
    assert a.returncode == 0 and json.loads(a.stdout)["style"]["id"] == STYLE
    assert a.stdout == b.stdout


def test_vd_c44_three_routes_validate(tmp_path):
    outs = []
    for args in (("--style", STYLE), ("--genre", "productivity-app"), ("--reference", str(REFERENCE))):
        out = tmp_path / ("%s.json" % args[0].strip("-"))
        proc = run_cli("profile", *args, "--platform", "web", "--out", out, cwd=tmp_path)
        assert proc.returncode == 0, proc.stderr
        outs.append(out)
    for out in outs:
        proc = run_cli("init", "--profile", out, "--output-dir", ".", cwd=tmp_path)
        assert proc.returncode == 0, proc.stderr


def test_profile_accepts_partial_fragment(tmp_path):
    fragment = {"schema": "vdp/1", "_partial": True, "shape": {"radius_class": "pill"}, "unknowns": ["from fragment"]}
    (tmp_path / "frag.json").write_text(json.dumps(fragment))
    proc = run_cli("profile", "--reference", "frag.json", "--style", STYLE, "--platform", "web", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    p = json.loads(proc.stdout)
    assert p["shape"]["radius_class"] == "pill" and "_partial" not in p and "from fragment" in p["unknowns"]


# ============================================================================ CLI: init

def test_vd_c21_c22_init_creates_folder(tmp_path):
    proc = run_cli("init", "--profile", VALID, "--output-dir", ".", "--json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["status"] == "ok" and data["master"] == "created" and data["skipped_files"] == []
    assert set(data) >= {"status", "design_system_dir", "created_files", "skipped_files"}
    ds = tmp_path / "design-system" / "onet-garden"
    assert set(p.name for p in ds.iterdir()) == EXPECTED_FILES
    assert (ds / "pages" / "README.md").is_file()
    original = json.loads(VALID.read_text())
    assert json.loads((ds / "style-profile.json").read_text()) == original
    assert "## Provenance" in (ds / "asset-guidelines.md").read_text(encoding="utf-8")


def test_vd_c23_existing_foreign_master_untouched(tmp_path):
    ds = tmp_path / "design-system" / "onet-garden"
    ds.mkdir(parents=True)
    (ds / "MASTER.md").write_text("# Sentinel master from search.py\n", encoding="utf-8")
    before = sha(ds / "MASTER.md")
    proc = run_cli("init", "--profile", VALID, "--output-dir", ".", cwd=tmp_path)
    assert proc.returncode == 0 and sha(ds / "MASTER.md") == before
    assert "## Visual Direction" in proc.stdout and (ds / "MASTER.visual-direction.md").is_file()
    data = json.loads(run_cli("init", "--profile", VALID, "--output-dir", ".", "--force", "--json", cwd=tmp_path).stdout)
    assert data["master"] == "kept" and sha(ds / "MASTER.md") == before and data["master_snippet"].startswith("---")


def test_vd_c24_rerun_skips_then_force_overwrites_tool_owned(initialised):
    root, ds = initialised
    before = sha(ds / "tokens.json")
    (ds / "tokens.json").write_text("{}", encoding="utf-8")
    data = json.loads(run_cli("init", "--profile", VALID, "--output-dir", ".", "--json", cwd=root).stdout)
    assert "tokens.json" in data["skipped_files"] and (ds / "tokens.json").read_text() == "{}"
    data = json.loads(run_cli("init", "--profile", VALID, "--output-dir", ".", "--force", "--json", cwd=root).stdout)
    assert "tokens.json" in data["overwritten_files"] and sha(ds / "tokens.json") == before
    assert data["master"] == "rewritten"
    heads = [l for l in (ds / "CHANGELOG.md").read_text(encoding="utf-8").splitlines() if l.startswith("## ")]
    assert len(heads) == 3 and "--force" in heads[-1]


def test_vd_c25_c26_init_invalid_or_missing_profile(tmp_path):
    proc = run_cli("init", "--profile", FIXTURES / "profile-bad-enum.json", "--output-dir", ".", cwd=tmp_path)
    assert proc.returncode == 1 and "radius_class" in proc.stderr and not (tmp_path / "design-system").exists()
    assert run_cli("init", "--profile", "nope.json", "--output-dir", ".", cwd=tmp_path).returncode == 2
    (tmp_path / "afile").write_text("x")
    assert run_cli("init", "--profile", VALID, "--output-dir", "afile", cwd=tmp_path).returncode == 2


def test_vd_c27_init_slug_safety(tmp_path, profile):
    profile["project"] = {"name": "../../x", "slug": "../../x"}
    (tmp_path / "p.json").write_text(json.dumps(profile))
    proc = run_cli("init", "--profile", "p.json", "--output-dir", ".", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "design-system" / "x" / "MASTER.md").is_file()
    assert not (tmp_path.parent / "x").exists()


# ============================================================================ CLI: page

def test_vd_c28_c29_c30_page(initialised):
    root, ds = initialised
    proc = run_cli("page", "--dir", ds, "--name", "shop", "--reason", "promo", cwd=root)
    assert proc.returncode == 0 and (ds / "pages" / "shop.md").is_file()
    text = (ds / "pages" / "shop.md").read_text(encoding="utf-8")
    assert "promo" in text and "## Overrides" in text
    assert "vd.py page shop" in (ds / "CHANGELOG.md").read_text(encoding="utf-8")
    before = sha(ds / "pages" / "shop.md")
    proc = run_cli("page", "--dir", ds, "--name", "shop", cwd=root)
    assert proc.returncode == 0 and "skipped" in proc.stdout and sha(ds / "pages" / "shop.md") == before
    data = json.loads(run_cli("page", "--dir", ds, "--name", "shop", "--force", "--json", cwd=root).stdout)
    assert data["created"] is True
    proc = run_cli("page", "--dir", ds, "--name", "../evil", cwd=root)
    assert proc.returncode == 0 and (ds / "pages" / "evil.md").is_file() and not (ds / "evil.md").exists()


def test_vd_c31_page_dir_missing(tmp_path):
    assert run_cli("page", "--dir", "design-system/nope", "--name", "shop", cwd=tmp_path).returncode == 2


# ============================================================================ CLI: validate

def test_vd_c32_validate_fresh_init(initialised):
    root, ds = initialised
    proc = run_cli("validate", "--dir", ds, "--json", cwd=root)
    assert proc.returncode == 0, proc.stdout
    data = json.loads(proc.stdout)
    assert data["status"] == "ok" and data["findings"] == []


def test_vd_c33_c34_validate_flags_page_copy(initialised):
    root, ds = initialised
    master = (ds / "MASTER.md").read_text(encoding="utf-8")
    (ds / "pages" / "home.md").write_text(master, encoding="utf-8")
    proc = run_cli("validate", "--dir", ds, "--json", cwd=root)
    data = json.loads(proc.stdout)
    assert proc.returncode == 1
    assert {"file": "pages/home.md", "rule": "page.copies-master"} in [{"file": f["file"], "rule": f["rule"]} for f in data["findings"]]
    lines = master.splitlines()
    lines[12] = "edited"
    lines[20] = "edited again"
    (ds / "pages" / "home.md").write_text("\n".join(lines), encoding="utf-8")
    assert run_cli("validate", "--dir", ds, cwd=root).returncode == 1


def test_vd_c35_validate_genuine_override_passes_and_restated_rows_fail(initialised, vd):
    root, ds = initialised
    run_cli("page", "--dir", ds, "--name", "shop", "--reason", "promo", cwd=root)
    page = ds / "pages" / "shop.md"
    text = page.read_text(encoding="utf-8").replace(
        "|---|---|---|---|\n", "|---|---|---|---|\n| component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | dense 8x8 grid |\n", 1)
    page.write_text(text, encoding="utf-8")
    assert run_cli("validate", "--dir", ds, cwd=root).returncode == 0
    rows = "".join("| component.card.padding | {primitive.spacing.5} | {primitive.spacing.5} | same %d |\n" % i for i in range(3))
    page.write_text(text.replace("|---|---|---|---|\n", "|---|---|---|---|\n" + rows, 1), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert data["status"] == "error" and any(f["rule"] == "page.copies-master" for f in data["findings"])
    page.write_text(text.replace("component.tile.radius", "semantic.color.primary"), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert any(f["rule"] == "page.semantic-remap" for f in data["findings"])
    page.write_text(text.replace("component.tile.radius", "component.nope.radius"), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert any(f["rule"] == "page.unknown-path" for f in data["findings"])


def test_vd_c36_validate_bad_profile_in_dir(initialised):
    root, ds = initialised
    (ds / "style-profile.json").write_text((FIXTURES / "profile-bad-enum.json").read_text(), encoding="utf-8")
    proc = run_cli("validate", "--dir", ds, "--json", cwd=root)
    data = json.loads(proc.stdout)
    assert proc.returncode == 1 and any("shape.radius_class" in f["message"] for f in data["findings"])


def test_vd_c37_c38_validate_tokens_damage(initialised):
    root, ds = initialised
    tokens = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
    del tokens["semantic"]["color"]["reward"]
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert data["status"] == "error" and any(f["rule"] == "tokens.semantic.color.reward" for f in data["findings"])
    tokens = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
    tokens["semantic"]["color"]["reward"] = {"$value": "{primitive.color.nope}", "$type": "color"}
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert any("primitive.color.nope" in f["message"] for f in data["findings"])


def test_vd_c39_validate_missing_dir_and_missing_file(initialised):
    root, ds = initialised
    assert run_cli("validate", "--dir", "design-system/nope", cwd=root).returncode == 2
    (ds / "tokens.json").unlink()
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert data["status"] == "error" and any(f["message"] == "missing-file: tokens.json" for f in data["findings"])


def test_validate_changelog_and_stale_warnings(initialised):
    root, ds = initialised
    cl = ds / "CHANGELOG.md"
    cl.write_text(cl.read_text(encoding="utf-8") + "\n## yesterday · me · [manual]\n- edited\n", encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert any(f["rule"] == "changelog.malformed" for f in data["findings"])
    cl.write_text(cl.read_text(encoding="utf-8").replace("## yesterday", "## 2026-10-15T10:00:00Z"), encoding="utf-8")
    profile = json.loads((ds / "style-profile.json").read_text(encoding="utf-8"))
    profile["unknowns"].append("edited after init")
    (ds / "style-profile.json").write_text(json.dumps(profile), encoding="utf-8")
    proc = run_cli("validate", "--dir", ds, "--json", cwd=root)
    data = json.loads(proc.stdout)
    assert proc.returncode == 0 and any(f["rule"] == "master.stale" and f["level"] == "warning" for f in data["findings"])


# ============================================================================ CLI: contract-level

@pytest.mark.parametrize("sub,flags", [
    ("styles", ["-n", "--json", "--family"]), ("genres", ["-n", "--json"]), ("components", ["--kind", "--json", "game", "app"]),
    ("profile", ["--style", "--genre", "--reference", "--seed-design-system", "--platform", "--stack", "--audience", "--project", "--out"]),
    ("init", ["--profile", "--output-dir", "--force", "--json"]), ("page", ["--dir", "--name", "--reason", "--json"]),
    ("validate", ["--dir", "--json"]),
])
def test_vd_c40_help_matches_contract(tmp_path, sub, flags):
    proc = run_cli(sub, "--help", cwd=tmp_path)
    assert proc.returncode == 0
    for flag in flags:
        assert flag in proc.stdout, flag


def test_vd_c41_no_args_exits_2(tmp_path):
    proc = run_cli(cwd=tmp_path)
    assert proc.returncode == 2 and "usage" in proc.stderr.lower()


# ============================================================================ fix round regressions

def _analysis(rules, observations=(), palette=(), roles=("color", "shapes", "buttons", "typography", "icons")):
    return {"schema": "vdp-reference-analysis/1",
            "references": [{"id": "ref-1", "path": "refs/a.png", "label": "a", "roles": list(roles), "viewed_by": "model-vision",
                            "screen_type": "home", "provenance": {"owner": "user", "license": "unknown", "note": "synthetic"}}],
            "observations": [dict(o, refs=["ref-1"], evidence="frame", confidence="observed") for o in observations],
            "rules": [dict(r, derived_from=r.get("derived_from", []), confidence=r.get("confidence", "observed"), scope="global") for r in rules],
            "conflicts": [], "not_derivable": [], "palette_observed": list(palette)}


def _custom_base(vd, kind="game"):
    return vd.build_profile_from_style(vd.vd_core.row_by_id("styles", "reference-derived-custom"), ["mobile-android"], kind=kind)


def test_fix1_reference_typography_is_a_classification_not_a_placeholder(vd):
    analysis = json.loads(REFERENCE.read_text(encoding="utf-8"))
    p = vd.build_profile_from_reference(analysis, "ra.json", _custom_base(vd))
    assert p["typography"]["display"] == "heavy rounded sans" and p["typography"]["body"] == "rounded sans"
    assert p["typography"]["display"] not in ("display", "body", "sans-serif")
    assert not any("'sans-serif' recorded" in u for u in p["unknowns"])
    fonts = vd.derive_tokens(p)["primitive"]["fontFamily"]
    assert fonts["display"]["$value"] == "heavy rounded sans" and fonts["body"]["$value"] == "rounded sans"
    bare = vd.build_profile_from_reference(_analysis([{"id": "rule-1", "target": "typography", "statement": "Display text uses a geometric sans; family unknown."}]), "x.json", _custom_base(vd))
    assert bare["typography"]["display"] == "geometric sans"


def test_fix2_style_and_genre_combine(vd, tmp_path):
    proc = run_cli("profile", "--style", STYLE, "--genre", "match-3", "--platform", "mobile-ios", "--out", "p.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    p = json.loads((tmp_path / "p.json").read_text())
    assert p["style"]["id"] == STYLE and p["product"]["genre"] == "match-3" and p["product"]["kind"] == "game"
    assert [s["type"] for s in p["sources"]] == ["genre", "catalog"]
    assert p["genre_profile"]["core_screens"] and p["genre_profile"]["hud_elements"] and p["genre_profile"]["touch_rules"]
    assert vd.validate_profile(p) == []
    proc = run_cli("profile", "--style", STYLE, "--genre", "match-3", "--reference", REFERENCE, "--platform", "mobile-ios", cwd=tmp_path)
    assert proc.returncode == 0 and json.loads(proc.stdout)["sources"][0]["type"] == "reference-analysis"
    proc = run_cli("profile", "--style", "japanese-cute-puzzel", "--genre", "match-3", "--platform", "mobile-ios", "--out", "q.json", cwd=tmp_path)
    assert proc.returncode == 1 and STYLE in proc.stderr and not (tmp_path / "q.json").exists()


def test_fix3a_radius_ladder_from_px_evidence(vd):
    rules = [{"id": "rule-1", "target": "radius", "statement": "Containers use 12px corners; buttons are circular.", "derived_from": ["obs-1"]}]
    obs = [{"id": "obs-1", "category": "shape", "statement": "Card corner radius measures about 14px; primary button is fully rounded."}]
    p = vd.build_profile_from_reference(_analysis(rules, obs), "x.json", _custom_base(vd))
    assert p["shape"]["radius_class"] == "lg" and p["shape"]["silhouette"] == "pill"
    assert vd.radius_class_from_px([2]) == "none" and vd.radius_class_from_px([5, 7]) == "sm" and vd.radius_class_from_px([40]) == "pill"
    words = vd.build_profile_from_reference(_analysis([{"id": "rule-1", "target": "radius", "statement": "Everything is fully rounded (pill)."}]), "x.json", _custom_base(vd))
    assert words["shape"]["radius_class"] == "pill"


def test_fix3b_outline_colour_rules(vd):
    for text, expected in (("2px outline in a light tint of the brand colour", "lighter-tint-of-fill"),
                           ("2px darker shade outline", "darker-shade-of-fill"), ("2px black outline", "contrast-dark")):
        p = vd.build_profile_from_reference(_analysis([{"id": "rule-1", "target": "outline", "statement": text}]), "x.json", _custom_base(vd))
        assert p["shape"]["outline"] == {"width": 2, "color_rule": expected}, text
    p = vd.build_profile_from_reference(_analysis([{"id": "rule-1", "target": "outline", "statement": "2px outline, lighter tint of the fill"}]), "x.json", _custom_base(vd))
    tokens = vd.derive_tokens(p)
    assert tokens["semantic"]["outline"]["colorRule"]["$value"] == "fill.200"
    assert tokens["component"]["button"]["primary"]["outlineColor"]["$value"] == "{primitive.color.brand.200}"


def test_fix3c_palette_surfaces_drive_semantic_colours(vd):
    analysis = json.loads(REFERENCE.read_text(encoding="utf-8"))
    p = vd.build_profile_from_reference(analysis, "ra.json", _custom_base(vd))
    assert p["palette"]["surfaces"] == {"background": "#FFD5E5", "surface": "#FFF3E0", "text": "#5B3A29"}
    assert vd.validate_profile(p) == []
    tokens = vd.derive_tokens(p)
    color = tokens["semantic"]["color"]
    assert color["background"]["$value"] == "#FFD5E5" and color["surface"]["$value"] == "#FFF3E0" and color["text"]["$value"] == "#5B3A29"
    assert vd.vd_tokens.validate_tokens(tokens, p) == []
    text_hue = vd.vd_tokens.hex_to_hsl("#5B3A29")[0]
    neutral_hue = vd.vd_tokens.hex_to_hsl(tokens["primitive"]["color"]["neutral"]["500"]["$value"])[0]
    assert abs(text_hue - neutral_hue) < 3
    p["palette"]["surfaces"]["outline"] = "not-a-hex"
    assert any("palette.surfaces.outline" in m for m in vd.validate_profile(p))


def test_fix3d_accent_derived_from_brand_when_missing(vd):
    palette = [{"hex": "#7ED3B2", "share": 0.3, "role_guess": "primary", "ref": "ref-1"}]
    p = vd.build_profile_from_reference(_analysis([{"id": "rule-1", "target": "palette", "statement": "Mint primary everywhere."}], palette=palette), "x.json", _custom_base(vd))
    assert p["palette"]["seeds"]["accent"] == vd.vd_tokens.ramp("#7ED3B2")["700"]
    assert any("accent colour not observed" in u and "brand.700" in u for u in p["unknowns"])
    observed = json.loads(REFERENCE.read_text(encoding="utf-8"))
    q = vd.build_profile_from_reference(observed, "ra.json", _custom_base(vd))
    assert q["palette"]["seeds"]["accent"] == "#FF8A3D" and not any("accent colour not observed" in u for u in q["unknowns"])


def test_fix3e_anti_patterns_are_negations_not_rule_copies(vd):
    analysis = json.loads(REFERENCE.read_text(encoding="utf-8"))
    p = vd.build_profile_from_reference(analysis, "ra.json", _custom_base(vd))
    statements = {r["statement"] for r in analysis["rules"]}
    assert not (set(p["anti_patterns"]) & statements)
    derived = [a for a in p["anti_patterns"] if a.startswith("Do not")]
    assert derived and "Do not use outline-only or thin-stroke icon sets" in derived
    weak = _analysis([{"id": "rule-1", "target": "icon", "statement": "Icons are filled; no thin strokes.", "confidence": "assumption"}])
    assert not any(a.startswith("Do not") for a in vd.build_profile_from_reference(weak, "x.json", _custom_base(vd))["anti_patterns"])


def test_fix4_token_remap_is_not_drift_but_literals_are(initialised):
    root, ds = initialised
    run_cli("page", "--dir", ds, "--name", "shop", "--reason", "promo", cwd=root)
    page = ds / "pages" / "shop.md"
    skeleton = page.read_text(encoding="utf-8")
    assert "Expires: an ISO date (YYYY-MM-DD) or the word never" in skeleton
    remaps = "".join("| %s | {primitive.radius.xl} | {primitive.radius.%s} | fit %d |\n" % (k, v, i) for i, (k, v) in enumerate(
        (("component.card.radius", "md"), ("component.popup.radius", "lg"), ("component.tile.radius", "sm"))))
    page.write_text(skeleton.replace("|---|---|---|---|\n", "|---|---|---|---|\n" + remaps, 1), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert data["status"] == "ok", data["findings"]
    literals = "| component.card.radius | {primitive.radius.xl} | 13px | odd grid |\n| component.popup.radius | {primitive.radius.xl} | 14px | odd grid |\n"
    page.write_text(skeleton.replace("|---|---|---|---|\n", "|---|---|---|---|\n" + literals, 1), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=root).stdout)
    assert any(f["rule"] == "page.drift-budget" and "radius: 2/1" in f["message"] for f in data["findings"])


def test_fix5_init_creates_missing_output_dir(tmp_path):
    proc = run_cli("init", "--profile", VALID, "--output-dir", "new/nested/project", "--json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "new" / "nested" / "project" / "design-system" / "onet-garden" / "MASTER.md").is_file()


def test_fix6_component_catalog_authoritative_tokens_and_size(vd, tmp_path):
    for args, kind in ((("--style", STYLE, "--genre", "match-3", "--stack", "flutter-flame"), "game"),
                       (("--style", STYLE, "--genre", "match-3"), "game"),
                       (("--genre", "productivity-app", "--stack", "react"), "app")):
        proc = run_cli("profile", *args, "--platform", "mobile-ios,mobile-android", "--project", "P %s %d" % (kind, len(args)), cwd=tmp_path)
        profile = json.loads(proc.stdout)
        text = vd.render_component_catalog(profile, tokens=vd.derive_tokens(profile))
        assert len(text.encode("utf-8")) < 60 * 1024, (kind, len(text))
        assert "Tokens (authoritative, `component.button.primary`)" in text
        assert "Style modifier (reference)" in text
        assert ("### `hud.score`" in text) == (kind == "game") and ("### `nav.tabs`" in text) == (kind == "app")
        assert "radius=16" in text.split("### `button.primary`")[1].split("###")[0] if kind == "game" else True


# ============================================================================ final fix round regressions

TWO_REFS = FIXTURES / "reference-analysis-two-refs.json"
EXAMPLE_B = FIXTURES / "reference-analysis-example-b.json"
SIBLING_RA = SCRIPTS.parent.parent / "reference-analysis" / "scripts" / "reference_analysis.py"
STRUCTURAL_KEYS = ("schema", "project", "product", "style", "shape", "rendering", "palette", "palette_strategy", "iconography",
                   "illustration", "motion", "components", "intentional_exceptions", "principles", "qa_criteria")


def _profile_pair(tmp_path, analysis_path, fragment_path):
    common = ["--platform", "mobile-ios", "--stack", "flutter-flame", "--project", "QA Run"]
    raw = run_cli("profile", "--reference", analysis_path, *common, cwd=tmp_path)
    frag = run_cli("profile", "--reference", fragment_path, *common, cwd=tmp_path)
    assert raw.returncode == 0, raw.stderr
    assert frag.returncode == 0, frag.stderr
    a, b = json.loads(raw.stdout), json.loads(frag.stdout)
    return a, b


def test_final1_fragment_route_honours_fragment_palette_and_shape(vd, tmp_path):
    """Self-contained F-03 regression: a hand-built to-profile fragment keeps its observed surfaces/seeds/shape."""
    fragment = {"schema": "vdp/1", "_partial": True, "style": {"id": "reference-derived-custom", "confidence": "high"},
                "product": {"kind": "app"},
                "sources": [{"type": "reference-analysis", "ref": "analysis.json", "roles": ["color", "shapes", "typography"]}],
                "shape": {"radius_class": "xl", "silhouette": "pill", "outline": {"width": 3, "color_rule": "contrast-dark"}},
                "rendering": {"shading": "soft-cel", "shadow": "hard-offset"},
                "typography": {"display": "heavy-rounded-sans", "body": "regular-humanist-sans", "case": "title"},
                "palette": {"seeds": {"brand": "#8ED6A8", "accent": "#FF6F61"},
                            "observed": [{"hex": "#C9F2DF", "share": 0.4, "role_guess": "background", "ref": "ref-1"},
                                         {"hex": "#FFF6E3", "share": 0.2, "role_guess": "surface", "ref": "ref-1"},
                                         {"hex": "#4A2E22", "share": 0.1, "role_guess": "outline", "ref": "ref-1"},
                                         {"hex": "#8ED6A8", "share": 0.1, "role_guess": "primary", "ref": "ref-1"}]},
                "components": {"button.primary": "pill, thick dark outline"}, "unknowns": ["from fragment"]}
    (tmp_path / "frag.json").write_text(json.dumps(fragment), encoding="utf-8")
    proc = run_cli("profile", "--reference", "frag.json", "--platform", "mobile-ios", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    p = json.loads(proc.stdout)
    assert p["palette"]["surfaces"] == {"background": "#C9F2DF", "surface": "#FFF6E3", "outline": "#4A2E22"}
    assert p["palette"]["seeds"]["brand"] == "#8ED6A8" and p["palette"]["seeds"]["accent"] == "#FF6F61"
    assert p["shape"]["outline"] == {"width": 3, "color_rule": "contrast-dark"} and p["rendering"]["shading"] == "soft-cel"
    assert p["typography"]["display"] == "heavy rounded sans" and p["typography"]["body"] == "regular humanist sans"
    assert p["components"]["button.primary"] == "pill, thick dark outline" and "from fragment" in p["unknowns"]
    assert "_partial" not in p and vd.validate_profile(p) == []
    assert p["product"]["kind"] == "app"
    assert p["sources"][0] == {"type": "reference-analysis", "ref": "analysis.json", "roles": ["color", "shapes", "typography"]}
    tokens = vd.derive_tokens(p)
    assert vd.vd_tokens.resolve_ref(tokens, tokens["semantic"]["color"]["background"]["$value"]) == "#C9F2DF"


@pytest.mark.parametrize("fixture", [TWO_REFS, REFERENCE, EXAMPLE_B], ids=["two-refs", "single-ref", "example-b"])
def test_final1_fragment_and_raw_routes_agree(tmp_path, fixture):
    """F-03: `--reference <to-profile fragment>` == `--reference <raw analysis>`: every structural key identical, including
    typography, product.kind and sources[0].roles; only the tool-written `unknowns` wording may differ."""
    if not SIBLING_RA.is_file():
        pytest.skip("reference-analysis sibling not installed")
    frag = subprocess.run([sys.executable, str(SIBLING_RA), "to-profile", str(fixture), "--out", "frag.json"],
                          capture_output=True, text=True, cwd=str(tmp_path), timeout=60)
    assert frag.returncode == 0, frag.stderr
    a, b = _profile_pair(tmp_path, fixture, tmp_path / "frag.json")
    assert a["typography"] == b["typography"]
    assert a["product"]["kind"] == b["product"]["kind"]
    assert a["sources"][0]["type"] == b["sources"][0]["type"] == "reference-analysis"
    assert a["sources"][0]["roles"] == b["sources"][0]["roles"] and a["sources"][0]["roles"]
    for key in STRUCTURAL_KEYS:
        assert a.get(key) == b.get(key), key
    assert a["anti_patterns"] == b["anti_patterns"]
    if fixture == EXAMPLE_B:
        assert a["product"]["kind"] == "app"
    not_derivable = lambda p: sorted(u for u in p["unknowns"] if u.startswith("not derivable"))
    assert not_derivable(a) == not_derivable(b)
    if fixture == TWO_REFS:
        assert a["palette"]["surfaces"]["background"] == "#C9F2DF" and a["palette"]["surfaces"]["outline"] == "#4A2E22"


def test_final2_body_typography_from_body_observations(vd):
    analysis = _analysis(
        [{"id": "rule-1", "target": "typography", "statement": "Bold rounded sans for display; regular humanist sans for body.", "derived_from": ["obs-6", "obs-7"], "confidence": "high"}],
        [{"id": "obs-6", "category": "typography", "statement": "Titles and HUD numerals are a bold rounded sans in Title Case."},
         {"id": "obs-7", "category": "typography", "statement": "Body copy and captions use a regular weight humanist sans for body text."}])
    p = vd.build_profile_from_reference(analysis, "b.json", _custom_base(vd))
    assert p["typography"]["display"] == "bold rounded sans"
    assert p["typography"]["body"] == "humanist sans"
    assert not any("typography.body classification" in u for u in p["unknowns"])
    no_body = vd.build_profile_from_reference(json.loads(REFERENCE.read_text(encoding="utf-8")), "ra.json", _custom_base(vd))
    assert no_body["typography"]["display"] == "heavy rounded sans" and no_body["typography"]["body"] == "rounded sans"
    assert any(u.startswith("typography.body classification 'rounded sans' inferred from the display family") for u in no_body["unknowns"])
    example_b = json.loads(EXAMPLE_B.read_text(encoding="utf-8"))
    b = vd.build_profile_from_reference(example_b, "reference-analysis.json", _custom_base(vd, kind="app"))
    assert b["typography"]["display"] == "bold rounded geometric sans" and b["typography"]["body"] == "humanist sans"
    assert vd.typography_classes("Heavy rounded sans for titles") == ("heavy rounded sans", "rounded sans", True)
    assert vd.normalise_classification("heavy-rounded-sans") == "heavy rounded sans"
    assert vd.normalise_classification("Fredoka") == "Fredoka"


def test_final3_catalog_border_follows_outline_rule(vd):
    expectations = {}
    for row in vd.vd_core.load_rows("styles"):
        profile = vd.build_profile_from_style(row, ["mobile-ios"])
        tokens = vd.derive_tokens(profile)
        color = tokens["semantic"]["color"]
        border = vd.vd_tokens.resolve_ref(tokens, color["border"]["$value"])
        bg = vd.vd_tokens.resolve_ref(tokens, color["background"]["$value"])
        rule = profile["shape"]["outline"]["color_rule"]
        assert border.upper() != "#BFBFBF", row["Style ID"]
        assert "outline" not in profile["palette"]["surfaces"], row["Style ID"]
        dark = vd.vd_tokens.rel_lum(bg) < 0.18
        if rule == "darker-shade-of-fill":
            if dark:
                assert color["border"]["$value"] == "{primitive.color.neutral.700}", row["Style ID"]
            else:
                h, s, l = vd.vd_tokens.hex_to_hsl(bg)
                assert border == vd.vd_tokens.hsl_to_hex(h, s, max(l - 12, 5)), row["Style ID"]
        elif rule == "lighter-tint-of-fill":
            assert color["border"]["$value"] == "{primitive.color.brand.200}", row["Style ID"]
        expectations[row["Style ID"]] = border
    assert expectations["japanese-cute-puzzle"] == "#FFDDAC"
    assert expectations["dark-fantasy-game-ui"] == vd.derive_tokens(vd.build_profile_from_style(
        vd.vd_core.row_by_id("styles", "dark-fantasy-game-ui"), ["mobile-ios"]))["primitive"]["color"]["neutral"]["700"]["$value"]


def test_final3_black_only_when_sole_passing_candidate(vd):
    for row in vd.vd_core.load_rows("styles"):
        profile = vd.build_profile_from_style(row, ["mobile-ios"])
        tokens = vd.derive_tokens(profile)
        color = tokens["semantic"]["color"]
        n900 = tokens["primitive"]["color"]["neutral"]["900"]["$value"]
        text = profile["palette"]["surfaces"]["text"]
        notes = tokens["$extensions"]["vdp"]["contrastNotes"]
        for role in ("primary", "secondary", "accent", "success", "warning", "danger", "reward"):
            on_key = "on" + role[0].upper() + role[1:]
            fill = vd.vd_tokens.resolve_ref(tokens, color[role]["$value"])
            others_pass = any(vd.vd_tokens.contrast(fill, c) >= 4.5 for c in (text, n900, "#FFFFFF"))
            if color[on_key]["$value"] == "{primitive.color.black}":
                assert not others_pass, (row["Style ID"], role)
                assert any(n.startswith("%s: on-colour is #000000" % role) for n in notes), (row["Style ID"], role)
            else:
                assert others_pass, (row["Style ID"], role)


def test_final4_negations_are_full_statements(vd):
    out = vd.negations_from_rule("No text below 12px except numerals; never use thin 1px strokes on interactive controls; no gradients; only pill buttons")
    assert out == ["Do not use thin 1px strokes on interactive controls"]
    for line in out:
        assert len(line.split()) - 2 >= 4 and "except" not in line
    p = vd.build_profile_from_reference(json.loads(TWO_REFS.read_text(encoding="utf-8")), "two.json", _custom_base(vd))
    for line in p["anti_patterns"]:
        if line.startswith("Do not"):
            assert len(line.split()) - 2 >= 4 and not line.startswith("Do not deviate"), line


def test_example_b_gold_warning_and_reward_keep_their_hue(vd, tmp_path):
    """Unseeded warning/reward must not turn brown just because the seed text (#9A3412) and white fail on gold."""
    proc = run_cli("profile", "--reference", EXAMPLE_B, "--platform", "mobile-ios", "--stack", "react-native",
                   "--project", "Example B", "--out", "b.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    profile = json.loads((tmp_path / "b.json").read_text(encoding="utf-8"))
    assert profile["palette"]["surfaces"]["text"] == "#9A3412"
    tokens = vd.derive_tokens(profile)
    color = tokens["semantic"]["color"]
    resolve = lambda key: vd.vd_tokens.resolve_ref(tokens, color[key]["$value"])
    default_warning = tokens["primitive"]["color"]["warning"]["500"]["$value"]
    assert default_warning == "#F5A524"
    expected = {"warning": "#F5A524", "reward": "#FFC83D"}  # AD-7: unseeded reward has its own gold seed
    for role in ("warning", "reward"):
        on = resolve("on" + role[0].upper() + role[1:])
        assert resolve(role) == expected[role], role
        on_hex = on
        assert vd.vd_tokens.contrast(expected[role], on_hex) >= 4.5, role
        assert vd.vd_tokens.rel_lum(on) < 0.18, (role, on)
        assert color["on" + role[0].upper() + role[1:]]["$value"] != "{primitive.color.black}"
    notes = tokens["$extensions"]["vdp"]["contrastNotes"]
    assert not any(n.startswith(("warning:", "reward:")) for n in notes)
    walks = [n for n in notes if "darkened" in n]
    assert all(n in profile["unknowns"] for n in walks) and walks
    assert run_cli("init", "--profile", "b.json", "--output-dir", ".", cwd=tmp_path).returncode == 0
    master = (tmp_path / "design-system" / "example-b" / "MASTER.md").read_text(encoding="utf-8")
    unknowns_section = master.split("## Unknowns")[1].split("## Change Log")[0]
    for note in walks:
        assert unknowns_section.count(note) == 1, note


# ============================================================================ art-direction round (QA pass 2)

import re as _re

DECORATIVE_OUTLINED = (("popup", "outlineColor"), ("hud.chip", "outlineColor"), ("progress", "outlineColor"), ("card", "borderColor"))
INTERACTIVE_OUTLINED = (("tile", "outlineColor"), ("button.icon", "outlineColor"))
HEX_RE = _re.compile(r"#[0-9A-Fa-f]{6}")


def _node(tokens, dotted):
    node = tokens["component"]
    for part in dotted.split("."):
        node = node[part]
    return node


def _all_style_tokens(vd):
    for row in vd.vd_core.load_rows("styles"):
        profile = vd.build_profile_from_style(row, ["mobile-ios", "mobile-android"])
        yield row["Style ID"], profile, vd.derive_tokens(profile)


def test_ad2_one_outline_family_for_every_style(vd):
    for style_id, profile, tokens in _all_style_tokens(vd):
        resolve = lambda v: vd.vd_tokens.resolve_ref(tokens, v)
        decorative = resolve(tokens["semantic"]["color"]["border"]["$value"])
        interactive = resolve(tokens["semantic"]["color"]["borderInteractive"]["$value"])
        explicit = profile["shape"]["outline"].get("secondary_button") == "primary"
        sets = {"decorative": set(), "interactive": set()}
        groups = (("decorative", decorative, DECORATIVE_OUTLINED),
                  ("interactive", interactive, INTERACTIVE_OUTLINED + ((("button.secondary", "outlineColor"),) if not explicit else ())))
        for name, expected, members in groups:
            for comp, key in members:
                ref = _node(tokens, comp)[key]["$value"]
                if ref == "transparent":
                    continue
                assert resolve(ref) == expected, (style_id, name, comp, ref)
                sets[name].add(resolve(ref))
            assert len(sets[name]) <= 1, (style_id, name, sets[name])
        if explicit:
            assert _node(tokens, "button.secondary")["outlineColor"]["$value"].startswith(("{semantic.color.primary}", "{primitive.color.brand.")), style_id
        primary_outline = _node(tokens, "button.primary")["outlineColor"]["$value"]
        assert primary_outline in ("transparent", "{semantic.color.border}") or primary_outline.startswith("{primitive.color.brand."), (style_id, primary_outline)
        for comp in ("popup", "tile", "hud.chip", "card", "progress", "button.icon"):
            for key in ("outlineColor", "borderColor"):
                ref = _node(tokens, comp).get(key, {}).get("$value", "")
                assert not _re.match(r"\{primitive\.color\.(brand|accent|secondary)\.", ref), (style_id, comp, key, ref)


def test_ad2_secondary_primary_outline_only_when_style_says_so(vd):
    explicit = {row["Style ID"] for row in vd.vd_core.load_rows("styles") if vd.SECONDARY_PRIMARY_OUTLINE_RE.search(row["Button Rule"])}
    assert explicit == {"japanese-cute-puzzle", "japanese-casual-game"}
    p = vd.build_profile_from_style(vd.vd_core.row_by_id("styles", "cute-animal-onet"), ["web"])
    assert "secondary_button" not in p["shape"]["outline"]
    assert _node(vd.derive_tokens(p), "button.secondary")["outlineColor"]["$value"] == "{semantic.color.borderInteractive}"


def test_ad3_pressed_state_distinct_and_within_ramp(vd):
    steps = vd.vd_tokens.STEPS
    for style_id, profile, tokens in _all_style_tokens(vd):
        resolve = lambda v: vd.vd_tokens.resolve_ref(tokens, v)
        primary = _node(tokens, "button.primary")
        hover_ref = resolve_chain_ref(tokens, primary["bgHover"]["$value"])
        pressed_ref = resolve_chain_ref(tokens, primary["bgPressed"]["$value"])
        fill_ref = resolve_chain_ref(tokens, primary["bg"]["$value"])
        for ref in (hover_ref, pressed_ref, fill_ref):
            assert ref.startswith("{primitive.color.brand."), (style_id, ref)
        step_of = lambda ref: steps.index(ref.strip("{}").split(".")[-1])
        if step_of(fill_ref) <= steps.index("600"):
            # pressed stays fill + 2 (AD-3); hover moves one step either way so the default label keeps passing
            assert step_of(pressed_ref) == step_of(fill_ref) + 2, style_id
            assert abs(step_of(hover_ref) - step_of(fill_ref)) == 1, style_id
        pressed = resolve(primary["bgPressed"]["$value"])
        outline = resolve(primary["outlineColor"]["$value"])
        hover = resolve(primary["bgHover"]["$value"])
        assert len({resolve(primary["bg"]["$value"]), hover, pressed} | ({outline} if outline != "transparent" else set())) == (4 if outline != "transparent" else 3), style_id
        shadow_hexes = {h.upper() for h in HEX_RE.findall(resolve(primary["shadow"]["$value"]))}
        assert pressed != outline and pressed.upper() not in shadow_hexes, (style_id, pressed, outline, shadow_hexes)
        secondary = _node(tokens, "button.secondary")
        sec_pressed = resolve(secondary["bgPressed"]["$value"])
        assert sec_pressed != resolve(secondary["outlineColor"]["$value"]), style_id
        assert sec_pressed.upper() not in {h.upper() for h in HEX_RE.findall(resolve(secondary["shadow"]["$value"]))}, style_id
        dark_surface = vd.vd_tokens.rel_lum(resolve(secondary["bg"]["$value"])) < 0.18
        assert resolve_chain_ref(tokens, secondary["bgPressed"]["$value"]) == ("{primitive.color.brand.800}" if dark_surface else "{primitive.color.brand.100}"), style_id


def resolve_chain_ref(tokens, value):
    """Follow semantic aliases down to the primitive reference (not the hex)."""
    while value.startswith("{semantic."):
        node = tokens
        for part in value.strip("{}").split("."):
            node = node[part]
        value = node["$value"]
    return value


def test_ad3_interaction_steps_never_collide(vd):
    for step in vd.vd_tokens.STEPS:
        hover, pressed, edge = vd.vd_tokens.interaction_steps(step)
        assert len({step, hover, pressed, edge}) == 4, step


def test_ad4_progress_never_overshoots_entrances_may(vd, profile):
    for cls in ("static", "snappy", "soft", "bouncy", "dramatic"):
        p = json.loads(json.dumps(profile))
        p["motion"] = {"class": cls, "duration_scale": None}
        tokens = vd.derive_tokens(p)
        fill = vd.vd_tokens.resolve_ref(tokens, tokens["component"]["progress"]["fillEasing"]["$value"])
        assert tokens["component"]["progress"]["fillEasing"]["$value"] in ("{primitive.easing.standard}", "{primitive.easing.enter}")
        assert not vd.vd_tokens.bezier_overshoots(fill), (cls, fill)
        assert not vd.vd_tokens.bezier_overshoots(tokens["primitive"]["easing"]["standard"]["$value"]), cls
    bouncy = vd.vd_tokens.EASING["bouncy"]
    assert vd.vd_tokens.bezier_overshoots(bouncy["enter"]) and vd.vd_tokens.bezier_overshoots(bouncy["emphasized"])


@pytest.mark.parametrize("width", [-3, float("nan"), float("inf"), True])
def test_low_outline_width_rejected(vd, profile, width):
    profile["shape"]["outline"]["width"] = width
    assert any(m.startswith("shape.outline.width") for m in vd.validate_profile(profile))


def test_low_outline_width_nan_via_cli(tmp_path):
    text = VALID.read_text(encoding="utf-8").replace('"width": 3', '"width": NaN', 1)
    assert "NaN" in text
    (tmp_path / "p.json").write_text(text, encoding="utf-8")
    proc = run_cli("init", "--profile", "p.json", "--output-dir", ".", cwd=tmp_path)
    assert proc.returncode == 1 and "shape.outline.width" in proc.stderr


def test_low_force_backs_up_hand_edited_master(initialised):
    root, ds = initialised
    master = ds / "MASTER.md"
    assert "; body-hash: " in master.read_text(encoding="utf-8").splitlines()[0]
    data = json.loads(run_cli("init", "--profile", VALID, "--output-dir", ".", "--force", "--json", cwd=root).stdout)
    assert data["backups"] == [] and not list(ds.glob("MASTER.md.bak-*"))
    master.write_text(master.read_text(encoding="utf-8") + "\n- hand edit: keep the tile radius at lg\n", encoding="utf-8")
    proc = run_cli("init", "--profile", VALID, "--output-dir", ".", "--force", "--json", cwd=root)
    data = json.loads(proc.stdout)
    assert proc.returncode == 0 and len(data["backups"]) == 1 and data["backups"][0].startswith("MASTER.md.bak-")
    backup = ds / data["backups"][0]
    assert "hand edit: keep the tile radius at lg" in backup.read_text(encoding="utf-8")
    assert "hand edit" not in master.read_text(encoding="utf-8")
    assert "backup (hand-edited MASTER.md)" in (ds / "CHANGELOG.md").read_text(encoding="utf-8")
    master.write_text(master.read_text(encoding="utf-8") + "\nedit two\n", encoding="utf-8")
    text = run_cli("init", "--profile", VALID, "--output-dir", ".", "--force", cwd=root).stdout
    assert "backup: hand edits to the tool-written MASTER.md were kept in MASTER.md.bak-" in text


def test_validate_rejects_hand_edited_2_to_1_pressed_label(initialised):
    root, ds = initialised
    tokens = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
    button = tokens["component"]["button"]["primary"]
    button["bgPressed"] = {"$value": "#9A9A9A", "$type": "color"}
    button["fgPressed"] = {"$value": "#E0E0E0", "$type": "color"}  # ~2:1
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    proc = run_cli("validate", "--dir", ds, "--json", cwd=root)
    data = json.loads(proc.stdout)
    assert proc.returncode == 1 and data["status"] == "error"
    assert any("button.primary.fgPressed" in f["message"] and "(< 4.5)" in f["message"] for f in data["findings"])


def test_validate_warns_on_weak_interactive_boundary(initialised):
    root, ds = initialised
    tokens = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
    tokens["component"]["tile"]["outlineColor"] = {"$value": "#F6F6F6", "$type": "color"}
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    proc = run_cli("validate", "--dir", ds, "--json", cwd=root)
    data = json.loads(proc.stdout)
    assert proc.returncode == 0
    assert any(f["level"] == "warning" and f["rule"] == "contrast.interactive-boundary" and "tile.outlineColor" in f["message"] for f in data["findings"])


def test_hover_keeps_default_label_and_no_black_hover_labels(vd):
    for style_id, profile, tokens in _all_style_tokens(vd):
        resolve = lambda v: vd.vd_tokens.resolve_ref(tokens, v)
        primary = _node(tokens, "button.primary")
        default_label = resolve(primary["fg"]["$value"])
        hover = resolve(primary["bgHover"]["$value"])
        assert "fgHover" not in primary or primary["fgHover"]["$value"] != "{primitive.color.black}", style_id
        if "fgHover" not in primary:
            assert vd.vd_tokens.contrast(default_label, hover) >= 4.5, (style_id, default_label, hover)
        assert hover != resolve(primary["bg"]["$value"]) and hover != resolve(primary["bgPressed"]["$value"]), style_id
        assert tokens["semantic"]["color"]["primaryHover"]["$value"].startswith("{primitive.color.brand."), style_id


def test_validate_errors_on_weak_focus_ring(initialised):
    root, ds = initialised
    tokens = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
    bg = vd_resolve(tokens, tokens["semantic"]["color"]["background"]["$value"])
    tokens["semantic"]["color"]["focusRing"] = {"$value": bg, "$type": "color"}
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    proc = run_cli("validate", "--dir", ds, "--json", cwd=root)
    data = json.loads(proc.stdout)
    assert proc.returncode == 1 and any("focusRing" in f["message"] and "(< 3)" in f["message"] for f in data["findings"])


def test_validate_warns_on_dark_page_edge(tmp_path):
    proc = run_cli("profile", "--style", "dark-fantasy-game-ui", "--platform", "web", "--stack", "react", "--project", "Dark", "--out", "p.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert run_cli("init", "--profile", "p.json", "--output-dir", ".", cwd=tmp_path).returncode == 0
    ds = tmp_path / "design-system" / "dark"
    assert json.loads(run_cli("validate", "--dir", ds, "--json", cwd=tmp_path).stdout)["findings"] == []
    tokens = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
    tokens["component"]["button"]["primary"]["outlineColor"] = {"$value": "#51111A", "$type": "color"}  # darker than the fill
    (ds / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    data = json.loads(run_cli("validate", "--dir", ds, "--json", cwd=tmp_path).stdout)
    assert any(f["level"] == "warning" and "button.primary.outlineColor" in f["message"] and "dark background" in f["message"] for f in data["findings"])


def vd_resolve(tokens, value):
    while isinstance(value, str) and value.startswith("{"):
        node = tokens
        for part in value.strip("{}").split("."):
            node = node[part]
        value = node["$value"]
    return value
