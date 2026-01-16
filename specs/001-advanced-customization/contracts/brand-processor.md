# Brand Processor API Contract

**Feature**: [spec.md](../spec.md) | **Data Model**: [data-model.md](../data-model.md)
**Date**: 2026-01-16

## Overview

This contract defines the API for processing personal/company brand configurations and integrating them with design system recommendations. The Brand Processor applies brand-specific modifications to search results while maintaining design excellence.

## Module: `brand_processor.py`

### Core Functions

#### `apply_brand_config(results: List[Dict], brand_config: Dict) -> List[Dict]`

**Purpose**: Apply brand configuration to search results, modifying recommendations to incorporate brand elements

**Parameters**:
- `results`: Search results from core search engine
- `brand_config`: Brand configuration dictionary from external config

**Returns**: Modified search results with brand-specific recommendations

**Processing Logic**:
1. **Color Integration**: Replace generic colors with brand colors in recommendations
2. **Typography Application**: Prioritize brand fonts in typography suggestions
3. **Style Filtering**: Filter results based on brand style preferences
4. **Industry Context**: Apply industry-specific design patterns
5. **Consistency Enforcement**: Ensure brand consistency across all recommendations

**Schema**:
```python
# Input results format (from core search)
List[{
    "term": str,
    "description": str,
    "examples": str,
    "code_example": str,
    "reasoning": str,
    "score": float,
    "domain": str
}]

# Output results format (brand-enhanced)
List[{
    "term": str,
    "description": str,           # Modified with brand context
    "examples": str,              # Updated with brand examples
    "code_example": str,          # Modified with brand colors/fonts
    "reasoning": str,             # Enhanced with brand reasoning
    "score": float,               # Adjusted for brand relevance
    "domain": str,
    "brand_applied": {
        "colors_replaced": List[str],    # Colors replaced with brand colors
        "fonts_applied": List[str],      # Fonts replaced with brand fonts
        "styles_filtered": bool,         # Whether style filtering was applied
        "industry_context": str,         # Applied industry context
        "modifications": List[str]       # List of brand modifications made
    }
}]
```

#### `extract_brand_colors(brand_config: Dict) -> Dict`

**Purpose**: Extract and process brand colors for use in design recommendations

**Parameters**:
- `brand_config`: Brand configuration with colors section

**Returns**: Processed color palette ready for application

**Schema**:
```python
{
    "primary_palette": {
        "primary": str,           # Hex color code
        "primary_light": str,     # Generated lighter variant
        "primary_dark": str,      # Generated darker variant
        "primary_variants": List[str]  # Generated color variants
    },
    "secondary_palette": {
        "secondary": str,
        "secondary_light": str,
        "secondary_dark": str,
        "secondary_variants": List[str]
    },
    "accent_palette": {
        "accent": str,
        "accent_light": str,
        "accent_dark": str,
        "accent_variants": List[str]
    },
    "neutral_palette": {
        "dark": str,
        "medium": str,
        "light": str,
        "variants": List[str]
    },
    "semantic_palette": {
        "success": str,
        "warning": str,
        "error": str,
        "info": str
    },
    "accessibility": {
        "aa_compliant_pairs": List[Tuple[str, str]],  # (text, background) pairs
        "aaa_compliant_pairs": List[Tuple[str, str]], # AAA compliant pairs
        "contrast_ratios": Dict[str, float]           # Contrast ratio calculations
    }
}
```

#### `apply_brand_typography(results: List[Dict], typography_config: Dict) -> List[Dict]`

**Purpose**: Apply brand typography preferences to typography and design recommendations

**Parameters**:
- `results`: Search results containing typography recommendations
- `typography_config`: Typography section from brand configuration

**Returns**: Results with brand typography applied

**Processing Logic**:
1. **Font Replacement**: Replace generic font recommendations with brand fonts
2. **Google Fonts Integration**: Ensure brand fonts have proper Google Fonts imports
3. **Fallback Chain**: Create proper fallback font stacks
4. **Scale Application**: Apply brand typography scale to size recommendations
5. **Line Height Adjustment**: Apply brand line height preferences

#### `filter_by_style_preferences(results: List[Dict], style_preferences: Dict) -> List[Dict]`

