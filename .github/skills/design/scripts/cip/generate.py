#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIP Design Generator - Generate corporate identity mockups using Gemini Nano Banana

Uses Gemini's native image generation (Nano Banana Flash/Pro) for high-quality mockups.
Supports text-and-image-to-image generation for using actual brand logos.

- gemini-2.5-flash-image: Fast generation, cost-effective (default)
- gemini-3-pro-image-preview: Pro quality, 4K text rendering

Image Editing (text-and-image-to-image):
  When --logo is provided, the script uses Gemini's image editing capability
  to incorporate the actual logo into CIP mockups instead of generating one.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from core import search, get_cip_brief

# Model options
MODELS = {
    "flash": "gemini-2.5-flash-image",      # Nano Banana Flash - fast, default
    "pro": "gemini-3-pro-image-preview"      # Nano Banana Pro - quality, 4K text
}
DEFAULT_MODEL = "flash"


def load_logo_image(logo_path):
    """Load logo image using PIL for Gemini image editing"""
    try:
        from PIL import Image
    except ImportError:
        print("Error: pillow package not installed.")
        print("Install with: pip install pillow")
        return None

    logo_path = Path(logo_path)
    if not logo_path.exists():
        print(f"Error: Logo file not found: {logo_path}")
        return None

    try:
        img = Image.open(logo_path)
        # Convert to RGB if necessary (Gemini works best with RGB)
        if img.mode in ('RGBA', 'P'):
            # Create white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception as e:
        print(f"Error loading logo: {e}")
        return None

