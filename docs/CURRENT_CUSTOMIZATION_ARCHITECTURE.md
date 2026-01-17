# UI/UX Pro Max Skill - Comprehensive Customization Architecture

**Version:** 2.0.0
**Generated:** 2026-01-16
**Focus:** S-Tier UI/UX Design Excellence with Advanced Customization

## Executive Summary

The UI/UX Pro Max skill represents a sophisticated design intelligence system with a modular, data-driven architecture that supports extensive customization for s-tier user interface development. This document provides a comprehensive analysis of all customization mechanisms and implementation strategies for advanced requirements including modern web stacks, desktop applications, clean architecture patterns, AI chat interfaces, personal branding integration, and existing codebase refactoring.

## S-Tier UI/UX Design Principles Integration

Based on current industry research and best practices, the skill incorporates these s-tier design principles:

### Core Excellence Attributes

1. **Advanced Micro-Interactions**
   - Emotion-based animations responding to user actions
   - Context-aware hints appearing only when needed
   - AI-driven interaction patterns for 2024-2025

2. **Visual Hierarchy & Information Architecture**
   - Dynamic visual hierarchy with expressive typography
   - Clean interfaces with purposeful spacing
   - Contextual personalization for user-specific experiences

3. **Performance-First Design**
   - Optimized animation timing (150-300ms for micro-interactions)
   - Progressive loading with skeleton screens
   - Accessibility-first approach with WCAG AAA compliance

4. **Predictable Yet Delightful Interfaces**
   - Consistent interaction patterns that reduce cognitive load
   - Strategic friction where needed for user awareness
   - Natural language conversational interfaces for AI applications

## Current Architecture Analysis

### 1. Core System Components

#### Search Engine (`core.py`)
- **BM25 Algorithm**: Advanced text ranking for relevance-based searches
- **Domain Auto-Detection**: Intelligent categorization based on query keywords
- **Modular CSV Configuration**: Extensible data structure for new domains

```python
CSV_CONFIG = {
    "style": {"file": "styles.csv", "search_cols": [...], "output_cols": [...]},
    "color": {"file": "colors.csv", "search_cols": [...], "output_cols": [...]},
    # Extensible for new domains
}
```

#### Design System Generator (`design_system.py`)
- **Multi-Domain Search**: Parallel searches across 5 domains (product, style, color, landing, typography)
- **Reasoning Engine**: 100+ rules from `ui-reasoning.csv` for intelligent recommendations
- **Priority-Based Selection**: Weighted matching based on product category and style preferences

#### Stack-Specific Guidelines (`data/stacks/`)
- **12 Supported Platforms**: React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, etc.
- **Consistent Structure**: All stacks follow same CSV schema with 9 columns
- **Extensible Framework**: Easy addition of new platforms through CSV files

### 2. Data Architecture

#### Domain Databases
- `styles.csv`: 50+ UI styles (glassmorphism, minimalism, brutalism, etc.)
- `colors.csv`: 97 color palettes organized by product type
- `typography.csv`: 57 font pairings with Google Fonts integration
- `ux-guidelines.csv`: 99+ UX best practices with severity levels
- `ui-reasoning.csv`: 100+ intelligent decision rules

#### Stack Guidelines
- Platform-specific best practices (40-50+ rules per stack)
- Code examples (good vs. bad patterns)
- Documentation links and severity ratings
- Consistent taxonomy across all platforms

## Customization Mechanisms - Comprehensive Analysis

### 1. Platform Addition (HTMX + Alpine.js + Axum Support)

**Current State**: Not directly supported
**Implementation Requirements**:

#### A. Add New Stack Configuration

```python
# In core.py STACK_CONFIG
"htmx-alpine": {"file": "stacks/htmx-alpine.csv"},
"axum-server": {"file": "stacks/axum-server.csv"},
```

#### B. Create Stack-Specific CSV Files

**Location**: `.claude/skills/ui-ux-pro-max/data/stacks/htmx-alpine.csv`

**Required Columns**:
- No, Category, Guideline, Description, Do, Don't, Code Good, Code Bad, Severity, Docs URL

**Key Categories for HTMX + Alpine.js + Axum**:

```csv
1,State Management,Use Alpine.js for client state,Alpine.js handles local component state efficiently,x-data for component scope,Global JavaScript variables,<div x-data="{ open: false }">...</div>,var isOpen = false;,High,https://alpinejs.dev/essentials/state
2,Server Communication,Use HTMX for server interactions,HTMX provides seamless server communication,hx-post hx-get for requests,Fetch API for simple updates,<button hx-post="/toggle">Toggle</button>,fetch('/toggle').then(...),High,https://htmx.org/docs/
3,Rust Integration,Implement proper Axum handlers,Structure handlers for HTMX responses,Response with proper headers,Plain JSON responses,Ok(Html("<div>Updated</div>")),Ok(Json(data)),Medium,https://docs.rs/axum/
4,Progressive Enhancement,Design for no-JS functionality,Ensure forms work without JavaScript,Plain HTML forms as base,JavaScript-only interactions,<form action="/submit" method="post">,<div onclick="jsOnly()">Submit</div>,High,
```

#### C. Domain Detection Enhancement

```python
# In core.py detect_domain() function
domain_keywords = {
    # ... existing domains
    "htmx": ["htmx", "hx-get", "hx-post", "hx-trigger", "server-sent", "hypermedia"],
    "alpine": ["alpine", "x-data", "x-show", "x-bind", "reactive", "component"],
    "axum": ["axum", "rust", "handler", "router", "extractor", "middleware"]
}
```

