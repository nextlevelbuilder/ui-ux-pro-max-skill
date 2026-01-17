#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max A2UI Exporter - Agent-to-UI protocol export
Converts UI/UX Pro Max recommendations to A2UI protocol format for cross-platform UI generation
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any


class A2UIExporter:
    """Exports UI/UX Pro Max search results to A2UI protocol format"""

    def __init__(self):
        """Initialize A2UI exporter"""
        self.component_counter = 0
        self.layout_counter = 0
        self.interaction_counter = 0

    def export_to_a2ui(self, results: List[Dict], export_options: Optional[Dict] = None) -> Dict:
        """
        Convert search results to A2UI protocol format

        Args:
            results: Search results from UI/UX Pro Max search
            export_options: Export configuration options

        Returns:
            A2UI protocol specification document
        """
        if not results:
            return self._create_empty_a2ui_spec()

        # Apply default export options
        options = self._apply_default_export_options(export_options or {})

        # Initialize A2UI specification structure
        a2ui_spec = {
            "a2ui_version": "1.0.0",
            "metadata": {
                "source": "ui-ux-pro-max",
                "generated_at": datetime.now().isoformat(),
                "query_info": {
                    "original_query": options.get("original_query", ""),
                    "domain": options.get("domain", ""),
                    "result_count": len(results)
                },
                "export_options": options
            },
            "design_system": {},
            "components": [],
            "layouts": [],
            "interactions": [],
            "rendering_targets": {}
        }

        # Extract design system from results
        if options.get("include_design_system", True):
            a2ui_spec["design_system"] = self.extract_design_system(results)

        # Convert components
        if options.get("include_components", True):
            a2ui_spec["components"] = self.convert_components_to_a2ui(results, a2ui_spec["design_system"])

        # Generate layouts
        if options.get("include_layouts", True):
            a2ui_spec["layouts"] = self._generate_layouts_from_results(results)

        # Generate interactions
        if options.get("include_interactions", True):
            a2ui_spec["interactions"] = self._generate_interactions_from_results(results)

        # Generate platform-specific rendering instructions
        target_platforms = options.get("target_platforms", ["html", "react"])
        for platform in target_platforms:
            a2ui_spec["rendering_targets"][platform] = self.export_for_platform(a2ui_spec, platform)

        # Apply optimization
        if options.get("optimization_level", "standard") != "none":
            a2ui_spec = self.optimize_a2ui_size(a2ui_spec)

        return a2ui_spec

    def extract_design_system(self, results: List[Dict]) -> Dict:
        """
        Extract design system tokens from search results

        Args:
            results: Search results containing design system information

        Returns:
            Design system specification for A2UI
        """
        design_system = {
            "colors": self._extract_colors_from_results(results),
            "typography": self._extract_typography_from_results(results),
            "spacing": self._extract_spacing_from_results(results),
            "borders": self._extract_borders_from_results(results),
            "shadows": self._extract_shadows_from_results(results)
        }

        return design_system

    def _extract_colors_from_results(self, results: List[Dict]) -> Dict:
        """Extract color system from results"""
        colors = {
            "primary": "#3b82f6",
            "secondary": "#64748b",
            "accent": "#f59e0b",
            "neutral": {
                "50": "#f8fafc",
                "100": "#f1f5f9",
                "200": "#e2e8f0",
                "300": "#cbd5e1",
                "400": "#94a3b8",
                "500": "#64748b",
                "600": "#475569",
                "700": "#334155",
                "800": "#1e293b",
                "900": "#0f172a"
            },
            "semantic": {
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "info": "#3b82f6"
            }
        }

        # Extract colors from brand-applied results
        for result in results:
            brand_applied = result.get("brand_applied", {})
            if brand_applied and "colors_replaced" in brand_applied:
                # Parse color replacements to update the design system
                for replacement in brand_applied["colors_replaced"]:
                    if " → " in replacement:
                        old_color, new_color = replacement.split(" → ")
                        if old_color == "#3b82f6":  # Primary color replacement
                            colors["primary"] = new_color
                        elif old_color == "#f59e0b":  # Accent color replacement
                            colors["accent"] = new_color

        return colors

    def _extract_typography_from_results(self, results: List[Dict]) -> Dict:
        """Extract typography system from results"""
        typography = {
            "font_families": {
                "primary": {
                    "name": "Inter",
                    "weights": [400, 500, 600, 700],
                    "import_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
                },
                "secondary": {
                    "name": "JetBrains Mono",
                    "weights": [400, 500, 600],
                    "import_url": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap"
                }
            },
            "scale": {
                "ratio": 1.25,
                "base_size": "16px",
                "sizes": {
                    "xs": "0.75rem",
                    "sm": "0.875rem",
                    "base": "1rem",
                    "lg": "1.125rem",
                    "xl": "1.25rem",
                    "2xl": "1.5rem",
                    "3xl": "1.875rem",
                    "4xl": "2.25rem",
                    "5xl": "3rem",
                    "6xl": "3.75rem"
                }
            },
            "line_heights": {
                "tight": 1.2,
                "normal": 1.5,
                "loose": 1.8
            }
        }

        # Extract typography from brand-applied results
        for result in results:
            brand_applied = result.get("brand_applied", {})
            if brand_applied and brand_applied.get("fonts_applied"):
                # Update font families based on brand fonts
                fonts_applied = brand_applied["fonts_applied"]
                if fonts_applied:
                    typography["font_families"]["primary"]["name"] = fonts_applied[0]
                if len(fonts_applied) > 1:
                    typography["font_families"]["secondary"]["name"] = fonts_applied[1]

        return typography

    def _extract_spacing_from_results(self, results: List[Dict]) -> Dict:
        """Extract spacing system from results"""
        return {
            "scale": "geometric",
            "base_unit": 4,
            "values": {
                "0": "0",
                "1": "0.25rem",
                "2": "0.5rem",
                "3": "0.75rem",
                "4": "1rem",
                "5": "1.25rem",
                "6": "1.5rem",
                "8": "2rem",
                "10": "2.5rem",
                "12": "3rem",
                "16": "4rem",
                "20": "5rem",
                "24": "6rem"
            }
        }

    def _extract_borders_from_results(self, results: List[Dict]) -> Dict:
        """Extract border system from results"""
        return {
            "radius": {
                "none": "0",
                "sm": "0.125rem",
                "md": "0.375rem",
                "lg": "0.5rem",
                "full": "9999px"
            },
            "widths": {
                "thin": "1px",
                "medium": "2px",
                "thick": "4px"
            }
        }

    def _extract_shadows_from_results(self, results: List[Dict]) -> Dict:
        """Extract shadow system from results"""
        return {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
        }

    def convert_components_to_a2ui(self, results: List[Dict], design_system: Dict) -> List[Dict]:
        """
        Convert UI recommendations to A2UI component specifications

        Args:
            results: Search results containing UI component recommendations
            design_system: Design system tokens

        Returns:
            List of A2UI component specifications
        """
        components = []

        for result in results:
            component = self._convert_single_result_to_component(result, design_system)
            if component:
                components.append(component)

        return components

    def _convert_single_result_to_component(self, result: Dict, design_system: Dict) -> Optional[Dict]:
        """Convert a single search result to A2UI component"""
        term = result.get("term", "")
        if not term:
            return None

        # Generate unique component ID
        self.component_counter += 1
        component_id = f"component_{self.component_counter}"

        # Map term to component category
        category = self._determine_component_category(term, result)

        # Extract properties from result
        props = self._extract_component_props(result)

        # Generate responsive behavior
        responsive_behavior = self.generate_responsive_specifications(result, self._get_default_breakpoints())

        # Generate accessibility specs
        accessibility = self.generate_accessibility_specs(result)

        # Extract interactions
        interactions = self._extract_component_interactions(result)

        # Generate styling
        styling = self._generate_component_styling(result, design_system)

        component = {
            "id": component_id,
            "name": self._format_component_name(term),
            "category": category,
            "description": result.get("description", ""),
            "props": props,
            "variants": self._generate_component_variants(result),
            "responsive_behavior": responsive_behavior,
            "accessibility": accessibility,
            "interactions": interactions,
            "children": [],  # TODO: Extract child relationships
            "styling": styling
        }

        return component

    def _determine_component_category(self, term: str, result: Dict) -> str:
        """Determine component category based on term and context"""
        term_lower = term.lower()

        # UI Control categories
        if any(keyword in term_lower for keyword in ["button", "link", "input", "form", "select", "checkbox", "radio"]):
            return "form_controls"
        elif any(keyword in term_lower for keyword in ["modal", "dialog", "popup", "tooltip", "alert"]):
            return "feedback"
        elif any(keyword in term_lower for keyword in ["nav", "menu", "breadcrumb", "pagination", "tab"]):
            return "navigation"
        elif any(keyword in term_lower for keyword in ["card", "panel", "grid", "list", "table"]):
            return "layout"
        elif any(keyword in term_lower for keyword in ["chart", "graph", "visualization", "progress"]):
            return "data_display"
        else:
            return "general"

    def _extract_component_props(self, result: Dict) -> Dict:
        """Extract component properties from result"""
        props = {}

        # Common properties based on component type
        term_lower = result.get("term", "").lower()

        if "button" in term_lower:
            props = {
                "variant": {"type": "string", "default": "primary", "options": ["primary", "secondary", "outline", "ghost"]},
                "size": {"type": "string", "default": "md", "options": ["sm", "md", "lg"]},
                "disabled": {"type": "boolean", "default": False},
                "loading": {"type": "boolean", "default": False}
            }
        elif "input" in term_lower:
            props = {
                "type": {"type": "string", "default": "text"},
                "placeholder": {"type": "string", "default": ""},
                "disabled": {"type": "boolean", "default": False},
                "required": {"type": "boolean", "default": False}
            }
        elif "modal" in term_lower:
            props = {
                "open": {"type": "boolean", "default": False},
                "size": {"type": "string", "default": "md", "options": ["sm", "md", "lg", "xl"]},
                "closable": {"type": "boolean", "default": True},
                "backdrop_dismissible": {"type": "boolean", "default": True}
            }

        return props

    def _generate_component_variants(self, result: Dict) -> List[Dict]:
        """Generate component variants"""
        variants = []

        # Generate common variants based on component type
        term_lower = result.get("term", "").lower()

        if "button" in term_lower:
            variants = [
                {"name": "primary", "props": {"variant": "primary"}},
                {"name": "secondary", "props": {"variant": "secondary"}},
                {"name": "outline", "props": {"variant": "outline"}},
                {"name": "small", "props": {"size": "sm"}},
                {"name": "large", "props": {"size": "lg"}}
            ]

        return variants

    def _extract_component_interactions(self, result: Dict) -> List[Dict]:
        """Extract component interactions"""
        interactions = []

        term_lower = result.get("term", "").lower()

        if "button" in term_lower:
            interactions.append({
                "trigger": "click",
                "action": "emit",
                "parameters": {"event": "click"}
            })
        elif "input" in term_lower:
            interactions.extend([
                {"trigger": "input", "action": "emit", "parameters": {"event": "input"}},
                {"trigger": "focus", "action": "emit", "parameters": {"event": "focus"}},
                {"trigger": "blur", "action": "emit", "parameters": {"event": "blur"}}
            ])

        return interactions

    def _generate_component_styling(self, result: Dict, design_system: Dict) -> Dict:
        """Generate component styling"""
        styling = {
            "base": {},
            "states": {},
            "breakpoints": {}
        }

        # Extract styling from code examples
        code_example = result.get("code_example", "")
        if code_example:
            styling["base"] = self._parse_css_from_code(code_example)

        # Add state styling
        styling["states"] = {
            "hover": {"opacity": "0.8"},
            "focus": {"outline": "2px solid var(--color-primary)", "outline-offset": "2px"},
            "active": {"transform": "scale(0.98)"},
            "disabled": {"opacity": "0.5", "cursor": "not-allowed"}
        }

        return styling

    def _parse_css_from_code(self, code: str) -> Dict:
        """Parse CSS properties from code example"""
        css_props = {}

        # Extract CSS property-value pairs
        css_pattern = r'([a-z-]+):\s*([^;]+);'
        matches = re.findall(css_pattern, code)

        for prop, value in matches:
            css_props[prop] = value.strip()

        return css_props

    def generate_responsive_specifications(self, component: Dict, breakpoints: Dict) -> Dict:
        """
        Generate responsive behavior specifications for components

        Args:
            component: Component specification or result
            breakpoints: Responsive breakpoint definitions

        Returns:
            Responsive specifications for the component
        """
        return {
            "breakpoints": breakpoints,
            "responsive_props": {
                "mobile": {
                    "size": "sm",
                    "layout": "stacked",
                    "spacing": "tight"
                },
                "tablet": {
                    "size": "md",
                    "layout": "grid-2",
                    "spacing": "normal"
                },
                "desktop": {
                    "size": "lg",
                    "layout": "grid-3",
                    "spacing": "loose"
                }
            }
        }

    def generate_accessibility_specs(self, component: Dict) -> Dict:
        """
        Generate accessibility specifications for components

        Args:
            component: Component specification or result

        Returns:
            Accessibility requirements and ARIA attributes
        """
        term_lower = component.get("term", "").lower()

        accessibility = {
            "wcag_level": "AA",
            "aria_attributes": {"required": [], "recommended": [], "conditional": {}},
            "keyboard_navigation": {"focusable": True, "tab_order": 0, "keyboard_shortcuts": []},
            "screen_reader": {"descriptions": [], "announcements": []},
            "color_contrast": {"minimum_ratio": 4.5, "compliant_combinations": []}
        }

        # Add specific accessibility requirements based on component type
        if "button" in term_lower:
            accessibility["aria_attributes"]["required"] = ["aria-label"]
            accessibility["keyboard_navigation"]["keyboard_shortcuts"] = [
                {"key": "Enter", "action": "activate"},
                {"key": "Space", "action": "activate"}
            ]
        elif "input" in term_lower:
            accessibility["aria_attributes"]["required"] = ["aria-label", "aria-describedby"]
            accessibility["aria_attributes"]["conditional"]["aria-invalid"] = "when input is invalid"
        elif "modal" in term_lower:
            accessibility["aria_attributes"]["required"] = ["aria-modal", "role", "aria-labelledby"]
            accessibility["keyboard_navigation"]["keyboard_shortcuts"] = [
                {"key": "Escape", "action": "close"}
            ]

        return accessibility

    def export_for_platform(self, a2ui_spec: Dict, platform: str) -> Dict:
        """
        Generate platform-specific rendering instructions from A2UI specification

        Args:
            a2ui_spec: Complete A2UI specification
            platform: Target platform ("react", "vue", "flutter", "html")

        Returns:
            Platform-specific rendering instructions
        """
        if platform == "react":
            return self._export_for_react(a2ui_spec)
        elif platform == "vue":
            return self._export_for_vue(a2ui_spec)
        elif platform == "flutter":
            return self._export_for_flutter(a2ui_spec)
        elif platform == "html":
            return self._export_for_html(a2ui_spec)
        else:
            return {"error": f"Unsupported platform: {platform}"}

    def _export_for_react(self, a2ui_spec: Dict) -> Dict:
        """Export for React platform"""
        react_export = {
            "framework": "react",
            "components": [],
            "theme_provider": self._generate_react_theme_provider(a2ui_spec["design_system"]),
            "global_styles": self._generate_react_global_styles(a2ui_spec["design_system"]),
            "package_json": {
                "dependencies": {
                    "react": "^18.0.0",
                    "styled-components": "^6.0.0",
                    "@types/styled-components": "^5.1.0"
                }
            }
        }

        # Convert components to React
        for component in a2ui_spec.get("components", []):
            react_component = self._convert_component_to_react(component, a2ui_spec["design_system"])
            react_export["components"].append(react_component)

        return react_export

    def _export_for_flutter(self, a2ui_spec: Dict) -> Dict:
        """Export for Flutter platform"""
        flutter_export = {
            "framework": "flutter",
            "widgets": [],
            "theme_data": self._generate_flutter_theme_data(a2ui_spec["design_system"]),
            "pubspec_dependencies": {
                "flutter": {"sdk": "flutter"},
                "material_color_utilities": "^0.2.0"
            }
        }

        # Convert components to Flutter widgets
        for component in a2ui_spec.get("components", []):
            flutter_widget = self._convert_component_to_flutter(component, a2ui_spec["design_system"])
            flutter_export["widgets"].append(flutter_widget)

        return flutter_export

    def _export_for_html(self, a2ui_spec: Dict) -> Dict:
        """Export for HTML platform"""
        return {
            "framework": "html",
            "components": [
                self._convert_component_to_html(comp, a2ui_spec["design_system"])
                for comp in a2ui_spec.get("components", [])
            ],
            "css": self._generate_css_from_design_system(a2ui_spec["design_system"]),
            "javascript": self._generate_vanilla_js_interactions(a2ui_spec.get("interactions", []))
        }

    def _export_for_vue(self, a2ui_spec: Dict) -> Dict:
        """Export for Vue platform"""
        return {
            "framework": "vue",
            "components": [
                self._convert_component_to_vue(comp, a2ui_spec["design_system"])
                for comp in a2ui_spec.get("components", [])
            ],
            "composables": [],
            "theme_config": a2ui_spec["design_system"]
        }

    def validate_a2ui_spec(self, a2ui_spec: Dict) -> Dict:
        """
        Validate A2UI specification against protocol schema

        Args:
            a2ui_spec: A2UI specification to validate

        Returns:
            Validation result with detailed error information
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Check required fields
        required_fields = ["a2ui_version", "metadata", "design_system", "components"]
        for field in required_fields:
            if field not in a2ui_spec:
                validation["errors"].append(f"Missing required field: {field}")
                validation["valid"] = False

        # Validate metadata
        metadata = a2ui_spec.get("metadata", {})
        if not metadata.get("source"):
            validation["warnings"].append("Missing metadata source information")

        # Validate components
        components = a2ui_spec.get("components", [])
        for i, component in enumerate(components):
            component_errors = self._validate_component(component)
            if component_errors:
                validation["errors"].extend([f"Component {i}: {error}" for error in component_errors])
                validation["valid"] = False

        return validation

    def _validate_component(self, component: Dict) -> List[str]:
        """Validate individual component"""
        errors = []

        required_fields = ["id", "name", "category"]
        for field in required_fields:
            if field not in component:
                errors.append(f"Missing required field: {field}")

        return errors

    def optimize_a2ui_size(self, a2ui_spec: Dict) -> Dict:
        """
        Optimize A2UI specification size by removing redundant information

        Args:
            a2ui_spec: A2UI specification to optimize

        Returns:
            Optimized A2UI specification
        """
        optimized = a2ui_spec.copy()

        # Remove empty arrays and objects
        optimized = self._remove_empty_values(optimized)

        # Compress design system tokens
        if "design_system" in optimized:
            optimized["design_system"] = self._compress_design_system(optimized["design_system"])

        return optimized

    def _remove_empty_values(self, obj: Any) -> Any:
        """Recursively remove empty values from nested structures"""
        if isinstance(obj, dict):
            return {k: self._remove_empty_values(v) for k, v in obj.items()
                   if v not in [None, "", [], {}]}
        elif isinstance(obj, list):
            return [self._remove_empty_values(item) for item in obj if item not in [None, "", [], {}]]
        else:
            return obj

    def _compress_design_system(self, design_system: Dict) -> Dict:
        """Compress design system by removing redundant tokens"""
        compressed = design_system.copy()

        # Remove duplicate color values
        if "colors" in compressed:
            colors = compressed["colors"]
            # Keep only unique colors
            seen_colors = set()
            for key, value in list(colors.items()):
                if isinstance(value, str):
                    if value in seen_colors:
                        continue
                    seen_colors.add(value)

        return compressed

    # Helper methods for platform-specific generation
    def _generate_react_theme_provider(self, design_system: Dict) -> str:
        """Generate React theme provider code"""
        return """
