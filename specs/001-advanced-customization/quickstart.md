# Quickstart Guide: Advanced Customization Architecture

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Data Model**: [data-model.md](data-model.md)
**Date**: 2026-01-16

## Overview

This guide helps developers quickly set up and use the Advanced Customization Architecture for the UI/UX Pro Max skill. Follow these steps to enable external configuration, brand integration, and new platform support.

## Prerequisites

- Python 3.7+ (existing UI/UX Pro Max skill requirement)
- Write access to your project directory
- Basic understanding of CSV and JSON file formats

## Quick Setup (5 minutes)

### 1. Create External Configuration Directory

```bash
# In your project root directory
mkdir -p .ui-ux-pro-max-config/{domains,stacks,reasoning,brand,extensions}
```

### 2. Initialize Main Configuration

Create `.ui-ux-pro-max-config/config.json`:

```json
{
  "version": "1.0.0",
  "enabled": true,
  "domains": {
    "enabled": [],
    "disabled": []
  },
  "stacks": {
    "enabled": [],
    "disabled": []
  },
  "brand": {
    "enabled": false,
    "file": "brand/brand.json"
  },
  "reasoning": {
    "enabled": false,
    "files": []
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

### 3. Test Basic Setup

```bash
# Run search with external configuration enabled
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "button design" --domain style

# You should see: "External configuration loaded: 0 custom domains, 0 custom stacks"
```

## Feature Walkthroughs

### Brand Configuration Setup (10 minutes)

#### 1. Create Brand Configuration

Create `.ui-ux-pro-max-config/brand/brand.json`:

```json
{
  "name": "Your Brand Name",
  "industry": "technology",
  "style_preferences": {
    "preferred_styles": ["minimalism", "glassmorphism"],
    "avoided_styles": ["brutalism"],
    "design_philosophy": "clean"
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
    "scale": "1.25",
    "line_height": {
      "tight": 1.2,
      "normal": 1.5,
      "loose": 1.8
    }
  }
}
```

#### 2. Enable Brand Configuration

Update `.ui-ux-pro-max-config/config.json`:

```json
{
  "brand": {
    "enabled": true,
    "file": "brand/brand.json"
  }
}
```

#### 3. Test Brand Integration

```bash
# Search for color recommendations
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "color palette" --domain color

# Results should now include your brand colors
```

### Custom Domain Setup (15 minutes)

#### 1. Create Custom Domain CSV

Create `.ui-ux-pro-max-config/domains/industry-specific.csv`:

```csv
term,description,examples,code_example,reasoning,category,priority,color_context,typography_context
fintech-dashboard,Financial technology dashboard with data visualization,Trading platforms like Robinhood,<div class="dashboard-grid"><div class="metric-card">Revenue: $1.2M</div></div>,Financial users need quick data comprehension,dashboard,high,success: green for gains; error: red for losses,tabular-nums for precise number alignment
healthcare-form,HIPAA-compliant form design with clear validation,Patient intake forms,<form class="secure-form"><fieldset class="patient-info">Name: <input required></fieldset></form>,Medical forms require absolute clarity and compliance,form,high,neutral colors for trust; info blue for help text,high contrast fonts for accessibility
```

#### 2. Enable Custom Domain

Update `.ui-ux-pro-max-config/config.json`:

```json
{
  "domains": {
    "enabled": ["industry-specific"],
    "disabled": []
  }
}
```

#### 3. Test Custom Domain

```bash
# Search for your custom domain terms
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech dashboard" --domain product

# Should return your custom fintech dashboard recommendations
```

### New Platform Support (10 minutes)

#### 1. Test HTMX + Alpine.js + Axum Platform

```bash
# Search for HTMX-specific patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "progressive enhancement" --stack htmx-alpine-axum

# Should return HTMX-specific guidelines and patterns
```

#### 2. Test Tauri Desktop Platform

```bash
# Search for desktop-specific patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "native window controls" --stack tauri

# Should return Tauri desktop application patterns
```

### AI Chat Interface Components (10 minutes)

#### 1. Test AI Interface Components

```bash
# Search for AI-specific UI patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "thinking display" --domain ai-chat

# Should return AI chat interface patterns and components
```

#### 2. Search for Tool Integration Patterns

```bash
# Search for AI tool visualization
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "tool call visualization" --domain ai-chat

