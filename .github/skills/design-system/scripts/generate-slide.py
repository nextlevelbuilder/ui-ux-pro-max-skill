#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slide Generator - Generates HTML slides using design tokens
ALL styles MUST use CSS variables from design-tokens.css
NO hardcoded colors, fonts, or spacing allowed
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
TOKENS_CSS = Path(__file__).resolve().parents[4] / "assets" / "design-tokens.css"
TOKENS_JSON = Path(__file__).resolve().parents[4] / "assets" / "design-tokens.json"
OUTPUT_DIR = Path(__file__).resolve().parents[4] / "assets" / "designs" / "slides"

# ============ BRAND-COMPLIANT SLIDE TEMPLATE ============
# ALL values reference CSS variables from design-tokens.css

SLIDE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <!-- Brand Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">

    <!-- Design Tokens - SINGLE SOURCE OF TRUTH -->
    <link rel="stylesheet" href="{tokens_css_path}">

    <style>
        /* ============================================
           STRICT TOKEN USAGE - NO HARDCODED VALUES
           All styles MUST use var(--token-name)
           ============================================ */

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            width: 100%;
            height: 100%;
        }}

        body {{
            font-family: var(--typography-font-body);
            background: var(--color-background);
            color: var(--color-foreground);
            line-height: var(--primitive-lineHeight-relaxed);
        }}

        /* Slide Container - 16:9 aspect ratio */
        .slide-deck {{
            width: 100%;
            max-width: 1920px;
            margin: 0 auto;
        }}

        .slide {{
            width: 100%;
            aspect-ratio: 16 / 9;
            padding: var(--slide-padding);
            background: var(--slide-bg);
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}

        .slide + .slide {{
            margin-top: var(--primitive-spacing-8);
        }}

        /* Background Variants */
        .slide--surface {{
            background: var(--slide-bg-surface);
        }}

        .slide--gradient {{
            background: var(--slide-bg-gradient);
        }}

        .slide--glow::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 150%;
            height: 150%;
            background: var(--primitive-gradient-glow);
            pointer-events: none;
        }}

        /* Typography - MUST use token fonts and sizes */
        h1, h2, h3, h4, h5, h6 {{
            font-family: var(--typography-font-heading);
            font-weight: var(--primitive-fontWeight-bold);
            line-height: var(--primitive-lineHeight-tight);
        }}

        .slide-title {{
            font-size: var(--slide-title-size);
            background: var(--primitive-gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .slide-heading {{
            font-size: var(--slide-heading-size);
            color: var(--color-foreground);
        }}

        .slide-subheading {{
            font-size: var(--primitive-fontSize-3xl);
            color: var(--color-foreground-secondary);
            font-weight: var(--primitive-fontWeight-medium);
        }}

        .slide-body {{
            font-size: var(--slide-body-size);
            color: var(--color-foreground-secondary);
            max-width: 80ch;
        }}

        /* Brand Colors - Primary/Secondary/Accent */
        .text-primary {{ color: var(--color-primary); }}
        .text-secondary {{ color: var(--color-secondary); }}
        .text-accent {{ color: var(--color-accent); }}
        .text-muted {{ color: var(--color-foreground-muted); }}

        .bg-primary {{ background: var(--color-primary); }}
        .bg-secondary {{ background: var(--color-secondary); }}
        .bg-accent {{ background: var(--color-accent); }}
        .bg-surface {{ background: var(--color-surface); }}

        /* Cards - Using component tokens */
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: var(--card-radius);
            padding: var(--card-padding);
            box-shadow: var(--card-shadow);
            transition: border-color var(--primitive-duration-base) var(--primitive-easing-out);
        }}

        .card:hover {{
            border-color: var(--card-border-hover);
        }}

        /* Buttons - Using component tokens */
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: var(--button-primary-padding-y) var(--button-primary-padding-x);
            border-radius: var(--button-primary-radius);
            font-size: var(--button-primary-font-size);
            font-weight: var(--button-primary-font-weight);
            font-family: var(--typography-font-body);
            text-decoration: none;
            cursor: pointer;
            border: none;
            transition: all var(--primitive-duration-base) var(--primitive-easing-out);
        }}

        .btn-primary {{
            background: var(--button-primary-bg);
            color: var(--button-primary-fg);
            box-shadow: var(--button-primary-shadow);
        }}

        .btn-primary:hover {{
            background: var(--button-primary-bg-hover);
        }}

        .btn-secondary {{
            background: transparent;
            color: var(--color-primary);
            border: 2px solid var(--color-primary);
        }}

        /* Layout Utilities */
        .flex {{ display: flex; }}
        .flex-col {{ flex-direction: column; }}
        .items-center {{ align-items: center; }}
        .justify-center {{ justify-content: center; }}
        .justify-between {{ justify-content: space-between; }}
        .gap-4 {{ gap: var(--primitive-spacing-4); }}
        .gap-6 {{ gap: var(--primitive-spacing-6); }}
        .gap-8 {{ gap: var(--primitive-spacing-8); }}

        .grid {{ display: grid; }}
        .grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
        .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
        .grid-4 {{ grid-template-columns: repeat(4, 1fr); }}

        .text-center {{ text-align: center; }}
        .mt-auto {{ margin-top: auto; }}
        .mb-4 {{ margin-bottom: var(--primitive-spacing-4); }}
        .mb-6 {{ margin-bottom: var(--primitive-spacing-6); }}
        .mb-8 {{ margin-bottom: var(--primitive-spacing-8); }}

        /* Metric Cards */
        .metric {{
            text-align: center;
            padding: var(--primitive-spacing-6);
        }}

        .metric-value {{
            font-family: var(--typography-font-heading);
            font-size: var(--primitive-fontSize-6xl);
            font-weight: var(--primitive-fontWeight-bold);
            background: var(--primitive-gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .metric-label {{
            font-size: var(--primitive-fontSize-lg);
            color: var(--color-foreground-secondary);
            margin-top: var(--primitive-spacing-2);
        }}

        /* Feature List */
        .feature-item {{
            display: flex;
            align-items: flex-start;
            gap: var(--primitive-spacing-4);
            padding: var(--primitive-spacing-4) 0;
        }}

        .feature-icon {{
            width: 48px;
            height: 48px;
            border-radius: var(--primitive-radius-lg);
            background: var(--color-surface-elevated);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--color-primary);
            font-size: var(--primitive-fontSize-xl);
            flex-shrink: 0;
        }}

        .feature-content h4 {{
            font-size: var(--primitive-fontSize-xl);
            color: var(--color-foreground);
            margin-bottom: var(--primitive-spacing-2);
        }}

        .feature-content p {{
            color: var(--color-foreground-secondary);
            font-size: var(--primitive-fontSize-base);
        }}

        /* Testimonial */
        .testimonial {{
            background: var(--color-surface);
            border-radius: var(--primitive-radius-xl);
            padding: var(--primitive-spacing-8);
            border-left: 4px solid var(--color-primary);
        }}

        .testimonial-quote {{
            font-size: var(--primitive-fontSize-2xl);
            color: var(--color-foreground);
            font-style: italic;
            margin-bottom: var(--primitive-spacing-6);
        }}

        .testimonial-author {{
            font-size: var(--primitive-fontSize-lg);
            color: var(--color-primary);
            font-weight: var(--primitive-fontWeight-semibold);
        }}

        .testimonial-role {{
            font-size: var(--primitive-fontSize-base);
            color: var(--color-foreground-muted);
        }}

        /* Badge/Tag */
        .badge {{
            display: inline-block;
            padding: var(--primitive-spacing-2) var(--primitive-spacing-4);
            background: var(--color-surface-elevated);
            border-radius: var(--primitive-radius-full);
            font-size: var(--primitive-fontSize-sm);
            color: var(--color-accent);
            font-weight: var(--primitive-fontWeight-medium);
        }}

        /* Chart Container */
        .chart-container {{
            background: var(--color-surface);
            border-radius: var(--primitive-radius-xl);
            padding: var(--primitive-spacing-6);
            height: 100%;
            display: flex;
            flex-direction: column;
        }}

        .chart-title {{
            font-family: var(--typography-font-heading);
            font-size: var(--primitive-fontSize-xl);
            color: var(--color-foreground);
            margin-bottom: var(--primitive-spacing-4);
        }}

        /* CSS-only Bar Chart */
        .bar-chart {{
            display: flex;
            align-items: flex-end;
            gap: var(--primitive-spacing-4);
            height: 200px;
            padding-top: var(--primitive-spacing-4);
        }}

        .bar {{
            flex: 1;
            background: var(--primitive-gradient-primary);
            border-radius: var(--primitive-radius-md) var(--primitive-radius-md) 0 0;
            position: relative;
            min-width: 40px;
        }}

        .bar-label {{
            position: absolute;
            bottom: -30px;
            left: 50%;
            transform: translateX(-50%);
            font-size: var(--primitive-fontSize-sm);
            color: var(--color-foreground-muted);
            white-space: nowrap;
        }}

        .bar-value {{
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: var(--primitive-fontSize-sm);
            color: var(--color-foreground);
            font-weight: var(--primitive-fontWeight-semibold);
        }}

        /* Progress Bar */
        .progress {{
            height: 12px;
            background: var(--color-surface-elevated);
            border-radius: var(--primitive-radius-full);
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: var(--primitive-gradient-primary);
            border-radius: var(--primitive-radius-full);
        }}

        /* Footer */
        .slide-footer {{
            margin-top: auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: var(--primitive-spacing-6);
            border-top: 1px solid var(--color-border);
            color: var(--color-foreground-muted);
            font-size: var(--primitive-fontSize-sm);
        }}

        /* Glow Effects */
        .glow-coral {{
            box-shadow: var(--primitive-shadow-glow-coral);
        }}

        .glow-purple {{
            box-shadow: var(--primitive-shadow-glow-purple);
        }}

        .glow-mint {{
            box-shadow: var(--primitive-shadow-glow-mint);
        }}
    </style>
</head>
<body>
    <div class="slide-deck">
        {slides_content}
    </div>
</body>
</html>
'''


# ============ SLIDE GENERATORS ============

def generate_title_slide(data):
    """Title slide with gradient headline"""
    return f'''
    <section class="slide slide--glow flex flex-col items-center justify-center text-center">
        <div class="badge mb-6">{data.get('badge', 'Pitch Deck')}</div>
        <h1 class="slide-title mb-6">{data.get('title', 'Your Title Here')}</h1>
        <p class="slide-subheading mb-8">{data.get('subtitle', 'Your compelling subtitle')}</p>
        <div class="flex gap-4">
            <a href="#" class="btn btn-primary">{data.get('cta', 'Get Started')}</a>
            <a href="#" class="btn btn-secondary">{data.get('secondary_cta', 'Learn More')}</a>
        </div>
        <div class="slide-footer">
            <span>{data.get('company', 'Company Name')}</span>
            <span>{data.get('date', datetime.now().strftime('%B %Y'))}</span>
        </div>
    </section>
    '''


def generate_problem_slide(data):
    """Problem statement slide using PAS formula"""
    return f'''
    <section class="slide slide--surface">
        <div class="badge mb-6">The Problem</div>
        <h2 class="slide-heading mb-8">{data.get('headline', 'The problem your audience faces')}</h2>
        <div class="grid grid-3 gap-8">
            <div class="card">
                <div class="text-primary" style="font-size: var(--primitive-fontSize-4xl); margin-bottom: var(--primitive-spacing-4);">01</div>
                <h4 style="margin-bottom: var(--primitive-spacing-2); font-size: var(--primitive-fontSize-xl);">{data.get('pain_1_title', 'Pain Point 1')}</h4>
                <p class="text-muted">{data.get('pain_1_desc', 'Description of the first pain point')}</p>
            </div>
            <div class="card">
                <div class="text-secondary" style="font-size: var(--primitive-fontSize-4xl); margin-bottom: var(--primitive-spacing-4);">02</div>
                <h4 style="margin-bottom: var(--primitive-spacing-2); font-size: var(--primitive-fontSize-xl);">{data.get('pain_2_title', 'Pain Point 2')}</h4>
                <p class="text-muted">{data.get('pain_2_desc', 'Description of the second pain point')}</p>
            </div>
            <div class="card">
                <div class="text-accent" style="font-size: var(--primitive-fontSize-4xl); margin-bottom: var(--primitive-spacing-4);">03</div>
                <h4 style="margin-bottom: var(--primitive-spacing-2); font-size: var(--primitive-fontSize-xl);">{data.get('pain_3_title', 'Pain Point 3')}</h4>
                <p class="text-muted">{data.get('pain_3_desc', 'Description of the third pain point')}</p>
            </div>
        </div>
        <div class="slide-footer">
            <span>{data.get('company', 'Company Name')}</span>
            <span>{data.get('page', '2')}</span>
        </div>
    </section>
    '''


def generate_solution_slide(data):
    """Solution slide with feature highlights"""
    return f'''
    <section class="slide">
        <div class="badge mb-6">The Solution</div>
        <h2 class="slide-heading mb-8">{data.get('headline', 'How we solve this')}</h2>
        <div class="flex gap-8" style="flex: 1;">
            <div style="flex: 1;">
                <div class="feature-item">
                    <div class="feature-icon">&#10003;</div>
                    <div class="feature-content">
                        <h4>{data.get('feature_1_title', 'Feature 1')}</h4>
                        <p>{data.get('feature_1_desc', 'Description of feature 1')}</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">&#10003;</div>
                    <div class="feature-content">
                        <h4>{data.get('feature_2_title', 'Feature 2')}</h4>
                        <p>{data.get('feature_2_desc', 'Description of feature 2')}</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">&#10003;</div>
                    <div class="feature-content">
                        <h4>{data.get('feature_3_title', 'Feature 3')}</h4>
                        <p>{data.get('feature_3_desc', 'Description of feature 3')}</p>
                    </div>
                </div>
            </div>
            <div style="flex: 1;" class="card flex items-center justify-center">
                <div class="text-center">
                    <div class="text-accent" style="font-size: 80px; margin-bottom: var(--primitive-spacing-4);">&#9670;</div>
                    <p class="text-muted">Product screenshot or demo</p>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>{data.get('company', 'Company Name')}</span>
            <span>{data.get('page', '3')}</span>
        </div>
    </section>
    '''


def generate_metrics_slide(data):
    """Traction/metrics slide with large numbers"""
    metrics = data.get('metrics', [
        {'value': '10K+', 'label': 'Active Users'},
        {'value': '95%', 'label': 'Retention Rate'},
        {'value': '3x', 'label': 'Revenue Growth'},
        {'value': '$2M', 'label': 'ARR'}
    ])

    metrics_html = ''.join([f'''
        <div class="card metric">
            <div class="metric-value">{m['value']}</div>
            <div class="metric-label">{m['label']}</div>
        </div>
    ''' for m in metrics[:4]])

    return f'''
    <section class="slide slide--surface slide--glow">
        <div class="badge mb-6">Traction</div>
        <h2 class="slide-heading mb-8 text-center">{data.get('headline', 'Our Growth')}</h2>
        <div class="grid grid-4 gap-6" style="flex: 1; align-items: center;">
            {metrics_html}
        </div>
        <div class="slide-footer">
            <span>{data.get('company', 'Company Name')}</span>
            <span>{data.get('page', '4')}</span>
        </div>
    </section>
    '''


def generate_chart_slide(data):
    """Chart slide with CSS bar chart"""
    bars = data.get('bars', [
        {'label': 'Q1', 'value': 40},
        {'label': 'Q2', 'value': 60},
        {'label': 'Q3', 'value': 80},
        {'label': 'Q4', 'value': 100}
    ])

    bars_html = ''.join([f'''
        <div class="bar" style="height: {b['value']}%;">
            <span class="bar-value">{b.get('display', str(b['value']) + '%')}</span>
            <span class="bar-label">{b['label']}</span>
        </div>
    ''' for b in bars])

    return f'''
    <section class="slide">
        <div class="badge mb-6">{data.get('badge', 'Growth')}</div>
        <h2 class="slide-heading mb-8">{data.get('headline', 'Revenue Growth')}</h2>
        <div class="chart-container" style="flex: 1;">
            <div class="chart-title">{data.get('chart_title', 'Quarterly Revenue')}</div>
            <div class="bar-chart" style="flex: 1; padding-bottom: 40px;">
                {bars_html}
            </div>
        </div>
        <div class="slide-footer">
            <span>{data.get('company', 'Company Name')}</span>
            <span>{data.get('page', '5')}</span>
        </div>
    </section>
    '''


def generate_testimonial_slide(data):
    """Social proof slide"""
    return f'''
    <section class="slide slide--surface flex flex-col justify-center">
        <div class="badge mb-6">What They Say</div>
        <div class="testimonial" style="max-width: 900px;">
            <p class="testimonial-quote">"{data.get('quote', 'This product changed how we work. Incredible results.')}"</p>
            <p class="testimonial-author">{data.get('author', 'Jane Doe')}</p>
            <p class="testimonial-role">{data.get('role', 'CEO, Example Company')}</p>
        </div>
        <div class="slide-footer">
            <span>{data.get('company', 'Company Name')}</span>
            <span>{data.get('page', '6')}</span>
        </div>
    </section>
    '''


def generate_cta_slide(data):
    """Closing CTA slide"""
    return f'''
    <section class="slide slide--gradient flex flex-col items-center justify-center text-center">
        <h2 class="slide-heading mb-6" style="color: var(--color-foreground);">{data.get('headline', 'Ready to get started?')}</h2>
        <p class="slide-body mb-8" style="color: rgba(255,255,255,0.8);">{data.get('subheadline', 'Join thousands of teams already using our solution.')}</p>
        <div class="flex gap-4">
            <a href="{data.get('cta_url', '#')}" class="btn" style="background: var(--color-foreground); color: var(--color-primary);">{data.get('cta', 'Start Free Trial')}</a>
        </div>
        <div class="slide-footer" style="border-color: rgba(255,255,255,0.2); color: rgba(255,255,255,0.6);">
            <span>{data.get('contact', 'contact@example.com')}</span>
            <span>{data.get('website', 'www.example.com')}</span>
        </div>
    </section>
    '''


# Slide type mapping
SLIDE_GENERATORS = {
    'title': generate_title_slide,
    'problem': generate_problem_slide,
    'solution': generate_solution_slide,
    'metrics': generate_metrics_slide,
    'traction': generate_metrics_slide,
    'chart': generate_chart_slide,
    'testimonial': generate_testimonial_slide,
    'cta': generate_cta_slide,
    'closing': generate_cta_slide
}


def generate_deck(slides_data, title="Pitch Deck"):
    """Generate complete deck from slide data list"""
    slides_html = ""
    for slide in slides_data:
        slide_type = slide.get('type', 'title')
        generator = SLIDE_GENERATORS.get(slide_type)
        if generator:
            slides_html += generator(slide)
        else:
            print(f"Warning: Unknown slide type '{slide_type}'")

    # Calculate relative path to tokens CSS
    tokens_rel_path = "../../../assets/design-tokens.css"

    return SLIDE_TEMPLATE.format(
        title=title,
        tokens_css_path=tokens_rel_path,
        slides_content=slides_html
    )


def main():
    parser = argparse.ArgumentParser(description="Generate brand-compliant slides")
    parser.add_argument("--json", "-j", help="JSON file with slide data")
    parser.add_argument("--output", "-o", help="Output HTML file path")
    parser.add_argument("--demo", action="store_true", help="Generate demo deck")

    args = parser.parse_args()

    if args.demo:
        # Demo deck showcasing all slide types
        demo_slides = [
            {
                'type': 'title',
                'badge': 'Investor Deck 2024',
                'title': 'ClaudeKit Marketing',
                'subtitle': 'Your AI marketing team. Always on.',
                'cta': 'Join Waitlist',
                'secondary_cta': 'See Demo',
                'company': 'ClaudeKit',
                'date': 'December 2024'
            },
            {
                'type': 'problem',
                'headline': 'Marketing teams are drowning',
                'pain_1_title': 'Content Overload',
                'pain_1_desc': 'Need to produce 10x content with same headcount',
                'pain_2_title': 'Tool Fatigue',
                'pain_2_desc': '15+ tools that don\'t talk to each other',
                'pain_3_title': 'No Time to Think',
                'pain_3_desc': 'Strategy suffers when execution consumes all hours',
                'company': 'ClaudeKit',
                'page': '2'
            },
            {
                'type': 'solution',
                'headline': 'AI agents that actually get marketing',
                'feature_1_title': 'Content Creation',
                'feature_1_desc': 'Blog posts, social, email - all on brand, all on time',
                'feature_2_title': 'Campaign Management',
                'feature_2_desc': 'Multi-channel orchestration with one command',
                'feature_3_title': 'Analytics & Insights',
                'feature_3_desc': 'Real-time optimization without the spreadsheets',
                'company': 'ClaudeKit',
                'page': '3'
            },
            {
                'type': 'metrics',
                'headline': 'Early traction speaks volumes',
                'metrics': [
                    {'value': '500+', 'label': 'Beta Users'},
                    {'value': '85%', 'label': 'Weekly Active'},
                    {'value': '4.9', 'label': 'NPS Score'},
                    {'value': '50hrs', 'label': 'Saved/Week'}
                ],
                'company': 'ClaudeKit',
                'page': '4'
            },
            {
                'type': 'chart',
                'badge': 'Revenue',
                'headline': 'Growing month over month',
                'chart_title': 'MRR Growth ($K)',
                'bars': [
                    {'label': 'Sep', 'value': 20, 'display': '$5K'},
                    {'label': 'Oct', 'value': 40, 'display': '$12K'},
                    {'label': 'Nov', 'value': 70, 'display': '$28K'},
                    {'label': 'Dec', 'value': 100, 'display': '$45K'}
                ],
                'company': 'ClaudeKit',
                'page': '5'
            },
            {
                'type': 'testimonial',
                'quote': 'ClaudeKit replaced 3 tools and 2 contractors. Our content output tripled while costs dropped 60%.',
                'author': 'Sarah Chen',
                'role': 'Head of Marketing, TechStartup',
                'company': 'ClaudeKit',
                'page': '6'
            },
            {
                'type': 'cta',
                'headline': 'Ship campaigns while you sleep',
                'subheadline': 'Early access available. Limited spots.',
                'cta': 'Join the Waitlist',
                'contact': 'hello@claudekit.ai',
                'website': 'claudekit.ai'
            }
        ]

        html = generate_deck(demo_slides, "ClaudeKit Marketing - Pitch Deck")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / f"demo-pitch-{datetime.now().strftime('%y%m%d')}.html"
        output_path.write_text(html, encoding='utf-8')
        print(f"Demo deck generated: {output_path}")

    elif args.json:
        with open(args.json, 'r') as f:
            data = json.load(f)

        html = generate_deck(data.get('slides', []), data.get('title', 'Presentation'))

        output_path = Path(args.output) if args.output else OUTPUT_DIR / f"deck-{datetime.now().strftime('%y%m%d-%H%M')}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        print(f"Deck generated: {output_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
