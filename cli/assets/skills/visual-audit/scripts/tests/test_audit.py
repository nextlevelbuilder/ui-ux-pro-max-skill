"""Tests for audit.py (visual-audit skill): unit tests per extractor/helper plus
subprocess CLI tests against the static drift-project fixture and its oracle
(fixtures/expected-findings.md). Offline, stdlib only, no conftest."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "audit.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
PROJECT = FIXTURES / "drift-project"
TOKENS = PROJECT / "tokens.json"
QA_PROFILE = FIXTURES / "qa" / "profile-with-qa.json"


def load_module():
    spec = importlib.util.spec_from_file_location("audit_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def audit():
    return load_module()


def run_cli(*args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT)] + [str(a) for a in args],
                          capture_output=True, text=True, cwd=str(cwd) if cwd else None, timeout=120)


@pytest.fixture(scope="module")
def report(audit):
    """One contract-mode scan of the fixture shared by the oracle tests."""
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    return audit.scan_dir(str(PROJECT), tokens, None, tokens_path=str(TOKENS))


# Oracle rows: (rule, severity, file, line). Two rows differ from expected-findings.md:
# row 28 names web/shop.css:28 but the fixture's second unlisted shadow sits on line 24
# (the file has 29 lines); row 35 (web icon.mixed-libraries) points at the library to
# REPLACE: with a 1-1 tie and no contract library in the web group the preferred library
# is alphabetical (@heroicons/react), so lucide-react in Button.tsx:4 is the finding.
# Rows 38 and 40 are medium (heuristic rules are capped at medium).
ORACLE = [
    ("color.off-palette", "high", "lib/screens/shop.dart", 12),
    ("color.off-palette", "high", "unity/Assets/UI/Shop.uss", 3),
    ("color.off-palette", "high", "unity/Assets/Scripts/ShopPanel.cs", 16),
    ("color.off-palette", "medium", "web/shop.css", 3),
    ("color.off-palette", "medium", "web/components/CtaButton.tsx", 8),
    ("color.near-duplicate", "low", "lib/screens/shop.dart", 18),
    ("color.near-duplicate", "low", "web/shop.css", 12),
    ("color.near-duplicate", "low", "unity/Assets/Scripts/ShopPanel.cs", 9),
    ("radius.off-scale", "high", "lib/screens/shop.dart", 19),
    ("radius.off-scale", "high", "unity/Assets/UI/Shop.uss", 4),
    ("radius.off-scale", "high", "unity/Assets/UI/Shop.uss", 5),
    ("radius.off-scale", "medium", "web/shop.css", 4),
    ("radius.off-scale", "medium", "web/components/CtaButton.tsx", 8),
    ("font-size.off-scale", "high", "lib/screens/shop.dart", 26),
    ("font-size.off-scale", "high", "web/shop.css", 11),
    ("font-size.off-scale", "high", "web/components/CtaButton.tsx", 8),
    ("font-size.off-scale", "high", "unity/Assets/UI/Shop.uss", 11),
    ("font-family.unlisted", "high", "lib/screens/shop.dart", 26),
    ("font-family.unlisted", "medium", "web/shop.css", 6),
    ("spacing.off-scale", "medium", "lib/screens/shop.dart", 13),
    ("spacing.off-scale", "medium", "lib/screens/shop.dart", 13),
    ("spacing.off-scale", "medium", "web/shop.css", 5),
    ("spacing.off-scale", "medium", "web/shop.css", 5),
    ("spacing.off-scale", "medium", "web/components/CtaButton.tsx", 8),
    ("spacing.off-scale", "medium", "unity/Assets/UI/Shop.uss", 6),
    ("shadow.variant-explosion", "medium", "lib/screens/shop.dart", 21),
    ("shadow.unlisted", "low", "lib/screens/shop.dart", 21),
    ("shadow.unlisted", "low", "web/shop.css", 24),
    ("duration.off-scale", "high", "lib/screens/shop.dart", 35),
    ("duration.off-scale", "high", "web/shop.css", 7),
    ("duration.off-scale", "high", "web/components/CtaButton.tsx", 9),
    ("duration.off-scale", "high", "unity/Assets/UI/Shop.uss", 7),
    ("duration.off-scale", "high", "unity/Assets/Scripts/ShopPanel.cs", 20),
    ("icon.mixed-libraries", "medium", "lib/screens/shop.dart", 3),
    ("icon.mixed-libraries", "medium", "web/components/Button.tsx", 4),
    ("component.duplicate-implementation", "medium", "lib/screens/rewards.dart", 6),
    ("component.duplicate-implementation", "medium", "web/components/CtaButton.tsx", 5),
    ("touch.target-too-small", "medium", "lib/screens/shop.dart", 30),   # heuristic cap (CC-10h): was high
    ("touch.target-too-small", "medium", "web/shop.css", 15),
    ("text.contrast-risk", "medium", "web/shop.css", 22),               # heuristic cap: was high
]
# Wave 1 oracle: 18/17/5. The heuristic cap (touch + contrast <= medium) moves rows 38 and 40 to medium: 16/19/5.
EXPECTED_SUMMARY = {"critical": 0, "high": 16, "medium": 19, "low": 5, "info": 0}
NEGATIVE = [  # (file, line) pairs that must not carry any finding
    ("lib/screens/shop.dart", 34), ("lib/screens/home.dart", 16), ("lib/screens/rewards.dart", 17),
    ("web/shop.css", 18), ("web/shop.css", 23), ("web/shop.css", 28), ("web/components/CtaButton.tsx", 9999),
    ("unity/Assets/UI/Shop.uss", 12), ("unity/Assets/Scripts/ShopPanel.cs", 11),
    ("unity/Assets/Scripts/ShopPanel.cs", 21), ("unity/Assets/Scripts/ShopPanel.cs", 22),
]
CLEAN_FILES = ["lib/theme/app_theme.dart", "lib/screens/home.dart", "lib/widgets/primary_button.dart",
               "web/styles.css", "unity/Assets/UI/Theme.uss",
               "build/generated_junk.css", "web/node_modules/x/index.css", "lib/screens/shop.g.dart"]
# web/components/Button.tsx is clean except for the web icon.mixed-libraries finding (it holds the library to replace)
FIELDS = {"id", "rule", "severity", "category", "file", "line", "evidence", "message", "violates", "nearest",
          "impact", "fix", "files_to_change", "verify", "kind"}


def write_project(root, files):
    for rel, content in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return root


# ------------------------------------------------------------------ unit: helpers
def test_au_u01_strip_comments_is_string_aware(audit):
    assert "https://example.com" in audit.strip_comments("x = 'https://example.com'; // c")
    assert audit.strip_comments("a /* b\nc */ d").count("\n") == 1
    out = audit.strip_comments("a // comment\nb")
    assert out.startswith("a ") and "comment" not in out and out.endswith("\nb")


def test_au_u01b_strip_comments_html_and_css_syntax(audit):
    lc, blocks = audit.comment_syntax(".css")
    assert lc == () and audit.strip_comments("a // not a comment in css", lc, blocks).strip() == "a // not a comment in css"
    lc, blocks = audit.comment_syntax(".html")
    assert "hidden" not in audit.strip_comments("<p>x</p><!-- hidden -->", lc, blocks)


@pytest.mark.parametrize("raw,expected", [
    ("abc", ("#AABBCC", None)), ("ABCD", ("#AABBCC", pytest.approx(221 / 255))),
    ("1E88E5", ("#1E88E5", None)), ("1E88E580", ("#1E88E5", pytest.approx(128 / 255))),
])
def test_au_u02_norm_hex(audit, raw, expected):
    assert audit.norm_hex(raw) == expected


def test_au_u03_argb_unity_hsl_normalisers(audit):
    assert audit.norm_argb("FFE91E63") == ("#E91E63", 1.0)
    assert audit.norm_argb("66000000")[1] == pytest.approx(0.4, abs=0.01)
    assert audit.unity_f_to_hex("0.98", "0.5", "0.31") == "#FA804F"
    assert audit.hsl_to_hex(0, 100, 50) == "#FF0000"
    assert audit.hsl_to_hex(120, 100, 50) == "#00FF00"


def test_au_u04_color_distance_thresholds(audit):
    assert audit.color_distance("#FF8B4D", "#FF8A4C") <= 12
    assert audit.color_distance("#FA804F", "#FF8A4C") <= 12
    assert audit.color_distance("#E91E63", "#E03E3E") > 12
    assert audit.color_distance("#1E88E5", "#3B5BDB") > 12
    assert audit.color_distance("#000000", "#000000") == 0


def test_au_u05_on_scale_integer_exact_non_integer_tolerance(audit):
    scale = [12, 14, 16, 20, 24, 32]
    assert not audit.on_scale(15, scale)
    assert audit.on_scale(15.5, scale)
    assert audit.on_scale(16, scale)
    assert not audit.on_scale(7, [4, 8, 16])
    assert audit.on_scale(7, [4, 8, 16], tolerance=1)
    assert audit.on_scale("pill", [4, 8, 9999]) and not audit.on_scale("pill", [4, 8])


def test_au_u06_nearest_tie_breaks_to_lower_step(audit):
    assert audit.nearest(15, [12, 14, 16, 20]) == 14
    assert audit.nearest(13, [4, 8, 16, 24, 9999]) == 16
    assert audit.nearest(337, [120, 200, 350]) == 350


def test_au_u07_shadow_signature_dart_equals_css(audit):
    dart = audit.shadow_signature_dart("color: Color(0x1A000000), blurRadius: 8, offset: Offset(0, 2)")
    css = audit.shadow_signature_css("0 2px 8px rgba(0, 0, 0, 0.10)")
    assert dart == css == "x=0 y=2 blur=8 spread=0 color=#000000 a=0.1"
    assert audit.shadow_signature_css("none") == "none"
    assert len(audit.shadow_signatures_css_multi("0 1px 2px rgba(0,0,0,.2), 0 4px 8px #00000033")) == 2


def test_au_u08_contrast_wcag(audit):
    assert audit.contrast("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.01)
    assert audit.contrast("#FFD43B", "#FFF8F0") == pytest.approx(1.35, abs=0.02)


def test_au_u09_flatten_at_rules_exposes_nested_rules(audit):
    css = "@media (max-width: 600px) {\n.btn { width: 20px; height: 20px; }\n}\n"
    flat = audit.flatten_at_rules(css)
    assert flat.count("\n") == css.count("\n")
    assert [m.group("sel").strip() for m in audit.RX["css.rule"].finditer(flat) if m.group("sel").strip()] == [".btn"]


# ------------------------------------------------------------------ unit: contract
def test_au_u10_load_contract_fixture(audit):
    c = audit.load_contract(json.loads(TOKENS.read_text(encoding="utf-8")))
    assert c["radius"] == [4, 8, 16, 24, 9999]
    assert c["fontSize"] == [12, 14, 16, 20, 24, 32]
    assert c["spacing"] == [4, 8, 12, 16, 24, 32]
    assert c["duration"] == [120, 200, 350]
    assert set(c["fontFamily"].values()) == {"Nunito", "Fredoka"}
    assert c["colors"]["#FF8A4C"] == "semantic.color.accent" and "#3B5BDB" in c["colors"]
    assert len(c["shadows"]) == 2 and c["minTouchTarget"] == 44 and c["iconLibrary"] == "material"
    assert c["notes"] == []


def test_au_u11_load_contract_dangling_ref_and_missing_groups_are_notes(audit):
    tokens = {"primitive": {"color": {"a": {"$value": "#112233", "$type": "color"}}},
              "semantic": {"color": {"x": {"$value": "{primitive.color.nope}", "$type": "color"}}}}
    c = audit.load_contract(tokens)
    assert any("unresolved" in n for n in c["notes"]) and any("missing" in n for n in c["notes"])
    assert c["colors"] == {"#112233": "primitive.color.a"}


def test_au_u12_load_contract_rejects_non_token_json(audit):
    with pytest.raises(audit.ContractError):
        audit.load_contract({"foo": 1})
    with pytest.raises(audit.ContractError):
        audit.load_contract([1, 2])


def test_au_u13_profile_fallbacks(audit):
    profile = json.loads(QA_PROFILE.read_text(encoding="utf-8"))
    c = audit.load_contract({"primitive": {"color": {}}}, profile)
    assert c["duration"] == [120, 200, 350] and c["iconLibrary"] == "material"
    assert {"fredoka", "nunito"} <= set(c["fontFamily"])


# ------------------------------------------------------------------ unit: walking
def test_au_u14_detect_platform(audit, tmp_path):
    assert audit.detect_platform(str(PROJECT)) == "mixed"
    assert audit.detect_platform(str(write_project(tmp_path / "f", {"pubspec.yaml": "name: x", "lib/a.dart": ""}))) == "flutter"
    assert audit.detect_platform(str(write_project(tmp_path / "w", {"package.json": "{}"}))) == "web"
    assert audit.detect_platform(str(write_project(tmp_path / "u", {"ProjectSettings/ProjectVersion.txt": "x"}))) == "unity"
    assert audit.detect_platform(str(write_project(tmp_path / "n", {"Package.swift": "x"}))) == "native"
    assert audit.detect_platform(str(write_project(tmp_path / "k", {"README.md": "x", "data.csv": "a,b"}))) == "unknown"
    (tmp_path / "e").mkdir()
    assert audit.detect_platform(str(tmp_path / "e")) == "unknown"


def test_au_u15_walk_skips_decoys_and_counts_them(audit):
    files, skipped = audit.walk(str(PROJECT))
    rels = [f for f, _ in files]
    assert len(rels) == 12 and skipped == 3
    for decoy in ("build/generated_junk.css", "web/node_modules/x/index.css", "lib/screens/shop.g.dart"):
        assert decoy not in rels
    assert rels == sorted(rels)


def test_au_u16_walk_exclude_glob_and_platform_filter(audit):
    files, skipped = audit.walk(str(PROJECT), excludes=("web/*",))
    assert all(not f.startswith("web/") for f, _ in files) and skipped == 7
    files, _ = audit.walk(str(PROJECT), allowed_platforms={"unity"})
    assert {p for _, p in files} == {"unity"} and len(files) == 3


def test_au_u17_read_source_skips_binary_huge_minified(audit, tmp_path):
    (tmp_path / "bin.css").write_bytes(b".a{color:#fff}\x00\x00")
    (tmp_path / "min.css").write_text(".a{}" * 2000, encoding="utf-8")
    (tmp_path / "big.css").write_text("x" * 100 + "\n" * (1024 * 1024 + 10), encoding="utf-8")
    (tmp_path / "ok.css").write_text(".a{color:#fff}\n", encoding="utf-8")
    assert audit.read_source(str(tmp_path / "bin.css")) is None
    assert audit.read_source(str(tmp_path / "min.css")) is None
    assert audit.read_source(str(tmp_path / "big.css")) is None
    assert audit.read_source(str(tmp_path / "ok.css")).startswith(".a")


def test_au_u18_is_primary(audit):
    assert audit.is_primary("lib/screens/shop.dart") and audit.is_primary("src/game/hud_overlay.tsx")
    assert not audit.is_primary("web/components/CtaButton.tsx") and not audit.is_primary("web/shop.css")
    assert audit.is_primary("web/shop.css", ("web/*.css",))


# ------------------------------------------------------------------ unit: extractors
def scan_one(audit, rel):
    s = audit.Scanner()
    text = (PROJECT / rel).read_text(encoding="utf-8")
    s.scan_file(rel, text, audit.EXT_PLATFORM[os.path.splitext(rel)[1]])
    return s


def vals(s, cat):
    return [(h.line, h.value, h.extra) for h in s.hits if h.cat == cat]


def test_au_u19_dart_extractors(audit):
    s = scan_one(audit, "lib/screens/shop.dart")
    colors = vals(s, "color")
    assert (12, "#E91E63", 1.0) in colors and (18, "#FF8B4D", 1.0) in colors
    assert any(l == 34 and v == "#000000" and abs(a - 0.4) < 0.01 for l, v, a in colors)  # scrim -> inventory only
    assert not any(l == 21 for l, _, _ in colors)  # BoxShadow colour is part of the signature
    assert vals(s, "radius") == [(19, 13, None)]
    assert vals(s, "fontSize") == [(26, 15, None)]
    assert vals(s, "fontFamily") == [(26, "Comic Sans MS", None)]
    assert vals(s, "duration") == [(35, 337, None)]
    assert sorted(v for _, v, _ in vals(s, "spacing")) == [10, 18]
    assert vals(s, "touch") == [(30, (32.0, 32.0), "IconButton")]
    assert set(s.icon_libs["flutter"]) == {"material", "font_awesome_flutter"}
    assert len(s.shadows) == 1 and "blur=13" in s.shadows[0][0] and s.shadows[0][2] == 21


def test_au_u20_dart_clean_theme_and_url_trap(audit):
    theme = scan_one(audit, "lib/theme/app_theme.dart")
    assert [v for _, v, _ in vals(theme, "radius")] == [4, 8, 16, "pill"]
    assert len({sig for sig, _, _, _, _ in theme.shadows}) == 2
    home = scan_one(audit, "lib/screens/home.dart")
    assert vals(home, "color") == [] and vals(home, "duration") == []
    assert set(home.icon_libs["flutter"]) == {"material"}


def test_au_u21_dart_named_colors_google_fonts_min_size(audit, tmp_path):
    s = audit.Scanner()
    s.scan_file("lib/x.dart", "Colors.blue; Colors.transparent; Colors.red[200]; GoogleFonts.comicNeue();"
                "ElevatedButton(style: ButtonStyle(minimumSize: Size(30, 30))); Color.fromARGB(255, 1, 2, 3); Color.fromRGBO(4, 5, 6, 0.5);"
                "Duration(seconds: 2)", "flutter")
    assert ("#2196F3", None) in [(v, a) for _, v, a in vals(s, "color")]
    assert s.named_colors == {"blue": 1, "transparent": 1, "red[200]": 1}
    assert vals(s, "fontFamily") == [(1, "Comic Neue", None)]
    assert vals(s, "touch")[0][1] == (30.0, 30.0)
    assert ("#010203", 1.0) in [(v, a) for _, v, a in vals(s, "color")] and ("#040506", 0.5) in [(v, a) for _, v, a in vals(s, "color")]
    assert vals(s, "duration") == [(1, 2000, None)]


def test_au_u22_css_extractors(audit):
    s = scan_one(audit, "web/shop.css")
    colors = [(v, a) for _, v, a in vals(s, "color")]
    assert ("#1E88E5", None) in colors and ("#FF8B4D", None) in colors and ("#FFD43B", None) in colors
    assert "#000000" not in [v for v, _ in colors]  # rgba inside box-shadow is masked
    assert [v for _, v, _ in vals(s, "radius")] == [7, 8]
    assert vals(s, "fontSize") == [(11, 15, None)]
    assert vals(s, "fontFamily") == [(6, "Poppins", None)]
    assert sorted(v for _, v, _ in vals(s, "spacing")) == [10, 18]
    assert vals(s, "duration") == [(7, 337, None)]
    assert vals(s, "touch") == [(15, (28.0, 28.0), ".icon-btn")]
    assert vals(s, "contrast")[0][0] == 22 and vals(s, "contrast")[0][1] < 3.0
    assert len({sig for sig, _, _, _, _ in s.shadows}) == 2


def test_au_u23_css_custom_property_routing(audit):
    s = scan_one(audit, "web/styles.css")
    assert [v for _, v, _ in vals(s, "radius")] == [8, 16, "pill"]
    assert [v for _, v, _ in vals(s, "fontFamily")] == ["Nunito", "Fredoka"]
    assert [v for _, v, _ in vals(s, "duration")] == [200, 200]
    assert vals(s, "touch") == [(25, (44.0, 44.0), ".btn-primary")]  # recorded; 44 is not below the minimum
    assert len(s.shadows) == 1 and s.shadows[0][0] == "x=0 y=2 blur=8 spread=0 color=#000000 a=0.1"


def test_au_u24_uss_and_csharp_extractors(audit):
    uss = scan_one(audit, "unity/Assets/UI/Shop.uss")
    assert [v for _, v, _ in vals(uss, "color")] == ["#E91E63", "#FF8A4C"]
    assert [v for _, v, _ in vals(uss, "radius")] == [13, 13]
    assert vals(uss, "fontSize") == [(11, 15, None)] and vals(uss, "duration") == [(7, 337, None)]
    cs = scan_one(audit, "unity/Assets/Scripts/ShopPanel.cs")
    assert [v for _, v, _ in vals(cs, "color")] == ["#FA804F", "#3B5BDB", "#E91E63"]
    assert [v for _, v, _ in vals(cs, "duration")] == [337, 200, 350]
    theme = scan_one(audit, "unity/Assets/UI/Theme.uss")
    assert vals(theme, "touch") == [(11, (48.0, 48.0), ".btn-primary")] and [v for _, v, _ in vals(theme, "fontSize")] == [16, 14]


def test_au_u25_web_markup_tailwind_masking_and_style_objects(audit):
    s = scan_one(audit, "web/components/CtaButton.tsx")
    assert [v for _, v, _ in vals(s, "color")] == ["#1E88E5", "#FFFFFF"]
    assert vals(s, "radius") == [(8, 7, None)] and vals(s, "fontSize") == [(8, 15, None)]
    assert vals(s, "spacing") == [(8, 18, None)] and vals(s, "duration") == [(9, 337, None)]
    assert set(s.icon_libs["web"]) == {"@heroicons/react"}
    assert list(s.components["web"]) == ["CtaButton"]


def test_au_u26_web_markup_extra_patterns(audit):
    s = audit.Scanner()
    s.scan_file("src/a.tsx", "import {X} from 'lucide-react';\nconst s = { borderRadius: 13, fontSize: '14px', color: 'rgb(1, 2, 3)' };\n"
                "<div className=\"duration-[337ms] text-[1rem] gap-[0.5rem]\" />", "web")
    assert [v for _, v, _ in vals(s, "radius")] == [13] and sorted(v for _, v, _ in vals(s, "fontSize")) == [14, 16]
    assert [v for _, v, _ in vals(s, "duration")] == [337] and [v for _, v, _ in vals(s, "spacing")] == [8]
    assert ("#010203", None) in [(v, a) for _, v, a in vals(s, "color")]


def test_au_u27_vue_style_block_and_uxml_inline_style(audit):
    s = audit.Scanner()
    s.scan_file("src/A.vue", "<template><div class=\"bg-[#ABCDEF]\"/></template>\n<style>\n.card { border-radius: 13px; color: #123456; }\n</style>\n", "web")
    assert vals(s, "radius") == [(3, 13, None)]
    assert sorted(v for _, v, _ in vals(s, "color")) == ["#123456", "#ABCDEF"]
    u = audit.Scanner()
    u.scan_file("Assets/UI/a.uxml", "<ui:VisualElement style=\"border-radius: 13px; background-color: #E91E63; padding: 10px;\" />\n", "unity")
    assert [v for _, v, _ in vals(u, "radius")] == [13] and [v for _, v, _ in vals(u, "color")] == ["#E91E63"]
    assert [v for _, v, _ in vals(u, "spacing")] == [10]


def test_au_u28_swift_kotlin_experimental(audit):
    s = audit.Scanner()
    s.scan_file("ios/A.swift", "Color(red: 0.98, green: 0.5, blue: 0.31).cornerRadius(13).font(.system(size: 15))", "native")
    assert [v for _, v, _ in vals(s, "color")] == ["#FA804F"] and [v for _, v, _ in vals(s, "radius")] == [13]
    assert [v for _, v, _ in vals(s, "fontSize")] == [15]
    k = audit.Scanner()
    k.scan_file("android/A.kt", "Color(0xFFE91E63); RoundedCornerShape(13.dp); fontSize = 15.sp; tween(durationMillis = 337)", "native")
    assert [v for _, v, _ in vals(k, "color")] == ["#E91E63"] and [v for _, v, _ in vals(k, "duration")] == [337]
    assert k.experimental == {"kotlin"} and s.experimental == {"swift"}


def test_au_u29_components_and_duplicate_pairs(audit, report):
    s = audit.Scanner()
    for rel in ("lib/widgets/primary_button.dart", "lib/screens/rewards.dart", "web/components/Button.tsx", "web/components/CtaButton.tsx"):
        s.scan_file(rel, (PROJECT / rel).read_text(encoding="utf-8"), audit.EXT_PLATFORM[os.path.splitext(rel)[1]])
    assert set(s.components["flutter"]) == {"PrimaryButton", "MainButton"} and set(s.components["web"]) == {"Button", "CtaButton"}
    dups = [f for f in report["findings"] if f["rule"] == "component.duplicate-implementation"]
    assert len(dups) == 2
    assert sorted(dups[0]["files_to_change"]) == ["lib/screens/rewards.dart", "lib/widgets/primary_button.dart"]
    assert all("divergent" in d["message"] for d in dups)


# ------------------------------------------------------------------ oracle
def test_au_u30_oracle_header_and_summary(report):
    assert report["schema"] == "visual-audit/1" and report["platform"] == "mixed"
    assert report["scanned_files"] == 12 and report["skipped_files"] == 3
    assert report["summary"] == EXPECTED_SUMMARY and len(report["findings"]) == 40
    assert report["contract"]["tokens"] == str(TOKENS)


def test_au_u31_oracle_every_row_present(report):
    got = [(f["rule"], f["severity"], f["file"], f["line"]) for f in report["findings"]]
    missing = [row for row in ORACLE if row not in got]
    assert missing == [], "missing oracle rows: %s" % missing
    assert sorted(got) == sorted(ORACLE)


@pytest.mark.parametrize("rule", load_module().MIN_RULE_IDS)
def test_au_u32_every_minimum_rule_id_fires(report, rule):
    assert any(f["rule"] == rule for f in report["findings"]), rule


def test_au_u33_negative_oracle(report):
    hit = {(f["file"], f["line"]) for f in report["findings"]}
    for loc in NEGATIVE:
        assert loc not in hit, loc
    for clean in CLEAN_FILES:
        assert not any(f["file"] == clean for f in report["findings"]), clean
    assert [f["rule"] for f in report["findings"] if f["file"] == "web/components/Button.tsx"] == ["icon.mixed-libraries"]


def test_au_u34_finding_fields_ids_and_order(report, audit):
    ids = [f["id"] for f in report["findings"]]
    assert ids == ["VA-%04d" % i for i in range(1, 41)]
    for f in report["findings"]:
        assert FIELDS <= set(f) and f["confidence"] in ("exact", "heuristic")
        assert isinstance(f["line"], int) and f["line"] >= 1 and f["evidence"] and f["files_to_change"]
        assert f["id"] in f["verify"] and f["kind"] in ("rule", "recommendation", "aesthetic", "intentional-exception")
    ranks = [audit.SEV_RANK[f["severity"]] for f in report["findings"]]
    assert ranks == sorted(ranks)
    heur = {f["rule"] for f in report["findings"] if f["confidence"] == "heuristic"}
    assert heur == {"component.duplicate-implementation", "touch.target-too-small", "text.contrast-risk"}


def test_au_u35_nearest_texts_and_evidence(report):
    by = {(f["rule"], f["file"], f["line"]): f for f in report["findings"]}
    f = by[("color.off-palette", "lib/screens/shop.dart", 12)]
    assert "#E03E3E" in f["nearest"] and "distance 28.0" in f["nearest"] and f["evidence"] == "Color(0xFFE91E63)"
    assert by[("color.near-duplicate", "lib/screens/shop.dart", 18)]["nearest"].startswith("semantic.color.accent #FF8A4C (distance 0.8)")
    assert by[("font-size.off-scale", "lib/screens/shop.dart", 26)]["nearest"].startswith("primitive.fontSize.sm 14 (scale")
    sh = by[("shadow.variant-explosion", "lib/screens/shop.dart", 21)]
    assert "distinct=3 allowed=2" in sh["message"] and sh["evidence"] == "x=0 y=5 blur=13 spread=0 color=#000000 a=0.25"
    ic = by[("icon.mixed-libraries", "lib/screens/shop.dart", 3)]
    assert "keep material, replace font_awesome_flutter" in ic["message"] and ic["nearest"].startswith("preferred for flutter: material")
    assert ic["fix"].startswith("Keep material and replace the font_awesome_flutter icons with material equivalents")
    assert by[("touch.target-too-small", "lib/screens/shop.dart", 30)]["message"].startswith("[heuristic]")
    assert "1.35" in by[("text.contrast-risk", "web/shop.css", 22)]["message"]


def test_au_u36_inventory_matches_oracle(report):
    inv = report["inventory"]
    assert inv["radii"] == {"4": 1, "7": 2, "8": 4, "13": 3, "16": 4, "9999": 2}
    assert inv["font_sizes"] == {"12": 1, "14": 1, "15": 4, "16": 3, "24": 1}
    assert inv["durations"] == {"120": 1, "200": 5, "337": 5, "350": 2}
    assert inv["shadows"] == 3
    assert inv["icon_libraries"] == ["@heroicons/react", "font_awesome_flutter", "lucide-react", "material"]
    assert inv["font_families"] == ["Comic Sans MS", "Fredoka", "Nunito", "Poppins"]
    assert inv["colors"]["#E91E63"] == 3 and inv["colors_with_alpha"] == {"#000000@0.40": 1, "#FF8A4C@0.90": 1}


def test_au_u37_inventory_mode_oracle(audit):
    rep = audit.scan_dir(str(PROJECT))
    assert rep["contract"] == {"tokens": None, "profile": None}
    rules = sorted(f["rule"] for f in rep["findings"])
    assert rules == sorted(["radius.variant-explosion", "font-family.variant-explosion", "icon.mixed-libraries",
                            "icon.mixed-libraries", "component.duplicate-implementation", "component.duplicate-implementation",
                            "touch.target-too-small", "touch.target-too-small", "text.contrast-risk"])
    assert rep["summary"] == {"critical": 0, "high": 0, "medium": 9, "low": 0, "info": 0}
    assert all(f["kind"] == "recommendation" for f in rep["findings"] if f["rule"].endswith("variant-explosion"))
    assert any("inventory-only" in n for n in rep["notes"])


# ------------------------------------------------------------------ severity / profile (synthetic)
MINI_TOKENS = {"primitive": {"color": {"a": {"$value": "#FF8A4C", "$type": "color"}},
                             "radius": {"md": {"$value": "8px", "$type": "dimension"}},
                             "spacing": {"2": {"$value": "8px", "$type": "dimension"}},
                             "fontSize": {"md": {"$value": "16px", "$type": "dimension"}},
                             "duration": {"base": {"$value": "200ms", "$type": "duration"}},
                             "shadow": {"sm": {"$value": "0 2px 8px rgba(0,0,0,0.1)", "$type": "shadow"}}},
               "$extensions": {"vdp": {"minTouchTarget": 44}}}


@pytest.mark.parametrize("n,expected", [(1, "medium"), (2, "medium"), (3, "high")])
def test_au_u38_severity_ladder_by_count(audit, tmp_path, n, expected):
    root = write_project(tmp_path / "p", {"src/a%d.css" % i: ".x { color: #1E88E5; }\n" for i in range(n)})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    offs = [f for f in rep["findings"] if f["rule"] == "color.off-palette"]
    assert len(offs) == n and {f["severity"] for f in offs} == {expected}


def test_au_u39_primary_screen_raises_single_occurrence_to_high(audit, tmp_path):
    root = write_project(tmp_path / "p", {"lib/screens/a.dart": "Color(0xFF1E88E5)"})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    assert rep["findings"][0]["severity"] == "high"


def test_au_u40_spacing_and_duration_caps(audit, tmp_path):
    root = write_project(tmp_path / "p", {"lib/screens/a.dart": "EdgeInsets.all(10); Duration(milliseconds: 337)"})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    sev = {f["rule"]: f["severity"] for f in rep["findings"]}
    assert sev["spacing.off-scale"] == "low" and sev["duration.off-scale"] == "medium"


def test_au_u41_touch_below_24_stays_medium_with_hint(audit, tmp_path):
    root = write_project(tmp_path / "p", {"lib/screens/a.dart": "SizedBox(width: 20, height: 20, child: IconButton())"})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    f = rep["findings"][0]
    assert f["rule"] == "touch.target-too-small" and f["severity"] == "medium" and "smallest dimension < 24" in f["message"]
    assert rep["summary"]["critical"] == 0 and rep["summary"]["high"] == 0


def test_au_u42_intentional_exception_from_profile(audit):
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    profile = json.loads(QA_PROFILE.read_text(encoding="utf-8"))
    rep = audit.scan_dir(str(PROJECT), tokens, profile)
    exc = [f for f in rep["findings"] if f["kind"] == "intentional-exception"]
    assert exc and all(f["rule"] == "radius.off-scale" and "shop" in f["file"].lower() and f["severity"] == "info" for f in exc)
    assert all(f["message"].startswith("[intentional: price tags are compact]") for f in exc)
    # shop.dart:19, Shop.uss:4, Shop.uss:5, shop.css:4 all carry "shop" in their path
    assert rep["summary"]["info"] == len(exc) == 4
    assert rep["summary"]["high"] == EXPECTED_SUMMARY["high"] - 3 and rep["summary"]["medium"] == EXPECTED_SUMMARY["medium"] - 1
    assert not audit.threshold_hit(exc, "low")
    colour = next(f for f in rep["findings"] if f["rule"] == "color.off-palette")
    assert "ad-hoc colours" in colour["violates"]


def test_au_u43_global_tolerance_and_near_threshold(audit, tmp_path):
    root = write_project(tmp_path / "p", {"src/a.css": ".x { border-radius: 7px; color: #FF8B4D; }\n"})
    rep = audit.scan_dir(str(root), MINI_TOKENS, tolerance=1, near_threshold=0.5)
    rules = sorted(f["rule"] for f in rep["findings"])
    assert rules == ["color.off-palette"]


def test_au_u44_markdown_report(audit, report):
    md = audit.to_markdown(report)
    assert md.startswith("# Visual audit") and "| 0 | 16 | 19 | 5 | 0 |" in md
    assert "lib/screens/shop.dart:12" in md and "### HIGH" in md and "## Inventory" in md
    assert "shadows: 3 distinct" in md


def test_au_u45_compare_ignores_lines_and_uses_multiset(audit, report):
    after = json.loads(json.dumps(report))
    for f in after["findings"]:
        f["line"] += 3
    after["findings"] = [f for f in after["findings"] if f["id"] != "VA-0001"]
    after["findings"].append({"id": "VA-9999", "rule": "color.off-palette", "severity": "low", "file": "x.css", "line": 1, "evidence": "#ABCDEF", "kind": "rule"})
    res = audit.compare_reports(report, after)
    assert res["counts"] == {"resolved": 1, "new": 1, "unchanged": 39, "changed_severity": 0}
    assert res["resolved"][0]["id"] == "VA-0001" and res["new"][0]["id"] == "VA-9999"
    assert not audit.threshold_hit(res["new"], "high") and audit.threshold_hit(res["new"], "low")


# ------------------------------------------------------------------ CLI
def test_au_c01_scan_json_rc1_schema(tmp_path):
    r = run_cli("scan", PROJECT, "--contract", TOKENS, "--json", cwd=tmp_path)
    assert r.returncode == 1, r.stderr
    rep = json.loads(r.stdout)
    assert rep["schema"] == "visual-audit/1" and rep["summary"] == EXPECTED_SUMMARY
    assert len({f["rule"] for f in rep["findings"]}) >= 12


@pytest.mark.parametrize("fail_on,rc", [("critical", 0), ("none", 0), ("high", 1), ("low", 1)])
def test_au_c02_fail_on_threshold(tmp_path, fail_on, rc):
    r = run_cli("scan", PROJECT, "--contract", TOKENS, "--fail-on", fail_on, cwd=tmp_path)
    assert r.returncode == rc


def test_au_c03_fail_on_bogus_rc2(tmp_path):
    assert run_cli("scan", PROJECT, "--contract", TOKENS, "--fail-on", "bogus", cwd=tmp_path).returncode == 2


def test_au_c04_empty_dir(tmp_path):
    (tmp_path / "empty").mkdir()
    r = run_cli("scan", tmp_path / "empty", "--json", cwd=tmp_path)
    assert r.returncode == 0 and "no source files" in r.stderr
    rep = json.loads(r.stdout)
    assert rep["scanned_files"] == 0 and rep["platform"] == "unknown" and rep["findings"] == []


def test_au_c05_unknown_platform_generic_patterns(tmp_path):
    root = write_project(tmp_path / "unk", {"README.md": "x", "data.csv": "a,b", "a.css": ".x { color: #123456; border-radius: 13px; }\n"})
    r = run_cli("scan", root, "--contract", TOKENS, "--json", cwd=tmp_path)
    assert r.returncode == 0 and "platform unknown" in r.stderr
    rep = json.loads(r.stdout)
    assert rep["platform"] == "unknown" and rep["scanned_files"] == 1
    assert {f["rule"] for f in rep["findings"]} == {"color.off-palette", "radius.off-scale"}


def test_au_c06_platform_cobol_rc2(tmp_path):
    r = run_cli("scan", PROJECT, "--platform", "cobol", cwd=tmp_path)
    assert r.returncode == 2 and "invalid choice" in r.stderr


def test_au_c07_forced_platform_restricts_files(tmp_path):
    r = run_cli("scan", PROJECT, "--contract", TOKENS, "--platform", "unity", "--json", cwd=tmp_path)
    rep = json.loads(r.stdout)
    assert rep["platform"] == "unity" and rep["scanned_files"] == 3 and rep["platform_detected"] == "mixed"
    assert all(f["file"].startswith("unity/") for f in rep["findings"])
    root = write_project(tmp_path / "f", {"pubspec.yaml": "name: x", "lib/a.dart": "Color(0xFF1E88E5)"})
    r = run_cli("scan", root, "--platform", "unity", "--json", cwd=tmp_path)
    assert r.returncode == 0 and "0 unity files" in r.stderr and json.loads(r.stdout)["scanned_files"] == 0


def test_au_c08_missing_dir_and_file_as_dir_rc2(tmp_path):
    assert run_cli("scan", tmp_path / "nope", cwd=tmp_path).returncode == 2
    assert run_cli("scan", TOKENS, cwd=tmp_path).returncode == 2


def test_au_c09_missing_contract_rc2_malformed_rc1(tmp_path):
    assert run_cli("scan", PROJECT, "--contract", tmp_path / "nope.json", cwd=tmp_path).returncode == 2
    (tmp_path / "bad.json").write_text("{ not json", encoding="utf-8")
    r = run_cli("scan", PROJECT, "--contract", tmp_path / "bad.json", cwd=tmp_path)
    assert r.returncode == 1 and "not valid JSON" in r.stderr
    (tmp_path / "list.json").write_text("[1]", encoding="utf-8")
    assert run_cli("scan", PROJECT, "--contract", tmp_path / "list.json", cwd=tmp_path).returncode == 1
    assert run_cli("scan", PROJECT, "--profile", tmp_path / "nope.json", cwd=tmp_path).returncode == 2
    assert run_cli("scan", PROJECT, "--profile", tmp_path / "bad.json", cwd=tmp_path).returncode == 1


def test_au_c10_out_json_md_and_format(tmp_path):
    r = run_cli("scan", PROJECT, "--contract", TOKENS, "--out", tmp_path / "f.json", "--md", tmp_path / "r.md", "--json", cwd=tmp_path)
    rep = json.loads((tmp_path / "f.json").read_text(encoding="utf-8"))
    assert rep["summary"] == EXPECTED_SUMMARY and len(rep["findings"]) == 40
    one_line = json.loads(r.stdout)  # --out + --json: a one-line summary, not the full report
    assert r.stdout.count("\n") == 1 and one_line["findings"] == 40 and one_line["summary"] == EXPECTED_SUMMARY
    assert set(one_line["out"]) == {str(tmp_path / "f.json"), str(tmp_path / "r.md")}
    md = (tmp_path / "r.md").read_text(encoding="utf-8")
    assert "lib/screens/shop.dart:12" in md
    r2 = run_cli("scan", PROJECT, "--contract", TOKENS, "--format", "md", "--out", tmp_path / "o.txt", cwd=tmp_path)
    assert (tmp_path / "o.txt").read_text(encoding="utf-8").startswith("# Visual audit")
    assert r2.stdout.count("\n") == 1 and r2.stdout.startswith("visual audit: 40 findings (critical 0, high 16, medium 19, low 5, info 0)")
    assert str(tmp_path / "o.txt") in r2.stdout
    r3 = run_cli("scan", PROJECT, "--contract", TOKENS, cwd=tmp_path)
    assert r3.stdout.startswith("# Visual audit")  # without --out the full report still goes to stdout


def test_au_c11_compare_oracle_end_to_end(tmp_path):
    before = tmp_path / "before.json"
    after_dir = tmp_path / "after"
    shutil.copytree(str(PROJECT), str(after_dir))
    shop = after_dir / "lib" / "screens" / "shop.dart"
    lines = shop.read_text(encoding="utf-8").replace("const Color(0xFFE91E63)", "AppColors.danger").split("\n")
    i = next(k for k, l in enumerate(lines) if "milliseconds: 337" in l)
    lines[i:i] = ["", ""]
    shop.write_text("\n".join(lines), encoding="utf-8")
    run_cli("scan", PROJECT, "--contract", TOKENS, "--out", before, cwd=tmp_path)
    run_cli("scan", after_dir, "--contract", TOKENS, "--out", tmp_path / "after.json", cwd=tmp_path)
    r = run_cli("compare", before, tmp_path / "after.json", cwd=tmp_path)
    assert r.returncode == 0 and r.stdout.startswith("resolved: 1  new: 0  unchanged: 39"), r.stdout
    assert "note: severity recomputed from project-wide occurrence counts after fixes" in r.stdout.splitlines()[1]
    rj = json.loads(run_cli("compare", before, tmp_path / "after.json", "--json", cwd=tmp_path).stdout)
    assert rj["counts"]["resolved"] == 1 and rj["counts"]["new"] == 0 and rj["counts"]["unchanged"] == 39
    assert rj["resolved"][0]["rule"] == "color.off-palette" and rj["counts"]["changed_severity"] == 2
    moved = [u for u in rj["unchanged"] if u["rule"] == "duration.off-scale" and u["file"] == "lib/screens/shop.dart"]
    assert moved, "moved duration line must be unchanged"


def test_au_c12_compare_identical_new_high_and_bad_inputs(tmp_path):
    before = tmp_path / "b.json"
    run_cli("scan", PROJECT, "--contract", TOKENS, "--out", before, cwd=tmp_path)
    r = run_cli("compare", before, before, cwd=tmp_path)
    assert r.returncode == 0 and r.stdout.startswith("resolved: 0  new: 0  unchanged: 40")
    rep = json.loads(before.read_text(encoding="utf-8"))
    rep["findings"].append({"id": "VA-0041", "rule": "color.off-palette", "severity": "high", "file": "new.css", "line": 1, "evidence": "#ABCDEF", "kind": "rule"})
    (tmp_path / "a.json").write_text(json.dumps(rep), encoding="utf-8")
    assert run_cli("compare", before, tmp_path / "a.json", cwd=tmp_path).returncode == 1
    rep["findings"][-1]["severity"] = "low"
    (tmp_path / "a.json").write_text(json.dumps(rep), encoding="utf-8")
    assert run_cli("compare", before, tmp_path / "a.json", cwd=tmp_path).returncode == 0
    (tmp_path / "bad.json").write_text(json.dumps({"schema": "other/1", "findings": []}), encoding="utf-8")
    assert run_cli("compare", before, tmp_path / "bad.json", cwd=tmp_path).returncode == 2
    assert run_cli("compare", before, tmp_path / "missing.json", cwd=tmp_path).returncode == 2


def test_au_c13_determinism(tmp_path):
    a = json.loads(run_cli("scan", PROJECT, "--contract", TOKENS, "--json", cwd=tmp_path).stdout)
    b = json.loads(run_cli("scan", PROJECT, "--contract", TOKENS, "--json", cwd=tmp_path).stdout)
    a.pop("generated_at")
    b.pop("generated_at")
    assert a == b


def test_au_c14_help_rules_and_no_args(tmp_path):
    assert run_cli(cwd=tmp_path).returncode == 2
    for sub in ("scan", "compare", "rules"):
        r = run_cli(sub, "--help", cwd=tmp_path)
        assert r.returncode == 0 and "--json" in r.stdout
    r = run_cli("rules", "--json", cwd=tmp_path)
    assert {row["rule"] for row in json.loads(r.stdout)} >= set(load_module().MIN_RULE_IDS)


# ------------------------------------------------------------------ fix-round regressions
def test_au_r01_var_and_keyword_shadows_are_not_literals(audit, tmp_path):
    assert audit.shadow_signatures_css_multi("var(--shadow-card)") == []
    for kw in ("none", "inherit", "initial", "unset", "{primitive.shadow.sm}", "$shadow", "@shadow"):
        assert audit.shadow_signatures_css_multi(kw) == [], kw
    assert audit.shadow_signatures_css_multi("0 2px 8px rgba(0,0,0,.1), var(--x)") == ["x=0 y=2 blur=8 spread=0 color=#000000 a=0.1"]
    assert audit.shadow_signature_dart("color: AppColors.shadow, blurRadius: 8, offset: Offset(0, 2)") is None
    root = write_project(tmp_path / "p", {
        "web/package.json": "{}",
        "web/styles.css": ":root { --shadow-card: 0 2px 8px rgba(0,0,0,0.1); --shadow-alias: var(--shadow-card); }\n"
                          ".card { box-shadow: var(--shadow-card); }\n.flat { box-shadow: none; }\n.inh { box-shadow: inherit; }\n",
        "lib/a.dart": "BoxShadow(color: AppColors.shadow, blurRadius: 8, offset: Offset(0, 2))",
    })
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    assert rep["inventory"]["shadows"] == 1
    assert not any(f["rule"].startswith("shadow.") for f in rep["findings"]), [f["rule"] for f in rep["findings"]]


def test_au_r01b_var_references_never_become_colour_radius_size_duration_literals(audit, tmp_path):
    css = (":root { --radius-x: var(--radius-md); --duration-x: var(--d); --space-x: var(--s); }\n"
           ".a { border-radius: var(--radius-md); padding: var(--space-2) var(--space-3); margin: calc(var(--r) + 2px);\n"
           "     transition: transform var(--duration-base) ease; color: var(--color-primary); font-family: var(--font-body); }\n"
           ".b { border-radius: calc(var(--r) + 13px); }\n")
    root = write_project(tmp_path / "p", {"package.json": "{}", "a.css": css})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    assert rep["findings"] == [], [(f["rule"], f["evidence"]) for f in rep["findings"]]
    inv = rep["inventory"]
    assert inv["radii"] == {} and inv["durations"] == {} and inv["spacing"] == {} and inv["colors"] == {} and inv["font_families"] == []
    assert audit.is_literal_value("13px") and not audit.is_literal_value("var(--x)") and not audit.is_literal_value("none")
    s = audit.Scanner()
    s.scan_file("lib/a.dart", "BorderRadius.circular(AppRadius.md); TextStyle(fontSize: AppText.size); Duration(milliseconds: kFast); color: AppColors.primary", "flutter")
    assert s.hits == []


def test_au_r02_icon_preferred_library_is_most_used_per_platform(audit, tmp_path):
    root = write_project(tmp_path / "p", {
        "package.json": "{}",
        "src/A.tsx": "import { X } from '@heroicons/react/24/solid';",
        "src/B.tsx": "import { Y } from '@heroicons/react/24/solid';",
        "src/C.tsx": "import { Z } from 'lucide-react';",
        "pubspec.yaml": "name: x",
        "lib/a.dart": "import 'package:font_awesome_flutter/font_awesome_flutter.dart';\nIcon(FontAwesomeIcons.cart); Icon(Icons.home);",
        "lib/b.dart": "Icon(FontAwesomeIcons.star);",
    })
    rep = audit.scan_dir(str(root), json.loads(TOKENS.read_text(encoding="utf-8")))
    icons = {f["file"].split("/")[0]: f for f in rep["findings"] if f["rule"] == "icon.mixed-libraries"}
    web = icons["src"]
    assert web["file"] == "src/C.tsx" and "preferred for web: @heroicons/react (most used in the web group)" == web["nearest"]
    assert web["fix"].startswith("Keep @heroicons/react and replace the lucide-react icons with @heroicons/react equivalents")
    assert "material" not in web["nearest"] and "material" not in web["fix"]
    fl = icons["lib"]  # font_awesome_flutter used in 2 files beats the contract's material (1 file)
    assert fl["nearest"].startswith("preferred for flutter: font_awesome_flutter") and fl["file"] == "lib/a.dart"
    assert fl["fix"].startswith("Keep font_awesome_flutter and replace the material icons")
    for f in icons.values():
        keep = f["fix"].split("Keep ")[1].split(" and replace the ")[0]
        replace = f["fix"].split(" and replace the ")[1].split(" icons")[0]
        assert keep != replace


def test_au_r02b_icon_tie_breaks_to_contract_then_alphabetical(audit, tmp_path, report):
    root = write_project(tmp_path / "p", {"pubspec.yaml": "name: x", "lib/a.dart": "Icon(Icons.home);", "lib/b.dart": "Icon(FontAwesomeIcons.star);"})
    rep = audit.scan_dir(str(root), json.loads(TOKENS.read_text(encoding="utf-8")))
    f = next(x for x in rep["findings"] if x["rule"] == "icon.mixed-libraries")
    assert f["nearest"] == "preferred for flutter: material (declared in the contract)" and f["file"] == "lib/b.dart"
    rep2 = audit.scan_dir(str(root))  # no contract -> alphabetical among the tied libraries
    f2 = next(x for x in rep2["findings"] if x["rule"] == "icon.mixed-libraries")
    assert f2["nearest"] == "preferred for flutter: font_awesome_flutter (tie broken alphabetically)" and f2["file"] == "lib/a.dart"
    web = next(x for x in report["findings"] if x["rule"] == "icon.mixed-libraries" and x["file"].startswith("web/"))
    assert web["file"] == "web/components/Button.tsx" and web["nearest"] == "preferred for web: @heroicons/react (tie broken alphabetically)"


@pytest.mark.parametrize("rel,slug", [
    ("lib/screens/shop_screen.dart", "shop"), ("unity/Assets/Scripts/ShopPanel.cs", "shop"), ("lib/screens/shop.dart", "shop"),
    ("web/components/CtaButton.tsx", "cta-button"), ("lib/screens/shop.g.dart", "shop"), ("src/pages/RewardsPage.tsx", "rewards"),
    ("lib/hud/HudOverlayWidget.dart", "hud-overlay"), ("web/shop.css", "shop"), ("lib/theme/app_theme.dart", "app-theme"),
    ("Assets/UI/MainMenuView.uxml", "main-menu"), ("Screen.dart", "screen"),
])
def test_au_r03_page_slug(audit, rel, slug):
    assert audit.page_slug(rel) == slug


def test_au_r03b_fix_text_uses_page_slug(report):
    by_file = {}
    for f in report["findings"]:
        if "intentional_exceptions" in f["fix"]:
            by_file.setdefault(f["file"], f["fix"])
    assert "`pages/shop.md`" in by_file["unity/Assets/Scripts/ShopPanel.cs"]
    assert "`pages/shop.md`" in by_file["unity/Assets/UI/Shop.uss"] and "`pages/shop.md`" in by_file["lib/screens/shop.dart"]
    assert "`pages/cta-button.md`" in by_file["web/components/CtaButton.tsx"]


def test_au_r05_far_token_fix_text(audit, report, tmp_path):
    by = {(f["file"], f["line"]): f for f in report["findings"] if f["rule"] == "color.off-palette"}
    far = by[("web/shop.css", 3)]
    assert far["nearest"].startswith("semantic.color.primary #3B5BDB (distance 38.1)")
    assert far["fix"].startswith("No close token") and "pick the semantic role (primary/accent/surface" in far["fix"]
    assert "Replace with the nearest token" not in far["fix"]
    near = by[("lib/screens/shop.dart", 12)]  # 28.0 < 30 keeps the concrete recommendation
    assert near["fix"].startswith("Replace with the nearest token semantic.color.danger")
    root = write_project(tmp_path / "p", {"a.css": ".x { color: #00FF00; }\n"})
    f = audit.scan_dir(str(root), MINI_TOKENS)["findings"][0]
    assert f["fix"].startswith("No close token") and f["nearest"].startswith("primitive.color.a #FF8A4C (distance")


def test_au_r06_compare_note_explains_changed_severity(audit, report):
    after = json.loads(json.dumps(report))
    after["findings"] = [f for f in after["findings"] if f["id"] != "VA-0001"]
    for f in after["findings"]:
        if f["rule"] == "color.off-palette" and f["severity"] == "high":
            f["severity"] = "medium"
    res = audit.compare_reports(report, after)
    assert res["counts"]["changed_severity"] == 2 and "not regressions" in res["note"]
    md = audit.compare_markdown(res)
    assert md.splitlines()[1].startswith("note: severity recomputed from project-wide occurrence counts after fixes")
    same = audit.compare_reports(report, report)
    assert "note:" not in audit.compare_markdown(same).splitlines()[0] and audit.compare_markdown(same).count("note:") == 0


# ------------------------------------------------------------------ final fix round (QA report F-01/F-04/F-05/F-06)
def test_au_f01_out_creates_parent_dirs_scan_and_compare(tmp_path):
    r = run_cli("scan", PROJECT, "--contract", TOKENS, "--out", "qa-logs/findings.json", "--md", "qa-logs/nested/findings.md", cwd=tmp_path)
    assert r.returncode == 1 and "Traceback" not in r.stderr, r.stderr
    assert (tmp_path / "qa-logs" / "findings.json").is_file() and (tmp_path / "qa-logs" / "nested" / "findings.md").is_file()
    r = run_cli("compare", tmp_path / "qa-logs" / "findings.json", tmp_path / "qa-logs" / "findings.json", "--out", "qa-logs/cmp/result.json", cwd=tmp_path)
    assert r.returncode == 0 and json.loads((tmp_path / "qa-logs" / "cmp" / "result.json").read_text(encoding="utf-8"))["counts"]["unchanged"] == 40


def test_au_f01b_unexpected_exception_is_one_error_line_exit_2(audit, monkeypatch, capsys):
    def boom(*a, **k):
        raise RuntimeError("disk on fire")
    monkeypatch.setattr(audit, "scan_dir", boom)
    assert audit.main(["scan", str(PROJECT)]) == 2
    err = capsys.readouterr().err
    assert err.strip() == "error: RuntimeError: disk on fire" and "Traceback" not in err


def test_au_f04_decorative_descendants_are_not_touch_targets(audit, tmp_path):
    for sel, expected in [(".icon-btn svg", False), (".icon-btn", True), ("button > span", False), (".btn::before", False),
                          (".btn:after", False), (".btn:hover", True), (".card .btn-primary", True), ("button", True),
                          ('[role="button"]', True), (".icon-btn img", False), (".icon-btn > i", False), ("nav button svg", False),
                          (".fab:not(.x)", True), ("--btn-size", False)]:
        assert audit.is_touch_selector(sel) is expected, sel
    css = ".icon-btn { width: 44px; height: 44px; }\n.icon-btn svg { width: 22px; height: 22px; }\n.icon-btn::before { width: 10px; height: 10px; }\n"
    root = write_project(tmp_path / "p", {"package.json": "{}", "src/a.css": css})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    assert [f["rule"] for f in rep["findings"]] == []


def test_au_f04b_heuristics_capped_at_medium(audit, tmp_path, report):
    heur = [f for f in report["findings"] if f["confidence"] == "heuristic"]
    assert heur and all(f["severity"] in ("medium", "low", "info") for f in heur)
    root = write_project(tmp_path / "p", {"package.json": "{}", "src/pages/a.css": ".promo { color: #FFFFFF; background: #FFFFF0; }\n.btn { width: 10px; height: 10px; }\n"})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    sev = {f["rule"]: f["severity"] for f in rep["findings"]}
    # primary screen (src/pages/) + contrast 1.0:1 + 10x10 target: the old ladder said high/critical; the cap says medium
    assert sev["text.contrast-risk"] == "medium" and sev["touch.target-too-small"] == "medium"
    assert rep["summary"]["critical"] == 0
    # the two off-palette colours on the same primary screen are rule findings and stay high (ladder unchanged)
    assert sorted(f["rule"] for f in rep["findings"] if f["severity"] == "high") == ["color.off-palette", "color.off-palette"]
    rules = {r["rule"]: r["severity"] for r in [dict(zip(("rule", "category", "kind", "severity", "confidence"), row)) for row in audit.RULE_TABLE]}
    assert rules["touch.target-too-small"].startswith("medium") and rules["text.contrast-risk"].startswith("medium")


def flutter_scaffold(tmp_path, with_web_shell=True):
    files = {
        "pubspec.yaml": "name: audit_probe\n", "lib/main.dart": "Color(0xFF1E88E5)", "test/widget_test.dart": "void main() {}",
        "android/build.gradle.kts": "", "android/app/build.gradle.kts": "",
        "android/app/src/main/kotlin/com/example/MainActivity.kt": "Color(0xFFE91E63); RoundedCornerShape(13.dp)",
        "ios/Runner/AppDelegate.swift": "Color(red: 0.1, green: 0.2, blue: 0.3).cornerRadius(13)",
        "ios/Runner.xcodeproj/project.pbxproj": "", "macos/Runner/AppDelegate.swift": "", "linux/main.cc": "", "windows/runner/main.cpp": "",
    }
    if with_web_shell:
        files.update({"web/index.html": "<html><style>.x{color:#123456}</style></html>", "web/manifest.json": "{}"})
    return write_project(tmp_path / "probe", files)


def test_au_f05_flutter_scaffold_is_flutter_not_mixed(audit, tmp_path):
    root = flutter_scaffold(tmp_path)
    assert audit.flutter_scaffold_dirs(str(root)) == {"android", "ios", "macos", "linux", "windows", "web"}
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    assert rep["platform"] == "flutter" and rep["platform_detected"] == "flutter"
    assert rep["scanned_files"] == 2 and rep["platforms"] == {"flutter": 2}
    assert not any("experimental" in n for n in rep["notes"]) and any("scaffold folders skipped" in n for n in rep["notes"])
    assert all(f["file"].startswith("lib/") for f in rep["findings"])
    native = audit.scan_dir(str(root), MINI_TOKENS, platform="native")
    # android MainActivity.kt + ios and macos AppDelegate.swift
    assert native["platform"] == "native" and native["platforms"] == {"native": 3} and any("experimental" in n for n in native["notes"])
    assert audit.flutter_scaffold_dirs(str(PROJECT)) == set()  # fixture web/ has package.json -> real web sources, kept


def test_au_f05b_web_folder_kept_when_it_is_a_real_web_project(audit, tmp_path):
    root = flutter_scaffold(tmp_path, with_web_shell=False)
    write_project(root, {"web/package.json": "{}", "web/app.css": ".x { color: #123456; }"})
    assert "web" not in audit.flutter_scaffold_dirs(str(root))
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    assert rep["platform"] == "mixed" and rep["platforms"] == {"flutter": 2, "web": 1}


def test_au_f05c_real_flutter_probe_if_present():
    """Opt-in check against a real `flutter create` app: set VISUAL_AUDIT_FLUTTER_PROBE=<app dir>."""
    probe = Path(os.environ.get("VISUAL_AUDIT_FLUTTER_PROBE", "") or "/nonexistent")
    if not (probe / "pubspec.yaml").is_file():
        pytest.skip("set VISUAL_AUDIT_FLUTTER_PROBE to a `flutter create` app to run this check")
    r = run_cli("scan", probe, "--json")
    rep = json.loads(r.stdout)
    assert rep["platform"] == "flutter" and rep["scanned_files"] == 2 and "native" not in rep["platforms"]
    assert not any("experimental" in n for n in rep["notes"])


def test_au_f06_durations_use_exact_integer_rule_no_ten_percent_band(audit, report):
    scale = [120, 200, 350]
    assert not audit.on_scale(337, scale) and not audit.on_scale(345, scale) and audit.on_scale(350, scale)
    assert audit.on_scale(349.5, scale) and not audit.on_scale(348.5, scale)
    assert audit.on_scale(337, scale, tolerance=35)  # only an explicit --tolerance widens the band
    assert sum(1 for f in report["findings"] if f["rule"] == "duration.off-scale") == 5
    text = (SCRIPTS.parent / "references" / "drift-rules.md").read_text(encoding="utf-8")
    assert "10 %" not in text and "10%" not in text


# ------------------------------------------------------------------ QA pass 2, N-1: fonts outside CSS declarations
FONTS = FIXTURES / "fonts"


@pytest.mark.parametrize("query,css2,expected", [
    ("family=Open+Sans:wght@300;400&family=Poppins:wght@400;500&display=swap", True,
     [("Open Sans", "Open+Sans:wght@300;400"), ("Poppins", "Poppins:wght@400;500")]),
    ("family=Space%20Grotesk:ital,wght@0,400;1,700&amp;family=Fira+Code", True,
     [("Space Grotesk", "Space%20Grotesk:ital,wght@0,400;1,700"), ("Fira Code", "Fira+Code")]),
    ("family=Open+Sans:400,700|Roboto+Slab&amp;subset=latin", False, [("Open Sans", "Open Sans:400,700"), ("Roboto Slab", "Roboto Slab")]),
    ("display=swap", True, []),
])
def test_au_n1_google_font_families_parser(audit, query, css2, expected):
    assert audit.google_font_families(query, css2) == expected


def test_au_n1b_html_page_link_tailwind_style_block_and_attribute(audit):
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    rep = audit.scan_dir(str(FONTS / "tailwind-page"), tokens)
    got = [(f["rule"], f["file"], f["line"], f["evidence"]) for f in rep["findings"]]
    assert got == [
        ("font-family.unlisted", "index.html", 4, "fonts.googleapis.com family=Open+Sans:wght@300;400;600"),
        ("font-family.unlisted", "index.html", 9, "heading: ['Poppins', 'sans-serif']"),
        ("font-family.unlisted", "index.html", 18, "fonts.googleapis.com family=Lobster"),
        ("font-family.unlisted", "index.html", 19, "font-family: 'Comic Sans MS', cursive"),
        ("font-family.unlisted", "index.html", 23, "font-family: Papyrus, serif"),
    ]
    assert all(f["kind"] == "rule" and f["confidence"] == "exact" and f["severity"] == "medium" for f in rep["findings"])
    assert rep["inventory"]["font_families"] == ["Comic Sans MS", "Fredoka", "Lobster", "Nunito", "Open Sans", "Papyrus", "Poppins"]
    assert rep["inventory"]["colors"] == {"#3B5BDB": 1}  # style-attr colour counted once, not twice
    msg = rep["findings"][0]["message"]
    assert "'Open Sans'" in msg and "Fredoka" in msg and "Nunito" in msg


def test_au_n1c_tailwind_config_js(audit):
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    rep = audit.scan_dir(str(FONTS / "tailwind-config"), tokens)
    got = [(f["rule"], f["file"], f["line"], f["evidence"]) for f in rep["findings"]]
    assert got == [
        ("font-family.unlisted", "tailwind.config.js", 8, "heading: ['Space Grotesk', 'sans-serif']"),
        ("font-family.unlisted", "tailwind.config.js", 10, "mono: 'Fira Code, monospace'"),
    ]
    # var() first entry, generic-only entry and on-contract Nunito are silent
    assert rep["inventory"]["font_families"] == ["Fira Code", "Nunito", "Space Grotesk"]


def test_au_n1d_cjs_mjs_ts_configs_are_routed(audit, tmp_path):
    cfg = "export default { theme: { fontFamily: { heading: ['Poppins', 'sans-serif'] } } }\n"
    root = write_project(tmp_path / "p", {"tailwind.config.cjs": cfg, "tailwind.config.mjs": cfg, "tailwind.config.ts": cfg})
    rep = audit.scan_dir(str(root), MINI_TOKENS)
    assert rep["scanned_files"] == 3 and rep["inventory"]["font_families"] == ["Poppins"]
    # MINI_TOKENS declares no families -> nothing to compare against, no finding (rule needs an allowed set)
    assert not any(f["rule"] == "font-family.unlisted" for f in rep["findings"])
    rep = audit.scan_dir(str(root), json.loads(TOKENS.read_text(encoding="utf-8")))
    assert sorted(f["file"] for f in rep["findings"] if f["rule"] == "font-family.unlisted") == [
        "tailwind.config.cjs", "tailwind.config.mjs", "tailwind.config.ts"]
    assert sorted(f["line"] for f in rep["findings"] if f["rule"] == "font-family.unlisted") == [1, 1, 1]
    assert rep["findings"][0]["severity"] == "high"  # count 3 -> ladder high


def test_au_n1e_google_import_in_css_and_selector_after_at_statement(audit, tmp_path):
    css = "@charset \"utf-8\";\n@import url(https://fonts.googleapis.com/css2?family=Lobster);\nh1 { font-family: 'Poppins'; border-radius: 13px; }\n"
    root = write_project(tmp_path / "p", {"package.json": "{}", "a.css": css})
    rep = audit.scan_dir(str(root), json.loads(TOKENS.read_text(encoding="utf-8")))
    got = sorted((f["rule"], f["line"], f["evidence"]) for f in rep["findings"])
    assert got == [("font-family.unlisted", 2, "fonts.googleapis.com family=Lobster"),
                   ("font-family.unlisted", 3, "font-family: 'Poppins'"),
                   ("radius.off-scale", 3, "border-radius: 13px")]


def test_au_n1f_vue_bound_style_ignored_and_inline_style_rules(audit, tmp_path):
    vue = ('<template><div :style="{ color: \'#E91E63\' }" style="border-radius: 13px; padding: 10px"/>'
           '<span v-bind:style="x"/></template>\n')
    root = write_project(tmp_path / "p", {"package.json": "{}", "src/A.vue": vue})
    rep = audit.scan_dir(str(root), json.loads(TOKENS.read_text(encoding="utf-8")))
    rules = sorted(f["rule"] for f in rep["findings"])
    # the :style colour is still a literal in markup (counted once by the markup pass), style="" goes through CSS rules
    assert rules == ["color.off-palette", "radius.off-scale", "spacing.off-scale"]


def test_au_n1g_drift_oracle_unchanged_by_font_extractors(report):
    assert len(report["findings"]) == 40 and report["summary"] == EXPECTED_SUMMARY
    assert report["inventory"]["font_families"] == ["Comic Sans MS", "Fredoka", "Nunito", "Poppins"]


# ------------------------------------------------------------------ QA pass 3, N3-1: every token layer is allowed
CONFORMANT = FIXTURES / "contract-conformant"
CONFORMANT_TOKENS = CONFORMANT / "tokens.json"
EXAMPLE_A_TOKENS = (SCRIPTS.parents[3] / "docs" / "examples" / "visual-design-pro-max" / "example-a-japanese-cute-animal-puzzle"
                    / "project" / "design-system" / "onet-garden" / "tokens.json")


def test_au_n31a_qa_reproduction_dart_press_duration_scans_clean(tmp_path):
    r = run_cli("scan", CONFORMANT / "flutter", "--contract", CONFORMANT_TOKENS, "--json", cwd=tmp_path)
    rep = json.loads(r.stdout)
    assert r.returncode == 0, [(f["rule"], f["file"], f["line"]) for f in rep["findings"]]
    assert rep["scanned_files"] == 3 and rep["findings"] == [] and rep["platform"] == "flutter"


def test_au_n31b_qa_reproduction_css_component_values_scan_clean(tmp_path):
    r = run_cli("scan", CONFORMANT / "web", "--contract", CONFORMANT_TOKENS, "--json", "--fail-on", "low", cwd=tmp_path)
    rep = json.loads(r.stdout)
    assert r.returncode == 0, [(f["rule"], f["line"], f["evidence"]) for f in rep["findings"]]
    assert rep["scanned_files"] == 1 and rep["findings"] == []
    # 7 distinct shadow layers: .btn-primary 2, .btn-secondary/.tile 2 (shared), .card adds 1, .popup 2
    assert rep["inventory"]["durations"] == {"90": 2, "200": 1, "350": 1} and rep["inventory"]["shadows"] == 7


def test_au_n31c_load_contract_reads_every_layer(audit):
    c = audit.load_contract(json.loads(CONFORMANT_TOKENS.read_text(encoding="utf-8")))
    assert 90 in c["duration"] and c["scale_paths"]["duration"][90] == "component.button.primary.pressDuration"
    assert c["scale_paths"]["duration"][120] == "primitive.duration.fast"
    assert "x=0 y=4 blur=0 spread=0 color=#972743 a=1.0" in c["shadows"]
    assert c["shadows"]["x=0 y=4 blur=0 spread=0 color=#972743 a=1.0"] == "component.button.primary.shadow"
    # semantic path preferred over primitive when both resolve to the same value
    assert c["scale_paths"]["radius"][c["radius"][0]].split(".")[0] in ("semantic", "component", "primitive")
    sem_control = c["scale_paths"]["radius"]
    assert any(p.startswith("semantic.radius.") for p in sem_control.values())
    assert c["notes"] == [] or all("missing" not in n for n in c["notes"])


def test_au_n31d_layers_dark_and_dimension_groups(audit):
    tokens = {
        "primitive": {"color": {"a": {"$value": "#FF8A4C", "$type": "color"}},
                      "radius": {"md": {"$value": "8px", "$type": "dimension"}},
                      "duration": {"base": {"$value": "200ms", "$type": "duration"}}},
        "semantic": {"radius": {"control": {"$value": "{primitive.radius.md}", "$type": "dimension"}},
                     "spacing": {"stack": {"$value": "12", "$type": "dimension"}}},
        "component": {"button": {"primary": {"radius": {"$value": "20px", "$type": "dimension"},
                                             "paddingX": {"$value": "18", "$type": "dimension"},
                                             "height": {"$value": "56", "$type": "dimension"},
                                             "fontSize": {"$value": "22px", "$type": "dimension"},
                                             "pressDuration": {"$value": "90ms", "$type": "duration"},
                                             "shadow": {"$value": "0 4px 0 #972743", "$type": "shadow"}}}},
        "dark": {"color": {"surface": {"$value": "#1A1A2E", "$type": "color"}},
                 "duration": {"fade": {"$value": "0.45s", "$type": "duration"}}},
    }
    assert audit.contract_layers(tokens) == ["semantic", "component", "primitive", "dark"]
    c = audit.load_contract(tokens)
    assert c["radius"] == [8, 20] and c["spacing"] == [12, 18] and c["fontSize"] == [22]
    assert c["duration"] == [90, 200, 450] and "#1A1A2E" in c["colors"] and c["colors"]["#1A1A2E"] == "dark.color.surface"
    assert c["scale_paths"]["radius"][8] == "semantic.radius.control"  # semantic named before primitive
    assert 56 not in c["radius"] + c["spacing"] + c["fontSize"]  # heights belong to no scanned scale
    for path, group in [(("radius", "md"), "radius"), (("button", "primary", "radius"), "radius"), (("corner",), "radius"),
                        (("button", "paddingX"), "spacing"), (("spacing", "stack"), "spacing"), (("hud", "chip", "gap"), "spacing"),
                        (("typography", "body", "fontSize"), "fontSize"), (("button", "height"), None),
                        (("button", "outlineWidth"), None), (("iconSize", "md"), None), (("touchTarget", "min"), None)]:
        assert audit.dimension_group(path) == group, path


def test_au_n31e_off_values_still_flagged_with_specific_nearest(audit, tmp_path):
    root = write_project(tmp_path / "p", {"pubspec.yaml": "name: x",
                                          "lib/widgets/a.dart": "AnimatedContainer(duration: const Duration(milliseconds: 95))"})
    rep = audit.scan_dir(str(root), json.loads(CONFORMANT_TOKENS.read_text(encoding="utf-8")))
    f = [x for x in rep["findings"] if x["rule"] == "duration.off-scale"]
    assert len(f) == 1 and f[0]["nearest"].startswith("component.button.primary.pressDuration 90 (scale ")
    assert "(component.button.primary.pressDuration)" in f[0]["fix"]
    css = ".x { box-shadow: 0 5px 0 #972743; }\n"
    root = write_project(tmp_path / "w", {"package.json": "{}", "a.css": css})
    rep = audit.scan_dir(str(root), json.loads(CONFORMANT_TOKENS.read_text(encoding="utf-8")))
    sh = [x for x in rep["findings"] if x["rule"] == "shadow.unlisted"]
    assert len(sh) == 1 and "all layers" in sh[0]["violates"] and "component.button.primary.shadow" in sh[0]["nearest"]


def test_au_n31f_live_example_a_contract_accepts_its_own_literals(audit, tmp_path):
    """Code generated from the CURRENT Example A tokens (every component/semantic duration, shadow,
    radius, spacing, font size and colour literal) must scan clean. Robust to regeneration."""
    if not EXAMPLE_A_TOKENS.is_file():
        pytest.skip("Example A tokens not present in this checkout")
    tokens = json.loads(EXAMPLE_A_TOKENS.read_text(encoding="utf-8"))
    c = audit.load_contract(tokens)
    css, dart = [], []
    for i, ms in enumerate(c["duration"]):
        if ms:
            css.append(".d%d { transition: transform %sms; }" % (i, ms))
            dart.append("Duration(milliseconds: %d);" % ms if float(ms).is_integer() else "")
    for i, sig in enumerate(sorted(c["shadows"])):
        m = dict(kv.split("=") for kv in sig.split())
        hexv, a = m["color"], float(m["a"])
        col = hexv if a >= 1 else "rgba(%d, %d, %d, %s)" % (int(hexv[1:3], 16), int(hexv[3:5], 16), int(hexv[5:7], 16), m["a"])
        css.append(".s%d { box-shadow: %spx %spx %spx %spx %s; }" % (i, m["x"], m["y"], m["blur"], m["spread"], col))
    for group, prop in (("radius", "border-radius"), ("spacing", "padding"), ("fontSize", "font-size")):
        for i, v in enumerate(c[group]):
            css.append(".%s%d { %s: %spx; }" % (group, i, prop, 9999 if v == "pill" else v))
    for i, hexv in enumerate(sorted(c["colors"])):
        css.append(".c%d { border-color: %s; }" % (i, hexv))
    root = write_project(tmp_path / "live", {"package.json": "{}", "src/all.css": "\n".join(css) + "\n",
                                             "lib/a.dart": "\n".join(d for d in dart if d) + "\n"})
    rep = audit.scan_dir(str(root), tokens)
    assert rep["findings"] == [], [(f["rule"], f["line"], f["evidence"]) for f in rep["findings"]][:10]
    for d in ("flutter", "web"):  # the QA reproduction verbatim against the live file
        r = audit.scan_dir(str(CONFORMANT / d), tokens)
        assert r["findings"] == [], (d, [(f["rule"], f["file"], f["line"]) for f in r["findings"]])


def test_au_n31g_drift_oracle_unchanged_by_all_layer_contract(report):
    assert len(report["findings"]) == 40 and report["summary"] == EXPECTED_SUMMARY
