#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design system generator: DesignSystemGenerator (search aggregation + reasoning).
"""

import csv
import re
from core import search, DATA_DIR
from reasoning_contract import apply_decision_rules, parse_decision_rules
from ds_config import REASONING_FILE, SEARCH_CONFIG, _resolve_dial
from ds_color import (
    _filter_anti_patterns_for_mode,
    _resolve_color_mode,
    _select_palette_for_mode,
)


# ============ DESIGN SYSTEM GENERATOR ============
class DesignSystemGenerator:
    """Generates design system recommendations from aggregated searches."""

    def __init__(self):
        self.reasoning_data = self._load_reasoning()
        self.style_data = self._load_styles()
        self.style_lookup = self._build_style_lookup(self.style_data)
        self.landing_lookup = self._load_landing_patterns()

    def _load_reasoning(self) -> list:
        """Load reasoning rules from CSV."""
        filepath = DATA_DIR / REASONING_FILE
        if not filepath.exists():
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _load_styles(self) -> list:
        filepath = DATA_DIR / "styles.csv"
        if not filepath.exists():
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _load_landing_patterns(self) -> dict:
        filepath = DATA_DIR / "landing.csv"
        if not filepath.exists():
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            lookup = {}
            for row in csv.DictReader(f):
                identities = [row.get("Pattern ID", ""), row.get("Pattern Name", "")]
                identities.extend(row.get("Aliases", "").split("|"))
                for identity in identities:
                    if identity.strip():
                        lookup[identity.strip().casefold()] = row
            return lookup

    @staticmethod
    def _build_style_lookup(styles: list) -> dict:
        lookup = {}
        for style in styles:
            keys = [style.get("Style ID", ""), style.get("Style Category", "")]
            keys.extend(style.get("Aliases", "").split("|"))
            for key in keys:
                if key.strip():
                    lookup[key.strip().casefold()] = style
        return lookup

    def _resolve_style(self, reference: str) -> dict:
        style = self.style_lookup.get(str(reference or "").strip().casefold(), {})
        seen = set()
        while style and style.get("Status", "active") == "deprecated":
            style_id = style.get("Style ID", "")
            parent_id = style.get("Parent Style ID", "")
            if not parent_id or style_id in seen:
                return {}
            seen.add(style_id)
            style = self.style_lookup.get(parent_id.casefold(), {})
        return style

    def _multi_domain_search(self, query: str, category: str,
                             reasoning: dict, style_priority: list = None) -> dict:
        """Execute searches across multiple domains."""
        results = {}
        constraints = " ".join(
            item.replace("-", " ")
            for item in reasoning.get("constraints", [])
        )
        resolved_query = " ".join(
            part for part in (query, category, constraints) if part
        )
        for domain, config in SEARCH_CONFIG.items():
            if domain == "style" and style_priority:
                priority_query = " ".join(style_priority[:2])
                results[domain] = search(
                    f"{resolved_query} {priority_query}", domain, config["max_results"])
            elif domain == "color":
                results[domain] = search(
                    f"{reasoning.get('color_mood', '')} {resolved_query}",
                    domain, config["max_results"])
            elif domain == "landing":
                # The reasoning pattern is the landing query contract. Mixing the
                # product prompt into it can push token coverage below the
                # abstention threshold even when the pattern names an exact row.
                pattern = reasoning.get("pattern", "")
                landing_query = pattern if pattern.casefold() in self.landing_lookup else (
                    f"{pattern} {resolved_query}"
                )
                results[domain] = search(
                    landing_query or query, domain, config["max_results"])
            elif domain == "typography":
                results[domain] = search(
                    f"{reasoning.get('typography_mood', '')} {resolved_query}",
                    domain, config["max_results"])
            else:
                results[domain] = search(query, domain, config["max_results"])
        return results

    def _find_reasoning_rule(self, category: str) -> dict:
        """Find matching reasoning rule for a category."""
        category_lower = category.strip().casefold()
        for rule in self.reasoning_data:
            if rule.get("UI_Category", "").strip().casefold() == category_lower:
                return rule
        return {}

    def _apply_reasoning(self, category: str, query: str) -> dict:
        """Apply reasoning rules to search results."""
        rule = self._find_reasoning_rule(category)

        if not rule:
            return {
                "pattern": "Hero + Features + CTA",
                "style_priority": ["Minimalism", "Flat Design"],
                "color_mood": "Professional",
                "typography_mood": "Clean",
                "key_effects": "Subtle hover transitions",
                "anti_patterns": "",
                "decision_rules": {},
                "activated_rules": [],
                "constraints": [],
                "preferred_mode": None,
                "is_default": True,
                "severity": "MEDIUM"
            }

        decision_rules = parse_decision_rules(rule.get("Decision_Rules", "{}"))
        applied = apply_decision_rules(decision_rules, query)
        style_priority = [s.strip() for s in rule.get("Style_Priority", "").split("+")]
        applied_style_names = [
            self._resolve_style(style_id).get("Style Category", style_id)
            for style_id in applied["style_ids"]
        ]

        return {
            "pattern": applied["pattern"] or rule.get("Recommended_Pattern", ""),
            "style_priority": applied_style_names + style_priority,
            "color_mood": rule.get("Color_Mood", ""),
            "typography_mood": rule.get("Typography_Mood", ""),
            "key_effects": rule.get("Key_Effects", ""),
            "anti_patterns": rule.get("Anti_Patterns", ""),
            "decision_rules": decision_rules,
            "activated_rules": applied["activated"],
            "constraints": applied["constraints"],
            "preferred_mode": applied["mode"],
            "is_default": False,
            "severity": rule.get("Severity", "MEDIUM")
        }

    def _select_best_match(self, results: list, priority_keywords: list) -> dict:
        """Select best matching result based on priority keywords."""
        if not results:
            return {}

        if not priority_keywords:
            return results[0]

        # Canonical reasoning has authority over lexical candidates. Returning
        # the resolved row directly prevents a platform variant in BM25 top-3
        # from displacing the explicit family recommendation.
        for priority in priority_keywords:
            resolved = self._resolve_style(priority)
            if resolved and resolved.get("Status", "active") != "deprecated":
                return dict(resolved)

        # Second: score by keyword match in all fields
        scored = []
        for result in results:
            result_str = str(result).lower()
            score = 0
            for kw in priority_keywords:
                kw_tokens = set(re.findall(r"[a-z0-9]+", kw.lower()))
                name_tokens = set(re.findall(
                    r"[a-z0-9]+", result.get("Style Category", "").lower()))
                if kw_tokens and kw_tokens <= name_tokens:
                    score += 10
                elif kw_tokens & set(re.findall(
                        r"[a-z0-9]+", result.get("Keywords", "").lower())):
                    score += 3
                elif any(token in result_str for token in kw_tokens):
                    score += 1
            scored.append((score, result))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored and scored[0][0] > 0 else results[0]

    def _extract_results(self, search_result: dict) -> list:
        """Extract results list from search result dict."""
        return search_result.get("results", [])

    def generate(self, query: str, project_name: str = None,
                 variance: int = None, motion: int = None, density: int = None) -> dict:
        """Generate complete design system recommendation.

        variance/motion/density are optional 1-10 dials (see DIAL_TIERS) that bias
        style selection, pull in a matching motion.csv snippet, and override the
        spacing scale, without changing behavior when left unset.
        """
        variance_info = _resolve_dial("variance", variance)
        motion_info = _resolve_dial("motion", motion)
        density_info = _resolve_dial("density", density)

        # Step 1: First search product to get category
        product_result = search(query, "product", 1)
        product_results = product_result.get("results", [])
        category = "General"
        if product_results:
            category = product_results[0].get("Product Type", "General")

        # Step 2: Get reasoning rules for this category
        reasoning = self._apply_reasoning(category, query)
        style_priority = reasoning.get("style_priority", [])

        # DESIGN_VARIANCE dial: bias style retrieval/selection toward
        # centered-minimal (low) or bold-asymmetric (high) keywords.
        effective_style_priority = style_priority
        if variance_info:
            effective_style_priority = variance_info["style_keywords"] + style_priority

        # Step 3: Multi-domain search with style priority hints
        search_results = self._multi_domain_search(
            query, category, reasoning, effective_style_priority)
        search_results["product"] = product_result  # Reuse product search

        # Step 4: Select best matches from each domain using priority
        style_results = self._extract_results(search_results.get("style", {}))
        color_results = self._extract_results(search_results.get("color", {}))
        typography_results = self._extract_results(search_results.get("typography", {}))
        landing_results = self._extract_results(search_results.get("landing", {}))

        best_style = self._select_best_match(style_results, effective_style_priority)
        # Resolve the mode from the style + query first, then pick a palette that
        # agrees with it. Ranking colors independently is what let a dark-primary
        # style ship with a light background.
        color_mode = reasoning.get("preferred_mode") or _resolve_color_mode(query, best_style)
        best_color = _select_palette_for_mode(color_results, color_mode, category)
        best_typography = typography_results[0] if typography_results else {}
        best_landing = next(
            (row for row in landing_results
             if row.get("Pattern Name") == reasoning.get("pattern")),
            landing_results[0] if landing_results else {},
        )

        # MOTION_INTENSITY dial: pull a matching GSAP skeleton from motion.csv
        # (domain key is "gsap", not "motion" - PR #296 already owns the "motion"
        # domain for Emil Kowalski's motion-design principles, motion-principles.csv).
        motion_snippet = {}
        if motion_info:
            motion_result = search(f"{query} {motion_info['tier']}", "gsap", 5)
            motion_matches = motion_result.get("results", [])
            tiered = [m for m in motion_matches if m.get("Intensity Tier") == motion_info["tier"]]
            if tiered:
                motion_snippet = tiered[0]
            elif motion_matches:
                motion_snippet = motion_matches[0]

        # Step 5: Build final recommendation
        # Combine effects from both reasoning and style search
        style_effects = best_style.get("Effects & Animation", "")
        reasoning_effects = reasoning.get("key_effects", "")
        combined_effects = style_effects if style_effects else reasoning_effects

        return {
            "project_name": project_name or query.upper(),
            "category": category,
            "pattern": {
                "name": best_landing.get("Pattern Name", reasoning.get("pattern", "Hero + Features + CTA")),
                "sections": best_landing.get("Section Order", "Hero > Features > CTA"),
                "cta_placement": best_landing.get("Primary CTA Placement", "Above fold"),
                "color_strategy": best_landing.get("Color Strategy", ""),
                "conversion": best_landing.get("Conversion Optimization", "")
            },
            "style": {
                "id": best_style.get("Style ID", "minimalism-and-swiss-style"),
                "name": best_style.get("Style Category", "Minimalism"),
                "type": best_style.get("Type", "General"),
                "effects": style_effects,
                "keywords": best_style.get("Keywords", ""),
                "best_for": best_style.get("Best For", ""),
                "performance": best_style.get("Performance", ""),
                "accessibility": best_style.get("Accessibility", ""),
                "light_mode": best_style.get("Light Mode ✓", ""),
                "dark_mode": best_style.get("Dark Mode ✓", ""),
            },
            "colors": {
                "primary": best_color.get("Primary", "#2563EB"),
                "on_primary": best_color.get("On Primary", ""),
                "secondary": best_color.get("Secondary", "#3B82F6"),
                "on_secondary": best_color.get("On Secondary", ""),
                "accent": best_color.get("Accent", "#F97316"),
                "on_accent": best_color.get("On Accent", ""),
                "background": best_color.get("Background", "#F8FAFC"),
                "foreground": best_color.get("Foreground", "#1E293B"),
                "card": best_color.get("Card", ""),
                "card_foreground": best_color.get("Card Foreground", ""),
                "muted": best_color.get("Muted", ""),
                "muted_foreground": best_color.get("Muted Foreground", ""),
                "border": best_color.get("Border", ""),
                "destructive": best_color.get("Destructive", ""),
                "on_destructive": best_color.get("On Destructive", ""),
                "ring": best_color.get("Ring", ""),
                "notes": best_color.get("Notes", ""),
                # Keep legacy keys for backward compat in MASTER.md
                "cta": best_color.get("Accent", "#F97316"),
                "text": best_color.get("Foreground", "#1E293B"),
                "on_cta": best_color.get("On Accent", ""),
            },
            "typography": {
                "heading": best_typography.get("Heading Font", "Inter"),
                "body": best_typography.get("Body Font", "Inter"),
                "mood": best_typography.get("Mood/Style Keywords", reasoning.get("typography_mood", "")),
                "best_for": best_typography.get("Best For", ""),
                "google_fonts_url": best_typography.get("Google Fonts URL", ""),
                "css_import": best_typography.get("CSS Import", "")
            },
            "key_effects": combined_effects,
            "anti_patterns": _filter_anti_patterns_for_mode(
                reasoning.get("anti_patterns", ""), color_mode
            ),
            "decision_rules": reasoning.get("decision_rules", {}),
            "activated_rules": reasoning.get("activated_rules", []),
            "constraints": reasoning.get("constraints", []),
            "reasoning_default": reasoning.get("is_default", False),
            "source_identities": {
                "product": category if product_results else None,
                "reasoning": category if not reasoning.get("is_default") else None,
                "style": best_style.get("Style ID") or best_style.get("Style Category"),
                "color": best_color.get("Product Type"),
                "typography": best_typography.get("Font Pairing Name"),
                "landing": best_landing.get("Pattern Name"),
            },
            "source_derivations": {
                "color_mode": best_color.get("_mode_derivation"),
            },
            "severity": reasoning.get("severity", "MEDIUM"),
            "dials": {
                "variance": variance_info["value"] if variance_info else None,
                "variance_label": variance_info["label"] if variance_info else None,
                "motion": motion_info["value"] if motion_info else None,
                "motion_label": motion_info["label"] if motion_info else None,
                "density": density_info["value"] if density_info else None,
                "density_label": density_info["label"] if density_info else None,
            },
            "motion_snippet": motion_snippet,
            "spacing_scale": density_info["spacing"] if density_info else None,
        }