### 2. Tauri Application Support

**Implementation Strategy**:

#### A. Create Tauri-Specific Guidelines

**Location**: `.claude/skills/ui-ux-pro-max/data/stacks/tauri.csv`

**Key Focus Areas**:
```csv
1,Window Management,Use proper window controls,Native window controls for desktop experience,tauri::window::WindowBuilder,Custom web-based controls,WindowBuilder::new("main").build(),<div class="custom-titlebar">,High,
2,Desktop Integration,Implement system tray,Provide system tray for background operation,tauri::SystemTray with menu,Always visible window,SystemTray::new().with_menu(menu),No system integration,Medium,
3,File System Access,Use secure file operations,Tauri's secure file system API,tauri::api::file for file ops,Direct fs access in frontend,api.file.readTextFile(path),fs.readFile in renderer,High,
4,Performance,Optimize bundle size,Keep Rust backend minimal for size,Core logic in Rust lightweight frontend,Heavy frontend framework,#[tauri::command] fn compute(),Heavy computation in JS,High,
```

#### B. Tauri-Specific Design Patterns

**New Domain**: Create `tauri-patterns.csv` for desktop-specific UI patterns:
- Native menu integration patterns
- Cross-platform design considerations
- System integration patterns
- File handling UI patterns

### 3. State Management Customization (Zustand, Riverpod, etc.)

**Current State**: Basic useState/useReducer recommendations
**Enhancement Strategy**:

#### A. Enhanced React Stack Guidelines

**Modify**: `.claude/skills/ui-ux-pro-max/data/stacks/react.csv`

**Add Advanced State Management Patterns**:
```csv
55,State,Use Zustand for global state,Lightweight global state without providers,create((set) => ({ ... })),Context + useReducer for simple global state,const useStore = create((set) => ({count: 0})),const [state] = useContext(GlobalContext),High,https://zustand.docs.pmnd.rs/
56,State,Use Valtio for proxy-based state,Reactive proxy state for complex objects,proxy() for mutable-style state,Manual immutable updates,const state = proxy({ user: { name: '' } }),const [user setUser] = useState({ name: '' }),Medium,https://valtio.pmnd.rs/
57,State,Use Jotai for atomic state,Bottom-up atomic state management,atom() for independent state pieces,Top-down global state for everything,const countAtom = atom(0),const GlobalState = { count: 0 },Medium,https://jotai.org/
```

#### B. Flutter Riverpod Integration

**Create**: `.claude/skills/ui-ux-pro-max/data/stacks/flutter-riverpod.csv`

```csv
1,State Management,Use Riverpod providers,Type-safe dependency injection with Riverpod,Provider for state management,setState for global state,final counterProvider = StateProvider((ref) => 0),setState(() => globalCounter++),High,https://riverpod.dev/
2,Architecture,Implement repository pattern,Separate data layer with repositories,Repository pattern with Riverpod,Direct API calls in widgets,ref.read(userRepositoryProvider),http.get() in StatefulWidget,High,
```

### 4. Feature-Based Clean Architecture Integration

**Implementation Approach**:

#### A. New Architecture Domain

**Create**: `.claude/skills/ui-ux-pro-max/data/architecture.csv`

**Update**: `core.py` CSV_CONFIG:
```python
"architecture": {
    "file": "architecture.csv",
    "search_cols": ["Pattern Name", "Keywords", "Best For", "Benefits"],
    "output_cols": ["Pattern Name", "Description", "Structure", "Benefits", "Drawbacks", "Code Example", "Best For"]
}
```

**Sample Architecture Patterns**:
```csv
1,Feature-Based Architecture,Organize by business domain not technical concerns,src/features/{auth users orders},Feature folders with domain logic,Better maintainability and team coordination,Technical debt in shared utilities,src/features/auth/{components hooks services},src/components/auth/ src/hooks/useAuth.ts,High
2,Hexagonal Architecture,Isolate business logic from external concerns,Domain-driven with ports/adapters,Framework-independent core logic,Testable business logic,Additional complexity,domain/ infrastructure/ presentation/,components/api/services/ mixed together,High
3,Clean Architecture Layers,Concentric dependency layers,Entities Use-Cases Interface-Adapters Frameworks,Stable business rules,Independent of frameworks,Learning curve and ceremony,entities/ use-cases/ controllers/ frameworks/,Flat structure with mixed concerns,Medium
```

#### B. Stack-Specific Architecture Guidelines

**Enhance each stack CSV** with architecture sections:

**React + Clean Architecture**:
```csv
60,Architecture,Implement feature slices,Feature-Sliced Design methodology,features/ shared/ pages/ app/,Technical layer separation,src/features/auth/ui/LoginForm.tsx,src/components/LoginForm.tsx,High,https://feature-sliced.design/
61,Architecture,Use dependency injection,Inject services through React context,DI container with providers,Direct service instantiation,<ServiceProvider value={services}>,const api = new ApiService(),Medium,
```

### 5. AI Chat UI Support (A2UI, AG-UI)

**Implementation Strategy**:

#### A. New AI Chat Domain

**Create**: `.claude/skills/ui-ux-pro-max/data/ai-chat.csv`

