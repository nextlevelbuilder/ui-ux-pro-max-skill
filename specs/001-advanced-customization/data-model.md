# Data Model: Advanced Customization Architecture

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Research**: [research.md](research.md)
**Date**: 2026-01-16

## Overview

This document defines the data structures, entity relationships, and storage patterns for the Advanced Customization Architecture. The design extends the existing CSV-based architecture while adding JSON configuration support for complex data structures.

## Core Entities

### 1. External Configuration Entity

**Purpose**: Represents user-defined customizations stored outside core skill files

**Storage**: File system directory structure `.ui-ux-pro-max-config/`

**Structure**:
```text
.ui-ux-pro-max-config/
├── config.json              # Main configuration file
├── domains/                 # Custom domain CSV files
│   ├── custom-domain.csv
│   └── industry-specific.csv
├── stacks/                  # Custom stack CSV files
│   ├── custom-stack.csv
│   └── enterprise-tools.csv
├── reasoning/               # Custom reasoning rules
│   ├── reasoning.json
│   └── priorities.json
├── brand/                   # Brand configuration files
│   ├── brand.json
│   ├── colors.json
│   └── typography.json
└── extensions/              # MCP server extensions (future)
    └── mcp-config.json
```

**Main Configuration Schema** (`config.json`):
```json
{
  "version": "1.0.0",
  "enabled": true,
  "domains": {
    "enabled": ["custom-domain", "industry-specific"],
    "disabled": []
  },
  "stacks": {
    "enabled": ["custom-stack", "enterprise-tools"],
    "disabled": []
  },
  "brand": {
    "enabled": true,
    "file": "brand/brand.json"
  },
  "reasoning": {
    "enabled": true,
    "files": ["reasoning/reasoning.json", "reasoning/priorities.json"]
  },
  "performance": {
    "max_entries": 1000,
    "cache_enabled": true,
    "warning_threshold": 800
  },
  "logging": {
    "level": "INFO",
    "conflicts": true,
    "validation": true
  }
}
```

### 2. Brand Configuration Entity

**Purpose**: Represents personal/company branding elements for design system integration

**Storage**: JSON files in `.ui-ux-pro-max-config/brand/`

**Core Brand Schema** (`brand.json`):
```json
{
  "name": "Brand Name",
  "industry": "technology|healthcare|finance|retail|education|other",
  "style_preferences": {
    "preferred_styles": ["minimalism", "glassmorphism"],
    "avoided_styles": ["brutalism", "claymorphism"],
    "design_philosophy": "clean|bold|playful|professional|innovative"
  },
  "colors": {
    "primary": "#1a73e8",
    "secondary": "#34a853",
    "accent": "#fbbc04",
    "neutral": {
      "dark": "#202124",
      "medium": "#5f6368",
      "light": "#f8f9fa"
    },
    "semantic": {
      "success": "#34a853",
      "warning": "#fbbc04",
      "error": "#ea4335",
      "info": "#1a73e8"
    }
  },
  "typography": {
    "primary_font": {
      "name": "Inter",
      "google_fonts_import": "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');",
      "fallback": "system-ui, -apple-system, sans-serif"
    },
    "secondary_font": {
      "name": "JetBrains Mono",
      "google_fonts_import": "@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');",
      "fallback": "Consolas, Monaco, monospace"
    },
    "scale": "1.2|1.25|1.33|1.414|1.5|1.618",
    "line_height": {
      "tight": 1.2,
      "normal": 1.5,
      "loose": 1.8
    }
  },
  "spacing": {
    "scale": "geometric|linear|custom",
    "base_unit": 8,
    "multipliers": [0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 16]
  },
  "borders": {
    "radius": {
      "none": "0",
      "small": "4px",
      "medium": "8px",
      "large": "16px",
      "full": "9999px"
    },
    "width": {
      "thin": "1px",
      "medium": "2px",
      "thick": "4px"
    }
  }
}
```

### 3. Platform Definition Entity

**Purpose**: Represents development platform specifications and guidelines

**Storage**: CSV files in `data/stacks/` (built-in) and `.ui-ux-pro-max-config/stacks/` (custom)

**CSV Schema**:
```csv
term,description,examples,anti_patterns,code_example,reasoning,category,priority,platform_specific,dependencies
```

**Example Structure** (HTMX + Alpine.js + Axum):
- **term**: Specific pattern or guideline name
- **description**: Detailed explanation of the pattern
- **examples**: Real-world usage examples
- **anti_patterns**: What to avoid
- **code_example**: Working code snippet
- **reasoning**: Why this pattern is recommended
- **category**: Pattern classification (UI, State, Integration, etc.)
- **priority**: Implementation priority (High, Medium, Low)
- **platform_specific**: Unique to this platform combination
- **dependencies**: Required libraries or setup

### 4. AI Interface Component Entity

**Purpose**: Represents specialized UI patterns for AI applications

**Storage**: CSV file `data/ai-chat.csv`

**CSV Schema**:
```csv
term,description,examples,implementation,accessibility,trust_factors,category,use_cases,frameworks,reasoning
```

**Categories**:
- **Thinking Display**: Reasoning visualization patterns
- **Tool Integration**: Function call and API interaction patterns
- **Citation Management**: Source attribution and verification patterns
- **Conversation Flow**: Chat interaction and navigation patterns
- **Trust & Transparency**: Confidence and limitation communication patterns

