#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Brand Processor - Personal/company brand integration
Applies brand configurations to design system recommendations
"""

import re
import colorsys
from typing import Dict, List, Tuple, Optional, Any
from math import sqrt


class BrandProcessor:
    """Processes brand configurations and integrates them with design recommendations"""

    def __init__(self):
        """Initialize brand processor"""
        self.color_cache = {}
        self.accessibility_cache = {}

    def apply_brand_config(self, results: List[Dict], brand_config: Dict) -> List[Dict]:
        """
        Apply brand configuration to search results

        Args:
            results: Search results from core search engine
            brand_config: Brand configuration dictionary

        Returns:
            Modified search results with brand-specific recommendations
        """
        if not brand_config or not results:
            return results

        enhanced_results = []

        # Extract brand elements
        brand_colors = self.extract_brand_colors(brand_config)
        typography_config = brand_config.get("typography", {})
        style_preferences = brand_config.get("style_preferences", {})
        industry = brand_config.get("industry", "")

        # Apply brand to each result
        for result in results:
            enhanced_result = result.copy()

            # Initialize brand application tracking
            enhanced_result["brand_applied"] = {
                "colors_replaced": [],
                "fonts_applied": [],
                "styles_filtered": False,
                "industry_context": industry,
                "modifications": []
            }

            # Apply color replacements
            enhanced_result = self._apply_brand_colors(enhanced_result, brand_colors)

            # Apply typography
            if typography_config:
                enhanced_result = self._apply_brand_typography_single(enhanced_result, typography_config)

            # Generate brand-aware examples
            enhanced_result = self.generate_brand_aware_examples(enhanced_result, brand_config)

            # Adjust relevance score based on brand alignment
            enhanced_result = self._adjust_brand_relevance_score(enhanced_result, style_preferences)

            enhanced_results.append(enhanced_result)

        # Apply style filtering to the entire result set
        if style_preferences:
            enhanced_results = self.filter_by_style_preferences(enhanced_results, style_preferences)

        return enhanced_results

    def extract_brand_colors(self, brand_config: Dict) -> Dict:
        """
        Extract and process brand colors for use in design recommendations

        Args:
            brand_config: Brand configuration with colors section

        Returns:
            Processed color palette ready for application
        """
        colors_section = brand_config.get("colors", {})
        if not colors_section:
            return {}

        # Cache key for color processing
        cache_key = str(sorted(colors_section.items()))
        if cache_key in self.color_cache:
            return self.color_cache[cache_key]

        processed_colors = {}

        # Process primary colors
        if "primary" in colors_section:
            primary = colors_section["primary"]
            processed_colors["primary_palette"] = {
                "primary": primary,
                "primary_light": self._lighten_color(primary, 0.2),
                "primary_dark": self._darken_color(primary, 0.2),
                "primary_variants": self.calculate_color_variants(primary, 5)
            }

        # Process secondary colors
        if "secondary" in colors_section:
            secondary = colors_section["secondary"]
            processed_colors["secondary_palette"] = {
                "secondary": secondary,
                "secondary_light": self._lighten_color(secondary, 0.2),
                "secondary_dark": self._darken_color(secondary, 0.2),
                "secondary_variants": self.calculate_color_variants(secondary, 5)
            }

        # Process accent colors
        if "accent" in colors_section:
            accent = colors_section["accent"]
            processed_colors["accent_palette"] = {
                "accent": accent,
                "accent_light": self._lighten_color(accent, 0.2),
                "accent_dark": self._darken_color(accent, 0.2),
                "accent_variants": self.calculate_color_variants(accent, 5)
            }

        # Process neutral colors
        neutral = colors_section.get("neutral", {})
        if neutral:
            processed_colors["neutral_palette"] = {
                "dark": neutral.get("dark", "#333333"),
                "medium": neutral.get("medium", "#666666"),
                "light": neutral.get("light", "#f5f5f5"),
                "variants": []
            }

            # Generate neutral variants if not provided
            if "dark" in neutral:
                processed_colors["neutral_palette"]["variants"] = self.calculate_color_variants(neutral["dark"], 9)

        # Process semantic colors
        semantic = colors_section.get("semantic", {})
        if semantic:
            processed_colors["semantic_palette"] = {
                "success": semantic.get("success", "#10b981"),
                "warning": semantic.get("warning", "#f59e0b"),
                "error": semantic.get("error", "#ef4444"),
                "info": semantic.get("info", "#3b82f6")
            }
        else:
            # Use brand primary color as base for semantic colors if not specified
            primary = colors_section.get("primary")
            if primary:
                processed_colors["semantic_palette"] = {
                    "success": "#10b981",
                    "warning": "#f59e0b",
                    "error": "#ef4444",
                    "info": primary
                }

        # Calculate accessibility compliance
        processed_colors["accessibility"] = self._calculate_accessibility_compliance(processed_colors)

        # Cache the result
        self.color_cache[cache_key] = processed_colors
        return processed_colors

    def apply_brand_typography(self, results: List[Dict], typography_config: Dict) -> List[Dict]:
        """
        Apply brand typography preferences to search results

        Args:
            results: Search results containing typography recommendations
            typography_config: Typography section from brand configuration

        Returns:
            Results with brand typography applied
        """
        if not typography_config or not results:
            return results

        enhanced_results = []
        for result in results:
            enhanced_result = self._apply_brand_typography_single(result, typography_config)
            enhanced_results.append(enhanced_result)

        return enhanced_results

    def _apply_brand_typography_single(self, result: Dict, typography_config: Dict) -> Dict:
        """Apply brand typography to a single result"""
        if not typography_config:
            return result

        enhanced_result = result.copy()

        # Get brand fonts
        primary_font = typography_config.get("primary_font", {})
        secondary_font = typography_config.get("secondary_font", {})

        # Apply font replacements in code examples and descriptions
        if "code_example" in enhanced_result and enhanced_result["code_example"]:
            code = enhanced_result["code_example"]

            # Replace common font declarations
            if primary_font.get("name"):
                code = re.sub(
                    r"font-family:\s*[^;]+;",
                    f"font-family: '{primary_font['name']}', {primary_font.get('fallback', 'sans-serif')};",
                    code
                )

            # Replace CSS custom property declarations
            if primary_font.get("name"):
                code = re.sub(
                    r"--font-primary:\s*[^;]+;",
                    f"--font-primary: '{primary_font['name']}', {primary_font.get('fallback', 'sans-serif')};",
                    code
                )

            enhanced_result["code_example"] = code

        # Track font applications
        if "brand_applied" in enhanced_result:
            fonts_applied = []
            if primary_font.get("name"):
                fonts_applied.append(primary_font["name"])
            if secondary_font.get("name"):
                fonts_applied.append(secondary_font["name"])

            enhanced_result["brand_applied"]["fonts_applied"] = fonts_applied
            if fonts_applied:
                enhanced_result["brand_applied"]["modifications"].append("typography_applied")

        return enhanced_result

    def filter_by_style_preferences(self, results: List[Dict], style_preferences: Dict) -> List[Dict]:
        """
        Filter and rank results based on brand style preferences

        Args:
            results: Search results to filter
            style_preferences: Style preferences from brand configuration

        Returns:
            Filtered and re-ranked results
        """
        if not style_preferences or not results:
            return results

        preferred_styles = set(style_preferences.get("preferred_styles", []))
        avoided_styles = set(style_preferences.get("avoided_styles", []))
        design_philosophy = style_preferences.get("design_philosophy", "")

        filtered_results = []
        filter_stats = {
            "filtered_count": 0,
            "boosted_count": 0,
            "style_matches": {},
            "philosophy_applied": design_philosophy,
            "industry_context": ""
        }

        for result in results:
            # Check if result should be filtered out
            should_filter = False

            # Get style context from the result
            result_text = f"{result.get('term', '')} {result.get('description', '')} {result.get('reasoning', '')}"
            result_text_lower = result_text.lower()

            # Filter out avoided styles
            for avoided_style in avoided_styles:
                if avoided_style.lower() in result_text_lower:
                    should_filter = True
                    filter_stats["filtered_count"] += 1
                    break

            if should_filter:
                continue

            # Boost preferred styles
            original_score = result.get("score", 1.0)
            boosted = False

            for preferred_style in preferred_styles:
                if preferred_style.lower() in result_text_lower:
                    result["score"] = original_score * 1.5  # Boost preferred styles
                    boosted = True
                    filter_stats["style_matches"][preferred_style] = filter_stats["style_matches"].get(preferred_style, 0) + 1

            if boosted:
                filter_stats["boosted_count"] += 1

            # Apply design philosophy filtering
            if design_philosophy:
                philosophy_boost = self._apply_design_philosophy(result, design_philosophy)
                if philosophy_boost != 1.0:
                    result["score"] = result.get("score", 1.0) * philosophy_boost

            # Mark as style filtered
            if "brand_applied" in result:
                result["brand_applied"]["styles_filtered"] = True

            filtered_results.append(result)

        # Sort by score after filtering and boosting
        filtered_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return filtered_results

    def _apply_design_philosophy(self, result: Dict, philosophy: str) -> float:
        """Apply design philosophy boost/penalty"""
        result_text = f"{result.get('term', '')} {result.get('description', '')}".lower()

        philosophy_keywords = {
            "minimalism": {"keywords": ["minimal", "clean", "simple", "whitespace"], "boost": 1.3},
            "modern": {"keywords": ["modern", "contemporary", "sleek"], "boost": 1.2},
            "playful": {"keywords": ["playful", "fun", "colorful", "vibrant"], "boost": 1.2},
            "professional": {"keywords": ["professional", "corporate", "formal"], "boost": 1.2},
            "elegant": {"keywords": ["elegant", "refined", "sophisticated"], "boost": 1.2}
        }

        if philosophy.lower() in philosophy_keywords:
            philosophy_config = philosophy_keywords[philosophy.lower()]
            for keyword in philosophy_config["keywords"]:
                if keyword in result_text:
                    return philosophy_config["boost"]

        return 1.0

    def generate_brand_aware_examples(self, result: Dict, brand_config: Dict) -> Dict:
        """
        Generate brand-specific code examples and implementation details

        Args:
            result: Single search result to enhance
            brand_config: Complete brand configuration

        Returns:
            Result with brand-aware examples and code snippets
        """
        enhanced_result = result.copy()

        if "code_example" not in enhanced_result or not enhanced_result["code_example"]:
            return enhanced_result

        code = enhanced_result["code_example"]
        colors_section = brand_config.get("colors", {})
        typography_config = brand_config.get("typography", {})

        # Replace color values with brand colors
        if colors_section:
            code = self._replace_colors_in_code(code, colors_section)

        # Replace font declarations with brand fonts
        if typography_config:
            code = self._replace_fonts_in_code(code, typography_config)

        # Generate CSS custom properties if applicable
        if "css" in code.lower() or ":root" in code:
            css_variables = self.generate_css_variables(brand_config)
            if css_variables and ":root" not in code:
                code = css_variables + "\n\n" + code

        enhanced_result["code_example"] = code

        return enhanced_result

    def _replace_colors_in_code(self, code: str, colors_section: Dict) -> str:
        """Replace color values in code with brand colors"""
        replacements = []

        # Map common color roles to brand colors
        color_mapping = {
            "#3b82f6": colors_section.get("primary", "#3b82f6"),  # Common blue
            "#1d4ed8": colors_section.get("primary", "#1d4ed8"),  # Dark blue
            "#60a5fa": self._lighten_color(colors_section.get("primary", "#60a5fa"), 0.2),  # Light blue
            "#f59e0b": colors_section.get("accent", "#f59e0b"),   # Amber
            "#10b981": colors_section.get("semantic", {}).get("success", "#10b981"),  # Green
            "#ef4444": colors_section.get("semantic", {}).get("error", "#ef4444"),    # Red
        }

        # Apply replacements
        for old_color, new_color in color_mapping.items():
            if old_color in code and old_color != new_color:
                code = code.replace(old_color, new_color)
                replacements.append(f"{old_color} → {new_color}")

        return code

    def _replace_fonts_in_code(self, code: str, typography_config: Dict) -> str:
        """Replace font declarations in code with brand fonts"""
        primary_font = typography_config.get("primary_font", {})
        secondary_font = typography_config.get("secondary_font", {})

        if primary_font.get("name"):
            # Replace common sans-serif declarations
            font_family = f"'{primary_font['name']}', {primary_font.get('fallback', 'sans-serif')}"
            code = re.sub(
                r"font-family:\s*(['\"]?)Inter\1,?\s*system-ui[^;]*;",
                f"font-family: {font_family};",
                code
            )
            code = re.sub(
                r"font-family:\s*(['\"]?)ui-sans-serif\1[^;]*;",
                f"font-family: {font_family};",
                code
            )

        if secondary_font.get("name"):
            # Replace monospace fonts
            mono_family = f"'{secondary_font['name']}', {secondary_font.get('fallback', 'monospace')}"
            code = re.sub(
                r"font-family:\s*(['\"]?)ui-monospace\1[^;]*;",
                f"font-family: {mono_family};",
                code
            )

        return code

    def validate_brand_config(self, brand_config: Dict) -> Dict:
        """
        Validate brand configuration for completeness and correctness

        Args:
            brand_config: Brand configuration to validate

        Returns:
            Validation result with detailed feedback
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "completeness_score": 0.0,
            "sections": {
                "colors": {"valid": False, "required_present": [], "missing_required": [], "accessibility_warnings": [], "contrast_issues": []},
                "typography": {"valid": False, "fonts_available": [], "google_fonts_valid": False, "fallback_chains": [], "scale_valid": False},
                "style_preferences": {"valid": False, "preferences_count": 0, "conflicts": [], "recommendations": []}
            }
        }

        completeness_points = 0
        max_points = 10

        # Validate colors section
        colors = brand_config.get("colors", {})
        if colors:
            completeness_points += 4
            colors_result = self._validate_colors_section(colors)
            result["sections"]["colors"] = colors_result
            if not colors_result["valid"]:
                result["valid"] = False
        else:
            result["errors"].append({"type": "missing_section", "message": "Colors section is required"})
            result["valid"] = False

        # Validate typography section
        typography = brand_config.get("typography", {})
        if typography:
            completeness_points += 4
            typography_result = self._validate_typography_section(typography)
            result["sections"]["typography"] = typography_result
            if not typography_result["valid"]:
                result["valid"] = False
        else:
            result["errors"].append({"type": "missing_section", "message": "Typography section is required"})
            result["valid"] = False

        # Validate style preferences (optional but recommended)
        style_prefs = brand_config.get("style_preferences", {})
        if style_prefs:
            completeness_points += 2
            style_result = self._validate_style_preferences_section(style_prefs)
            result["sections"]["style_preferences"] = style_result

        # Calculate completeness score
        result["completeness_score"] = completeness_points / max_points

        return result

    def _validate_colors_section(self, colors: Dict) -> Dict:
        """Validate colors section"""
        result = {
            "valid": True,
            "required_present": [],
            "missing_required": [],
            "accessibility_warnings": [],
            "contrast_issues": []
        }

        required_colors = ["primary"]
        recommended_colors = ["secondary", "accent"]

        # Check required colors
        for color in required_colors:
            if color in colors and self._is_valid_hex_color(colors[color]):
                result["required_present"].append(color)
            else:
                result["missing_required"].append(color)
                result["valid"] = False

        # Check recommended colors
        for color in recommended_colors:
            if color in colors and self._is_valid_hex_color(colors[color]):
                result["required_present"].append(color)

        # Check accessibility
        if "primary" in colors:
            primary = colors["primary"]
            # Check contrast against common backgrounds
            backgrounds = ["#ffffff", "#f9fafb", "#000000"]
            for bg in backgrounds:
                contrast_info = self.check_color_accessibility(primary, bg)
                if not contrast_info["aa_compliant"]:
                    result["contrast_issues"].append({
                        "text_color": primary,
                        "background_color": bg,
                        "contrast_ratio": contrast_info["contrast_ratio"],
                        "aa_compliant": contrast_info["aa_compliant"]
                    })

        return result

    def _validate_typography_section(self, typography: Dict) -> Dict:
        """Validate typography section"""
        result = {
            "valid": True,
            "fonts_available": [],
            "google_fonts_valid": False,
            "fallback_chains": [],
            "scale_valid": False
        }

        # Check primary font
        primary_font = typography.get("primary_font", {})
        if primary_font.get("name"):
            result["fonts_available"].append(primary_font["name"])
            if primary_font.get("google_fonts_import"):
                result["google_fonts_valid"] = True
            if primary_font.get("fallback"):
                result["fallback_chains"].append(primary_font["fallback"])

        # Check secondary font
        secondary_font = typography.get("secondary_font", {})
        if secondary_font.get("name"):
            result["fonts_available"].append(secondary_font["name"])
            if secondary_font.get("fallback"):
                result["fallback_chains"].append(secondary_font["fallback"])

        # Check typography scale
        if "scale" in typography:
            scale = typography["scale"]
            if isinstance(scale, str) and scale in ["1.125", "1.25", "1.333", "1.414", "1.5", "1.618"]:
                result["scale_valid"] = True

        # Require at least primary font
        if not result["fonts_available"]:
            result["valid"] = False

        return result

    def _validate_style_preferences_section(self, style_prefs: Dict) -> Dict:
        """Validate style preferences section"""
        result = {
            "valid": True,
            "preferences_count": 0,
            "conflicts": [],
            "recommendations": []
        }

        preferred = style_prefs.get("preferred_styles", [])
        avoided = style_prefs.get("avoided_styles", [])

        result["preferences_count"] = len(preferred) + len(avoided)

        # Check for conflicts
        conflicts = set(preferred) & set(avoided)
        if conflicts:
            result["conflicts"] = list(conflicts)
            result["valid"] = False

        # Provide recommendations
        if not preferred and not avoided:
            result["recommendations"].append("Consider specifying preferred or avoided styles for better personalization")

        return result

    def calculate_color_variants(self, base_color: str, variant_count: int = 5) -> List[str]:
        """
        Generate color variants from a base brand color

        Args:
            base_color: Hex color code
            variant_count: Number of variants to generate

        Returns:
            List of color variants (lighter and darker shades)
        """
        if not self._is_valid_hex_color(base_color):
            return []

        variants = []

        # Convert hex to RGB
        r, g, b = self._hex_to_rgb(base_color)
        h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)

        # Generate lighter variants
        for i in range(1, (variant_count // 2) + 1):
            lightness_increase = 0.1 * i
            new_l = min(1.0, l + lightness_increase)
            new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_l, s)
            new_hex = self._rgb_to_hex(int(new_r * 255), int(new_g * 255), int(new_b * 255))
            variants.append(new_hex)

        # Add original color
        variants.append(base_color)

        # Generate darker variants
        for i in range(1, (variant_count // 2) + 1):
            lightness_decrease = 0.1 * i
            new_l = max(0.0, l - lightness_decrease)
            new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_l, s)
            new_hex = self._rgb_to_hex(int(new_r * 255), int(new_g * 255), int(new_b * 255))
            variants.append(new_hex)

        return variants[:variant_count]

    def check_color_accessibility(self, text_color: str, background_color: str) -> Dict:
        """
        Calculate color contrast ratios and accessibility compliance

        Args:
            text_color: Text color in hex format
            background_color: Background color in hex format

        Returns:
            Dictionary with contrast information
        """
        cache_key = f"{text_color}:{background_color}"
        if cache_key in self.accessibility_cache:
            return self.accessibility_cache[cache_key]

        if not self._is_valid_hex_color(text_color) or not self._is_valid_hex_color(background_color):
            return {"contrast_ratio": 0.0, "aa_compliant": False, "aaa_compliant": False, "wcag_level": "fail"}

        # Calculate relative luminance for both colors
        text_luminance = self._calculate_luminance(text_color)
        bg_luminance = self._calculate_luminance(background_color)

        # Calculate contrast ratio
        lighter = max(text_luminance, bg_luminance)
        darker = min(text_luminance, bg_luminance)
        contrast_ratio = (lighter + 0.05) / (darker + 0.05)

        # Determine compliance levels
        aa_compliant = contrast_ratio >= 4.5
        aaa_compliant = contrast_ratio >= 7.0

        # Determine WCAG level
        if aaa_compliant:
            wcag_level = "AAA"
        elif aa_compliant:
            wcag_level = "AA"
        else:
            wcag_level = "fail"

        result = {
            "contrast_ratio": round(contrast_ratio, 2),
            "aa_compliant": aa_compliant,
            "aaa_compliant": aaa_compliant,
            "wcag_level": wcag_level
        }

        self.accessibility_cache[cache_key] = result
        return result

    def generate_css_variables(self, brand_config: Dict) -> str:
        """
        Generate CSS custom properties from brand configuration

        Args:
            brand_config: Complete brand configuration

        Returns:
            CSS string with brand color and typography variables
        """
        css_lines = [":root {"]

        # Process colors
        colors = brand_config.get("colors", {})
        if colors:
            # Primary colors
            if "primary" in colors:
                css_lines.append(f"  --color-primary: {colors['primary']};")
                css_lines.append(f"  --color-primary-light: {self._lighten_color(colors['primary'], 0.2)};")
                css_lines.append(f"  --color-primary-dark: {self._darken_color(colors['primary'], 0.2)};")

            # Secondary colors
            if "secondary" in colors:
                css_lines.append(f"  --color-secondary: {colors['secondary']};")
                css_lines.append(f"  --color-secondary-light: {self._lighten_color(colors['secondary'], 0.2)};")
                css_lines.append(f"  --color-secondary-dark: {self._darken_color(colors['secondary'], 0.2)};")

            # Accent colors
            if "accent" in colors:
                css_lines.append(f"  --color-accent: {colors['accent']};")

            # Neutral colors
            neutral = colors.get("neutral", {})
            for key, value in neutral.items():
                css_lines.append(f"  --color-{key}: {value};")

            # Semantic colors
            semantic = colors.get("semantic", {})
            for key, value in semantic.items():
                css_lines.append(f"  --color-{key}: {value};")

        # Process typography
        typography = brand_config.get("typography", {})
        if typography:
            primary_font = typography.get("primary_font", {})
            if primary_font.get("name"):
                fallback = primary_font.get("fallback", "sans-serif")
                css_lines.append(f"  --font-primary: '{primary_font['name']}', {fallback};")

            secondary_font = typography.get("secondary_font", {})
            if secondary_font.get("name"):
                fallback = secondary_font.get("fallback", "monospace")
                css_lines.append(f"  --font-secondary: '{secondary_font['name']}', {fallback};")

            # Typography scale
            if "scale" in typography:
                css_lines.append(f"  --type-scale: {typography['scale']};")

            # Line heights
            line_heights = typography.get("line_heights", {})
            for key, value in line_heights.items():
                css_lines.append(f"  --line-height-{key}: {value};")

        css_lines.append("}")
        return "\n".join(css_lines)

    def _apply_brand_colors(self, result: Dict, brand_colors: Dict) -> Dict:
        """Apply brand colors to a single result"""
        if not brand_colors or "code_example" not in result:
            return result

        code = result.get("code_example", "")
        if not code:
            return result

        colors_replaced = []

        # Replace colors based on extracted brand palette
        primary_palette = brand_colors.get("primary_palette", {})
        if primary_palette.get("primary"):
            # Replace common blue colors with primary brand color
            for old_color in ["#3b82f6", "#2563eb", "#1d4ed8"]:
                if old_color in code:
                    code = code.replace(old_color, primary_palette["primary"])
                    colors_replaced.append(f"{old_color} → {primary_palette['primary']}")

        # Update tracking
        if "brand_applied" in result:
            result["brand_applied"]["colors_replaced"] = colors_replaced
            if colors_replaced:
                result["brand_applied"]["modifications"].append("colors_replaced")

        result["code_example"] = code
        return result

    def _adjust_brand_relevance_score(self, result: Dict, style_preferences: Dict) -> Dict:
        """Adjust search relevance score based on brand alignment"""
        if not style_preferences:
            return result

        # This is already handled in filter_by_style_preferences
        # This function exists for individual result processing if needed
        return result

    def _calculate_accessibility_compliance(self, processed_colors: Dict) -> Dict:
        """Calculate accessibility compliance for color combinations"""
        accessibility = {
            "aa_compliant_pairs": [],
            "aaa_compliant_pairs": [],
            "contrast_ratios": {}
        }

        # Get all colors for testing
        all_colors = []

        for palette_name, palette in processed_colors.items():
            if isinstance(palette, dict):
                for color_name, color_value in palette.items():
                    if isinstance(color_value, str) and self._is_valid_hex_color(color_value):
                        all_colors.append((f"{palette_name}_{color_name}", color_value))

        # Test common combinations
        common_backgrounds = [("#ffffff", "white"), ("#000000", "black"), ("#f9fafb", "light_gray")]

        for bg_name, bg_color in common_backgrounds:
            for color_name, color_value in all_colors:
                contrast_info = self.check_color_accessibility(color_value, bg_color)
                combination_key = f"{color_name}_on_{bg_name}"

                accessibility["contrast_ratios"][combination_key] = contrast_info["contrast_ratio"]

                if contrast_info["aa_compliant"]:
                    accessibility["aa_compliant_pairs"].append((color_value, bg_color))

                if contrast_info["aaa_compliant"]:
                    accessibility["aaa_compliant_pairs"].append((color_value, bg_color))

        return accessibility

    # Color utility functions
    def _is_valid_hex_color(self, color: str) -> bool:
        """Check if string is a valid hex color"""
        if not isinstance(color, str):
            return False
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB values to hex color"""
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """Lighten a hex color by specified amount (0.0 to 1.0)"""
        if not self._is_valid_hex_color(hex_color):
            return hex_color

        r, g, b = self._hex_to_rgb(hex_color)
        h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)

        new_l = min(1.0, l + amount)
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_l, s)

        return self._rgb_to_hex(int(new_r * 255), int(new_g * 255), int(new_b * 255))

    def _darken_color(self, hex_color: str, amount: float) -> str:
        """Darken a hex color by specified amount (0.0 to 1.0)"""
        if not self._is_valid_hex_color(hex_color):
            return hex_color

        r, g, b = self._hex_to_rgb(hex_color)
        h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)

        new_l = max(0.0, l - amount)
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_l, s)

        return self._rgb_to_hex(int(new_r * 255), int(new_g * 255), int(new_b * 255))

    def _calculate_luminance(self, hex_color: str) -> float:
        """Calculate relative luminance of a color"""
        r, g, b = self._hex_to_rgb(hex_color)

        # Convert to relative values
        r_rel, g_rel, b_rel = r/255.0, g/255.0, b/255.0

        # Apply gamma correction
        def gamma_correct(c):
            return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)

        r_linear = gamma_correct(r_rel)
        g_linear = gamma_correct(g_rel)
        b_linear = gamma_correct(b_rel)

        # Calculate luminance
        return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear


# Convenience functions for backward compatibility
def apply_brand_config(results: List[Dict], brand_config: Dict) -> List[Dict]:
    """Apply brand configuration (convenience function)"""
    processor = BrandProcessor()
    return processor.apply_brand_config(results, brand_config)


def extract_brand_colors(brand_config: Dict) -> Dict:
    """Extract brand colors (convenience function)"""
    processor = BrandProcessor()
    return processor.extract_brand_colors(brand_config)


def validate_brand_config(brand_config: Dict) -> Dict:
    """Validate brand configuration (convenience function)"""
    processor = BrandProcessor()
    return processor.validate_brand_config(brand_config)


def generate_css_variables(brand_config: Dict) -> str:
    """Generate CSS variables (convenience function)"""
    processor = BrandProcessor()
    return processor.generate_css_variables(brand_config)