```python
# Add to CSV_CONFIG in core.py
"ai-chat": {
    "file": "ai-chat.csv",
    "search_cols": ["Component Type", "Keywords", "Use Case", "Best For"],
    "output_cols": ["Component Type", "Description", "Design Pattern", "Interaction Model", "Code Example", "Accessibility Notes", "Performance Notes"]
}
```

**Sample AI Chat Components**:
```csv
1,Thinking Display,Show AI reasoning process,Expandable thinking bubble,Real-time thought streaming,Enhanced transparency and trust,Potential information overload,<ThinkingBubble stream={thinkingData} expandable />,Static loading spinner,High
2,Tool Call Visualization,Display function executions,Progressive disclosure pattern,Tool execution with loading states,User understands AI actions,Screen space usage,<ToolCallCard name="search" status="executing" />,Generic "Processing..." text,High
3,Citation Display,Show source attributions,Inline citation with popover,Hover/click for source details,Information credibility,Link management complexity,<Citation source={source} inline />,Unmarked AI responses,High
4,Reasoning Breakdown,Explain step-by-step logic,Accordion/tree structure,Expandable reasoning steps,Educational transparency,Cognitive overhead,<ReasoningSteps steps={analysis} />,Black box responses,Medium
```

#### B. Chat Interface Patterns

**Enhance existing domains** with AI-specific patterns:

**UX Guidelines for AI Chat**:
```csv
100,AI Chat,Provide thinking indicators,Show AI processing states clearly,Typing indicators + thinking displays,Silent processing periods,<TypingIndicator type="thinking" />,No processing feedback,High
101,AI Chat,Enable conversation branching,Allow users to explore alternatives,Branch points in conversation,Linear chat only,<ConversationBranch alternatives={options} />,Single conversation thread,Medium
102,AI Chat,Show confidence levels,Display AI uncertainty appropriately,Confidence indicators on responses,Present all responses as certain,"Response confidence: 85%",All responses appear definitive,High
```

### 6. Personal Branding Guide Integration

**Implementation Strategy**:

#### A. Brand Configuration System

**Create**: `.claude/skills/ui-ux-pro-max/data/brand-config.json`

```json
{
  "personal_brand": {
    "colors": {
      "primary": "#your-brand-color",
      "secondary": "#your-secondary",
      "accent": "#your-accent"
    },
    "typography": {
      "heading_font": "Your Brand Font",
      "body_font": "Your Body Font",
      "font_personality": "modern|classic|playful|serious"
    },
    "style_preferences": {
      "primary_style": "Minimalism",
      "avoid_styles": ["Brutalism", "Claymorphism"],
      "preferred_effects": ["subtle-hover", "smooth-transitions"]
    },
    "brand_personality": ["professional", "innovative", "trustworthy"],
    "industry_context": "fintech|healthcare|education|creative"
  }
}
```

#### B. Brand-Aware Design System Generation

**Modify**: `design_system.py` to incorporate personal branding:

```python
def _apply_brand_preferences(self, design_system: dict, brand_config: dict) -> dict:
    """Override design system with personal brand preferences."""
    if not brand_config:
        return design_system

    # Override colors with brand colors
    if brand_config.get("colors"):
        design_system["colors"].update(brand_config["colors"])

    # Override typography with brand fonts
    if brand_config.get("typography"):
        brand_typo = brand_config["typography"]
        design_system["typography"]["heading"] = brand_typo.get("heading_font", design_system["typography"]["heading"])
        design_system["typography"]["body"] = brand_typo.get("body_font", design_system["typography"]["body"])

    # Filter style recommendations based on preferences
    preferred_style = brand_config.get("style_preferences", {}).get("primary_style")
    if preferred_style:
        design_system["style"]["name"] = preferred_style

    return design_system
```

#### C. Mood Board Integration

**Create**: `.claude/skills/ui-ux-pro-max/scripts/mood_board_analyzer.py`

```python
def analyze_mood_board(image_path: str) -> dict:
    """Analyze uploaded mood board for design preferences."""
    # This would integrate with image analysis APIs
    return {
        "dominant_colors": ["#2D3748", "#4299E1", "#F7FAFC"],
        "style_indicators": ["minimalism", "modern", "clean"],
        "typography_mood": ["sans-serif", "geometric", "clean"],
        "spacing_style": "generous",
        "visual_weight": "light"
    }
```

### 7. Existing Codebase Refactoring Support

**Implementation Strategy**:

#### A. Codebase Analysis Tools

**Create**: `.claude/skills/ui-ux-pro-max/scripts/codebase_analyzer.py`

```python
class CodebaseAnalyzer:
    """Analyze existing codebase for UI/UX improvement opportunities."""

    def analyze_project(self, project_path: str) -> dict:
        """Scan project for UI/UX issues and improvement opportunities."""
        return {
            "framework_detected": "react|vue|angular",
            "ui_libraries": ["tailwind", "chakra-ui", "material-ui"],
            "accessibility_issues": [...],
            "performance_issues": [...],
            "style_inconsistencies": [...],
            "refactor_opportunities": [...]
        }

    def generate_refactor_plan(self, analysis: dict) -> dict:
        """Generate step-by-step refactoring recommendations."""
        return {
            "priority": "high|medium|low",
            "steps": [...],
            "estimated_impact": "significant|moderate|minor",
            "breaking_changes": [...]
        }
```

#### B. Incremental Refactoring Patterns

