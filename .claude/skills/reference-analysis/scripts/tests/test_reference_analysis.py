"""Unit and CLI tests for scripts/reference_analysis.py (offline, fixtures in-repo).

Synthetic images are generated with Pillow under `pytest.importorskip`; the BLOCKED
path is tested without Pillow in-process (sys.modules['PIL'] = None) and in a
subprocess that injects a fake PIL package raising ImportError.
"""

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "reference_analysis.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SINGLE = FIXTURES / "sample-single-reference.json"
TWO = FIXTURES / "sample-two-references-with-conflict.json"


def load_module():
    spec = importlib.util.spec_from_file_location("reference_analysis_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ra():
    return load_module()


def run_cli(*args, cwd):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True, cwd=str(cwd), timeout=60)


def run_cli_without_pillow(*args, cwd):
    """Poison the PIL import inside the child process (sys.modules['PIL'] = None)."""
    code = ("import sys, runpy; sys.modules['PIL'] = None; sys.modules['PIL.Image'] = None; "
            "sys.argv = [%r] + %r; runpy.run_path(%r, run_name='__main__')"
            % (str(SCRIPT), [str(a) for a in args], str(SCRIPT)))
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=str(cwd), timeout=60)


def run_cli_with_fake_pil(*args, cwd, tmp_path):
    """Subprocess variant: a fake `PIL` package on PYTHONPATH raises ImportError on import."""
    fake = tmp_path / "fakepil" / "PIL"
    fake.mkdir(parents=True, exist_ok=True)
    (fake / "__init__.py").write_text("raise ImportError('fake PIL: Pillow is not installed')\n", encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(tmp_path / "fakepil") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True,
                          cwd=str(cwd), timeout=60, env=env)


def single():
    return json.loads(SINGLE.read_text(encoding="utf-8"))


def two():
    return json.loads(TWO.read_text(encoding="utf-8"))


def write(tmp_path, name, doc):
    p = tmp_path / name
    p.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return p


def codes(errors):
    return [e["code"] for e in errors]


def minimal(ref_ids=("ref-1",), roles=None, viewed_by="model-vision"):
    roles = roles or {}
    return {
        "schema": "vdp-reference-analysis/1",
        "project": "synthetic test document",
        "references": [{"id": r, "path": "refs/%s.png" % r, "label": "screen %s" % r, "roles": roles.get(r, []),
                        "viewed_by": viewed_by, "screen_type": "home",
                        "provenance": {"owner": "user", "license": "unknown"}} for r in ref_ids],
        "observations": [], "rules": [], "conflicts": [], "not_derivable": [], "palette_observed": [],
    }


def make_image(path, size=(100, 100)):
    """100x100 image: pink background, dark right band (40 %), orange block (9 %)."""
    Image = pytest.importorskip("PIL.Image")
    im = Image.new("RGB", size, (255, 213, 229))
    w, h = size
    for x in range(int(w * 0.6), w):
        for y in range(h):
            im.putpixel((x, y), (40, 30, 20))
    for x in range(0, int(w * 0.3)):
        for y in range(int(h * 0.7), h):
            im.putpixel((x, y), (255, 138, 61))
    im.save(str(path))
    return path


# --------------------------------------------------------------------------- unit: validate

def test_ra_u01_valid_single_fixture_passes(ra):
    assert ra.validate_analysis(single()) == []


def test_ra_u02_conflict_fixture_passes_and_strict_flags_open_conflict(ra):
    assert ra.validate_analysis(two()) == []
    strict = ra.validate_analysis(two(), strict=True)
    assert len(strict) == 1 and strict[0]["code"] == "R-CONF-OPEN" and "label case" in strict[0]["message"]


def test_ra_u03_schema_value_named(ra):
    doc = single()
    doc["schema"] = "vdp/1"
    errs = ra.validate_analysis(doc)
    assert codes(errs) == ["R-SCHEMA"] and "vdp-reference-analysis/1" in errs[0]["message"]


def test_ra_u04_role_enum_lists_roles(ra):
    doc = single()
    doc["references"][0]["roles"] = ["colours"]
    errs = ra.validate_analysis(doc)
    msg = [e for e in errs if e["code"] == "R-ROLE-ENUM"]
    assert msg and msg[0]["path"] == "references[0].roles"
    for role in ra.ROLES:
        assert role in msg[0]["message"]


def test_ra_u05_confidence_enum_names_obs_and_value(ra):
    doc = single()
    doc["observations"][0]["confidence"] = "medium"
    errs = [e for e in ra.validate_analysis(doc) if e["code"] == "R-CONF-ENUM"]
    assert errs and "obs-1" in errs[0]["message"] and "medium" in errs[0]["message"]


@pytest.mark.parametrize("section,index,key,bad,code,path", [
    ("references", 0, "viewed_by", "camera", "R-VIEW-ENUM", "references[0].viewed_by"),
    ("references", 0, "screen_type", "lobby", "R-SCREEN-ENUM", "references[0].screen_type"),
    ("observations", 0, "category", "colours", "R-OBS-CAT", "observations[0].category"),
])
def test_ra_u06_enums_name_the_path(ra, section, index, key, bad, code, path):
    doc = single()
    doc[section][index][key] = bad
    errs = [e for e in ra.validate_analysis(doc) if e["code"] == code]
    assert len(errs) == 1 and errs[0]["path"] == path


