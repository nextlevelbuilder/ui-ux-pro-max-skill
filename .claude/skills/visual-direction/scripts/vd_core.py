#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visual Direction core: compact CSV loader + BM25 search (stdlib only).

Deliberately independent from the orchestrator's core.py (sub-skills never import
across skill directories -- see docs/architecture/INTEGRATION_CONTRACT.md §2).
"""

import csv
import difflib
import re
from collections import defaultdict
from math import log
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 5

CATALOGS = {
    "styles": {
        "file": "visual-styles.csv",
        "id_col": "Style ID",
        "search_cols": ["Style ID", "Style Name", "Family", "Keywords", "Best For", "Mood",
                        "Shape Language", "Shading", "Illustration Style"],
    },
    "genres": {
        "file": "genre-profiles.csv",
        "id_col": "Genre ID",
        "search_cols": ["Genre ID", "Genre Name", "Kind", "Keywords", "Core Screens", "HUD Elements"],
    },
    "components": {
        "file": "component-catalog.csv",
        "id_col": "Component ID",
        "search_cols": ["Component ID", "Name", "Group", "Purpose", "Applies To"],
    },
}

_STOPWORDS = {"to", "in", "on", "at", "is", "of", "by", "or", "an", "if", "no", "so",
              "do", "be", "we", "it", "as", "the", "and", "for", "are", "was", "a"}
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#-]*")


def tokenize(text):
    return [t for t in _TOKEN_RE.findall(str(text).lower()) if t not in _STOPWORDS]


class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.doc_len, self.avgdl, self.df, self.idf, self.docs, self.n = [], 0.0, defaultdict(int), {}, [], 0

    def fit(self, documents):
        self.docs = [tokenize(d) for d in documents]
        self.n = len(self.docs)
        self.doc_len = [len(d) for d in self.docs]
        self.avgdl = (sum(self.doc_len) / self.n) if self.n else 0.0
        for d in self.docs:
            for term in set(d):
                self.df[term] += 1
        for term, df in self.df.items():
            self.idf[term] = log((self.n - df + 0.5) / (df + 0.5) + 1.0)
        return self

    def score(self, query):
        q = tokenize(query)
        scores = []
        for i, doc in enumerate(self.docs):
            s = 0.0
            if doc:
                counts = defaultdict(int)
                for t in doc:
                    counts[t] += 1
                for term in q:
                    if term in counts:
                        tf = counts[term]
                        s += self.idf.get(term, 0.0) * tf * (self.k1 + 1) / (
                            tf + self.k1 * (1 - self.b + self.b * self.doc_len[i] / (self.avgdl or 1)))
            scores.append(s)
        return scores

    @property
    def vocabulary(self):
        return set(self.df)


def load_rows(catalog):
    cfg = CATALOGS[catalog]
    path = DATA_DIR / cfg["file"]
    if not path.is_file():
        raise FileNotFoundError(f"catalog file missing: {path}")
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows


def row_by_id(catalog, identifier):
    cfg = CATALOGS[catalog]
    for row in load_rows(catalog):
        if row.get(cfg["id_col"], "").strip().lower() == identifier.strip().lower():
            return row
    return None


def closest_ids(catalog, identifier, limit=5):
    cfg = CATALOGS[catalog]
    ids = [r.get(cfg["id_col"], "") for r in load_rows(catalog)]
    return difflib.get_close_matches(identifier.lower(), ids, n=limit, cutoff=0.4)


def search(catalog, query, max_results=MAX_RESULTS, filters=None):
    """Return {"catalog", "query", "count", "results": [row + _score]} ranked by BM25.

    An exact id match is always returned first. `filters` is a dict of column -> value
    (case-insensitive equality) applied before ranking.
    """
    cfg = CATALOGS[catalog]
    rows = load_rows(catalog)
    if filters:
        rows = [r for r in rows if all(
            r.get(col, "").strip().lower() == str(val).strip().lower() for col, val in filters.items())]
    if not rows:
        return {"catalog": catalog, "query": query, "count": 0, "results": [], "suggestions": []}
    docs = [" ".join(r.get(c, "") for c in cfg["search_cols"]) for r in rows]
    index = BM25().fit(docs)
    scores = index.score(query)
    ranked = sorted(zip(scores, range(len(rows))), key=lambda p: (-p[0], p[1]))
    results = []
    exact = [r for r in rows if r.get(cfg["id_col"], "").lower() == query.strip().lower()]
    for r in exact:
        results.append(dict(r, _score=float("inf")))
    for score, idx in ranked:
        if score <= 0:
            continue
        row = rows[idx]
        if row in exact:
            continue
        results.append(dict(row, _score=round(score, 3)))
        if len(results) >= max_results:
            break
    suggestions = []
    if not results:
        vocab = sorted(index.vocabulary)
        for term in tokenize(query):
            suggestions.extend(difflib.get_close_matches(term, vocab, n=3, cutoff=0.6))
    return {"catalog": catalog, "query": query, "count": len(results),
            "results": results, "suggestions": sorted(set(suggestions))}


def split_list(value, sep="|"):
    """Split a ' | ' or ';' separated CSV cell into a clean list."""
    if value is None:
        return []
    parts = re.split(r"\s*[%s]\s*" % re.escape(sep), str(value))
    return [p.strip() for p in parts if p.strip()]