**Add to UX Guidelines**:
```csv
103,Refactoring,Implement design tokens first,Establish consistent design system foundation,CSS custom properties or design tokens,Hard-coded values throughout,--color-primary: #2563EB; var(--color-primary),color: #2563EB scattered everywhere,High
104,Refactoring,Audit accessibility incrementally,Fix accessibility issues by priority,Focus on WCAG A then AA then AAA,Attempt to fix everything at once,Fix color contrast issues first,Try to address all a11y issues simultaneously,High
105,Refactoring,Modernize interaction patterns,Update to current UI/UX best practices,Replace outdated patterns progressively,Complete UI rewrite,Replace hover-only tooltips with click,Redesign entire interface,Medium
```

## Advanced Customization Implementation Guide

### 1. Adding New Platforms - Step-by-Step

#### Enhanced HTMX + Alpine.js + Axum Support with Web Components

**Research Findings**: HTMX 2.0 has excellent Web Components integration, enabling self-initializing components that work seamlessly with AJAX updates.

1. **Update Core Configuration**:
   ```python
   # In core.py
   STACK_CONFIG["htmx-alpine-wc"] = {"file": "stacks/htmx-alpine-wc.csv"}
   STACK_CONFIG["axum-server"] = {"file": "stacks/axum-server.csv"}
   AVAILABLE_STACKS = list(STACK_CONFIG.keys())  # Auto-updates
   ```

2. **Create Enhanced HTMX Platform CSV**:
   ```bash
   # Create comprehensive HTMX + Web Components stack
   cp .claude/skills/ui-ux-pro-max/data/stacks/react.csv .claude/skills/ui-ux-pro-max/data/stacks/htmx-alpine-wc.csv
   ```

3. **Web Components Integration Guidelines**:
   ```csv
   1,Web Components,Use self-initializing custom elements,Web Components auto-initialize when HTMX injects them,Custom elements with connectedCallback,Manual initialization after HTMX swap,<my-component data="..." hx-trigger="load"></my-component>,Manual DOM manipulation post-swap,High,https://htmx.org/examples/web-components/
   2,Shadow DOM,Implement HTMX inside shadow DOM,HTMX works within Web Component shadow boundaries,hx-* attributes inside shadow DOM,Global HTMX attributes outside components,class MyComponent extends HTMLElement {connectedCallback() {this.innerHTML = '<div hx-get="/data"></div>'}},<div hx-get="/data"><my-component></my-component></div>,High,
   3,Custom Events,Use Web Component custom events,Components communicate via custom events,this.dispatchEvent(new CustomEvent('data-updated')),Direct DOM manipulation between components,element.addEventListener('data-updated' handler),element.querySelector('other-component').update(),Medium,
   4,Progressive Enhancement,Design components for no-JS,Ensure Web Components work without JavaScript,HTML with is="" attribute fallback,JavaScript-only components,<button is="enhanced-button">Click</button>,<enhanced-button>Click</enhanced-button>,High,
   ```

4. **Update Domain Detection**:
   ```python
   # Enhanced detection for modern HTMX patterns
   domain_keywords = {
       # ... existing domains
       "htmx": ["htmx", "hx-get", "hx-post", "hx-trigger", "server-sent", "hypermedia", "web-component", "custom-element"],
       "alpine": ["alpine", "x-data", "x-show", "x-bind", "reactive", "component"],
       "axum": ["axum", "rust", "handler", "router", "extractor", "middleware", "askama", "templates"],
       "web-components": ["custom-element", "shadow-dom", "connectedCallback", "lit-element", "stencil"]
   }
   ```

5. **Sync Changes** (per CLAUDE.md):
   ```bash
   # Copy to all agent workflows
   cp -r .claude/skills/ui-ux-pro-max/ .shared/ui-ux-pro-max/
   cp -r .claude/ .agent/workflows/ui-ux-pro-max/
   # etc.
   ```

### 2. Custom Domain Creation

1. **Define Domain Structure**:
   ```python
   # In CSV_CONFIG
   "your-domain": {
       "file": "your-domain.csv",
       "search_cols": ["Column1", "Column2", "Keywords"],
       "output_cols": ["All", "Relevant", "Output", "Columns"]
   }
   ```

2. **Create Data File**:
   ```csv
   No,Column1,Column2,Keywords,Description,Example,Notes
   1,Value1,Value2,keyword1 keyword2,Description text,Code example,Additional notes
   ```

3. **Update Search Keywords**:
   ```python
   # Add to domain_keywords in detect_domain()
   "your-domain": ["domain", "specific", "keywords"]
   ```

### 3. Reasoning Rules Enhancement

**Modify**: `.claude/skills/ui-ux-pro-max/data/ui-reasoning.csv`

**Add Custom Decision Logic**:
```csv
21,Your Custom Category,Custom Pattern,Style Priority,Color Mood,Typography Mood,Key Effects,"{""if_condition"": ""action"", ""must_have"": ""requirement""}",Anti-Pattern List,HIGH
```

**Decision Rules JSON Schema**:
```json
{
  "if_condition": "action_to_take",
  "must_have": "required_element",
  "if_user_preference": "override_default",
  "priority_boost": "element_to_prioritize"
}
```

## Non-Intrusive Extensibility Architecture

**Core Philosophy**: Enable advanced customization without modifying the skill's source code through external configuration and tool-based extension patterns.

### 1. External Configuration-Based Customization