import { ThemeProvider, createGlobalStyle } from 'styled-components';

const theme = {
  colors: {
    primary: '""" + design_system.get("colors", {}).get("primary", "#3b82f6") + """',
    secondary: '""" + design_system.get("colors", {}).get("secondary", "#64748b") + """'
  }
};

export { theme, ThemeProvider };
"""

    def _generate_react_global_styles(self, design_system: Dict) -> str:
        """Generate React global styles"""
        return """
const GlobalStyles = createGlobalStyle`
  :root {
    --color-primary: """ + design_system.get("colors", {}).get("primary", "#3b82f6") + """;
  }
`;

export default GlobalStyles;
"""

    def _convert_component_to_react(self, component: Dict, design_system: Dict) -> Dict:
        """Convert component to React format"""
        return {
            "name": component["name"],
            "file_path": f"components/{component['name']}.tsx",
            "jsx_template": self._generate_react_jsx_template(component),
            "props_interface": self._generate_react_props_interface(component),
            "styled_components": self._generate_react_styled_components(component, design_system),
            "hooks_required": [],
            "dependencies": []
        }

    def _generate_react_jsx_template(self, component: Dict) -> str:
        """Generate React JSX template"""
        return f"""
import React from 'react';
import {{ Styled{component['name']} }} from './{component['name']}.styles';

