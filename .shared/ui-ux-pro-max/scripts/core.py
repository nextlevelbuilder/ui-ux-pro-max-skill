#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Core - BM25 search engine for UI/UX style guides
"""

import csv
import re
from pathlib import Path
from math import log
from collections import defaultdict
from typing import Dict, List, Optional, Any

# Import external configuration modules
try:
    from .config_loader import ConfigLoader
    from .brand_processor import BrandProcessor
    EXTERNAL_CONFIG_AVAILABLE = True
except ImportError:
    try:
        from config_loader import ConfigLoader
        from brand_processor import BrandProcessor
        EXTERNAL_CONFIG_AVAILABLE = True
    except ImportError:
        EXTERNAL_CONFIG_AVAILABLE = False

# ============ CONFIGURATION ============
DATA_DIR = Path(__file__).parent.parent / "data"
MAX_RESULTS = 3

CSV_CONFIG = {
    "style": {
        "file": "styles.csv",
        "search_cols": ["Style Category", "Keywords", "Best For", "Type"],
        "output_cols": ["Style Category", "Type", "Keywords", "Primary Colors", "Effects & Animation", "Best For", "Performance", "Accessibility", "Framework Compatibility", "Complexity"]
    },
    "prompt": {
        "file": "prompts.csv",
        "search_cols": ["Style Category", "AI Prompt Keywords (Copy-Paste Ready)", "CSS/Technical Keywords"],
        "output_cols": ["Style Category", "AI Prompt Keywords (Copy-Paste Ready)", "CSS/Technical Keywords", "Implementation Checklist"]
    },
    "color": {
        "file": "colors.csv",
        "search_cols": ["Product Type", "Keywords", "Notes"],
        "output_cols": ["Product Type", "Keywords", "Primary (Hex)", "Secondary (Hex)", "CTA (Hex)", "Background (Hex)", "Text (Hex)", "Border (Hex)", "Notes"]
    },
    "chart": {
        "file": "charts.csv",
        "search_cols": ["Data Type", "Keywords", "Best Chart Type", "Accessibility Notes"],
        "output_cols": ["Data Type", "Keywords", "Best Chart Type", "Secondary Options", "Color Guidance", "Accessibility Notes", "Library Recommendation", "Interactive Level"]
    },
    "landing": {
        "file": "landing.csv",
        "search_cols": ["Pattern Name", "Keywords", "Conversion Optimization", "Section Order"],
        "output_cols": ["Pattern Name", "Keywords", "Section Order", "Primary CTA Placement", "Color Strategy", "Conversion Optimization"]
    },
    "product": {
        "file": "products.csv",
        "search_cols": ["Product Type", "Keywords", "Primary Style Recommendation", "Key Considerations"],
        "output_cols": ["Product Type", "Keywords", "Primary Style Recommendation", "Secondary Styles", "Landing Page Pattern", "Dashboard Style (if applicable)", "Color Palette Focus"]
    },
    "ux": {
        "file": "ux-guidelines.csv",
        "search_cols": ["Category", "Issue", "Description", "Platform"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "typography": {
        "file": "typography.csv",
        "search_cols": ["Font Pairing Name", "Category", "Mood/Style Keywords", "Best For", "Heading Font", "Body Font"],
        "output_cols": ["Font Pairing Name", "Category", "Heading Font", "Body Font", "Mood/Style Keywords", "Best For", "Google Fonts URL", "CSS Import", "Tailwind Config", "Notes"]
    },
    "icons": {
        "file": "icons.csv",
        "search_cols": ["Category", "Icon Name", "Keywords", "Best For"],
        "output_cols": ["Category", "Icon Name", "Keywords", "Library", "Import Code", "Usage", "Best For", "Style"]
    },
    "react": {
        "file": "react-performance.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "web": {
        "file": "web-interface.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "ai-chat": {
        "file": "ai-chat-patterns.csv",
        "search_cols": ["Pattern_Name", "Category", "Description", "UX_Principle", "Use_Cases"],
        "output_cols": ["Pattern_Name", "Category", "Description", "Visual_Design", "Interaction_Behavior", "Code_Example_Good", "UX_Principle", "Technical_Implementation", "Use_Cases", "Anti_Patterns", "Severity"]
    },
    "architecture": {
        "file": "architecture.csv",
        "search_cols": ["term", "description", "examples", "reasoning"],
        "output_cols": ["term", "description", "examples", "code_example", "reasoning", "category", "priority"]
    }
}

STACK_CONFIG = {
    "html-tailwind": {"file": "stacks/html-tailwind.csv"},
    "react": {"file": "stacks/react.csv"},
    "nextjs": {"file": "stacks/nextjs.csv"},
    "vue": {"file": "stacks/vue.csv"},
    "nuxtjs": {"file": "stacks/nuxtjs.csv"},
    "nuxt-ui": {"file": "stacks/nuxt-ui.csv"},
    "svelte": {"file": "stacks/svelte.csv"},
    "swiftui": {"file": "stacks/swiftui.csv"},
    "react-native": {"file": "stacks/react-native.csv"},
    "flutter": {"file": "stacks/flutter.csv"},
    "shadcn": {"file": "stacks/shadcn.csv"},
    "jetpack-compose": {"file": "stacks/jetpack-compose.csv"},
    "htmx-alpine-axum": {"file": "stacks/htmx-alpine-axum.csv"},
    "tauri": {"file": "stacks/tauri.csv"}
}

# Common columns for all stacks
_STACK_COLS = {
    "search_cols": ["Category", "Guideline", "Description", "Do", "Don't"],
    "output_cols": ["Category", "Guideline", "Description", "Do", "Don't", "Code Good", "Code Bad", "Severity", "Docs URL"]
}

AVAILABLE_STACKS = list(STACK_CONFIG.keys())


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
        "color": ["color", "palette", "hex", "#", "rgb"],
        "chart": ["chart", "graph", "visualization", "trend", "bar", "pie", "scatter", "heatmap", "funnel"],
        "landing": ["landing", "page", "cta", "conversion", "hero", "testimonial", "pricing", "section"],
        "product": ["saas", "ecommerce", "e-commerce", "fintech", "healthcare", "gaming", "portfolio", "crypto", "dashboard"],
        "prompt": ["prompt", "css", "implementation", "variable", "checklist", "tailwind"],
        "style": ["style", "design", "ui", "minimalism", "glassmorphism", "neumorphism", "brutalism", "dark mode", "flat", "aurora"],
        "ux": ["ux", "usability", "accessibility", "wcag", "touch", "scroll", "animation", "keyboard", "navigation", "mobile"],
        "typography": ["font", "typography", "heading", "serif", "sans"],
        "icons": ["icon", "icons", "lucide", "heroicons", "symbol", "glyph", "pictogram", "svg icon"],
        "react": ["react", "next.js", "nextjs", "suspense", "memo", "usecallback", "useeffect", "rerender", "bundle", "waterfall", "barrel", "dynamic import", "rsc", "server component"],
        "web": ["aria", "focus", "outline", "semantic", "virtualize", "autocomplete", "form", "input type", "preconnect"],
        "ai-chat": ["ai", "chat", "chatbot", "streaming", "thinking", "reasoning", "tool execution", "citation", "confidence", "uncertainty", "conversation", "branching", "multi-modal", "feedback", "error recovery", "transparency", "trust", "ai interface", "llm", "gpt", "claude"],
        "architecture": ["architecture", "clean architecture", "hexagonal", "feature", "domain", "ddd", "domain-driven", "layer", "separation", "modular", "structure", "organization", "pattern", "boundary", "aggregate", "entity", "use case", "port", "adapter", "slice"]
    }

    scores = {domain: sum(1 for kw in keywords if kw in query_lower) for domain, keywords in domain_keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "style"


def search(query, domain=None, max_results=MAX_RESULTS):
    """Main search function with auto-domain detection"""
    if domain is None:
        domain = detect_domain(query)

    config = CSV_CONFIG.get(domain, CSV_CONFIG["style"])
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


def search_stack(query, stack, max_results=MAX_RESULTS):
    """Search stack-specific guidelines"""
    if stack not in STACK_CONFIG:
        return {"error": f"Unknown stack: {stack}. Available: {', '.join(AVAILABLE_STACKS)}"}

    filepath = DATA_DIR / STACK_CONFIG[stack]["file"]

    if not filepath.exists():
        return {"error": f"Stack file not found: {filepath}", "stack": stack}

    results = _search_csv(filepath, _STACK_COLS["search_cols"], _STACK_COLS["output_cols"], query, max_results)

    return {
        "domain": "stack",
        "stack": stack,
        "query": query,
        "file": STACK_CONFIG[stack]["file"],
        "count": len(results),
        "results": results
    }


# ============ EXTERNAL CONFIGURATION SUPPORT ============

def search_with_external_config(query: str, domain: Optional[str] = None,
                               stack: Optional[str] = None,
                               max_results: int = MAX_RESULTS,
                               config_path: Optional[str] = None,
                               apply_brand: bool = True) -> Dict[str, Any]:
    """
    Enhanced search function with external configuration support

    Args:
        query: Search query string
        domain: Domain filter (optional, auto-detected if None)
        stack: Stack filter (optional)
        max_results: Maximum number of results to return
        config_path: Path to external configuration directory
        apply_brand: Whether to apply brand configuration to results

    Returns:
        Search results with external configuration and brand integration applied
    """
    if not EXTERNAL_CONFIG_AVAILABLE:
        # Fall back to standard search if external config is not available
        if stack:
            return search_stack(query, stack, max_results)
        else:
            return search(query, domain, max_results)

    # Load external configuration
    config_loader = ConfigLoader(config_path)
    external_config = config_loader.load_external_config()

    # Get built-in data
    builtin_data = _get_builtin_data()

    # Merge external and built-in data
    merged_data = config_loader.merge_with_builtin(external_config, builtin_data)

    # Perform search on merged data
    if stack:
        results = _search_with_merged_data_stack(query, stack, merged_data, max_results)
    else:
        results = _search_with_merged_data_domain(query, domain, merged_data, max_results)

    # Apply brand configuration if enabled and available
    if (apply_brand and external_config.get("brand", {}).get("enabled", False)
        and "config" in external_config.get("brand", {})):
        brand_processor = BrandProcessor()
        if "results" in results:
            results["results"] = brand_processor.apply_brand_config(
                results["results"],
                external_config["brand"]["config"]
            )
            results["brand_applied"] = True

    # Add external configuration metadata
    results["external_config"] = {
        "enabled": external_config["enabled"],
        "domains_loaded": len(external_config.get("domains", {}).get("files", [])),
        "stacks_loaded": len(external_config.get("stacks", {}).get("files", [])),
        "brand_enabled": external_config.get("brand", {}).get("enabled", False),
        "total_external_entries": external_config.get("performance", {}).get("current_entries", 0)
    }

    return results


def _get_builtin_data() -> Dict[str, List[Dict]]:
    """Load all built-in CSV data for merging"""
    builtin_data = {
        "domains": [],
        "stacks": []
    }

    # Load domain data
    for domain_name, config in CSV_CONFIG.items():
        filepath = DATA_DIR / config["file"]
        if filepath.exists():
            try:
                domain_data = _load_csv(filepath)
                # Add metadata to each row
                for row in domain_data:
                    row["_domain"] = domain_name
                    row["_source"] = "builtin"
                builtin_data["domains"].extend(domain_data)
            except Exception:
                # Skip files that can't be loaded
                continue

    # Load stack data
    for stack_name, config in STACK_CONFIG.items():
        filepath = DATA_DIR / config["file"]
        if filepath.exists():
            try:
                stack_data = _load_csv(filepath)
                # Add metadata to each row
                for row in stack_data:
                    row["_stack"] = stack_name
                    row["_source"] = "builtin"
                builtin_data["stacks"].extend(stack_data)
            except Exception:
                # Skip files that can't be loaded
                continue

    return builtin_data


def _search_with_merged_data_domain(query: str, domain: Optional[str],
                                  merged_data: Dict, max_results: int) -> Dict[str, Any]:
    """Search domain data with merged external and built-in data"""
    if domain is None:
        domain = detect_domain(query)

    # Get all domain data (built-in + external)
    all_domain_data = merged_data.get("domains", [])

    # Filter by domain if specified and not searching external data
    domain_filtered_data = []
    for row in all_domain_data:
        if "_domain" in row and row["_domain"] == domain:
            domain_filtered_data.append(row)
        elif "_source" in row and row["_source"] != "builtin":
            # Include external data regardless of domain
            domain_filtered_data.append(row)

    if not domain_filtered_data:
        # Fall back to standard search if no merged data
        return search(query, domain, max_results)

    # Use the search columns from the domain config
    config = CSV_CONFIG.get(domain, CSV_CONFIG["style"])
    search_cols = config["search_cols"]
    output_cols = config["output_cols"]

    # Perform BM25 search on merged data
    results = _search_data_list(domain_filtered_data, search_cols, output_cols, query, max_results)

    return {
        "domain": domain,
        "query": query,
        "source": "merged_data",
        "count": len(results),
        "results": results
    }


def _search_with_merged_data_stack(query: str, stack: str,
                                 merged_data: Dict, max_results: int) -> Dict[str, Any]:
    """Search stack data with merged external and built-in data"""
    if stack not in STACK_CONFIG:
        return {"error": f"Unknown stack: {stack}. Available: {', '.join(AVAILABLE_STACKS)}"}

    # Get all stack data (built-in + external)
    all_stack_data = merged_data.get("stacks", [])

    # Filter by stack if specified and not searching external data
    stack_filtered_data = []
    for row in all_stack_data:
        if "_stack" in row and row["_stack"] == stack:
            stack_filtered_data.append(row)
        elif "_source" in row and row["_source"] != "builtin":
            # Include external stack data
            stack_filtered_data.append(row)

    if not stack_filtered_data:
        # Fall back to standard search if no merged data
        return search_stack(query, stack, max_results)

    # Use stack search columns
    search_cols = _STACK_COLS["search_cols"]
    output_cols = _STACK_COLS["output_cols"]

    # Perform BM25 search on merged data
    results = _search_data_list(stack_filtered_data, search_cols, output_cols, query, max_results)

    return {
        "domain": "stack",
        "stack": stack,
        "query": query,
        "source": "merged_data",
        "count": len(results),
        "results": results
    }


def _search_data_list(data_list: List[Dict], search_cols: List[str],
                     output_cols: List[str], query: str, max_results: int) -> List[Dict]:
    """Perform BM25 search on a list of data dictionaries"""
    if not data_list:
        return []

    # Build documents from search columns
    documents = []
    for row in data_list:
        doc_text = " ".join(str(row.get(col, "")) for col in search_cols)
        documents.append(doc_text)

    # BM25 search
    bm25 = BM25()
    bm25.fit(documents)
    ranked = bm25.score(query)

    # Get top results with score > 0
    results = []
    for idx, score in ranked[:max_results]:
        if score > 0:
            row = data_list[idx]
            result = {col: row.get(col, "") for col in output_cols if col in row}
            result["score"] = score  # Add BM25 score for debugging

            # Add source metadata
            if "_source" in row:
                result["_source"] = row["_source"]

            results.append(result)

    return results


def get_external_config_status(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get status of external configuration system

    Args:
        config_path: Path to external configuration directory

    Returns:
        Status information about external configuration
    """
    if not EXTERNAL_CONFIG_AVAILABLE:
        return {
            "available": False,
            "error": "External configuration modules not available"
        }

    config_loader = ConfigLoader(config_path)
    status = config_loader.get_config_status()
    status["available"] = True

    return status


def validate_external_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate external configuration

    Args:
        config_path: Path to external configuration directory

    Returns:
        Validation results
    """
    if not EXTERNAL_CONFIG_AVAILABLE:
        return {
            "valid": False,
            "error": "External configuration modules not available"
        }

    config_loader = ConfigLoader(config_path)
    external_config = config_loader.load_external_config()
    validation_result = config_loader.validate_configuration(external_config)

    return validation_result


# Backward compatibility aliases
def search_domains(query: str, domain: Optional[str] = None,
                  external_config: Optional[Dict] = None,
                  max_results: int = MAX_RESULTS) -> List[Dict]:
    """
    Search domains with optional external configuration (compatibility function)

    Args:
        query: Search query string
        domain: Domain filter
        external_config: External configuration data (deprecated, use search_with_external_config)
        max_results: Maximum results to return

    Returns:
        List of search results
    """
    if external_config:
        # Use enhanced search with external config
        results = search_with_external_config(query, domain, None, max_results)
        return results.get("results", [])
    else:
        # Use standard search
        results = search(query, domain, max_results)
        return results.get("results", [])