def test_ra_u07_dangling_obs_ref(ra):
    doc = single()
    doc["observations"][0]["refs"] = ["ref-9"]
    errs = ra.validate_analysis(doc)
    assert any(e["message"] == "obs-1 refers to unknown reference ref-9" for e in errs)


def test_ra_u08_dangling_rule_obs(ra):
    doc = single()
    doc["rules"][0]["derived_from"] = ["obs-99"]
    errs = ra.validate_analysis(doc)
    assert any(e["code"] == "R-RULE-REF" and "obs-99" in e["message"] for e in errs)


def test_ra_u09_duplicate_ids_and_pattern(ra):
    doc = single()
    doc["observations"][1]["id"] = "obs-1"
    assert "R-ID-DUP" in codes(ra.validate_analysis(doc))
    doc = single()
    doc["rules"][0]["id"] = "r1"
    assert "R-ID" in codes(ra.validate_analysis(doc))


def test_ra_u10_two_owners_of_one_role(ra):
    doc = minimal(("ref-1", "ref-2"), roles={"ref-1": ["color"], "ref-2": ["color", "shapes"]})
    errs = ra.validate_analysis(doc)
    assert any(e["code"] == "R-ROLE-1" and e["message"] == "role 'color' owned by ref-1 and ref-2" for e in errs)


def test_ra_u11_rule_confidence_capped_by_observations(ra):
    doc = single()
    doc["rules"][0]["derived_from"] = ["obs-11"]  # obs-11 is an assumption
    errs = [e for e in ra.validate_analysis(doc) if e["code"] == "R-RULE-1"]
    assert errs and "rule-1" in errs[0]["message"] and "assumption" in errs[0]["message"]


def test_ra_u12_rule_never_not_derivable(ra):
    doc = single()
    doc["rules"][0]["confidence"] = "not-derivable"
    assert "R-RULE-ND" in codes(ra.validate_analysis(doc))
    doc = single()
    doc["rules"][0]["derived_from"] = ["obs-12"]  # not-derivable observation
    assert "R-RULE-1" in codes(ra.validate_analysis(doc))


def test_ra_u13_unviewed_reference_cannot_support_observations(ra):
    doc = two()
    doc["references"][1]["viewed_by"] = "none"
    errs = ra.validate_analysis(doc)
    assert any(e["code"] == "R-VIEW-2" and "obs-6" in e["message"] for e in errs)
    warnings = ra.validate(doc)["warnings"]
    assert any(w["code"] == "R-VIEW-1" for w in warnings)


def test_ra_u13b_human_description_capped_at_high(ra):
    doc = two()
    doc["observations"][5]["confidence"] = "observed"  # obs-6 derives only from ref-2 (human-description)
    errs = ra.validate_analysis(doc)
    assert any(e["code"] == "R-VIEW-3" and "obs-6" in e["message"] for e in errs)


def test_ra_u14_palette_hex_and_share(ra):
    doc = single()
    doc["palette_observed"][0]["hex"] = "#GGGGGG"
    doc["palette_observed"][1]["share"] = 1.2
    got = codes(ra.validate_analysis(doc))
    assert got.count("R-PAL-HEX") == 1 and got.count("R-PAL-SHARE") == 1
    doc = single()
    doc["palette_observed"][0]["hex"] = "#ffd5e5"
    res = ra.validate(doc)
    assert res["errors"] == [] and any(w["code"] == "W-HEX-CASE" for w in res["warnings"])


def test_ra_u14b_palette_share_sum_and_role_enum(ra):
    doc = single()
    doc["palette_observed"][0]["share"] = 0.9
    assert "R-PAL-1" in codes(ra.validate_analysis(doc))
    doc = single()
    doc["palette_observed"][0]["role_guess"] = "border"
    assert "R-PAL-ROLE" in codes(ra.validate_analysis(doc))


def test_ra_u14c_conflict_rules(ra):
    doc = two()
    doc["conflicts"][0]["resolution"] = "resolved somehow"
    assert "R-CONF-1" in codes(ra.validate_analysis(doc))
    doc = two()
    doc["references"][0]["roles"].append("typography")  # now the open 'label case' conflict has an owner
    assert "R-CONF-2" in codes(ra.validate_analysis(doc))
    doc = two()
    doc["conflicts"][1]["topic"] = "Panel Corner Radius"
    assert "R-CONF-TOPIC" in codes(ra.validate_analysis(doc))


def test_ra_u14d_motion_observation_needs_sequence(ra):
    doc = single()
    doc["observations"][11]["confidence"] = "observed"  # obs-12 motion on a static image
    doc["observations"][11]["evidence"] = "frame"
    assert "R-OBS-1" in codes(ra.validate_analysis(doc))
    doc["references"][0]["path"] = "refs/home.gif"
    assert "R-OBS-1" not in codes(ra.validate_analysis(doc))


def test_ra_u14e_not_derivable_evidence_and_duplicates(ra):
    doc = single()
    doc["observations"][11]["evidence"] = "static image"
    assert "R-OBS-EVIDENCE" in codes(ra.validate_analysis(doc))
    doc = single()
    doc["not_derivable"].append(" Font Family Names ")
    assert "R-ND-DUP" in codes(ra.validate_analysis(doc))


def test_ra_u14f_target_vocabulary_is_a_warning_not_an_error(ra):
    doc = single()
    doc["rules"][0]["target"] = "nav"
    res = ra.validate(doc)
    assert res["status"] == "OK" and res["errors"] == []
    assert any(w["code"] == "W-TARGET" and "nav" in w["message"] for w in res["warnings"])