**Purpose**: Filter and rank results based on brand style preferences

**Parameters**:
- `results`: Search results to filter
- `style_preferences`: Style preferences from brand configuration

**Returns**: Filtered and re-ranked results

**Processing Logic**:
1. **Preferred Styles**: Boost scores for preferred styles
2. **Avoided Styles**: Lower scores or remove avoided styles
3. **Design Philosophy**: Apply philosophy-based filtering
4. **Industry Alignment**: Prioritize industry-appropriate patterns

**Schema**:
```python
{
    "filtered_count": int,        # Number of results filtered out
    "boosted_count": int,         # Number of results with boosted scores
    "style_matches": Dict[str, int],  # Count of matches per style preference
    "philosophy_applied": str,    # Design philosophy applied
    "industry_context": str       # Industry context applied
}
```

#### `generate_brand_aware_examples(result: Dict, brand_config: Dict) -> Dict`

**Purpose**: Generate brand-specific code examples and implementation details

**Parameters**:
- `result`: Single search result to enhance
- `brand_config`: Complete brand configuration

**Returns**: Result with brand-aware examples and code snippets

**Processing Logic**:
1. **Color Variable Injection**: Replace hardcoded colors with brand color variables
2. **Font Integration**: Update font-family declarations with brand fonts
3. **Class Name Conventions**: Apply brand-specific naming conventions
4. **Component Branding**: Add brand-specific component variations
5. **CSS Custom Properties**: Generate brand-aware CSS variables

#### `validate_brand_config(brand_config: Dict) -> ValidationResult`

**Purpose**: Validate brand configuration for completeness and correctness

**Parameters**:
- `brand_config`: Brand configuration to validate

**Returns**: Validation result with detailed feedback

**Schema**:
```python
ValidationResult = {
    "valid": bool,
    "errors": List[Dict],
    "warnings": List[Dict],
    "completeness_score": float,  # 0.0 to 1.0 completeness rating
    "sections": {
        "colors": {
            "valid": bool,
            "required_present": List[str],
            "missing_required": List[str],
            "accessibility_warnings": List[str],
            "contrast_issues": List[Dict]
        },
        "typography": {
            "valid": bool,
            "fonts_available": List[str],
            "google_fonts_valid": bool,
            "fallback_chains": List[str],
            "scale_valid": bool
        },
        "style_preferences": {
            "valid": bool,
            "preferences_count": int,
            "conflicts": List[str],
            "recommendations": List[str]
        }
    }
}
```

### Utility Functions

#### `calculate_color_variants(base_color: str, variant_count: int = 5) -> List[str]`

**Purpose**: Generate color variants from a base brand color

**Parameters**:
- `base_color`: Hex color code
- `variant_count`: Number of variants to generate

**Returns**: List of color variants (lighter and darker shades)

#### `check_color_accessibility(text_color: str, background_color: str) -> Dict`

**Purpose**: Calculate color contrast ratios and accessibility compliance

**Returns**:
```python
{
    "contrast_ratio": float,
    "aa_compliant": bool,
    "aaa_compliant": bool,
    "wcag_level": str
}
```

#### `generate_css_variables(brand_config: Dict) -> str`

**Purpose**: Generate CSS custom properties from brand configuration

**Returns**: CSS string with brand color and typography variables

**Example Output**:
```css
:root {
  /* Brand Colors */
  --brand-primary: #1a73e8;
  --brand-primary-light: #4285f4;
  --brand-primary-dark: #1557b0;

  /* Brand Typography */
  --brand-font-primary: 'Inter', system-ui, -apple-system, sans-serif;
  --brand-font-secondary: 'JetBrains Mono', Consolas, Monaco, monospace;

  /* Brand Spacing */
  --brand-spacing-xs: 0.5rem;
  --brand-spacing-sm: 1rem;
  --brand-spacing-md: 1.5rem;
  --brand-spacing-lg: 2rem;

  /* Brand Borders */
  --brand-radius-sm: 4px;
  --brand-radius-md: 8px;
  --brand-radius-lg: 16px;
}
```

#### `extract_brand_reasoning(brand_config: Dict) -> List[str]`