#### A. Configuration Directory Structure
```
.ui-ux-pro-max-config/
├── domains/                    # Custom domains (no core modification)
│   ├── custom-domain.csv
│   └── ai-frameworks.csv
├── stacks/                     # Custom stacks (no core modification)
│   ├── htmx-alpine-custom.csv
│   └── tauri-custom.csv
├── reasoning/                  # Custom reasoning rules
│   ├── brand-specific-rules.csv
│   └── industry-patterns.csv
├── extensions/                 # MCP servers and tool extensions
│   ├── brand-analyzer/
│   └── codebase-scanner/
├── brand/                      # Personal branding configurations
│   ├── brand-config.json
│   └── mood-boards/
└── config.json               # Main configuration file
```

#### B. Configuration Loading System
**Create**: `.claude/skills/ui-ux-pro-max/scripts/config_loader.py`

```python
class ExternalConfigLoader:
    """Load external configurations without modifying core system."""

    def __init__(self, config_dir: str = ".ui-ux-pro-max-config"):
        self.config_dir = Path(config_dir)
        self.loaded_domains = {}
        self.loaded_stacks = {}
        self.loaded_reasoning = {}

    def load_external_domains(self) -> dict:
        """Load custom domains from external directory."""
        domains_dir = self.config_dir / "domains"
        if not domains_dir.exists():
            return {}

        external_domains = {}
        for csv_file in domains_dir.glob("*.csv"):
            domain_name = csv_file.stem
            external_domains[domain_name] = {
                "file": str(csv_file),
                "search_cols": self._detect_search_columns(csv_file),
                "output_cols": self._detect_output_columns(csv_file)
            }
        return external_domains

    def load_external_stacks(self) -> dict:
        """Load custom stacks from external directory."""
        stacks_dir = self.config_dir / "stacks"
        if not stacks_dir.exists():
            return {}

        external_stacks = {}
        for csv_file in stacks_dir.glob("*.csv"):
            stack_name = csv_file.stem
            external_stacks[stack_name] = {"file": str(csv_file)}
        return external_stacks

    def merge_configurations(self, core_config: dict) -> dict:
        """Merge external configurations with core system."""
        merged = core_config.copy()

        # Add external domains
        external_domains = self.load_external_domains()
        merged.update(external_domains)

        # Add external stacks
        external_stacks = self.load_external_stacks()
        merged.update(external_stacks)

        return merged
```

### 2. MCP Server-Based Tool Extensions

**Research Findings**: Tool calling combined with skills enables hyperpersonalization and dynamic agent-based UI generation through real-time data analysis and context adaptation.

#### A. Brand Analysis MCP Server
**Create**: `.ui-ux-pro-max-config/extensions/brand-analyzer/server.py`

```python
from mcp import create_server
from mcp.types import Tool, TextContent

app = create_server("brand-analyzer")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="analyze_brand_preferences",
            description="Analyze user's brand preferences from mood board or style guide",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to mood board image"},
                    "brand_keywords": {"type": "array", "items": {"type": "string"}},
                    "industry": {"type": "string"}
                }
            }
        ),
        Tool(
            name="generate_brand_config",
            description="Generate brand configuration from analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_data": {"type": "object"},
                    "output_format": {"type": "string", "enum": ["json", "csv", "yaml"]}
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_brand_preferences":
        # Analyze mood board, extract colors, typography, style preferences
        analysis = analyze_visual_preferences(arguments["image_path"])
        return [TextContent(type="text", text=json.dumps(analysis))]

    elif name == "generate_brand_config":
        # Generate configuration files from analysis
        config = generate_brand_configuration(arguments["analysis_data"])
        return [TextContent(type="text", text=json.dumps(config))]
```

#### B. Hyperpersonalization MCP Server
**Create**: `.ui-ux-pro-max-config/extensions/hyperpersonalization/server.py`

```python
@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="analyze_user_context",
            description="Analyze user context for hyperpersonalized UI recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_behavior": {"type": "object"},
                    "current_session": {"type": "object"},
                    "project_context": {"type": "object"}
                }
            }
        ),
        Tool(
            name="generate_personalized_ui",
            description="Generate personalized UI recommendations using A2UI format",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_analysis": {"type": "object"},
                    "ui_context": {"type": "string"},
                    "target_platform": {"type": "string"}
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_user_context":
        # Real-time user behavior analysis
        analysis = {
            "preferences": extract_user_preferences(arguments["user_behavior"]),
            "context": analyze_current_context(arguments["current_session"]),
            "patterns": identify_usage_patterns(arguments["project_context"])
        }
        return [TextContent(type="text", text=json.dumps(analysis))]

    elif name == "generate_personalized_ui":
        # Generate A2UI specifications for personalized interfaces
        a2ui_spec = generate_a2ui_interface(
            arguments["user_analysis"],
            arguments["ui_context"],
            arguments["target_platform"]
        )
        return [TextContent(type="text", text=json.dumps(a2ui_spec))]
```

### 3. AI-Centric UI Framework Integration

Based on research findings, three major protocols have emerged for agent-driven interfaces:

#### A. A2UI (Agent-to-UI) Integration
**Purpose**: JSON-based declarative UI protocol for multi-platform rendering

**Create**: `.ui-ux-pro-max-config/extensions/a2ui-generator/server.py`