interface {component['name']}Props {{
  // Props will be generated based on component specification
}}

export const {component['name']}: React.FC<{component['name']}Props> = (props) => {{
  return (
    <Styled{component['name']} {{...props}}>
      {{props.children}}
    </Styled{component['name']}>
  );
}};
"""

    def _generate_react_props_interface(self, component: Dict) -> str:
        """Generate TypeScript props interface"""
        props = component.get("props", {})
        interface_props = []

        for prop_name, prop_config in props.items():
            prop_type = prop_config.get("type", "any")
            optional = "?" if not prop_config.get("required", False) else ""
            interface_props.append(f"  {prop_name}{optional}: {prop_type};")

        return f"""
interface {component['name']}Props {{
{chr(10).join(interface_props)}
}}
"""

    def _generate_react_styled_components(self, component: Dict, design_system: Dict) -> str:
        """Generate styled-components CSS"""
        return f"""
import styled from 'styled-components';

export const Styled{component['name']} = styled.div`
  // Base styles
  color: var(--color-primary);
`;
"""

    def _generate_flutter_theme_data(self, design_system: Dict) -> str:
        """Generate Flutter ThemeData"""
        colors = design_system.get("colors", {})
        return f"""
ThemeData(
  primarySwatch: Colors.blue,
  primaryColor: Color(0xFF{colors.get('primary', '#3b82f6').lstrip('#')}),
  colorScheme: ColorScheme.fromSeed(
    seedColor: Color(0xFF{colors.get('primary', '#3b82f6').lstrip('#')}),
  ),
)
"""

    def _convert_component_to_flutter(self, component: Dict, design_system: Dict) -> Dict:
        """Convert component to Flutter widget"""
        return {
            "name": component["name"],
            "file_path": f"lib/widgets/{component['name'].lower()}.dart",
            "dart_class": self._generate_flutter_dart_class(component),
            "theme_integration": "Uses Theme.of(context)",
            "state_management": "StatefulWidget",
            "accessibility": "Semantics widget integration"
        }

    def _generate_flutter_dart_class(self, component: Dict) -> str:
        """Generate Flutter Dart class"""
        return f"""
