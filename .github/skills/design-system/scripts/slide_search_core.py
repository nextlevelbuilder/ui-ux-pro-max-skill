#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slide Search Core - BM25 search engine for slide design databases
"""

import csv
import re
from pathlib import Path
from math import log
from collections import defaultdict

# ============ CONFIGURATION ============
DATA_DIR = Path(__file__).parent.parent / "data"
MAX_RESULTS = 3

CSV_CONFIG = {
    "strategy": {
        "file": "slide-strategies.csv",
        "search_cols": ["strategy_name", "keywords", "goal", "audience", "narrative_arc"],
        "output_cols": ["strategy_name", "keywords", "slide_count", "structure", "goal", "audience", "tone", "narrative_arc", "sources"]
    },
    "layout": {
        "file": "slide-layouts.csv",
        "search_cols": ["layout_name", "keywords", "use_case", "recommended_for"],
        "output_cols": ["layout_name", "keywords", "use_case", "content_zones", "visual_weight", "cta_placement", "recommended_for", "avoid_for", "css_structure"]
    },
    "copy": {
        "file": "slide-copy.csv",
        "search_cols": ["formula_name", "keywords", "use_case", "emotion_trigger", "slide_type"],
        "output_cols": ["formula_name", "keywords", "components", "use_case", "example_template", "emotion_trigger", "slide_type", "source"]
    },
    "chart": {
        "file": "slide-charts.csv",
        "search_cols": ["chart_type", "keywords", "best_for", "when_to_use", "slide_context"],
        "output_cols": ["chart_type", "keywords", "best_for", "data_type", "when_to_use", "when_to_avoid", "max_categories", "slide_context", "css_implementation", "accessibility_notes"]
    }
}

AVAILABLE_DOMAINS = list(CSV_CONFIG.keys())


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
        "strategy": ["pitch", "deck", "investor", "yc", "seed", "series", "demo", "sales", "webinar",
                     "conference", "board", "qbr", "all-hands", "duarte", "kawasaki", "structure"],
        "layout": ["slide", "layout", "grid", "column", "title", "hero", "section", "cta",
                   "screenshot", "quote", "timeline", "comparison", "pricing", "team"],
        "copy": ["headline", "copy", "formula", "aida", "pas", "hook", "cta", "benefit",
                 "objection", "proof", "testimonial", "urgency", "scarcity"],
        "chart": ["chart", "graph", "bar", "line", "pie", "funnel", "metrics", "data",
                  "visualization", "kpi", "trend", "comparison", "heatmap", "gauge"]
    }

    scores = {domain: sum(1 for kw in keywords if kw in query_lower) for domain, keywords in domain_keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "strategy"


def search(query, domain=None, max_results=MAX_RESULTS):
    """Main search function with auto-domain detection"""
    if domain is None:
        domain = detect_domain(query)

    config = CSV_CONFIG.get(domain, CSV_CONFIG["strategy"])
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
    """Search across all domains for comprehensive results"""
    all_results = {}

    for domain in AVAILABLE_DOMAINS:
        result = search(query, domain, max_results)
        if result.get("count", 0) > 0:
            all_results[domain] = result

    return all_results


# ============ CONTEXTUAL SEARCH (Premium Slide System) ============

# New CSV configurations for decision system
DECISION_CSV_CONFIG = {
    "layout-logic": {
        "file": "slide-layout-logic.csv",
        "key_col": "goal"
    },
    "typography": {
        "file": "slide-typography.csv",
        "key_col": "content_type"
    },
    "color-logic": {
        "file": "slide-color-logic.csv",
        "key_col": "emotion"
    },
    "backgrounds": {
        "file": "slide-backgrounds.csv",
        "key_col": "slide_type"
    }
}


def _load_decision_csv(csv_type):
    """Load a decision CSV and return as dict keyed by primary column."""
    config = DECISION_CSV_CONFIG.get(csv_type)
    if not config:
        return {}

    filepath = DATA_DIR / config["file"]
    if not filepath.exists():
        return {}

    data = _load_csv(filepath)
    return {row[config["key_col"]]: row for row in data if config["key_col"] in row}


def get_layout_for_goal(goal, previous_emotion=None):
    """
    Get layout recommendation based on slide goal.
    Uses slide-layout-logic.csv for decision.
    """
    layouts = _load_decision_csv("layout-logic")
    row = layouts.get(goal, layouts.get("features", {}))

    result = dict(row) if row else {}

    # Apply pattern-breaking logic
    if result.get("break_pattern") == "true" and previous_emotion:
        result["_pattern_break"] = True
        result["_contrast_with"] = previous_emotion

    return result


def get_typography_for_slide(slide_type, has_metrics=False, has_quote=False):
    """
    Get typography recommendation based on slide content.
    Uses slide-typography.csv for decision.
    """
    typography = _load_decision_csv("typography")

    if has_metrics:
        return typography.get("metric-callout", {})
    if has_quote:
        return typography.get("quote-block", {})

    # Map slide types to typography
    type_map = {
        "hero": "hero-statement",
        "hook": "hero-statement",
        "title": "title-only",
        "problem": "subtitle-heavy",
        "agitation": "metric-callout",
        "solution": "subtitle-heavy",
        "features": "feature-grid",
        "proof": "metric-callout",
        "traction": "data-insight",
        "social": "quote-block",
        "testimonial": "testimonial",
        "pricing": "pricing",
        "team": "team",
        "cta": "cta-action",
        "comparison": "comparison",
        "timeline": "timeline",
    }

    content_type = type_map.get(slide_type, "feature-grid")
    return typography.get(content_type, {})


def get_color_for_emotion(emotion):
    """
    Get color treatment based on emotional beat.
    Uses slide-color-logic.csv for decision.
    """
    colors = _load_decision_csv("color-logic")
    return colors.get(emotion, colors.get("clarity", {}))


def get_background_config(slide_type):
    """
    Get background image configuration.
    Uses slide-backgrounds.csv for decision.
    """
    backgrounds = _load_decision_csv("backgrounds")
    return backgrounds.get(slide_type, {})


def should_use_full_bleed(slide_index, total_slides, emotion):
    """
    Determine if slide should use full-bleed background.
    Premium decks use 2-3 full-bleed slides strategically.

    Rules:
    1. Never consecutive full-bleed
    2. One in first third, one in middle, one at end
    3. Reserved for high-emotion beats (hope, urgency, fear)
    """
    high_emotion_beats = ["hope", "urgency", "fear", "curiosity"]

    if emotion not in high_emotion_beats:
        return False

    if total_slides < 3:
        return False

    third = total_slides // 3
    strategic_positions = [1, third, third * 2, total_slides - 1]

    return slide_index in strategic_positions


def calculate_pattern_break(slide_index, total_slides, previous_emotion=None):
    """
    Determine if this slide should break the visual pattern.
    Used for emotional contrast (Duarte Sparkline technique).
    """
    # Pattern breaks at strategic positions
    if total_slides < 5:
        return False

    # Break at 1/3 and 2/3 points
    third = total_slides // 3
    if slide_index in [third, third * 2]:
        return True

    # Break when switching between frustration and hope
    contrasting_emotions = {
        "frustration": ["hope", "relief"],
        "hope": ["frustration", "fear"],
        "fear": ["hope", "relief"],
    }

    if previous_emotion in contrasting_emotions:
        return True

    return False


def search_with_context(query, slide_position=1, total_slides=9, previous_emotion=None):
    """
    Enhanced search that considers deck context.

    Args:
        query: Search query
        slide_position: Current slide index (1-based)
        total_slides: Total slides in deck
        previous_emotion: Emotion of previous slide (for contrast)

    Returns:
        Search results enriched with contextual recommendations
    """
    # Get base results from existing BM25 search
    base_results = search_all(query, max_results=2)

    # Detect likely slide goal from query
    goal = detect_domain(query.lower())
    if "problem" in query.lower():
        goal = "problem"
    elif "solution" in query.lower():
        goal = "solution"
    elif "cta" in query.lower() or "call to action" in query.lower():
        goal = "cta"
    elif "hook" in query.lower() or "title" in query.lower():
        goal = "hook"
    elif "traction" in query.lower() or "metric" in query.lower():
        goal = "traction"

    # Enrich with contextual recommendations
    context = {
        "slide_position": slide_position,
        "total_slides": total_slides,
        "previous_emotion": previous_emotion,
        "inferred_goal": goal,
    }

    # Get layout recommendation
    layout = get_layout_for_goal(goal, previous_emotion)
    if layout:
        context["recommended_layout"] = layout.get("layout_pattern")
        context["layout_direction"] = layout.get("direction")
        context["visual_weight"] = layout.get("visual_weight")
        context["use_background_image"] = layout.get("use_bg_image") == "true"

    # Get typography recommendation
    typography = get_typography_for_slide(goal)
    if typography:
        context["typography"] = {
            "primary_size": typography.get("primary_size"),
            "secondary_size": typography.get("secondary_size"),
            "weight_contrast": typography.get("weight_contrast"),
        }

    # Get color treatment
    emotion = layout.get("emotion", "clarity") if layout else "clarity"
    color = get_color_for_emotion(emotion)
    if color:
        context["color_treatment"] = {
            "background": color.get("background"),
            "text_color": color.get("text_color"),
            "accent_usage": color.get("accent_usage"),
            "card_style": color.get("card_style"),
        }

    # Calculate pattern breaking
    context["should_break_pattern"] = calculate_pattern_break(
        slide_position, total_slides, previous_emotion
    )
    context["should_use_full_bleed"] = should_use_full_bleed(
        slide_position, total_slides, emotion
    )

    # Get background config if needed
    if context.get("use_background_image"):
        bg_config = get_background_config(goal)
        if bg_config:
            context["background"] = {
                "image_category": bg_config.get("image_category"),
                "overlay_style": bg_config.get("overlay_style"),
                "search_keywords": bg_config.get("search_keywords"),
            }

    # Suggested animation classes
    animation_map = {
        "hook": "animate-fade-up",
        "problem": "animate-fade-up",
        "agitation": "animate-count animate-stagger",
        "solution": "animate-scale",
        "features": "animate-stagger",
        "traction": "animate-chart animate-count",
        "proof": "animate-stagger-scale",
        "social": "animate-fade-up",
        "cta": "animate-pulse",
    }
    context["animation_class"] = animation_map.get(goal, "animate-fade-up")

    return {
        "query": query,
        "context": context,
        "base_results": base_results,
    }
