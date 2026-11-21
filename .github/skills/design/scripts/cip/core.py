#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIP Design Core - BM25 search engine for Corporate Identity Program design guidelines
"""

import csv
import re
from pathlib import Path
from math import log
from collections import defaultdict

# ============ CONFIGURATION ============
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "cip"
MAX_RESULTS = 3

CSV_CONFIG = {
    "deliverable": {
        "file": "deliverables.csv",
        "search_cols": ["Deliverable", "Category", "Keywords", "Description", "Mockup Context"],
        "output_cols": ["Deliverable", "Category", "Keywords", "Description", "Dimensions", "File Format", "Logo Placement", "Color Usage", "Typography Notes", "Mockup Context", "Best Practices", "Avoid"]
    },
    "style": {
        "file": "styles.csv",
        "search_cols": ["Style Name", "Category", "Keywords", "Description", "Mood"],
        "output_cols": ["Style Name", "Category", "Keywords", "Description", "Primary Colors", "Secondary Colors", "Typography", "Materials", "Finishes", "Mood", "Best For", "Avoid For"]
    },
    "industry": {
        "file": "industries.csv",
        "search_cols": ["Industry", "Keywords", "CIP Style", "Mood"],
        "output_cols": ["Industry", "Keywords", "CIP Style", "Primary Colors", "Secondary Colors", "Typography", "Key Deliverables", "Mood", "Best Practices", "Avoid"]
    },
    "mockup": {
        "file": "mockup-contexts.csv",
        "search_cols": ["Context Name", "Category", "Keywords", "Scene Description"],
        "output_cols": ["Context Name", "Category", "Keywords", "Scene Description", "Lighting", "Environment", "Props", "Camera Angle", "Background", "Style Notes", "Best For", "Prompt Modifiers"]
    }
}


# ============ BM25 IMPLEMENTATION ============
class BM25:
    """BM25 ranking algorithm for text search"""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_lengths = []
        self.avgdl = 0
        self.idf = {}
        self.doc_freqs = defaultdict(int)
        self.N = 0

    def tokenize(self, text):
        """Lowercase, split, remove punctuation, filter short words"""
        text = re.sub(r'[^\w\s]', ' ', str(text).lower())
        return [w for w in text.split() if len(w) > 2]

    def fit(self, documents):
        """Build BM25 index from documents"""
        self.corpus = [self.tokenize(doc) for doc in documents]
        self.N = len(self.corpus)
        if self.N == 0:
            return
        self.doc_lengths = [len(doc) for doc in self.corpus]
        self.avgdl = sum(self.doc_lengths) / self.N

        for doc in self.corpus:
            seen = set()
            for word in doc:
                if word not in seen:
                    self.doc_freqs[word] += 1
                    seen.add(word)

        for word, freq in self.doc_freqs.items():
            self.idf[word] = log((self.N - freq + 0.5) / (freq + 0.5) + 1)

    def score(self, query):
        """Score all documents against query"""
        query_tokens = self.tokenize(query)
        scores = []

        for idx, doc in enumerate(self.corpus):
            score = 0
            doc_len = self.doc_lengths[idx]
            term_freqs = defaultdict(int)
            for word in doc:
                term_freqs[word] += 1

            for token in query_tokens:
                if token in self.idf:
                    tf = term_freqs[token]
                    idf = self.idf[token]
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                    score += idf * numerator / denominator

            scores.append((idx, score))

        return sorted(scores, key=lambda x: x[1], reverse=True)


# ============ SEARCH FUNCTIONS ============
def _load_csv(filepath):
    """Load CSV and return list of dicts"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _search_csv(filepath, search_cols, output_cols, query, max_results):
    """Core search function using BM25"""
    if not filepath.exists():
        return []

    data = _load_csv(filepath)

    # Build documents from search columns
    documents = [" ".join(str(row.get(col, "")) for col in search_cols) for row in data]

    # BM25 search
    bm25 = BM25()
    bm25.fit(documents)
    ranked = bm25.score(query)

    # Get top results with score > 0
    results = []
    for idx, score in ranked[:max_results]:
        if score > 0:
            row = data[idx]
            results.append({col: row.get(col, "") for col in output_cols if col in row})

    return results


def detect_domain(query):
    """Auto-detect the most relevant domain from query"""
    query_lower = query.lower()

    domain_keywords = {
        "deliverable": ["card", "letterhead", "envelope", "folder", "shirt", "cap", "badge", "signage", "vehicle", "car", "van", "stationery", "uniform", "merchandise", "packaging", "banner", "booth"],
        "style": ["style", "minimal", "modern", "luxury", "vintage", "industrial", "elegant", "bold", "corporate", "organic", "playful"],
        "industry": ["tech", "finance", "legal", "healthcare", "hospitality", "food", "fashion", "retail", "construction", "logistics"],
        "mockup": ["mockup", "scene", "context", "photo", "shot", "lighting", "background", "studio", "lifestyle"]
    }

    scores = {domain: sum(1 for kw in keywords if kw in query_lower) for domain, keywords in domain_keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "deliverable"


def search(query, domain=None, max_results=MAX_RESULTS):
    """Main search function with auto-domain detection"""
    if domain is None:
        domain = detect_domain(query)

    config = CSV_CONFIG.get(domain, CSV_CONFIG["deliverable"])
    filepath = DATA_DIR / config["file"]

    if not filepath.exists():
        return {"error": f"File not found: {filepath}", "domain": domain}

    results = _search_csv(filepath, config["search_cols"], config["output_cols"], query, max_results)

    return {
        "domain": domain,
        "query": query,
        "file": config["file"],
        "count": len(results),
        "results": results
    }


def search_all(query, max_results=2):
    """Search across all domains and combine results"""
    all_results = {}
    for domain in CSV_CONFIG.keys():
        result = search(query, domain, max_results)
        if result.get("results"):
            all_results[domain] = result["results"]
    return all_results


def get_cip_brief(brand_name, industry_query, style_query=None):
    """Generate a comprehensive CIP brief for a brand"""
    # Search industry
    industry_results = search(industry_query, "industry", 1)
    industry = industry_results.get("results", [{}])[0] if industry_results.get("results") else {}

    # Search style (use industry style if not specified)
    style_query = style_query or industry.get("CIP Style", "corporate minimal")
    style_results = search(style_query, "style", 1)
    style = style_results.get("results", [{}])[0] if style_results.get("results") else {}

    # Get recommended deliverables for the industry
    key_deliverables = industry.get("Key Deliverables", "").split()
    deliverable_results = []
    for d in key_deliverables[:5]:
        result = search(d, "deliverable", 1)
        if result.get("results"):
            deliverable_results.append(result["results"][0])

    return {
        "brand_name": brand_name,
        "industry": industry,
        "style": style,
        "recommended_deliverables": deliverable_results,
        "color_system": {
            "primary": style.get("Primary Colors", industry.get("Primary Colors", "")),
            "secondary": style.get("Secondary Colors", industry.get("Secondary Colors", ""))
        },
        "typography": style.get("Typography", industry.get("Typography", "")),
        "materials": style.get("Materials", ""),
        "finishes": style.get("Finishes", "")
    }
