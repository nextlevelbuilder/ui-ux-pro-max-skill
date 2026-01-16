# A2UI Exporter API Contract

**Feature**: [spec.md](../spec.md) | **Data Model**: [data-model.md](../data-model.md)
**Date**: 2026-01-16

## Overview

This contract defines the API for exporting UI/UX Pro Max search results to A2UI (Agent-to-UI) protocol format. The A2UI Exporter enables declarative UI specification and cross-platform rendering of design recommendations.

## Module: `a2ui_exporter.py`

### Core Functions

#### `export_to_a2ui(results: List[Dict], export_options: Dict = None) -> Dict`

**Purpose**: Convert search results to A2UI protocol format for cross-platform UI generation

**Parameters**:
- `results`: Search results from UI/UX Pro Max search
- `export_options`: Export configuration options

**Returns**: A2UI protocol specification document

**A2UI Schema**:
```python
{
    "a2ui_version": "1.0.0",
    "metadata": {
        "source": "ui-ux-pro-max",
        "generated_at": str,        # ISO timestamp
        "query_info": {
            "original_query": str,
            "domain": str,
            "result_count": int
        },
        "export_options": Dict
    },
    "design_system": {
        "colors": {
            "primary": str,
            "secondary": str,
            "accent": str,
            "neutral": {
                "50": str, "100": str, "200": str, # ... up to "900"
            },
            "semantic": {
                "success": str,
                "warning": str,
                "error": str,
                "info": str
            }
        },
        "typography": {
            "font_families": {
                "primary": {
                    "name": str,
                    "weights": List[int],
                    "import_url": str
                },
                "secondary": {
                    "name": str,
                    "weights": List[int],
                    "import_url": str
                }
            },
            "scale": {
                "ratio": float,
                "base_size": str,
                "sizes": {
                    "xs": str, "sm": str, "base": str, "lg": str, "xl": str,
                    "2xl": str, "3xl": str, "4xl": str, "5xl": str, "6xl": str
                }
            },
            "line_heights": {
                "tight": float,
                "normal": float,
                "loose": float
            }
        },
        "spacing": {
            "scale": str,           # "geometric" | "linear"
            "base_unit": int,       # Base spacing unit in px
            "values": {
                "0": str, "1": str, "2": str, # ... spacing scale
            }
        },
        "borders": {
            "radius": {
                "none": str, "sm": str, "md": str, "lg": str, "full": str
            },
            "widths": {
                "thin": str, "medium": str, "thick": str
            }
        },
        "shadows": {
            "sm": str, "md": str, "lg": str, "xl": str
        }
    },
    "components": List[{
        "id": str,                  # Unique component identifier
        "name": str,                # Component name
        "category": str,            # Component category
        "description": str,         # Component description
        "props": Dict,              # Component properties
        "variants": List[Dict],     # Component variants
        "responsive_behavior": Dict, # Responsive specifications
        "accessibility": Dict,      # Accessibility specifications
        "interactions": List[Dict], # User interactions
        "children": List[str],      # Child component IDs
        "styling": {
            "base": Dict,           # Base styles
            "states": Dict,         # State-based styles (hover, focus, etc.)
            "breakpoints": Dict     # Responsive breakpoint styles
        }
    }],
    "layouts": List[{
        "id": str,
        "name": str,
        "type": str,                # "grid" | "flex" | "absolute"
        "structure": Dict,          # Layout structure definition
        "responsive": Dict,         # Responsive layout rules
        "components": List[str]     # Component IDs in this layout
    }],
    "interactions": List[{
        "id": str,
        "trigger": str,             # Event trigger
        "target": str,              # Target component ID
        "action": str,              # Action to perform
        "parameters": Dict,         # Action parameters
        "conditions": List[Dict]    # Conditional logic
    }],
    "rendering_targets": {
        "react": Dict,              # React-specific rendering instructions
        "vue": Dict,                # Vue-specific rendering instructions
        "flutter": Dict,            # Flutter-specific rendering instructions
        "html": Dict                # HTML/CSS rendering instructions
    }
}
```

#### `extract_design_system(results: List[Dict]) -> Dict`

**Purpose**: Extract design system tokens from search results

**Parameters**:
- `results`: Search results containing design system information

**Returns**: Design system specification for A2UI

**Processing Logic**:
1. **Color Extraction**: Extract color palettes from color domain results
2. **Typography Processing**: Process font pairings and typography scales
3. **Spacing Analysis**: Derive spacing system from layout results
4. **Component Analysis**: Identify reusable design patterns
5. **Token Generation**: Generate design tokens for cross-platform use

#### `convert_components_to_a2ui(results: List[Dict], design_system: Dict) -> List[Dict]`

