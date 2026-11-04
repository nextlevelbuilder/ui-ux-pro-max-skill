"""Unit tests for vd_core.py (catalog loader + BM25 search). Offline, no writes outside tmp_path."""

import importlib.util
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent


def load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def core():
    return load_module("vd_core.py", "vd_core_under_test")


MIN_ROWS = {"styles": 12, "genres": 10, "components": 25}


@pytest.mark.parametrize("catalog", ["styles", "genres", "components"])
def test_vd_u01_load_rows_reads_every_catalog(core, catalog):
    rows = core.load_rows(catalog)
    id_col = core.CATALOGS[catalog]["id_col"]
    assert len(rows) >= MIN_ROWS[catalog]
    assert all(r.get(id_col, "").strip() for r in rows)
    assert None not in rows[0] and None not in rows[0].values()


def test_vd_u02_load_rows_missing_file(core, tmp_path, monkeypatch):
    monkeypatch.setattr(core, "DATA_DIR", tmp_path)
    with pytest.raises(FileNotFoundError) as exc:
        core.load_rows("styles")
    assert str(tmp_path) in str(exc.value)


def test_vd_u03_row_by_id_case_insensitive_and_unknown(core):
    first = core.load_rows("styles")[0]["Style ID"]
    row = core.row_by_id("styles", "  %s " % first.upper())
    assert row is not None and row["Style ID"] == first
    assert core.row_by_id("styles", "does-not-exist") is None


def test_vd_u04_closest_ids_suggests_on_typo(core):
    first = core.load_rows("styles")[0]["Style ID"]
    typo = first[:-1]
    close = core.closest_ids("styles", typo)
    assert close and first in close
    assert len(core.closest_ids("styles", typo, limit=1)) == 1
    assert core.closest_ids("styles", "zzzz") == []


def test_vd_u05_search_exact_id_first(core):
    first = core.load_rows("genres")[0]["Genre ID"]
    result = core.search("genres", first)
    assert result["count"] >= 1
    assert result["results"][0]["Genre ID"] == first
    assert result["results"][0]["_score"] == float("inf")


def test_vd_u06_search_ranks_by_keywords(core):
    row = core.load_rows("styles")[0]
    words = core.split_list(row["Keywords"], ",")[:3]
    result = core.search("styles", " ".join(words))
    top = [r["Style ID"] for r in result["results"][:3]]
    assert row["Style ID"] in top


def test_vd_u07_search_zero_results_suggests(core):
    result = core.search("styles", "kawai")
    assert result["count"] == 0 and result["results"] == []
    assert "kawaii" in result["suggestions"]


def test_vd_u08_search_filters(core):
    result = core.search("genres", "puzzle", filters={"Kind": "game"})
    assert result["count"] >= 1
    assert all(r["Kind"].lower() == "game" for r in result["results"])
    none = core.search("genres", "puzzle", filters={"Kind": "cobol"})
    assert none["count"] == 0 and none["suggestions"] == []


def test_vd_u09_search_max_results_honoured(core):
    result = core.search("styles", "cute casual game", max_results=2)
    assert len(result["results"]) <= 2


@pytest.mark.parametrize("value,sep,expected", [
    ("a | b|c ", "|", ["a", "b", "c"]),
    ("a; b", ";", ["a", "b"]),
    (None, "|", []),
    ("", "|", []),
])
def test_vd_u10_split_list(core, value, sep, expected):
    assert core.split_list(value, sep) == expected


def test_vd_u11_tokenize_drops_stopwords_keeps_symbols(core):
    assert core.tokenize("The UI of C# and ui+ux") == ["ui", "c#", "ui+ux"]


def test_vd_u12_bm25_deterministic(core):
    a = [r["Component ID"] for r in core.search("components", "popup reward coins")["results"]]
    b = [r["Component ID"] for r in core.search("components", "popup reward coins")["results"]]
    assert a == b and a


def test_bm25_empty_corpus_is_safe(core):
    index = core.BM25().fit([])
    assert index.score("anything") == []
    assert index.vocabulary == set()
