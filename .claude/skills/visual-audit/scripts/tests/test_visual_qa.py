"""Tests for visual_qa.py (visual-audit skill). Synthetic PNGs are generated with
Pillow under pytest.importorskip; the BLOCKED paths run without Pillow (sys.modules
monkeypatch in-process, poisoned/fake PIL in subprocesses). No conftest."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "visual_qa.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "qa"
PROFILE = FIXTURES / "profile-with-qa.json"
PROFILE_NO_QA = FIXTURES / "profile-no-qa.json"
STACKS = ["flutter", "flutter-flame", "unity-ugui", "unity-ui-toolkit", "web", "swiftui", "jetpack-compose"]


def load_module():
    spec = importlib.util.spec_from_file_location("visual_qa_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def vq():
    return load_module()


def run_cli(*args, cwd=None, env=None):
    return subprocess.run([sys.executable, str(SCRIPT)] + [str(a) for a in args],
                          capture_output=True, text=True, cwd=str(cwd) if cwd else None, timeout=120, env=env)


def run_cli_without_pillow(*args, cwd):
    """Poison the PIL import in the child so `from PIL import Image` raises ImportError."""
    code = ("import sys, runpy; sys.modules['PIL'] = None; sys.modules['PIL.Image'] = None; "
            "sys.argv = [%r] + %r; runpy.run_path(%r, run_name='__main__')"
            % (str(SCRIPT), [str(a) for a in args], str(SCRIPT)))
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=str(cwd), timeout=120)


@pytest.fixture
def no_pillow(monkeypatch):
    monkeypatch.setitem(sys.modules, "PIL", None)
    monkeypatch.setitem(sys.modules, "PIL.Image", None)


@pytest.fixture
def png_pair(tmp_path):
    """Two 100x100 images that differ in a 10x10 black block (ratio 0.01)."""
    Image = pytest.importorskip("PIL.Image")
    a = Image.new("RGB", (100, 100), (255, 255, 255))
    a.save(tmp_path / "a.png")
    b = a.copy()
    for x in range(20, 30):
        for y in range(40, 50):
            b.putpixel((x, y), (0, 0, 0))
    b.save(tmp_path / "b.png")
    return tmp_path / "a.png", tmp_path / "b.png"


# ------------------------------------------------------------------ unit: diff
def test_vq_u01_identical_pass(vq, png_pair):
    a, _ = png_pair
    r = vq.diff_images(str(a), str(a))
    assert r["status"] == "PASS" and r["diff_ratio"] == 0.0 and r["bbox"] is None and r["clusters"] == []


def test_vq_u02_block_fail_bbox_exclusive(vq, png_pair):
    a, b = png_pair
    r = vq.diff_images(str(a), str(b))
    assert r["status"] == "FAIL" and r["diff_ratio"] == pytest.approx(0.01, abs=1e-6)
    assert r["diff_percent"] == pytest.approx(1.0, abs=1e-4) and r["bbox"] == [20, 40, 30, 50]
    assert r["changed_pixels"] == 100 and r["size"] == [100, 100]


def test_vq_u03_threshold_is_percent(vq, png_pair):
    a, b = png_pair
    assert vq.diff_images(str(a), str(b), threshold=0.5)["status"] == "FAIL"
    assert vq.diff_images(str(a), str(b), threshold=2)["status"] == "PASS"
    assert vq.diff_images(str(a), str(b), threshold=1.0)["status"] == "PASS"  # 1.0 % is not > 1.0


def test_vq_u04_size_mismatch_blocked(vq, png_pair, tmp_path):
    Image = pytest.importorskip("PIL.Image")
    a, _ = png_pair
    Image.new("RGB", (120, 100), (255, 255, 255)).save(tmp_path / "c.png")
    r = vq.diff_images(str(a), str(tmp_path / "c.png"))
    assert r["status"] == "BLOCKED" and r["reason"].startswith("size mismatch 100x100 vs 120x100")
    assert r["diff_ratio"] is None


def test_vq_u05_rgba_vs_rgb_pass_and_tolerance(vq, png_pair, tmp_path):
    Image = pytest.importorskip("PIL.Image")
    a, _ = png_pair
    Image.open(a).convert("RGBA").save(tmp_path / "a_rgba.png")
    assert vq.diff_images(str(a), str(tmp_path / "a_rgba.png"))["status"] == "PASS"
    noisy = Image.new("RGB", (100, 100), (245, 255, 255))
    noisy.save(tmp_path / "noisy.png")
    assert vq.diff_images(str(a), str(tmp_path / "noisy.png"), tolerance=16)["status"] == "PASS"
    assert vq.diff_images(str(a), str(tmp_path / "noisy.png"), tolerance=0)["status"] == "FAIL"


def test_vq_u06_out_diff_image(vq, png_pair, tmp_path):
    Image = pytest.importorskip("PIL.Image")
    a, b = png_pair
    out = tmp_path / "diff.png"
    r = vq.diff_images(str(a), str(b), out=str(out))
    assert r["diff_image"] == str(out) and out.is_file()
    im = Image.open(out)
    assert im.size == (300, 100)
    assert im.getpixel((225, 45))[0] > 150 and im.getpixel((225, 45))[1] < 120  # red heat inside the block
    assert im.getpixel((210, 10)) == (255, 255, 255)  # untouched area stays grey/white


def test_vq_u07_no_pillow_blocked_in_process(vq, no_pillow, tmp_path):
    r = vq.diff_images(str(tmp_path / "a.png"), str(tmp_path / "b.png"))
    assert r["status"] == "BLOCKED" and "Pillow not installed" in r["reason"]
    assert vq.main(["diff", str(tmp_path / "a.png"), str(tmp_path / "b.png"), "--json"]) == 3


def test_vq_u08_unreadable_blocked(vq, png_pair, tmp_path):
    a, _ = png_pair
    (tmp_path / "t.png").write_text("not a png", encoding="utf-8")
    r = vq.diff_images(str(a), str(tmp_path / "t.png"))
    assert r["status"] == "BLOCKED" and r["reason"].startswith("unreadable image: ")
    assert vq.diff_images(str(a), str(tmp_path / "missing.png"))["status"] == "BLOCKED"


def test_vq_u09_ignore_region_pass_and_masked_ratio(vq, png_pair):
    a, b = png_pair
    r = vq.diff_images(str(a), str(b), ignore=[(20, 40, 30, 50)])
    assert r["status"] == "PASS" and r["masked_pixels"] == 100 and r["masked_ratio"] == pytest.approx(0.01)
    r2 = vq.diff_images(str(a), str(b), ignore=[(20, 40, 25, 50)])
    assert r2["status"] == "FAIL" and r2["changed_pixels"] == 50 and r2["bbox"] == [25, 40, 30, 50]
    assert r2["diff_ratio"] == pytest.approx(50 / 9950.0, abs=1e-6)


def test_vq_u10_clusters(vq, png_pair, tmp_path):
    Image = pytest.importorskip("PIL.Image")
    a, b = png_pair
    c = Image.open(b).copy()
    for x in range(80, 84):
        for y in range(5, 9):
            c.putpixel((x, y), (0, 0, 0))
    c.save(tmp_path / "c.png")
    r = vq.diff_images(str(a), str(tmp_path / "c.png"))
    assert len(r["clusters"]) == 2 and r["clusters"][0]["changed_pixels"] == 100 and r["clusters"][1]["changed_pixels"] == 16
    assert r["clusters"][0]["bbox"] == [16, 40, 32, 56] and r["bbox"] == [20, 5, 84, 50]


def test_vq_u11_parse_rect_and_threshold_validation(vq):
    import argparse
    assert vq.parse_rect("0,0,10,20") == [0, 0, 10, 20]
    for bad in ("1,2,3", "a,b,c,d", "10,10,5,20"):
        with pytest.raises(argparse.ArgumentTypeError):
            vq.parse_rect(bad)
    with pytest.raises(argparse.ArgumentTypeError):
        vq.non_negative_float("-1")
    assert vq.non_negative_float("0.5") == 0.5


# ------------------------------------------------------------------ unit: checklist
def test_vq_u12_build_checklist_profile_items(vq):
    cl = vq.build_checklist(json.loads(PROFILE.read_text(encoding="utf-8")), "gameplay")
    prof = [i for i in cl["items"] if i["source"] == "qa_criteria"]
    assert [i["id"] for i in prof] == ["QA-P-01", "QA-P-02", "QA-P-03", "QA-P-04"]
    assert all(i["status"] == "NOT RUN" and i["screen"] == "gameplay" for i in cl["items"])
    assert {"id", "text", "source", "screen", "status"} <= set(cl["items"][0])
    assert cl["project"] == "Onet Garden" and cl["kind"] == "game"


def test_vq_u13_checklist_screen_filtering(vq):
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    gameplay = {i["id"] for i in vq.build_checklist(profile, "gameplay")["items"]}
    shop = {i["id"] for i in vq.build_checklist(profile, "shop")["items"]}
    assert "QA-G-A4" in gameplay and "QA-G-A4" not in shop
    assert "QA-G-D3" in shop and "QA-G-D3" not in gameplay
    assert "QA-G-C1" in gameplay and "QA-G-C1" in shop
    home = {i["id"] for i in vq.build_checklist(profile, "home")["items"]}
    assert "QA-G-B1" not in home and "QA-G-B1" in shop
    rw = vq.build_checklist(profile, "rewards")
    assert rw["screen"] == "rewards" and rw["screen_type"] == "reward"
    assert "QA-A-01" in gameplay


def test_vq_u14_checklist_missing_qa_raises(vq):
    with pytest.raises(ValueError) as e:
        vq.build_checklist(json.loads(PROFILE_NO_QA.read_text(encoding="utf-8")))
    assert "qa_criteria" in str(e.value)
    with pytest.raises(ValueError):
        vq.build_checklist({"qa_criteria": "not a list"})


def test_vq_u15_checklist_app_kind_drops_game_items(vq):
    cl = vq.build_checklist({"product": {"kind": "app"}, "qa_criteria": ["x"]}, "gameplay")
    ids = {i["id"] for i in cl["items"]}
    assert "QA-G-A4" not in ids and "QA-G-D2" in ids
    md = vq.checklist_markdown(cl)
    assert md.startswith("# Visual QA checklist") and "- [ ] QA-P-01" in md and "gameplay" in md.splitlines()[0]


# ------------------------------------------------------------------ unit: manifest
@pytest.mark.parametrize("stack", STACKS)
def test_vq_u16_build_manifest_each_stack(vq, stack):
    mf = vq.build_manifest(stack, ["home", "gameplay"])
    assert mf["resolved_stack"] == stack and "not executed" in mf["note"]
    assert len(mf["entries"]) == 2 * len(mf["devices"])
    for e in mf["entries"]:
        assert e["executed"] is False and e["status"] == "NOT RUN" and "not executed" in e["note"]
        assert e["file"] == "%s_%s.png" % (e["screen"], e["device"])
        assert e["capture"]["tool"] in {"integration_test", "ScreenCapture", "playwright", "XCTest", "captureToImage"}
        assert "<<" not in e["capture"]["snippet"] and e["file"][:-4] in e["capture"]["snippet"] or e["file"] in e["capture"]["snippet"]
        assert e["screen"] in e["capture"]["snippet"]


def test_vq_u17_manifest_unknown_stack_device_and_aliases(vq):
    with pytest.raises(ValueError) as e:
        vq.build_manifest("cobol", ["home"])
    assert "supported" in str(e.value)
    with pytest.raises(ValueError):
        vq.build_manifest("web", ["home"], devices=["watch"])
    with pytest.raises(ValueError):
        vq.build_manifest("web", [""])
    assert vq.build_manifest("nextjs", ["home"])["resolved_stack"] == "web"


def test_vq_u18_manifest_profile_adds_tablet_and_custom_devices(vq):
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    names = [d["name"] for d in vq.build_manifest("flutter-flame", ["home"], profile=profile)["devices"]]
    assert names == ["phone-s", "phone-m", "phone-l", "tablet"]
    mf = vq.build_manifest("web", ["home"], devices=["desktop"])
    assert [d["name"] for d in mf["devices"]] == ["desktop"] and mf["entries"][0]["suggested_masks"][0]["region"] is None
    phone = vq.build_manifest("web", ["home"], devices=["phone-m"])["entries"][0]
    assert phone["suggested_masks"][0]["region"] == [0, 0, 390, 47] and phone["dpr"] == 3


# ------------------------------------------------------------------ CLI
def test_vq_c01_diff_identical_rc0(png_pair, tmp_path):
    a, _ = png_pair
    r = run_cli("diff", a, a, "--json", cwd=tmp_path)
    assert r.returncode == 0 and json.loads(r.stdout)["status"] == "PASS"


def test_vq_c02_diff_fail_rc1_with_bbox(png_pair, tmp_path):
    a, b = png_pair
    r = run_cli("diff", a, b, "--json", cwd=tmp_path)
    assert r.returncode == 1
    out = json.loads(r.stdout)
    assert out["status"] == "FAIL" and out["bbox"] == [20, 40, 30, 50] and out["diff_percent"] == pytest.approx(1.0)
    r2 = run_cli("diff", a, b, cwd=tmp_path)
    assert r2.returncode == 1 and r2.stdout.startswith("FAIL")


def test_vq_c03_diff_threshold_ignore_and_out(png_pair, tmp_path):
    a, b = png_pair
    assert run_cli("diff", a, b, "--threshold", "5", cwd=tmp_path).returncode == 0
    assert run_cli("diff", a, b, "--ignore", "20,40,30,50", cwd=tmp_path).returncode == 0
    r = run_cli("diff", a, b, "--out", tmp_path / "d.png", "--json", cwd=tmp_path)
    assert r.returncode == 1 and (tmp_path / "d.png").is_file()


def test_vq_c04_diff_without_pillow_subprocess_rc3(tmp_path):
    r = run_cli_without_pillow("diff", "a.png", "b.png", "--json", cwd=tmp_path)
    assert r.returncode == 3, r.stderr
    assert json.loads(r.stdout)["status"] == "BLOCKED" and "Traceback" not in r.stderr
    assert "BLOCKED: Pillow not installed" in r.stderr


def test_vq_c05_diff_with_fake_pil_package_rc3(tmp_path):
    fake = tmp_path / "fakepil" / "PIL"
    fake.mkdir(parents=True)
    (fake / "__init__.py").write_text("raise ImportError('fake PIL: Pillow is not installed on this machine')\n", encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(tmp_path / "fakepil")
    r = run_cli("diff", "a.png", "b.png", "--json", cwd=tmp_path, env=env)
    assert r.returncode == 3 and json.loads(r.stdout)["status"] == "BLOCKED" and "Traceback" not in r.stderr
    r2 = run_cli("diff", "a.png", "b.png", cwd=tmp_path, env=env)
    assert r2.returncode == 3 and r2.stdout.startswith("BLOCKED: Pillow not installed")


def test_vq_c06_diff_missing_file_rc3_not_2(png_pair, tmp_path):
    a, _ = png_pair
    r = run_cli("diff", a, tmp_path / "missing.png", "--json", cwd=tmp_path)
    assert r.returncode == 3 and "unreadable" in json.loads(r.stdout)["reason"]


def test_vq_c07_diff_size_mismatch_rc3(png_pair, tmp_path):
    Image = pytest.importorskip("PIL.Image")
    a, _ = png_pair
    Image.new("RGB", (120, 100)).save(tmp_path / "c.png")
    r = run_cli("diff", a, tmp_path / "c.png", cwd=tmp_path)
    assert r.returncode == 3 and "size mismatch" in r.stdout and "BLOCKED" in r.stderr


def test_vq_c08_diff_bad_args_rc2(tmp_path):
    assert run_cli("diff", "a.png", "b.png", "--threshold", "-1", cwd=tmp_path).returncode == 2
    assert run_cli("diff", "a.png", "b.png", "--threshold", "abc", cwd=tmp_path).returncode == 2
    assert run_cli("diff", "a.png", "b.png", "--ignore", "1,2,3", cwd=tmp_path).returncode == 2
    assert run_cli("diff", "a.png", cwd=tmp_path).returncode == 2


def test_vq_c09_checklist_json_and_md(tmp_path):
    r = run_cli("checklist", "--profile", PROFILE, "--screen", "gameplay", "--format", "json", cwd=tmp_path)
    assert r.returncode == 0
    cl = json.loads(r.stdout)
    assert cl["screen"] == "gameplay" and len(cl["items"]) >= 5 and all(i["status"] == "NOT RUN" for i in cl["items"])
    r = run_cli("checklist", "--profile", PROFILE, "--screen", "gameplay", "--out", tmp_path / "c.md", cwd=tmp_path)
    assert r.returncode == 0 and "gameplay" in r.stdout.splitlines()[0]
    assert all(l.startswith("- [ ]") for l in r.stdout.splitlines() if l.startswith("- "))
    assert (tmp_path / "c.md").read_text(encoding="utf-8") == r.stdout
    assert json.loads(run_cli("checklist", "--profile", PROFILE, "--json", cwd=tmp_path).stdout)["screen"] == "all"


def test_vq_c10_checklist_missing_rc2_invalid_rc1(tmp_path):
    assert run_cli("checklist", "--profile", tmp_path / "nope.json", cwd=tmp_path).returncode == 2
    r = run_cli("checklist", "--profile", PROFILE_NO_QA, cwd=tmp_path)
    assert r.returncode == 1 and "qa_criteria" in r.stderr
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    assert run_cli("checklist", "--profile", tmp_path / "bad.json", cwd=tmp_path).returncode == 1


def test_vq_c11_manifest_out_file(tmp_path):
    r = run_cli("manifest", "--stack", "flutter-flame", "--screens", "home,gameplay", "--out", tmp_path / "s.json", cwd=tmp_path)
    assert r.returncode == 0 and "not executed" in r.stdout
    mf = json.loads((tmp_path / "s.json").read_text(encoding="utf-8"))
    assert len(mf["entries"]) == 6 and all(e["status"] == "NOT RUN" for e in mf["entries"])
    assert mf["entries"][0]["file"] == "home_phone-s.png"
    rj = run_cli("manifest", "--stack", "web", "--screens", "home", "--json", "--profile", PROFILE, cwd=tmp_path)
    assert rj.returncode == 0 and json.loads(rj.stdout)["resolved_stack"] == "web"


def test_vq_c12_manifest_bad_stack_rc2(tmp_path):
    r = run_cli("manifest", "--stack", "cobol", "--screens", "home", cwd=tmp_path)
    assert r.returncode == 2 and "supported" in r.stderr
    assert run_cli("manifest", "--stack", "web", cwd=tmp_path).returncode == 2
    assert run_cli("manifest", "--stack", "web", "--screens", "home", "--profile", tmp_path / "nope.json", cwd=tmp_path).returncode == 2


def test_vq_c13_help_devices_and_no_args(tmp_path):
    assert run_cli(cwd=tmp_path).returncode == 2
    h = run_cli("diff", "--help", cwd=tmp_path)
    assert h.returncode == 0 and "PERCENT" in h.stdout and "3 BLOCKED" in h.stdout and "--json" in h.stdout
    for sub in ("checklist", "manifest", "devices"):
        r = run_cli(sub, "--help", cwd=tmp_path)
        assert r.returncode == 0 and "--json" in r.stdout
    d = json.loads(run_cli("devices", "--json", cwd=tmp_path).stdout)
    assert [x["name"] for x in d] == ["phone-s", "phone-m", "phone-l", "tablet", "desktop"]


# ------------------------------------------------------------------ final fix round (F-01)
def test_vq_f01_out_creates_parent_dirs(png_pair, tmp_path):
    a, b = png_pair
    r = run_cli("diff", a, b, "--out", "qa-logs/img/x.png", "--json", cwd=tmp_path)
    assert r.returncode == 1 and "Traceback" not in r.stderr and (tmp_path / "qa-logs" / "img" / "x.png").is_file()
    r = run_cli("checklist", "--profile", PROFILE, "--screen", "shop", "--out", "qa-logs/checklist-shop.md", cwd=tmp_path)
    assert r.returncode == 0 and (tmp_path / "qa-logs" / "checklist-shop.md").is_file()
    r = run_cli("manifest", "--stack", "flutter-flame", "--screens", "home", "--out", "qa-logs/deep/screens.json", cwd=tmp_path)
    assert r.returncode == 0 and (tmp_path / "qa-logs" / "deep" / "screens.json").is_file()


def test_vq_f01b_unexpected_exception_is_one_error_line_exit_2(vq, monkeypatch, capsys):
    def boom(*a, **k):
        raise RuntimeError("disk on fire")
    monkeypatch.setattr(vq, "build_manifest", boom)
    assert vq.main(["manifest", "--stack", "web", "--screens", "home"]) == 2
    err = capsys.readouterr().err
    assert err.strip() == "error: RuntimeError: disk on fire" and "Traceback" not in err


def test_vq_f01c_help_has_no_literal_double_percent(tmp_path):
    h = run_cli("diff", "--help", cwd=tmp_path).stdout
    assert "%%" not in h and "percent" in h.lower()


# ------------------------------------------------------------------ F-09: --screen accepts only known ids
KNOWN_IDS = ["home", "gameplay", "level-select", "pause", "win", "lose", "settings", "shop", "rewards", "profile", "tutorial"]


def test_vq_f09_known_screen_ids_and_groups(vq):
    assert list(vq.KNOWN_SCREENS) == KNOWN_IDS
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    for sid in KNOWN_IDS:
        cl = vq.build_checklist(profile, sid)
        assert cl["screen"] == sid and all(i["screen"] == sid for i in cl["items"])
    ids = lambda s: {i["id"] for i in vq.build_checklist(profile, s)["items"]}
    assert "QA-G-E3" in ids("win") and "QA-G-E3" in ids("lose") and "QA-G-E3" in ids("pause")  # result/popup states
    assert "QA-G-D3" in ids("rewards") and "QA-G-A4" in ids("gameplay")
    assert "QA-G-B1" not in ids("home") and "QA-G-B1" in ids("level-select") and "QA-G-B1" in ids("tutorial")
    assert vq.build_checklist(profile, "Shop")["screen"] == "shop"  # case-insensitive


@pytest.mark.parametrize("bad", ["cobol", "reward", "menu", "popup", "result", "store", "../shop", ""])
def test_vq_f09b_unknown_screen_raises_with_valid_list(vq, bad):
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    if bad == "":
        assert vq.build_checklist(profile, bad)["screen"] == "all"  # empty = no filter
        return
    with pytest.raises(vq.UnknownScreen) as e:
        vq.build_checklist(profile, bad)
    assert all(k in str(e.value) for k in KNOWN_IDS)


def test_vq_f09c_pages_next_to_profile_are_valid_screens(vq, tmp_path):
    d = tmp_path / "design-system" / "onet"
    (d / "pages").mkdir(parents=True)
    (d / "style-profile.json").write_text(PROFILE.read_text(encoding="utf-8"), encoding="utf-8")
    (d / "pages" / "boss-fight.md").write_text("# boss-fight overrides\n", encoding="utf-8")
    (d / "pages" / "Store.md").write_text("# store overrides\n", encoding="utf-8")
    assert vq.page_screens(str(d / "style-profile.json")) == ["boss-fight", "store"]
    assert vq.page_screens(str(PROFILE)) == []
    cl = vq.build_checklist(json.loads(PROFILE.read_text(encoding="utf-8")), "store", ["boss-fight", "store"])
    assert cl["screen"] == "store" and cl["screen_type"] == "shop" and "QA-G-D3" in {i["id"] for i in cl["items"]}
    r = run_cli("checklist", "--profile", d / "style-profile.json", "--screen", "boss-fight", "--json", cwd=tmp_path)
    assert r.returncode == 0 and json.loads(r.stdout)["screen"] == "boss-fight"
    r = run_cli("checklist", "--profile", d / "style-profile.json", "--screen", "cobol", cwd=tmp_path)
    assert r.returncode == 2 and "pages/boss-fight.md" in r.stderr and "level-select" in r.stderr


def test_vq_f09d_cli_unknown_screen_exit_2(tmp_path):
    r = run_cli("checklist", "--profile", PROFILE, "--screen", "cobol", cwd=tmp_path)
    assert r.returncode == 2 and r.stdout == "" and "Traceback" not in r.stderr
    assert r.stderr.startswith("error: unknown screen 'cobol'; valid ids: home, gameplay, level-select")
    # unknown screen is a usage error even when the profile itself is invalid (exit 2, not 1)
    assert run_cli("checklist", "--profile", PROFILE_NO_QA, "--screen", "cobol", cwd=tmp_path).returncode == 2
    h = run_cli("checklist", "--help", cwd=tmp_path).stdout
    assert all(k in h for k in KNOWN_IDS)