```python
class A2UIGenerator:
    """Generate A2UI specifications from UI/UX Pro Max recommendations."""

    def generate_a2ui_from_design_system(self, design_system: dict, platform: str) -> dict:
        """Convert design system to A2UI JSON specification."""

        # A2UI message structure for multi-platform rendering
        a2ui_messages = [
            {
                "surfaceUpdate": {
                    "components": [
                        {
                            "id": "root",
                            "component": {
                                "Column": {
                                    "children": {"explicitList": ["header", "content", "footer"]},
                                    "alignment": "start",
                                    "distribution": "spaceBetween"
                                }
                            }
                        },
                        {
                            "id": "header",
                            "component": {
                                "Card": {
                                    "child": "header_content",
                                    "style": self._convert_to_platform_style(
                                        design_system["style"], platform
                                    )
                                }
                            }
                        }
                    ]
                }
            },
            {
                "dataModelUpdate": {
                    "contents": {
                        "theme": design_system["colors"],
                        "typography": design_system["typography"],
                        "branding": design_system.get("brand_config", {})
                    }
                }
            },
            {"beginRendering": {"root": "root"}}
        ]

        return a2ui_messages
```

#### B. AG-UI (Agent-User Interaction) Integration
**Purpose**: Event-based protocol for real-time agent-user interaction

```python
class AGUIIntegration:
    """Integrate with AG-UI protocol for real-time design system updates."""

    def stream_design_updates(self, design_process: dict) -> Generator[dict, None, None]:
        """Stream design system generation process via AG-UI events."""

        # AG-UI event types for design system generation
        yield {
            "type": "AGENT_STATUS",
            "status": "thinking",
            "message": "Analyzing your design requirements..."
        }

        yield {
            "type": "TOOL_CALL",
            "tool": "ui_ux_pro_max_search",
            "args": {"query": design_process["query"], "domain": "product"}
        }

        yield {
            "type": "GENERATIVE_UI",
            "ui_spec": {
                "type": "A2UI",
                "payload": self._generate_preview_interface(design_process)
            }
        }

        yield {
            "type": "CONTEXT_UPDATE",
            "context": {
                "design_system": design_process["final_system"],
                "reasoning": design_process["applied_rules"]
            }
        }
```

#### C. MCP-UI Integration
**Purpose**: Rich interactive components for Model Context Protocol

```python
class MCPUIIntegration:
    """Generate MCP-UI components for interactive design system exploration."""

    def create_design_system_explorer(self, design_system: dict) -> str:
        """Create interactive MCP-UI component for design system exploration."""

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Design System Explorer</title>
            <style>
                :root {{
                    --primary: {design_system["colors"]["primary"]};
                    --secondary: {design_system["colors"]["secondary"]};
                    --font-heading: {design_system["typography"]["heading"]};
                    --font-body: {design_system["typography"]["body"]};
                }}
            </style>
        </head>
        <body>
            <div id="design-explorer">
                <h1 style="font-family: var(--font-heading)">
                    {design_system.get("project_name", "Design System")}
                </h1>
                <div class="color-palette">
                    <!-- Interactive color palette with copy-to-clipboard -->
                </div>
                <div class="typography-showcase">
                    <!-- Live typography preview -->
                </div>
                <div class="component-preview">
                    <!-- Interactive component examples -->
                </div>
            </div>
            <script>
                // Interactive functionality for MCP communication
                function updateDesignSystem(changes) {{
                    // Communicate back to MCP server
                    window.parent.postMessage({{
                        type: 'mcp-ui-update',
                        data: changes
                    }}, '*');
                }}
            </script>
        </body>
        </html>
        """
        return html_template
```

### 4. Dynamic Extension Loading

**Create**: `.claude/skills/ui-ux-pro-max/scripts/extension_manager.py`

```python
class ExtensionManager:
    """Manage external extensions and MCP servers without core modification."""

    def discover_extensions(self, config_dir: str) -> dict:
        """Discover available extensions in config directory."""
        extensions_dir = Path(config_dir) / "extensions"
        discovered = {}

        for ext_dir in extensions_dir.glob("*/"):
            if (ext_dir / "server.py").exists():
                discovered[ext_dir.name] = {
                    "type": "mcp_server",
                    "path": ext_dir,
                    "config": self._load_extension_config(ext_dir)
                }
        return discovered

    def load_extension_tools(self, extension_name: str) -> list:
        """Load tools from MCP server extension."""
        # Dynamic loading of MCP server tools
        # Returns list of available tools for skill integration
        pass

    def integrate_with_skill(self, extensions: dict) -> None:
        """Integrate loaded extensions with skill search system."""
        for ext_name, ext_config in extensions.items():
            if ext_config["type"] == "mcp_server":
                tools = self.load_extension_tools(ext_name)
                # Add tools to skill's available functionality
                self._register_external_tools(tools)
```

## Performance and Scalability Considerations

### 1. Search Performance
- **BM25 Indexing**: Pre-compute indices for large datasets
- **Caching Strategy**: Implement result caching for common queries
- **Parallel Search**: Design system searches 5 domains in parallel

### 2. Data Management
- **CSV Size Limits**: Keep individual CSVs under 1MB for performance
- **Index Management**: Consider database migration for >10k records per domain
- **Memory Usage**: Current system loads all data in memory

### 3. Extensibility Patterns
- **Modular Architecture**: Each domain is completely independent
- **Plugin System**: Easy addition of new domains without core changes
- **API Integration**: Framework for external data source integration

## Integration Patterns with Modern Development

### 1. CI/CD Integration
```yaml
# GitHub Actions example
- name: Validate UI/UX Guidelines
  run: python3 .claude/skills/ui-ux-pro-max/scripts/validate_guidelines.py
```