class {component['name']} extends StatelessWidget {{
  const {component['name']}({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return Container(
      // Widget implementation
    );
  }}
}}
"""

    def _convert_component_to_html(self, component: Dict, design_system: Dict) -> Dict:
        """Convert component to HTML"""
        return {
            "tag": "div",
            "attributes": {"class": component["name"].lower()},
            "content": f"<div class='{component['name'].lower()}'></div>",
            "css_class": component["name"].lower()
        }

    def _convert_component_to_vue(self, component: Dict, design_system: Dict) -> Dict:
        """Convert component to Vue component"""
        return {
            "name": component["name"],
            "template": f"<div class='{component['name'].lower()}'></div>",
            "script": "export default { name: '" + component["name"] + "' }",
            "style": f".{component['name'].lower()} {{ color: var(--color-primary); }}"
        }

    def _generate_css_from_design_system(self, design_system: Dict) -> str:
        """Generate CSS from design system"""
        css_lines = [":root {"]

        colors = design_system.get("colors", {})
        for key, value in colors.items():
            if isinstance(value, str):
                css_lines.append(f"  --color-{key}: {value};")

        css_lines.append("}")
        return "\n".join(css_lines)

    def _generate_vanilla_js_interactions(self, interactions: List[Dict]) -> str:
        """Generate vanilla JavaScript for interactions"""
        return """