# Load environment variables
def load_env():
    """Load environment variables from .env files"""
    env_paths = [
        Path(__file__).parent.parent.parent / ".env",
        Path.home() / ".github" / "skills" / ".env",
        Path.home() / ".github" / ".env"
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key not in os.environ:
                            os.environ[key] = value.strip('"\'')

load_env()


def build_cip_prompt(deliverable, brand_name, style=None, industry=None, mockup=None, use_logo_image=False):
    """Build an optimized prompt for CIP mockup generation

    Args:
        deliverable: Type of deliverable (business card, letterhead, etc.)
        brand_name: Name of the brand
        style: Design style preference
        industry: Industry for style recommendations
        mockup: Mockup context override
        use_logo_image: If True, prompt is optimized for image editing with logo
    """

    # Get deliverable details
    deliverable_info = search(deliverable, "deliverable", 1)
    deliverable_data = deliverable_info.get("results", [{}])[0] if deliverable_info.get("results") else {}

    # Get style details
    style_info = search(style or "corporate minimal", "style", 1) if style else {}
    style_data = style_info.get("results", [{}])[0] if style_info.get("results") else {}

    # Get industry details
    industry_info = search(industry or "technology", "industry", 1) if industry else {}
    industry_data = industry_info.get("results", [{}])[0] if industry_info.get("results") else {}

    # Get mockup context
    mockup_context = deliverable_data.get("Mockup Context", "clean professional")
    if mockup:
        mockup_info = search(mockup, "mockup", 1)
        if mockup_info.get("results"):
            mockup_data = mockup_info["results"][0]
            mockup_context = mockup_data.get("Scene Description", mockup_context)

    # Build prompt components
    deliverable_name = deliverable_data.get("Deliverable", deliverable)
    description = deliverable_data.get("Description", "")
    dimensions = deliverable_data.get("Dimensions", "")
    logo_placement = deliverable_data.get("Logo Placement", "center")

    style_name = style_data.get("Style Name", style or "corporate")
    primary_colors = style_data.get("Primary Colors", industry_data.get("Primary Colors", "#0F172A #FFFFFF"))
    typography = style_data.get("Typography", industry_data.get("Typography", "clean sans-serif"))
    materials = style_data.get("Materials", "premium quality")
    finishes = style_data.get("Finishes", "professional")

    mood = style_data.get("Mood", industry_data.get("Mood", "professional"))

    # Construct the prompt - different for image editing vs pure generation
    if use_logo_image:
        # Image editing prompt: instructs to USE the provided logo image
        prompt_parts = [
            f"Create a professional corporate identity mockup photograph of a {deliverable_name}",
            f"Use the EXACT logo from the provided image - do NOT modify or recreate the logo",
            f"The logo MUST appear exactly as shown in the input image",
            f"Place the logo on the {deliverable_name} at: {logo_placement}",
            f"Brand name: '{brand_name}'",
            f"{description}" if description else "",
            f"Design style: {style_name}",
            f"Color scheme matching the logo colors",
            f"Materials: {materials} with {finishes} finish",
            f"Setting: {mockup_context}",
            f"Mood: {mood}",
            "Photorealistic product photography",
            "Soft natural lighting, professional studio quality",
            "8K resolution, sharp details"
        ]
    else:
        # Pure text-to-image prompt
        prompt_parts = [
            f"Professional corporate identity mockup photograph",
            f"showing {deliverable_name} for brand '{brand_name}'",
            f"{description}" if description else "",
            f"{style_name} design style",
            f"using colors {primary_colors}",
            f"{typography} typography",
            f"logo placement: {logo_placement}",
            f"{materials} materials with {finishes} finish",
            f"{mockup_context} setting",
            f"{mood} mood",
            "photorealistic product photography",
            "soft natural lighting",
            "high quality professional shot",
            "8k resolution detailed"
        ]

    prompt = ", ".join([p for p in prompt_parts if p])

    return {
        "prompt": prompt,
        "deliverable": deliverable_name,
        "style": style_name,
        "brand": brand_name,
        "colors": primary_colors,
        "mockup_context": mockup_context,
        "logo_placement": logo_placement
    }


def generate_with_nano_banana(prompt_data, output_dir=None, model_key="flash", aspect_ratio="1:1", logo_image=None):
    """Generate image using Gemini Nano Banana (native image generation)

    Supports two modes:
    1. Text-to-image: Pure prompt-based generation (logo_image=None)
    2. Image editing: Text-and-image-to-image using provided logo (logo_image=PIL.Image)

    Models:
    - flash: gemini-2.5-flash-image (fast, cost-effective) - DEFAULT
    - pro: gemini-3-pro-image-preview (quality, 4K text rendering)

    Args:
        prompt_data: Dict with prompt, deliverable, brand, etc.
        output_dir: Output directory for generated images
        model_key: 'flash' or 'pro'
        aspect_ratio: Output aspect ratio (1:1, 16:9, etc.)
        logo_image: PIL.Image object of the brand logo for image editing mode
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed.")
        print("Install with: pip install google-genai")
        return None

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY or GOOGLE_API_KEY not set")
        return None

    client = genai.Client(api_key=api_key)

    prompt = prompt_data["prompt"]
    model_name = MODELS.get(model_key, MODELS[DEFAULT_MODEL])

    # Determine mode
    mode = "image-editing" if logo_image else "text-to-image"

    print(f"\n🎨 Generating CIP mockup...")
    print(f"   Mode: {mode}")
    print(f"   Deliverable: {prompt_data['deliverable']}")
    print(f"   Brand: {prompt_data['brand']}")
    print(f"   Style: {prompt_data['style']}")
    print(f"   Model: {model_name}")
    print(f"   Context: {prompt_data['mockup_context']}")
    if logo_image:
        print(f"   Logo: Using provided image ({logo_image.size[0]}x{logo_image.size[1]})")

    try:
        # Build contents: either just prompt or [prompt, image] for image editing
        if logo_image:
            # Image editing mode: pass both prompt and logo image
            contents = [prompt, logo_image]
        else:
            # Text-to-image mode: just the prompt
            contents = prompt

        # Use generate_content with response_modalities=['IMAGE'] for Nano Banana
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],  # Uppercase required
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )

        # Extract image from response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Save image
                    output_dir = output_dir or Path.cwd()
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    brand_slug = prompt_data["brand"].lower().replace(" ", "-")
                    deliverable_slug = prompt_data["deliverable"].lower().replace(" ", "-")
                    filename = f"{brand_slug}-{deliverable_slug}-{timestamp}.png"
                    filepath = output_dir / filename

                    image_data = part.inline_data.data
                    with open(filepath, "wb") as f:
                        f.write(image_data)

                    print(f"\n✅ Generated: {filepath}")
                    return str(filepath)

        print("No image generated in response")
        return None

    except Exception as e:
        print(f"Error generating image: {e}")
        return None


def generate_cip_set(brand_name, industry, style=None, deliverables=None, output_dir=None, model_key="flash", logo_path=None, aspect_ratio="1:1"):
    """Generate a complete CIP set for a brand

    Args:
        brand_name: Brand name to generate for
        industry: Industry type for style recommendations
        style: Optional specific style override
        deliverables: List of deliverables to generate (default: core set)
        output_dir: Output directory for images
        model_key: 'flash' (fast) or 'pro' (quality)
        logo_path: Path to brand logo image for image editing mode
        aspect_ratio: Output aspect ratio
    """

    # Load logo image if provided
    logo_image = None
    if logo_path:
        logo_image = load_logo_image(logo_path)
        if not logo_image:
            print("Warning: Could not load logo, falling back to text-to-image mode")

    # Get CIP brief for the brand
    brief = get_cip_brief(brand_name, industry, style)

    # Default deliverables if not specified
    if not deliverables:
        deliverables = ["business card", "letterhead", "office signage", "vehicle", "polo shirt"]

    results = []
    for deliverable in deliverables:
        prompt_data = build_cip_prompt(
            deliverable=deliverable,
            brand_name=brand_name,
            style=brief.get("style", {}).get("Style Name"),
            industry=industry,
            use_logo_image=(logo_image is not None)
        )

        filepath = generate_with_nano_banana(
            prompt_data,
            output_dir,
            model_key=model_key,
            aspect_ratio=aspect_ratio,
            logo_image=logo_image
        )
        if filepath:
            results.append({
                "deliverable": deliverable,
                "filepath": filepath,
                "prompt": prompt_data["prompt"]
            })

    return results


def check_logo_required(brand_name, skip_prompt=False):
    """Check if logo is required and suggest logo-design skill if not provided

    Returns:
        str: 'continue' to proceed without logo, 'generate' to use logo-design skill, 'exit' to abort
    """
    if skip_prompt:
        return 'continue'

    print(f"\n⚠️  No logo image provided for '{brand_name}'")
    print("   Without a logo, AI will generate its own interpretation of the brand logo.")
    print("")
    print("   Options:")
    print("   1. Continue without logo (AI-generated logo interpretation)")
    print("   2. Generate a logo first using 'logo-design' skill")
    print("   3. Exit and provide a logo path with --logo")
    print("")

    try:
        choice = input("   Enter choice [1/2/3] (default: 1): ").strip()
        if choice == '2':
            return 'generate'
        elif choice == '3':
            return 'exit'
        return 'continue'
    except (EOFError, KeyboardInterrupt):
        return 'continue'


def main():
    parser = argparse.ArgumentParser(
        description="Generate CIP mockups using Gemini Nano Banana",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with brand logo (RECOMMENDED)
  python generate.py --brand "TopGroup" --logo /path/to/logo.png --deliverable "business card"

  # Generate CIP set with logo
  python generate.py --brand "TopGroup" --logo /path/to/logo.png --industry "consulting" --set

  # Generate without logo (AI interprets brand)
  python generate.py --brand "TechFlow" --deliverable "business card" --no-logo-prompt

  # Generate with Pro model (higher quality, 4K text)
  python generate.py --brand "TechFlow" --logo logo.png --deliverable "business card" --model pro

  # Specify output directory and aspect ratio
  python generate.py --brand "MyBrand" --logo logo.png --deliverable "vehicle" --output ./mockups --ratio 16:9

Models:
  flash (default): gemini-2.5-flash-image - Fast, cost-effective
  pro: gemini-3-pro-image-preview - Quality, 4K text rendering

Image Editing Mode:
  When --logo is provided, uses Gemini's text-and-image-to-image capability
  to incorporate your ACTUAL logo into the CIP mockups.
        """
    )

    parser.add_argument("--brand", "-b", required=True, help="Brand name")
    parser.add_argument("--logo", "-l", help="Path to brand logo image (enables image editing mode)")
    parser.add_argument("--deliverable", "-d", help="Single deliverable to generate")
    parser.add_argument("--deliverables", help="Comma-separated list of deliverables")
    parser.add_argument("--industry", "-i", default="technology", help="Industry type")
    parser.add_argument("--style", "-s", help="Design style")
    parser.add_argument("--mockup", "-m", help="Mockup context")
    parser.add_argument("--set", action="store_true", help="Generate full CIP set")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--model", default="flash", choices=["flash", "pro"], help="Model: flash (fast) or pro (quality)")
    parser.add_argument("--ratio", default="1:1", help="Aspect ratio (1:1, 16:9, 4:3, etc.)")
    parser.add_argument("--prompt-only", action="store_true", help="Only show prompt, don't generate")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--no-logo-prompt", action="store_true", help="Skip logo prompt, proceed without logo")

    args = parser.parse_args()

    # Check if logo is provided, prompt user if not
    logo_image = None
    if args.logo:
        logo_image = load_logo_image(args.logo)
        if not logo_image:
            print("Error: Could not load logo image")
            sys.exit(1)
    elif not args.prompt_only:
        # No logo provided - ask user what to do
        action = check_logo_required(args.brand, skip_prompt=args.no_logo_prompt)
        if action == 'generate':
            print("\n💡 To generate a logo, use the logo-design skill:")
            print(f"   python ~/.github/skills/design/scripts/logo/generate.py --brand \"{args.brand}\" --industry \"{args.industry}\"")
            print("\n   Then re-run this command with --logo <generated_logo.png>")
            sys.exit(0)
        elif action == 'exit':
            print("\n   Provide logo with: --logo /path/to/your/logo.png")
            sys.exit(0)
        # else: continue without logo

    use_logo = logo_image is not None

    if args.set or args.deliverables:
        # Generate multiple deliverables
        deliverables = args.deliverables.split(",") if args.deliverables else None

        if args.prompt_only:
            results = []
            deliverables = deliverables or ["business card", "letterhead", "office signage", "vehicle", "polo shirt"]
            for d in deliverables:
                prompt_data = build_cip_prompt(d, args.brand, args.style, args.industry, args.mockup, use_logo_image=use_logo)
                results.append(prompt_data)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                for r in results:
                    print(f"\n{r['deliverable']}:\n{r['prompt']}\n")
        else:
            results = generate_cip_set(
                args.brand, args.industry, args.style, deliverables, args.output,
                model_key=args.model, logo_path=args.logo, aspect_ratio=args.ratio
            )
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"\n✅ Generated {len(results)} CIP mockups")
    else:
        # Generate single deliverable
        deliverable = args.deliverable or "business card"
        prompt_data = build_cip_prompt(deliverable, args.brand, args.style, args.industry, args.mockup, use_logo_image=use_logo)

        if args.prompt_only:
            if args.json:
                print(json.dumps(prompt_data, indent=2))
            else:
                print(f"\nPrompt:\n{prompt_data['prompt']}")
        else:
            filepath = generate_with_nano_banana(
                prompt_data, args.output, model_key=args.model,
                aspect_ratio=args.ratio, logo_image=logo_image
            )
            if args.json:
                print(json.dumps({"filepath": filepath, **prompt_data}, indent=2))


if __name__ == "__main__":
    main()