### 2. IDE Integration
```json
// VS Code settings.json
{
  "uiux-pro-max.autoSuggest": true,
  "uiux-pro-max.preferredStack": "react",
  "uiux-pro-max.brandConfig": "./brand-config.json"
}
```

### 3. Design System Export
```bash
# Generate design system for external tools
python3 .claude/skills/ui-ux-pro-max/scripts/export.py \
  --format figma-tokens \
  --output design-tokens.json
```

## Security and Validation

### 1. Data Validation
- **CSV Schema Validation**: Enforce column requirements
- **Content Filtering**: Sanitize user input in search queries
- **Brand Config Validation**: Validate JSON schema for brand preferences

### 2. Access Control
- **Brand Configuration**: Protect personal brand data
- **Custom Domains**: Validate user-added domains
- **Code Examples**: Sanitize code samples in guidelines

## Advanced AI-Centric UI Framework Integration

**Research Findings**: The convergence of Agent-driven interfaces around A2UI, AG-UI, and MCP-UI protocols enables sophisticated hyperpersonalization and dynamic interface generation.

### 1. Protocol Ecosystem Overview

| Protocol | Purpose | Maintained By | Use Case |
|----------|---------|---------------|----------|
| **A2UI** | Agent → UI declarative specification | Google | Multi-platform native rendering from JSON |
| **AG-UI** | Agent ↔ User real-time interaction | CopilotKit | Streaming updates, state sync, tool calls |
| **MCP-UI** | Rich interactive components | Anthropic + Shopify | HTML-based interactive tools in chat |

**Integration Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│ UI/UX Pro Max Skill (Enhanced)                         │
├─────────────────────────────────────────────────────────┤
│ AG-UI (Runtime Layer)                                   │
│ ├── Handles streaming design system generation         │
│ ├── Real-time user context updates                     │
│ └── Manages hyperpersonalization workflow              │
├─────────────────────────────────────────────────────────┤
│ A2UI / MCP-UI (UI Specification Layer)                │
│ ├── A2UI: Cross-platform component blueprints         │
│ └── MCP-UI: Interactive design system explorers        │
├─────────────────────────────────────────────────────────┤
│ MCP Extensions (Tool Layer)                            │
│ ├── Brand Analysis Tools                               │
│ ├── Codebase Analysis Tools                           │
│ └── Hyperpersonalization Engines                       │
└─────────────────────────────────────────────────────────┘
```

### 2. Hyperpersonalization Implementation

#### A. Real-Time Context Analysis

**Create**: `.ui-ux-pro-max-config/extensions/context-analyzer/server.py`

```python
class ContextAnalyzer:
    """Advanced context analysis for hyperpersonalized UI generation."""

    def analyze_user_session(self, session_data: dict) -> dict:
        """Analyze real-time user behavior for personalization."""
        return {
            "interaction_patterns": self._extract_interaction_patterns(session_data),
            "preference_signals": self._detect_preference_signals(session_data),
            "context_switches": self._identify_context_changes(session_data),
            "emotional_indicators": self._analyze_emotional_context(session_data)
        }

    def generate_personalized_recommendations(self, context: dict, project: dict) -> dict:
        """Generate hyperpersonalized UI/UX recommendations."""
        base_recommendations = self._get_base_recommendations(project)

        # Apply real-time personalization
        personalized = self._apply_behavioral_adaptations(
            base_recommendations, context["interaction_patterns"]
        )

        # Apply emotional context
        emotionally_adapted = self._apply_emotional_adaptations(
            personalized, context["emotional_indicators"]
        )

        # Apply contextual preferences
        contextually_adapted = self._apply_contextual_preferences(
            emotionally_adapted, context["preference_signals"]
        )

        return contextually_adapted
```

#### B. Dynamic Interface Generation

```python
class DynamicInterfaceGenerator:
    """Generate adaptive interfaces based on user context."""

    def generate_adaptive_a2ui(self, user_context: dict, base_design: dict) -> list:
        """Generate A2UI specification adapted to user context."""

        # Determine optimal layout based on user behavior
        layout_preference = self._infer_layout_preference(user_context)

        # Adapt color scheme based on context and time
        adaptive_colors = self._adapt_color_scheme(
            base_design["colors"],
            user_context["environmental_context"]
        )

        # Adjust interaction patterns based on usage patterns
        interaction_adaptations = self._adapt_interactions(
            user_context["interaction_patterns"]
        )

        return [
            {
                "surfaceUpdate": {
                    "components": [
                        {
                            "id": "adaptive_root",
                            "component": {
                                layout_preference["type"]: {
                                    "children": {"explicitList": layout_preference["children"]},
                                    "alignment": layout_preference["alignment"],
                                    "distribution": layout_preference["distribution"],
                                    "adaptiveProps": interaction_adaptations
                                }
                            }
                        }
                    ]
                }
            },
            {
                "dataModelUpdate": {
                    "contents": {
                        "adaptiveTheme": adaptive_colors,
                        "userContext": user_context,
                        "personalizationLevel": "high"
                    }
                }
            }
        ]