**Purpose**: Convert UI recommendations to A2UI component specifications

**Parameters**:
- `results`: Search results containing UI component recommendations
- `design_system`: Design system tokens

**Returns**: List of A2UI component specifications

**Component Mapping Logic**:
```python
# Map UI/UX Pro Max terms to A2UI components
COMPONENT_MAPPING = {
    "button": {
        "a2ui_type": "interactive",
        "category": "form_controls",
        "base_props": ["variant", "size", "disabled", "loading"],
        "accessibility": ["aria-label", "role", "tabindex"]
    },
    "card": {
        "a2ui_type": "container",
        "category": "layout",
        "base_props": ["elevation", "padding", "border_radius"],
        "accessibility": ["aria-labelledby", "role"]
    },
    "modal": {
        "a2ui_type": "overlay",
        "category": "feedback",
        "base_props": ["size", "closable", "backdrop_dismissible"],
        "accessibility": ["aria-modal", "role", "focus_management"]
    }
}
```

#### `generate_responsive_specifications(component: Dict, breakpoints: Dict) -> Dict`

**Purpose**: Generate responsive behavior specifications for components

**Parameters**:
- `component`: Component specification
- `breakpoints`: Responsive breakpoint definitions

**Returns**: Responsive specifications for the component

**Responsive Schema**:
```python
{
    "breakpoints": {
        "mobile": {"min_width": "0px", "max_width": "767px"},
        "tablet": {"min_width": "768px", "max_width": "1023px"},
        "desktop": {"min_width": "1024px"}
    },
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
```

#### `generate_accessibility_specs(component: Dict) -> Dict`

**Purpose**: Generate accessibility specifications for components

**Returns**: Accessibility requirements and ARIA attributes

**Accessibility Schema**:
```python
{
    "wcag_level": "AA",
    "aria_attributes": {
        "required": List[str],      # Required ARIA attributes
        "recommended": List[str],   # Recommended ARIA attributes
        "conditional": Dict         # Conditional ARIA requirements
    },
    "keyboard_navigation": {
        "focusable": bool,
        "tab_order": int,
        "keyboard_shortcuts": List[Dict]
    },
    "screen_reader": {
        "descriptions": List[str],
        "announcements": List[str]
    },
    "color_contrast": {
        "minimum_ratio": float,
        "compliant_combinations": List[Tuple[str, str]]
    }
}
```

#### `export_for_platform(a2ui_spec: Dict, platform: str) -> Dict`

**Purpose**: Generate platform-specific rendering instructions from A2UI specification

**Parameters**:
- `a2ui_spec`: Complete A2UI specification
- `platform`: Target platform ("react", "vue", "flutter", "html")

**Returns**: Platform-specific rendering instructions

**Platform Mappings**:

**React Platform**:
```python
{
    "framework": "react",
    "components": List[{
        "name": str,
        "file_path": str,
        "jsx_template": str,         # JSX component template
        "props_interface": str,      # TypeScript interface
        "styled_components": str,    # Styled-components CSS
        "hooks_required": List[str], # Required React hooks
        "dependencies": List[str]    # NPM package dependencies
    }],
    "theme_provider": str,          # Theme provider setup
    "global_styles": str,           # Global CSS/styled-components
    "package_json": Dict            # Required dependencies
}
```

**Flutter Platform**:
```python
{
    "framework": "flutter",
    "widgets": List[{
        "name": str,
        "file_path": str,
        "dart_class": str,           # Dart widget class
        "theme_integration": str,    # Flutter theme integration
        "state_management": str,     # State management approach
        "accessibility": str         # Flutter accessibility implementation
    }],
    "theme_data": str,              # Flutter ThemeData configuration
    "pubspec_dependencies": Dict    # pubspec.yaml dependencies
}
```

### Utility Functions

#### `validate_a2ui_spec(a2ui_spec: Dict) -> ValidationResult`

**Purpose**: Validate A2UI specification against protocol schema

**Returns**: Validation result with detailed error information

#### `optimize_a2ui_size(a2ui_spec: Dict) -> Dict`

**Purpose**: Optimize A2UI specification size by removing redundant information

#### `merge_design_systems(systems: List[Dict]) -> Dict`

**Purpose**: Merge multiple design systems into a cohesive A2UI design system

## Export Options

### Configuration Schema

```python
ExportOptions = {
    "include_design_system": bool,      # Include design tokens
    "include_components": bool,         # Include component specifications
    "include_layouts": bool,           # Include layout specifications
    "include_interactions": bool,       # Include interaction specifications
    "target_platforms": List[str],      # Target rendering platforms
    "accessibility_level": str,        # "A", "AA", "AAA"
    "responsive_breakpoints": Dict,     # Custom breakpoint definitions
    "code_examples": bool,             # Include platform-specific code
    "optimization_level": str,         # "none", "standard", "aggressive"
    "brand_integration": bool,         # Apply brand configuration
    "export_format": str              # "json", "yaml", "compressed"
}
```