def test_ra_u14g_missing_keys_and_non_object(ra):
    doc = single()
    del doc["conflicts"]
    assert "R-KEYS" in codes(ra.validate_analysis(doc))
    assert ra.validate([])["status"] == "FAIL"
    assert ra.validate({"schema": "vdp-reference-analysis/1"})["counts"] == {} or \
        "R-REFS" in codes(ra.validate_analysis({"schema": "vdp-reference-analysis/1"}))


def test_ra_u14h_rule_on_owned_role_from_non_owner_is_an_error(ra):
    doc = two()
    # rule-3 (button.primary -> buttons, owned by ref-2) now derives only from a ref-1 observation
    doc["rules"][2]["derived_from"] = ["obs-2"]
    errs = [e for e in ra.validate_analysis(doc) if e["code"] == "R-RULE-2"]
    assert errs and "rule-3" in errs[0]["message"] and "ref-2" in errs[0]["message"]


def test_topic_to_role_component_first(ra):
    assert ra.topic_to_role("button corner radius") == "buttons"
    assert ra.topic_to_role("panel corner radius") == "shapes"
    assert ra.topic_to_role("label case") == "typography"
    assert ra.topic_to_role("outline colour") == "color"
    assert ra.topic_to_role("reward") is None


# --------------------------------------------------------------------------- unit: merge

def left_right():
    left = minimal(("ref-1",), roles={"ref-1": ["color", "shapes"]})
    left["observations"] = [
        {"id": "obs-1", "category": "shape", "statement": "Panel corner radius: xl class (about 25% of height).",
         "refs": ["ref-1"], "evidence": "cards", "confidence": "observed"},
        {"id": "obs-2", "category": "typography", "statement": "Label case: Title Case on buttons.",
         "refs": ["ref-1"], "evidence": "play button", "confidence": "observed"}]
    left["rules"] = [
        {"id": "rule-1", "target": "radius", "statement": "Panels use xl radius.", "derived_from": ["obs-1"],
         "confidence": "observed", "scope": "global"},
        {"id": "rule-2", "target": "typography", "statement": "Title Case labels.", "derived_from": ["obs-2"],
         "confidence": "observed", "scope": "global"}]
    left["not_derivable"] = ["font family names"]
    left["palette_observed"] = [{"hex": "#FFD5E5", "share": 0.4, "role_guess": "background", "ref": "ref-1"}]
    right = minimal(("ref-2",), roles={"ref-2": ["buttons", "popup"]})
    right["references"][0]["screen_type"] = "popup"
    right["observations"] = [
        {"id": "obs-10", "category": "shape", "statement": "Panel corner radius: md class (about 8% of height).",
         "refs": ["ref-2"], "evidence": "popup panel", "confidence": "observed"},
        {"id": "obs-11", "category": "typography", "statement": "Label case: ALL CAPS on popup buttons.",
         "refs": ["ref-2"], "evidence": "two buttons", "confidence": "high"}]
    right["rules"] = [{"id": "rule-10", "target": "popup", "statement": "Centred panel.", "derived_from": ["obs-10"],
                       "confidence": "observed", "scope": "context:popup"}]
    right["not_derivable"] = ["Font family names", "pressed and disabled states"]
    return left, right


def test_ra_u15_merge_disjoint(ra):
    left, right = left_right()
    merged, warnings = ra.merge_analyses([left, right], names=["left.json", "right.json"])
    assert ra.validate_analysis(merged) == []
    assert [r["id"] for r in merged["references"]] == ["ref-1", "ref-2"]
    ids = [o["id"] for o in merged["observations"]]
    assert len(ids) == len(set(ids))
    assert [s.lower() for s in merged["not_derivable"]] == ["font family names", "pressed and disabled states"]
    topics = {c["topic"]: c["status"] for c in merged["conflicts"]}
    assert topics == {"panel corner radius": "resolved", "label case": "open"}
    resolved = next(c for c in merged["conflicts"] if c["status"] == "resolved")
    assert "ref-1 wins" in resolved["resolution"]
    assert "rule-2" not in [r["id"] for r in merged["rules"]]  # dropped: open conflict, no owner
    assert any("rule-2" in w for w in warnings)


def test_ra_u16_merge_overlapping_role_rejected(ra):
    left, right = left_right()
    right["references"][0]["roles"].append("shapes")
    with pytest.raises(ra.MergeError) as exc:
        ra.merge_analyses([left, right], names=["left.json", "right-overlap.json"])
    msg = str(exc.value)
    assert "shapes" in msg and "ref-1" in msg and "ref-2" in msg and "left.json" in msg and "right-overlap.json" in msg


def test_ra_u16b_merge_id_collision_rejected(ra):
    left, right = left_right()
    right["references"][0]["id"] = "ref-1"
    for o in right["observations"]:
        o["refs"] = ["ref-1"]
    right["references"][0]["roles"] = ["buttons"]
    with pytest.raises(ra.MergeError) as exc:
        ra.merge_analyses([left, right])
    assert "collision" in str(exc.value) and "ref-1" in str(exc.value)


def test_ra_u17_merge_is_pure(ra):
    left, right = left_right()
    before = (copy.deepcopy(left), copy.deepcopy(right))
    ra.merge_analyses([left, right])
    assert (left, right) == before