```

### 3. Cross-Protocol Integration Patterns

#### A. Unified Design System Export

```python
class UnifiedExporter:
    """Export design systems to all supported AI-UI protocols."""

    def export_to_all_protocols(self, design_system: dict) -> dict:
        """Export design system to A2UI, AG-UI, and MCP-UI formats."""

        return {
            "a2ui": self.export_to_a2ui(design_system),
            "ag_ui": self.export_to_ag_ui(design_system),
            "mcp_ui": self.export_to_mcp_ui(design_system),
            "metadata": {
                "source": "ui-ux-pro-max",
                "version": "2.0.0",
                "generated": datetime.now().isoformat(),
                "personalization_applied": True
            }
        }

    def export_to_a2ui(self, design_system: dict) -> list:
        """Convert to A2UI JSON specification for cross-platform rendering."""
        # Implementation for A2UI format
        pass

    def export_to_ag_ui(self, design_system: dict) -> dict:
        """Convert to AG-UI event stream format."""
        # Implementation for AG-UI streaming format
        pass

    def export_to_mcp_ui(self, design_system: dict) -> str:
        """Convert to MCP-UI HTML template."""
        # Implementation for MCP-UI HTML format
        pass
```

### 4. Advanced Personalization Features

#### A. Behavioral Adaptation Engine

**Key Capabilities**:
- **Micro-interaction Timing**: Adapt animation speeds based on user interaction patterns
- **Cognitive Load Management**: Adjust interface complexity based on user expertise
- **Context-Aware Theming**: Dynamic color schemes based on environment and time
- **Accessibility Personalization**: Real-time adjustments based on accessibility needs

```python
class BehavioralAdaptationEngine:
    """Advanced behavioral adaptation for UI personalization."""

    def adapt_micro_interactions(self, base_timings: dict, user_behavior: dict) -> dict:
        """Adapt interaction timing based on user behavior patterns."""

        user_speed_preference = self._calculate_user_speed_preference(user_behavior)

        adapted_timings = {}
        for interaction, timing in base_timings.items():
            if user_speed_preference == "fast":
                adapted_timings[interaction] = max(100, timing * 0.7)  # Faster
            elif user_speed_preference == "slow":
                adapted_timings[interaction] = min(500, timing * 1.3)  # Slower
            else:
                adapted_timings[interaction] = timing

        return adapted_timings

    def adapt_cognitive_complexity(self, base_ui: dict, user_expertise: str) -> dict:
        """Adapt UI complexity based on user expertise level."""

        if user_expertise == "beginner":
            return self._simplify_interface(base_ui)
        elif user_expertise == "expert":
            return self._enhance_interface_with_shortcuts(base_ui)
        else:
            return base_ui
```

#### B. Emotional Context Integration

```python
class EmotionalContextEngine:
    """Integrate emotional context into design decisions."""

    def detect_emotional_state(self, interaction_data: dict) -> dict:
        """Detect user emotional state from interaction patterns."""

        return {
            "frustration_indicators": self._detect_frustration(interaction_data),
            "engagement_level": self._measure_engagement(interaction_data),
            "confidence_level": self._assess_confidence(interaction_data),
            "stress_indicators": self._detect_stress_patterns(interaction_data)
        }

    def adapt_ui_for_emotion(self, base_ui: dict, emotional_state: dict) -> dict:
        """Adapt UI based on detected emotional state."""

        if emotional_state["frustration_indicators"]["high"]:
            # Simplify interface, add helpful hints
            return self._apply_frustration_mitigation(base_ui)

        if emotional_state["engagement_level"] == "low":
            # Add engaging micro-interactions, gamification elements
            return self._apply_engagement_boost(base_ui)

        return base_ui
```

## Future Enhancement Roadmap

### Phase 1: Advanced Platforms (Q2 2026)
- HTMX + Alpine.js + Axum complete integration with Web Components
- Tauri desktop application patterns with native OS integration
- Advanced state management libraries integration (Zustand, Riverpod, etc.)

### Phase 2: AI-Native Features (Q3 2026)
- Full A2UI/AG-UI/MCP-UI protocol implementation
- Real-time hyperpersonalized design system generation
- AI-powered accessibility auditing with emotional context awareness
- Dynamic agent-based UI interfaces with behavioral adaptation

### Phase 3: Enterprise Features (Q4 2026)
- Team collaboration on brand guides with version control
- Multi-agent design system orchestration
- Performance monitoring integration with real-time optimization
- Advanced codebase refactoring with context preservation

### Phase 4: Advanced Intelligence (Q1 2027)
- Machine learning-based style recommendations with continuous learning
- Automated codebase refactoring with architectural intelligence
- Visual design analysis from screenshots with brand consistency checking
- Predictive UI generation based on user behavior patterns

## Conclusion

The UI/UX Pro Max skill architecture provides a robust foundation for s-tier interface development with extensive customization capabilities. The modular, data-driven design enables rapid expansion for new platforms, architectural patterns, and design requirements while maintaining consistency and performance.

The system's strength lies in its intelligent reasoning engine, comprehensive data coverage, and flexible extension mechanisms. By implementing the customizations outlined in this document, developers can create highly specialized design intelligence tailored to specific platforms, architectural preferences, and brand requirements.

**Key Success Factors**:
1. **Maintain Data Quality**: Ensure all CSV files follow consistent schemas
2. **Test Customizations**: Validate all modifications with comprehensive testing
3. **Sync Across Workflows**: Keep all agent integrations up-to-date
4. **Monitor Performance**: Track search performance with large datasets
5. **Iterate Based on Usage**: Continuously refine reasoning rules based on real usage

This architecture positions the UI/UX Pro Max skill as a comprehensive solution for modern interface development, capable of scaling from simple component libraries to complex enterprise design systems while maintaining the highest standards of usability and design excellence.