# Should return patterns for displaying AI function calls
```

## Common Usage Patterns

### 1. Brand-Aware Design System Generation

```bash
# Generate a complete design system with brand integration
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "design system" --domain style --n 10

# With brand enabled, results will use your brand colors and fonts
```

### 2. Platform-Specific Development

```bash
# Get HTMX-specific form handling patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "form validation" --stack htmx-alpine-axum

# Get Tauri-specific file handling patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "file operations" --stack tauri
```

### 3. AI Application UI Development

```bash
# Get comprehensive AI interface patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "chat interface" --domain ai-chat --n 15

# Get specific AI transparency patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "confidence indicators" --domain ai-chat
```

### 4. Clean Architecture Integration

```bash
# Get feature-based architecture guidance
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "feature slice" --domain architecture

# Get hexagonal architecture patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "ports and adapters" --domain architecture
```

## Advanced Configuration

### Custom Reasoning Rules

Create `.ui-ux-pro-max-config/reasoning/reasoning.json`:

```json
{
  "search_preferences": {
    "accessibility_weight": 1.5,
    "performance_weight": 1.3,
    "brand_consistency_weight": 2.0
  },
  "style_priorities": {
    "mobile_first": true,
    "semantic_html": true,
    "progressive_enhancement": true
  },
  "industry_adjustments": {
    "healthcare": {
      "accessibility_weight": 3.0,
      "trust_indicators": true
    },
    "finance": {
      "security_weight": 2.5,
      "data_accuracy": true
    }
  }
}
```

### A2UI Export Setup

```bash
# Export search results to A2UI format
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "button component" --domain style --export-a2ui --platforms react,flutter

# Generates ui-specification.json with cross-platform component definitions
```

### Performance Optimization

For large external configurations:

```json
{
  "performance": {
    "max_entries": 500,          // Reduce for faster searches
    "cache_enabled": true,       // Enable caching
    "warning_threshold": 400,    // Earlier warnings
    "lazy_loading": true         // Load external config only when needed
  }
}
```

## Troubleshooting

### Common Issues

**1. "External configuration not loaded"**
- Check `.ui-ux-pro-max-config/` directory exists
- Verify `config.json` has valid JSON syntax
- Ensure file permissions allow reading

**2. "Brand configuration invalid"**
- Check `brand.json` has required `colors` and `typography` sections
- Verify color codes are in hex format (#RRGGBB)
- Ensure Google Fonts imports are valid URLs

**3. "Custom domain not found"**
- Verify CSV file has required columns: `term,description,examples,code_example,reasoning`
- Check domain is listed in `config.json` enabled array
- Ensure CSV file uses proper encoding (UTF-8)

**4. "Performance warnings"**
- Reduce `max_entries` in config if you have large custom datasets
- Enable caching for frequently used configurations
- Consider splitting large CSV files into smaller, focused domains

### Debug Commands

```bash
# Check configuration status
python3 .claude/skills/ui-ux-pro-max/scripts/search.py --config-status

# Validate external configuration
python3 .claude/skills/ui-ux-pro-max/scripts/search.py --validate-config

# Test configuration loading
python3 .claude/skills/ui-ux-pro-max/scripts/search.py --test-config
```

### Log Analysis

Enable detailed logging in `config.json`:

```json
{
  "logging": {
    "level": "DEBUG",
    "conflicts": true,
    "validation": true,
    "performance": true,
    "file_operations": true
  }
}
```

## Next Steps

### 1. Explore Advanced Features
- Set up hyperpersonalization tracking for usage-based recommendations
- Configure MCP server extensions for team collaboration
- Implement automated brand compliance checking

### 2. Integration with Development Workflow
- Add external configuration to your version control system
- Set up automated validation in CI/CD pipelines
- Create team-shared brand configurations

### 3. Custom Extension Development
- Create custom domains for your specific industry or use case
- Develop custom reasoning rules for your team's preferences
- Build MCP server extensions for advanced functionality

## Getting Help

- Check the [specification](spec.md) for detailed feature descriptions
- Review [contracts](contracts/) for API documentation
- Examine the [data model](data-model.md) for structure details
- Use debug commands to troubleshoot configuration issues

The Advanced Customization Architecture provides powerful extension capabilities while maintaining the simplicity and performance of the original UI/UX Pro Max skill.