def test_ra_u17b_merge_roles_override_moves_role_and_resolves(ra):
    left, right = left_right()
    merged, warnings = ra.merge_analyses([left, right], roles={"ref-2": ["typography", "buttons", "popup"]})
    assert ra.role_owners(merged)["typography"] == ["ref-2"]
    assert all(c["status"] == "resolved" for c in merged["conflicts"])
    assert any("dropped rule-2" in w for w in warnings)
    assert "typography" not in merged["references"][0]["roles"]


def test_ra_u17c_merge_downgrades_rule_confidence(ra):
    left, right = left_right()
    left["observations"][0]["confidence"] = "high"
    left["rules"][0]["confidence"] = "high"
    # authored too high relative to a later edit of the observation
    left["observations"][0]["confidence"] = "assumption"
    with pytest.raises(ra.MergeError):  # inputs are validated first: R-RULE-1 makes left invalid
        ra.merge_analyses([left, right])


def test_parse_role_specs(ra):
    assert ra.parse_role_specs(["ref-1:color,shapes", "ref-2:buttons"]) == {"ref-1": ["color", "shapes"], "ref-2": ["buttons"]}
    with pytest.raises(ValueError):
        ra.parse_role_specs(["ref-1:colours"])
    with pytest.raises(ValueError):
        ra.parse_role_specs(["nocolon"])


# --------------------------------------------------------------------------- unit: to-profile

def test_ra_u18_to_profile_fragment_mapping(ra):
    doc = single()
    frag = ra.to_profile_fragment(doc)
    assert frag["schema"] == "vdp/1" and frag["_partial"] is True
    assert frag["sources"][0]["type"] == "reference-analysis"
    assert frag["sources"][0]["roles"] == doc["references"][0]["roles"]
    assert frag["shape"]["radius_class"] == "xl"
    assert frag["palette_strategy"].startswith("Pastel light background")
    assert "button.primary" in frag["components"]
    assert frag["typography"]["display"] == "heavy rounded sans"  # classification string (CC-4)
    assert frag["typography"]["case"] == "title"
    assert frag["iconography"]["style"] == "filled-rounded"
    assert frag["style"]["id"] == "reference-derived-custom" and frag["style"]["confidence"] == "high"
    for entry in doc["not_derivable"]:
        assert "not derivable from references: " + entry in frag["unknowns"]
    assert frag["intentional_exceptions"][0]["scope"] == "home"
    assert frag["palette"]["seeds"] == {"brand": "#7ED3B2", "accent": "#FF8A3D", "neutral": "#5B3A29"}
    assert "Do not use outline-only or thin-stroke icon sets" in frag["anti_patterns"]
    assert 3 <= len(frag["principles"]) <= 5


def test_ra_u18b_assumptions_and_open_conflicts_go_to_unknowns(ra):
    doc = two()
    doc["rules"].append({"id": "rule-7", "target": "shadow", "statement": "Soft 40% black blur under popups.",
                         "derived_from": ["obs-6"], "confidence": "assumption", "scope": "global"})
    frag = ra.to_profile_fragment(doc, style_id="candy-glossy", project="Test Game")
    assert frag["style"]["id"] == "candy-glossy" and frag["style"]["confidence"] == "assumption"
    assert frag["project"] == {"name": "Test Game", "slug": "test-game"}
    assert "assumption (rule-7, assumption): Soft 40% black blur under popups." in frag["unknowns"]
    assert "open conflict on label case between ref-1, ref-2" in frag["unknowns"]
    assert "shadow" not in frag["rendering"]
    assert frag["illustration"]["character_style"].startswith("chibi-proportion mascot")
    assert frag["intentional_exceptions"] and {e["scope"] for e in frag["intentional_exceptions"]} == {"popup", "home"}


def test_ra_u18c_f03_fragment_carries_observed_surfaces_and_distinct_typography(ra):
    """Regression for QA F-03: the fragment route must not lose observed surfaces or the body classification."""
    doc = single()
    frag = ra.to_profile_fragment(doc)
    assert frag["palette"]["surfaces"] == {"background": "#FFD5E5", "surface": "#FFF3E0", "text": "#5B3A29"}
    assert frag["palette"]["surfaces"]["background"] == next(
        p["hex"] for p in doc["palette_observed"] if p["role_guess"] == "background")
    assert frag["palette"]["observed"] == doc["palette_observed"]
    display, body = frag["typography"]["display"], frag["typography"]["body"]
    assert display and body and display != body
    assert display == "heavy rounded sans" and body == "rounded sans"
    assert any("typography.body classification 'rounded sans' inferred" in u for u in frag["unknowns"])


def test_ra_u18d_body_clause_classifies_body_separately(ra):
    doc = minimal(roles={"ref-1": ["typography"]})
    doc["observations"] = [{"id": "obs-1", "category": "typography", "refs": ["ref-1"], "evidence": "headers vs captions",
                            "confidence": "high",
                            "statement": "Rounded geometric sans-serif for display (title, stat numbers, bold), regular "
                                         "weight humanist sans for body/sub-labels."}]
    doc["rules"] = [{"id": "rule-1", "target": "typography", "statement": "Two-family system: rounded display family for "
                     "headings, neutral sans for body.", "derived_from": ["obs-1"], "confidence": "high", "scope": "global"}]
    typo = ra.to_profile_fragment(doc)["typography"]
    assert "rounded" in typo["display"] and "geometric" in typo["display"]
    assert typo["body"] == "humanist sans"