### 5. Architecture Pattern Entity

**Purpose**: Represents clean architecture approaches and structural patterns

**Storage**: CSV file `data/architecture.csv`

**CSV Schema**:
```csv
term,description,structure,benefits,trade_offs,implementation_guide,examples,testing_approach,category,complexity
```

**Categories**:
- **Feature-Based**: Feature slice organization patterns
- **Hexagonal**: Ports and adapters architecture patterns
- **Domain-Driven**: Domain boundary and aggregate patterns
- **Clean Architecture**: Dependency inversion and layer separation
- **Component Architecture**: UI component organization patterns

## Data Relationships

### Configuration Loading Hierarchy

```text
1. Load built-in data (data/*.csv)
2. Discover external configuration (.ui-ux-pro-max-config/)
3. Validate external configuration files
4. Merge external data with built-in data
5. Apply brand configuration to search results
6. Cache merged configuration for performance
```

### Brand Integration Flow

```text
Search Query → BM25 Search → Results → Brand Filter → Brand Application → Final Results
```

**Brand Application Process**:
1. Check if result involves colors → Apply brand color palette
2. Check if result involves typography → Apply brand font preferences
3. Check if result involves styles → Filter by brand style preferences
4. Apply brand-specific reasoning adjustments
5. Ensure brand consistency across all recommendations

### External Configuration Validation

**Validation Levels**:
1. **File Structure**: Check required directories and files exist
2. **JSON Schema**: Validate JSON files against defined schemas
3. **CSV Format**: Validate CSV column headers and data types
4. **Cross-Reference**: Check references between configuration files
5. **Conflict Detection**: Identify conflicts with built-in data

**Conflict Resolution Strategy**:
```text
1. Log conflict to console with details
2. Use external configuration value for non-critical conflicts
3. Use built-in value for critical system conflicts
4. Merge arrays/lists where applicable
5. Provide override mechanism for critical conflicts
```

## Storage Implementation

### CSV Data Extension

**Existing Structure** (maintained for backward compatibility):
```text
data/
├── styles.csv        # UI styles and design patterns
├── colors.csv        # Color palettes by product type
├── typography.csv    # Font pairings and typography
├── products.csv      # Product type recommendations
├── landing.csv       # Landing page patterns
├── charts.csv        # Chart types and libraries
├── ux.csv           # UX best practices
├── prompts.csv      # AI prompts and keywords
└── stacks/          # Framework-specific guidelines
    ├── html-tailwind.csv
    ├── react.csv
    ├── nextjs.csv
    ├── vue.csv
    ├── svelte.csv
    ├── swiftui.csv
    ├── react-native.csv
    └── flutter.csv
```

**New Additions**:
```text
data/
├── [existing files above]
├── ai-chat.csv           # NEW: AI interface components
├── architecture.csv      # NEW: Clean architecture patterns
└── stacks/
    ├── [existing files above]
    ├── htmx-alpine-axum.csv  # NEW: HTMX platform
    └── tauri.csv             # NEW: Tauri desktop platform
```

### JSON Configuration Storage

**Brand Configuration Files**:
- Primary: `brand.json` (main brand definition)
- Extended: `colors.json`, `typography.json` (detailed specifications)
- Optional: `assets.json` (logos, images, brand assets)

**External Configuration Files**:
- Primary: `config.json` (main configuration)
- Extended: `reasoning.json` (custom reasoning rules)
- Optional: `priorities.json` (search ranking preferences)

## Performance Considerations

### Caching Strategy

```text
1. File System Cache: Cache external configuration parsing
2. Search Cache: Cache BM25 index with external data
3. Brand Cache: Cache brand-applied results for common queries
4. Validation Cache: Cache validation results for unchanged files
```

### Scaling Limits

- **Maximum Entries**: 1000 external configuration entries
- **Warning Threshold**: 800 entries (performance warnings displayed)
- **Cache Size**: Configurable, default 100MB memory limit
- **File Watch**: Monitor external files for changes, invalidate cache

### Memory Management

```text
1. Lazy Loading: Load external configuration only when needed
2. Selective Caching: Cache only frequently accessed data
3. Memory Limits: Configurable memory usage caps
4. Garbage Collection: Periodic cleanup of unused cached data
```

## Data Validation Schema

### CSV Validation Rules

**Required Columns**: Each CSV must have minimum required columns
**Data Types**: Enforce string/numeric types where applicable
**Length Limits**: Reasonable limits on description and example lengths
**Format Validation**: URL validation, color code validation, etc.

### JSON Schema Validation

**Brand Configuration**: Strict schema validation with required fields
**Main Configuration**: Schema validation with optional field handling
**Reasoning Rules**: Custom validation for reasoning logic consistency

### Error Handling Strategy

```text
1. Validation Errors: Log detailed error messages, continue with valid data
2. Format Errors: Skip invalid entries, warn user, continue processing
3. Conflict Errors: Log conflicts, apply resolution strategy, continue
4. System Errors: Graceful degradation to built-in data only
```

This data model provides the foundation for implementing all Advanced Customization Architecture requirements while maintaining performance and reliability standards.