## Integration Points

### With `search.py` (CLI)

```python
# CLI integration for A2UI export
def main():
    # ... existing search logic ...

    # Add A2UI export option
    if args.export_a2ui:
        export_options = {
            "target_platforms": args.platforms or ["html", "react"],
            "include_design_system": True,
            "accessibility_level": "AA"
        }
        a2ui_spec = export_to_a2ui(results, export_options)

        # Save A2UI specification
        output_path = args.a2ui_output or "ui-specification.json"
        with open(output_path, 'w') as f:
            json.dump(a2ui_spec, f, indent=2)

        print(f"A2UI specification exported to: {output_path}")
```

### With `brand_processor.py`

```python
# Brand integration with A2UI export
def export_with_brand(results: List[Dict], brand_config: Dict, export_options: Dict) -> Dict:
    """
    Export to A2UI with brand configuration applied

    Args:
        results: Search results
        brand_config: Brand configuration
        export_options: Export configuration

    Returns:
        Brand-enhanced A2UI specification
    """
```

## Platform-Specific Examples

### React Component Generation

**A2UI Component**:
```json
{
  "id": "primary_button",
  "name": "PrimaryButton",
  "category": "form_controls",
  "props": {
    "variant": {"type": "string", "default": "filled"},
    "size": {"type": "string", "default": "md"},
    "disabled": {"type": "boolean", "default": false}
  }
}
```

**Generated React Code**:
```typescript
import React from 'react';
import styled from 'styled-components';

interface PrimaryButtonProps {
  variant?: 'filled' | 'outlined' | 'text';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

const StyledButton = styled.button<PrimaryButtonProps>`
  background-color: ${props => props.variant === 'filled' ? 'var(--color-primary)' : 'transparent'};
  color: ${props => props.variant === 'filled' ? 'white' : 'var(--color-primary)'};
  border: 1px solid var(--color-primary);
  padding: ${props => {
    switch(props.size) {
      case 'sm': return '0.5rem 1rem';
      case 'lg': return '1rem 2rem';
      default: return '0.75rem 1.5rem';
    }
  }};
  border-radius: var(--border-radius-md);
  font-family: var(--font-primary);

  &:hover:not(:disabled) {
    background-color: ${props => props.variant === 'filled' ? 'var(--color-primary-dark)' : 'var(--color-primary-light)'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

export const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  variant = 'filled',
  size = 'md',
  disabled = false,
  children,
  onClick
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      disabled={disabled}
      onClick={onClick}
      aria-label={typeof children === 'string' ? children : undefined}
    >
      {children}
    </StyledButton>
  );
};
```

## Error Handling

### Export Errors

```python
{
    "error": "invalid_component_specification",
    "component_id": "custom_button",
    "field": "props.variant.type",
    "message": "Component prop type must be one of: string, number, boolean, array, object",
    "action": "skip_component_continue_export"
}
```

### Platform Rendering Errors

```python
{
    "error": "unsupported_platform_feature",
    "platform": "flutter",
    "feature": "css_grid_layout",
    "message": "CSS Grid layout not supported in Flutter platform",
    "action": "use_alternative_layout_system"
}
```

## Testing Contract

### Unit Test Requirements

```python
class TestA2UIExporter(unittest.TestCase):
    def test_export_to_a2ui_basic(self):
        """Test basic A2UI export functionality"""

    def test_extract_design_system(self):
        """Test design system extraction from results"""

    def test_convert_components_to_a2ui(self):
        """Test component conversion to A2UI format"""

    def test_generate_responsive_specifications(self):
        """Test responsive specification generation"""

    def test_generate_accessibility_specs(self):
        """Test accessibility specification generation"""

    def test_export_for_platform_react(self):
        """Test React platform export"""

    def test_export_for_platform_flutter(self):
        """Test Flutter platform export"""

    def test_validate_a2ui_spec(self):
        """Test A2UI specification validation"""
```

### Integration Test Requirements

```python
class TestA2UIExporterIntegration(unittest.TestCase):
    def test_end_to_end_export_workflow(self):
        """Test complete export workflow from search to A2UI"""

    def test_multi_platform_export(self):
        """Test exporting to multiple platforms simultaneously"""

    def test_brand_integrated_export(self):
        """Test A2UI export with brand configuration"""

    def test_large_specification_export(self):
        """Test performance with large A2UI specifications"""
```

This contract provides comprehensive A2UI export functionality, enabling cross-platform UI generation from UI/UX Pro Max recommendations.