def test_ra_u18e_seed_mapping_matches_vd_and_surfaces_take_outline(ra):
    frag = ra.to_profile_fragment(two())
    assert frag["palette"]["seeds"] == {"brand": "#8ED6A8", "accent": "#FF6F61"}  # outline is never the neutral seed
    assert frag["palette"]["surfaces"] == {"background": "#C9F2DF", "surface": "#FFF6E3", "outline": "#4A2E22"}
    assert ra.to_profile_fragment(minimal()).get("palette") is None  # no palette_observed -> no palette block


def test_ra_u18f_product_kind_hint_matches_vd_rule(ra):
    assert ra.to_profile_fragment(single())["product"] == {"kind": "game"}  # owns the hud role
    app = minimal(roles={"ref-1": ["color", "shapes"]})
    assert ra.to_profile_fragment(app)["product"] == {"kind": "app"}
    app["references"][0]["screen_type"] = "gameplay"
    assert ra.to_profile_fragment(app)["product"] == {"kind": "game"}
    assert "product" not in ra.to_profile_fragment(single(), style_id="japanese-cute-puzzle")


@pytest.mark.parametrize("fixture", [SINGLE, TWO])
def test_ra_c21_fragment_route_matches_raw_route_in_vd(tmp_path, fixture):
    """F-03: `vd.py profile --reference <raw>` and `--reference <to-profile fragment>` agree on derived fields."""
    vd = SCRIPTS.parent.parent / "visual-direction" / "scripts" / "vd.py"
    if not vd.is_file():
        pytest.skip("sibling visual-direction skill not installed")
    r = run_cli("to-profile", fixture, "--out", "frag.json", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    common = ["--platform", "mobile-ios", "--stack", "flutter-flame", "--project", "Equivalence"]
    outs = {}
    for name, ref in (("raw", fixture), ("frag", tmp_path / "frag.json")):
        p = subprocess.run([sys.executable, str(vd), "profile", "--reference", str(ref)] + common + ["--out", name + ".json"],
                           capture_output=True, text=True, cwd=str(tmp_path), timeout=60)
        assert p.returncode == 0, p.stderr
        outs[name] = json.loads((tmp_path / (name + ".json")).read_text(encoding="utf-8"))
    raw, frag = outs["raw"], outs["frag"]
    # data fields derived from the analysis must be identical on both routes (F-03)
    for key in ("shape", "rendering", "iconography", "palette_strategy", "components",
                "intentional_exceptions", "qa_criteria"):
        assert raw.get(key) == frag.get(key), key
    # presentational text shares one formatting convention with vd.py; checked loosely so that
    # wording tweaks on either side do not mask the data checks above
    raw_negations = set(a for a in raw.get("anti_patterns") or [] if a.startswith("Do not"))
    assert raw_negations <= set(frag.get("anti_patterns") or [])
    assert len(frag.get("principles") or []) == len(raw.get("principles") or [])
    for key in ("surfaces", "seeds", "observed"):
        assert raw.get("palette", {}).get(key) == frag.get("palette", {}).get(key), "palette." + key
    assert raw["typography"]["display"] == frag["typography"]["display"]
    assert raw["style"]["confidence"] == frag["style"]["confidence"]


def test_ra_u19_fragment_has_contract_key_shapes(ra):
    frag = ra.to_profile_fragment(single())
    for key in ("schema", "sources", "principles", "shape", "rendering", "typography", "motion",
                "components", "anti_patterns", "qa_criteria", "intentional_exceptions", "unknowns"):
        assert key in frag
    assert frag["shape"]["radius_class"] in {"none", "sm", "md", "lg", "xl", "pill"}
    assert isinstance(frag["components"], dict) and all(isinstance(v, str) for v in frag["components"].values())
    assert frag["sources"][0]["ref"].endswith(".json")


def test_radius_class_heuristic(ra):
    assert ra._radius_class("Two radius classes only: pill for buttons and chips, xl for containers and panels.") == "xl"
    assert ra._radius_class("Cards and panels use the lg radius class.") == "lg"
    assert ra._radius_class("Sharp corners everywhere.") == "none"
    assert ra._radius_class("Radius ladder in px only.") is None


def test_outline_and_shading_heuristics(ra):
    assert ra._outline("All surfaces use a 2px peach outline (light tint of brand), never grey/black") == \
        ({"width": 2, "color_rule": "lighter-tint-of-fill"}, True)
    assert ra._outline("Outline ~2% of element height, darker shade of each fill.") == \
        ({"width": 2, "color_rule": "darker-shade-of-fill"}, False)
    assert ra._outline("Thick dark outline.") == ({"width": 3, "color_rule": "contrast-dark"}, False)
    assert ra._outline("No outline on any element.") == ({"width": 0, "color_rule": "none"}, True)
    assert ra._shading("Flat fill, one soft cel shadow under the chin.") == "soft-cel"
    assert ra._shading("Glossy top-left highlight on every button.") == "glossy"
    assert ra._shading("Flat fills throughout.") == "flat"


def test_safe_slug(ra):
    assert ra.safe_slug("Onet Garden!") == "onet-garden"
    assert ra.safe_slug("") == "default"


# --------------------------------------------------------------------------- unit: extract-colors

def test_ra_u20_extract_colors_synthetic(ra, tmp_path):
    img = make_image(tmp_path / "synth.png")
    res = ra.extract_colors(str(img), k=10, ref_id="ref-1")
    assert res["status"] == "OK" and res["confidence"] == "assumption"
    pal = res["palette_observed"]
    assert res["colors_kept"] == len(pal) == 3
    shares = [p["share"] for p in pal]
    assert shares == sorted(shares, reverse=True)
    assert abs(sum(shares) - 1.0) <= 0.02
    for p in pal:
        assert ra.HEX_RE.match(p["hex"]) and 0 < p["share"] <= 1 and p["ref"] == "ref-1"
        assert p["role_guess"] in ra.ROLE_GUESS
    by_role = {p["role_guess"]: p for p in pal}
    assert abs(by_role["background"]["share"] - 0.51) <= 0.02
    assert ra.rgb_distance(ra.hex_to_rgb(by_role["background"]["hex"]), (255, 213, 229)) <= 8
    assert abs(by_role["text"]["share"] - 0.40) <= 0.02
    assert by_role["accent"]["hex"] and ra.rgb_distance(ra.hex_to_rgb(by_role["accent"]["hex"]), (255, 138, 61)) <= 8
    doc = minimal()
    doc["palette_observed"] = pal
    assert ra.validate_analysis(doc) == []


def test_ra_u20b_extract_colors_alpha_and_transparent(ra, tmp_path):
    Image = pytest.importorskip("PIL.Image")
    im = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    for x in range(25):
        for y in range(50):
            im.putpixel((x, y), (30, 120, 220, 255))
    im.save(str(tmp_path / "half.png"))
    res = ra.extract_colors(str(tmp_path / "half.png"), k=8)
    assert res["status"] == "OK" and len(res["palette_observed"]) == 1
    assert abs(res["palette_observed"][0]["share"] - 1.0) <= 0.02
    Image.new("RGBA", (20, 20), (0, 0, 0, 0)).save(str(tmp_path / "clear.png"))
    res = ra.extract_colors(str(tmp_path / "clear.png"))
    assert res["status"] == "BLOCKED" and res["reason"] == "image-transparent"


def test_ra_u21_extract_colors_without_pillow(ra, monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "PIL", None)
    monkeypatch.setitem(sys.modules, "PIL.Image", None)
    img = tmp_path / "x.png"
    img.write_bytes(b"\x89PNG not really")
    res = ra.extract_colors(str(img))
    assert res == {"status": "BLOCKED", "reason": "pillow-missing", "message": res["message"]}
    assert "Pillow (PIL) is not installed" in res["message"]


def test_ra_u22_extract_colors_unreadable(ra, tmp_path):
    pytest.importorskip("PIL")
    bad = tmp_path / "x.png"
    bad.write_text("not an image", encoding="utf-8")
    res = ra.extract_colors(str(bad))
    assert res["status"] == "BLOCKED" and res["reason"] == "unreadable-image"


def test_guess_roles_is_assumption_only(ra):
    entries = [{"hex": "#FFFFFF", "share": 0.6}, {"hex": "#111111", "share": 0.3}, {"hex": "#FF3300", "share": 0.1}]
    ra.guess_roles(entries)
    assert [e["role_guess"] for e in entries] == ["background", "text", "accent"]
    assert "assumption" in ra.guess_roles.__doc__


# --------------------------------------------------------------------------- unit: summary / template

def test_summary_is_at_most_12_lines(ra):
    for doc in (single(), two()):
        text = ra.summarize(doc)
        lines = text.splitlines()
        assert 1 <= len(lines) <= 12
    text = ra.summarize(two())
    assert "per your description" in text and "OPEN label case" in text
    assert "I saw" not in text


def test_template_is_valid_and_matches_shipped_file(ra):
    doc = ra.template_doc()
    assert ra.validate_analysis(doc) == []
    shipped = json.loads((SCRIPTS.parent / "templates" / "reference-analysis.template.json").read_text(encoding="utf-8"))
    assert shipped == doc


# --------------------------------------------------------------------------- CLI

def test_ra_c01_validate_fixture(tmp_path):
    r = run_cli("validate", SINGLE, cwd=tmp_path)
    assert r.returncode == 0 and r.stdout.startswith("OK") and "12 observations" in r.stdout


def test_ra_c02_validate_json(tmp_path):
    r = run_cli("validate", SINGLE, "--json", cwd=tmp_path)
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["status"] == "OK" and out["errors"] == [] and out["counts"]["rules"] == 6


def test_ra_c03_validate_invalid_json(tmp_path):
    bad = tmp_path / "not-json.json"
    bad.write_text("{\"schema\": ", encoding="utf-8")
    r = run_cli("validate", bad, cwd=tmp_path)
    assert r.returncode == 1 and "not-json.json" in r.stderr and "line" in r.stderr
    r = run_cli("validate", bad, "--json", cwd=tmp_path)
    assert r.returncode == 1 and json.loads(r.stdout)["status"] == "FAIL"


def test_ra_c04_validate_missing_file(tmp_path):
    r = run_cli("validate", tmp_path / "missing.json", cwd=tmp_path)
    assert r.returncode == 2 and "missing.json" in r.stderr


def test_ra_c05_validate_two_owners(tmp_path):
    doc = minimal(("ref-1", "ref-2"), roles={"ref-1": ["color"], "ref-2": ["color"]})
    p = write(tmp_path, "two-owners.json", doc)
    r = run_cli("validate", p, cwd=tmp_path)
    assert r.returncode == 1 and "role 'color' owned by ref-1 and ref-2" in r.stdout
    r = run_cli("validate", p, "--json", cwd=tmp_path)
    assert r.returncode == 1 and "R-ROLE-1" in [e["code"] for e in json.loads(r.stdout)["errors"]]


def test_ra_c06_validate_strict_open_conflict(tmp_path):
    r = run_cli("validate", TWO, "--strict", cwd=tmp_path)
    assert r.returncode == 1 and "R-CONF-OPEN" in r.stdout
    r = run_cli("validate", TWO, cwd=tmp_path)
    assert r.returncode == 0 and "WARN" in r.stderr


def test_ra_c06b_validate_check_paths_warns(tmp_path):
    r = run_cli("validate", SINGLE, "--check-paths", cwd=tmp_path)
    assert r.returncode == 0 and "W-PATH" in r.stderr


def test_ra_c07_merge_disjoint(tmp_path):
    left, right = left_right()
    lp, rp = write(tmp_path, "left.json", left), write(tmp_path, "right.json", right)
    r = run_cli("merge", lp, rp, "--out", "m.json", cwd=tmp_path)
    assert r.returncode == 0 and "OK merged 2 inputs" in r.stdout
    r2 = run_cli("validate", tmp_path / "m.json", cwd=tmp_path)
    assert r2.returncode == 0
    r3 = run_cli("merge", lp, rp, "--out", "m2.json", "--roles", "ref-2:typography,buttons,popup", "--json", cwd=tmp_path)
    assert r3.returncode == 0
    rep = json.loads(r3.stdout)
    assert rep["roles"]["typography"] == "ref-2" and rep["conflicts"]["open"] == []


def test_ra_c08_merge_overlapping_role(tmp_path):
    left, right = left_right()
    right["references"][0]["roles"].append("shapes")
    lp, rp = write(tmp_path, "left.json", left), write(tmp_path, "overlap.json", right)
    r = run_cli("merge", lp, rp, "--out", "m.json", cwd=tmp_path)
    assert r.returncode == 1 and "shapes" in r.stderr and not (tmp_path / "m.json").exists()


def test_ra_c09_merge_one_input_invalid(tmp_path):
    left, _ = left_right()
    lp = write(tmp_path, "left.json", left)
    bad = tmp_path / "bad.json"
    bad.write_text("[not json", encoding="utf-8")
    r = run_cli("merge", lp, bad, "--out", "m.json", cwd=tmp_path)
    assert r.returncode == 1 and not (tmp_path / "m.json").exists()
    r = run_cli("merge", lp, tmp_path / "missing.json", "--out", "m.json", cwd=tmp_path)
    assert r.returncode == 2


def test_ra_c10_merge_needs_two_inputs(tmp_path):
    r = run_cli("merge", SINGLE, "--out", "m.json", cwd=tmp_path)
    assert r.returncode == 2 and not (tmp_path / "m.json").exists()
    r = run_cli("merge", SINGLE, SINGLE, "--out", "m.json", "--roles", "ref-1:colours", cwd=tmp_path)
    assert r.returncode == 2


def test_ra_c11_extract_colors_json(tmp_path):
    img = make_image(tmp_path / "synth.png")
    r = run_cli("extract-colors", img, "--json", "--ref-id", "ref-1", "--out", "pal.json", cwd=tmp_path)
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["status"] == "OK" and out["confidence"] == "assumption" and len(out["palette_observed"]) == 3
    assert json.loads((tmp_path / "pal.json").read_text(encoding="utf-8")) == out
    r = run_cli("extract-colors", img, cwd=tmp_path)
    assert r.returncode == 0 and "(assumption)" in r.stdout and r.stdout.count("#") == 3


def test_ra_c12_extract_colors_without_pillow(tmp_path):
    img = tmp_path / "img.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    r = run_cli_without_pillow("extract-colors", img, "--json", cwd=tmp_path)
    assert r.returncode == 3
    assert "BLOCKED: Pillow (PIL) is not installed" in r.stderr and "Traceback" not in r.stderr
    assert json.loads(r.stdout)["status"] == "BLOCKED"


def test_ra_c12b_extract_colors_with_fake_pil_package(tmp_path):
    img = tmp_path / "img.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    r = run_cli_with_fake_pil("extract-colors", img, "--json", cwd=tmp_path, tmp_path=tmp_path)
    assert r.returncode == 3 and "BLOCKED: Pillow (PIL) is not installed" in r.stderr
    assert json.loads(r.stdout) == {"status": "BLOCKED", "reason": "pillow-missing",
                                    "message": json.loads(r.stdout)["message"]}
    r = run_cli_with_fake_pil("extract-colors", img, cwd=tmp_path, tmp_path=tmp_path)
    assert r.returncode == 3 and r.stdout == ""


def test_ra_c13_extract_colors_unreadable(tmp_path):
    pytest.importorskip("PIL")
    bad = tmp_path / "bad.png"
    bad.write_text("nope", encoding="utf-8")
    r = run_cli("extract-colors", bad, cwd=tmp_path)
    assert r.returncode == 3 and r.stderr.startswith("BLOCKED:")


def test_ra_c14_extract_colors_missing_file_and_bad_k(tmp_path):
    r = run_cli("extract-colors", tmp_path / "missing.png", cwd=tmp_path)
    assert r.returncode == 2
    img = tmp_path / "img.png"
    img.write_bytes(b"x")
    r = run_cli("extract-colors", img, "--k", "3", cwd=tmp_path)
    assert r.returncode == 2 and "--k" in r.stderr


def test_ra_c15_to_profile(tmp_path):
    r = run_cli("to-profile", SINGLE, "--out", "f.json", "--project", "Onet Garden", cwd=tmp_path)
    assert r.returncode == 0 and "OK partial profile" in r.stdout
    frag = json.loads((tmp_path / "f.json").read_text(encoding="utf-8"))
    assert frag["_partial"] is True and frag["sources"][0]["type"] == "reference-analysis"
    assert frag["project"]["slug"] == "onet-garden"
    r = run_cli("to-profile", SINGLE, "--style-id", "japanese-cute-puzzle", cwd=tmp_path)
    assert r.returncode == 0 and json.loads(r.stdout)["style"]["id"] == "japanese-cute-puzzle"


def test_ra_c15b_to_profile_refuses_invalid_analysis(tmp_path):
    doc = single()
    doc["schema"] = "vdp/1"
    p = write(tmp_path, "bad-schema.json", doc)
    r = run_cli("to-profile", p, "--out", "f.json", cwd=tmp_path)
    assert r.returncode == 1 and "R-SCHEMA" in r.stderr and not (tmp_path / "f.json").exists()
    r = run_cli("to-profile", tmp_path / "missing.json", cwd=tmp_path)
    assert r.returncode == 2


def test_ra_c16_summary_cli(tmp_path):
    r = run_cli("summary", TWO, cwd=tmp_path)
    assert r.returncode == 0 and len(r.stdout.strip().splitlines()) <= 12 and "Conflicts: 2 (1 open)" in r.stdout
    r = run_cli("summary", tmp_path / "missing.json", cwd=tmp_path)
    assert r.returncode == 2


def test_ra_c17_template_out_validates(tmp_path):
    r = run_cli("template", "--out", "t.json", cwd=tmp_path)
    assert r.returncode == 0
    r = run_cli("validate", tmp_path / "t.json", cwd=tmp_path)
    assert r.returncode == 0
    r = run_cli("template", cwd=tmp_path)
    assert r.returncode == 0 and json.loads(r.stdout)["schema"] == "vdp-reference-analysis/1"


@pytest.mark.parametrize("sub,flags", [
    ("validate", ["--json", "--strict", "--check-paths"]),
    ("merge", ["--out", "--roles", "--json"]),
    ("extract-colors", ["--k", "--ref-id", "--json", "--out"]),
    ("to-profile", ["--style-id", "--project", "--out", "--json"]),
    ("summary", []),
    ("template", ["--out"]),
])
def test_ra_c18_help_each_subcommand(tmp_path, sub, flags):
    r = run_cli(sub, "--help", cwd=tmp_path)
    assert r.returncode == 0
    for flag in flags:
        assert flag in r.stdout


def test_ra_c19_no_args_and_unknown_flag(tmp_path):
    r = run_cli(cwd=tmp_path)
    assert r.returncode == 2
    r = run_cli("validate", SINGLE, "--bogus", cwd=tmp_path)
    assert r.returncode == 2


def test_ra_c20_validate_does_not_modify_input(tmp_path):
    p = tmp_path / "copy.json"
    p.write_bytes(SINGLE.read_bytes())
    before = p.read_bytes()
    run_cli("validate", p, cwd=tmp_path)
    run_cli("summary", p, cwd=tmp_path)
    run_cli("to-profile", p, "--out", "f.json", cwd=tmp_path)
    assert p.read_bytes() == before


# --------------------------------------------------------------------------- CC-14: writers create parents, no tracebacks

def _writer_args(name, tmp_path):
    target = tmp_path / "missing" / "sub" / "x.json"
    if name == "template":
        return ["template", "--out", target], target
    if name == "to-profile":
        return ["to-profile", SINGLE, "--out", target], target
    if name == "merge":
        left, right = left_right()
        return ["merge", write(tmp_path, "left.json", left), write(tmp_path, "right.json", right), "--out", target], target
    img = make_image(tmp_path / "synth.png")  # skips without Pillow
    return ["extract-colors", img, "--json", "--out", target], target


@pytest.mark.parametrize("writer", ["template", "to-profile", "merge", "extract-colors"])
def test_cc14_out_creates_missing_parent_directories(tmp_path, writer):
    args, target = _writer_args(writer, tmp_path)
    assert not target.parent.exists()
    r = run_cli(*args, cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "Traceback" not in r.stderr
    assert isinstance(json.loads(target.read_text(encoding="utf-8")), dict)


@pytest.mark.parametrize("writer", ["template", "to-profile"])
def test_cc14_unwritable_out_is_one_error_line_exit_2(tmp_path, writer):
    (tmp_path / "blocker").write_text("a file, not a directory", encoding="utf-8")
    args = {"template": ["template"], "to-profile": ["to-profile", SINGLE]}[writer]
    r = run_cli(*(args + ["--out", tmp_path / "blocker" / "x.json"]), cwd=tmp_path)
    assert r.returncode == 2
    assert "Traceback" not in r.stderr
    lines = [l for l in r.stderr.splitlines() if l.strip()]
    assert len(lines) == 1 and lines[0].startswith("error: %s failed:" % writer)