// Interaction handlers
document.addEventListener('DOMContentLoaded', function() {
  // Interaction code will be generated based on specifications
});
"""

    def _generate_layouts_from_results(self, results: List[Dict]) -> List[Dict]:
        """Generate layout specifications from results"""
        layouts = []
        # TODO: Implement layout extraction logic
        return layouts

    def _generate_interactions_from_results(self, results: List[Dict]) -> List[Dict]:
        """Generate interaction specifications from results"""
        interactions = []
        # TODO: Implement interaction extraction logic
        return interactions

    def _apply_default_export_options(self, options: Dict) -> Dict:
        """Apply default export options"""
        defaults = {
            "include_design_system": True,
            "include_components": True,
            "include_layouts": True,
            "include_interactions": True,
            "target_platforms": ["html", "react"],
            "accessibility_level": "AA",
            "responsive_breakpoints": self._get_default_breakpoints(),
            "code_examples": True,
            "optimization_level": "standard",
            "brand_integration": True,
            "export_format": "json"
        }

        # Merge with provided options
        for key, value in defaults.items():
            if key not in options:
                options[key] = value

        return options

    def _get_default_breakpoints(self) -> Dict:
        """Get default responsive breakpoints"""
        return {
            "mobile": {"min_width": "0px", "max_width": "767px"},
            "tablet": {"min_width": "768px", "max_width": "1023px"},
            "desktop": {"min_width": "1024px"}
        }

    def _format_component_name(self, term: str) -> str:
        """Format term as component name"""
        # Convert to PascalCase
        words = re.sub(r'[^a-zA-Z0-9\s]', '', term).split()
        return ''.join(word.capitalize() for word in words if word)

    def _create_empty_a2ui_spec(self) -> Dict:
        """Create empty A2UI specification"""
        return {
            "a2ui_version": "1.0.0",
            "metadata": {
                "source": "ui-ux-pro-max",
                "generated_at": datetime.now().isoformat(),
                "query_info": {
                    "original_query": "",
                    "domain": "",
                    "result_count": 0
                }
            },
            "design_system": {},
            "components": [],
            "layouts": [],
            "interactions": [],
            "rendering_targets": {}
        }


# Convenience functions
def export_to_a2ui(results: List[Dict], export_options: Optional[Dict] = None) -> Dict:
    """Export to A2UI (convenience function)"""
    exporter = A2UIExporter()
    return exporter.export_to_a2ui(results, export_options)


def validate_a2ui_spec(a2ui_spec: Dict) -> Dict:
    """Validate A2UI specification (convenience function)"""
    exporter = A2UIExporter()
    return exporter.validate_a2ui_spec(a2ui_spec)