**Purpose**: Extract brand-specific reasoning rules for search ranking

**Returns**: List of reasoning adjustments to apply to search results

## Integration Points

### With `config_loader.py`

```python
# Brand configuration loading interface
def load_brand_configuration(config_path: str) -> Dict:
    """
    Load brand configuration from external config

    Returns:
        Validated brand configuration ready for processing
    """
```

### With `core.py`

```python
# Enhanced search function with brand support
def search_with_brand(query: str, domain: str = None, brand_config: Dict = None) -> List[Dict]:
    """
    Perform search with brand configuration integration

    Args:
        query: Search query
        domain: Domain filter
        brand_config: Brand configuration from external config

    Returns:
        Brand-enhanced search results
    """
```

### With `search.py` (CLI)

```python
# CLI integration for brand-aware search
def search_with_brand_options(query: str, brand_enabled: bool = True) -> List[Dict]:
    """
    CLI search function with brand configuration support
    """
```

## Brand Application Examples

### Color Application

**Before** (Generic recommendation):
```css
.button {
  background-color: #007bff;
  color: #ffffff;
  border: 1px solid #007bff;
}
```

**After** (Brand-applied):
```css
.button {
  background-color: var(--brand-primary); /* #1a73e8 from brand config */
  color: #ffffff;
  border: 1px solid var(--brand-primary);
}

.button:hover {
  background-color: var(--brand-primary-dark); /* Generated variant */
}
```

### Typography Application

**Before** (Generic recommendation):
```css
.heading {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 600;
}
```

**After** (Brand-applied):
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.heading {
  font-family: var(--brand-font-primary); /* 'Inter' from brand config */
  font-weight: 600;
}
```

### Style Preference Filtering

**Brand Configuration**:
```json
{
  "style_preferences": {
    "preferred_styles": ["minimalism", "glassmorphism"],
    "avoided_styles": ["brutalism", "claymorphism"]
  }
}
```

**Result**: Search results for UI styles will:
- Boost minimalism and glassmorphism recommendations (higher scores)
- Filter out or lower scores for brutalism and claymorphism
- Apply minimalist principles to other design recommendations

## Error Handling

### Brand Configuration Errors

```python
{
    "error": "invalid_color_format",
    "field": "colors.primary",
    "value": "blue",
    "message": "Color must be in hex format (#RRGGBB)",
    "action": "use_default_primary_color"
}
```

### Typography Errors

```python
{
    "error": "font_not_available",
    "field": "typography.primary_font.name",
    "value": "CustomFont",
    "message": "Font not available in Google Fonts",
    "action": "use_fallback_font"
}
```

### Accessibility Warnings

```python
{
    "warning": "low_contrast_ratio",
    "text_color": "#cccccc",
    "background_color": "#ffffff",
    "contrast_ratio": 2.1,
    "wcag_requirement": 4.5,
    "recommendation": "Use darker text color for better accessibility"
}
```

## Testing Contract

### Unit Test Requirements

```python
class TestBrandProcessor(unittest.TestCase):
    def test_apply_brand_config_colors(self):
        """Test color application to search results"""

    def test_apply_brand_config_typography(self):
        """Test typography application to search results"""

    def test_filter_by_style_preferences(self):
        """Test style preference filtering"""

    def test_generate_brand_aware_examples(self):
        """Test brand-specific code example generation"""

    def test_validate_brand_config(self):
        """Test brand configuration validation"""

    def test_calculate_color_variants(self):
        """Test color variant generation"""

    def test_check_color_accessibility(self):
        """Test color accessibility validation"""

    def test_generate_css_variables(self):
        """Test CSS custom property generation"""
```

### Integration Test Requirements

```python
class TestBrandProcessorIntegration(unittest.TestCase):
    def test_end_to_end_brand_application(self):
        """Test complete brand application workflow"""

    def test_accessibility_compliance(self):
        """Test accessibility compliance of brand-applied results"""

    def test_multiple_brand_configurations(self):
        """Test switching between different brand configurations"""

    def test_performance_with_large_results(self):
        """Test performance with large result sets"""
```

This contract ensures robust brand integration that enhances user recommendations while maintaining design quality and accessibility standards.