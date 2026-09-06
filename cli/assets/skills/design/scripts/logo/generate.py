#!/usr/bin/env python3
"""Logo generation with Gemini, Atlas Cloud, or MuAPI.

Gemini remains the default provider. Atlas Cloud is opt-in with
``--provider atlas`` and uses its asynchronous image generation API. MuAPI is
opt-in with ``--provider muapi`` and uses its asynchronous image generation API
with the selected model's prompt/aspect-ratio contract.

Models:
- Nano Banana (default): gemini-2.5-flash-image - fast, high-volume, low-latency
- Nano Banana Pro (--pro): gemini-3-pro-image-preview - professional quality, advanced reasoning
- MuAPI Nano Banana (--provider muapi): nano-banana - hosted asynchronous image generation

Usage:
    python generate.py --prompt "tech startup logo minimalist blue"
    python generate.py --prompt "coffee shop vintage badge" --style vintage --output logo.png
    python generate.py --brand "TechFlow" --industry tech --style minimalist
    python generate.py --brand "TechFlow" --pro  # Use Nano Banana Pro model
    python generate.py --brand "TechFlow" --provider atlas
    python generate.py --brand "TechFlow" --provider muapi
    python generate.py --brand "TechFlow" --provider muapi --muapi-model nano-banana-pro

Batch mode (generates multiple variants):
    python generate.py --brand "Unikorn" --batch 9 --output-dir ./logos --pro
"""

import argparse
import ipaddress
import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


# Load environment variables
def load_env():
    """Load .env files in priority order"""
    env_paths = [
        Path(__file__).parent.parent.parent / ".env",
        Path.home() / ".claude" / "skills" / ".env",
        Path.home() / ".claude" / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key not in os.environ:
                            os.environ[key] = value.strip("\"'")


load_env()


# ============ CONFIGURATION ============
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ATLASCLOUD_API_KEY = os.environ.get("ATLASCLOUD_API_KEY")
MUAPI_API_KEY = os.environ.get("MUAPI_API_KEY")

# Gemini "Nano Banana" model configurations for image generation
GEMINI_FLASH = "gemini-2.5-flash-image"  # Nano Banana: fast, high-volume, low-latency
GEMINI_PRO = "gemini-3-pro-image-preview"  # Nano Banana Pro: professional quality, advanced reasoning

# Atlas Cloud model validated against the live model catalog and schema.
ATLAS_MODEL = "google/nano-banana-2-lite/text-to-image"
ATLAS_API_BASE = "https://api.atlascloud.ai/api/v1"
MUAPI_MODEL = "nano-banana"
MUAPI_MODELS = ("nano-banana", "nano-banana-pro")
MUAPI_API_BASE = "https://api.muapi.ai/api/v1"
HTTP_USER_AGENT = "ui-ux-pro-max/2.5 (logo generation)"
ATLAS_POLL_INTERVAL = 2
ATLAS_MAX_POLLS = 90
MUAPI_POLL_INTERVAL = 2
MUAPI_MAX_POLLS = 90

# Supported aspect ratios
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]
DEFAULT_ASPECT_RATIO = "1:1"  # Square is ideal for logos

# Logo-specific prompt templates
LOGO_PROMPT_TEMPLATE = """Generate a professional logo image: {prompt}

Style requirements:
- Clean vector-style illustration suitable for a logo
- Simple, scalable design that works at any size
- Clear silhouette and recognizable shape
- Professional quality suitable for business use
- Centered composition on plain white or transparent background
- No text unless specifically requested
- High contrast and clear edges
- Square format, perfectly centered
- Output as a clean, high-quality logo image
"""

STYLE_MODIFIERS = {
    "minimalist": "minimalist, simple geometric shapes, clean lines, lots of white space, single color or limited palette",
    "vintage": "vintage, retro, badge style, distressed texture, heritage feel, warm earth tones",
    "modern": "modern, sleek, gradient colors, tech-forward, innovative feel",
    "luxury": "luxury, elegant, gold accents, refined, premium feel, serif typography",
    "playful": "playful, fun, colorful, friendly, approachable, rounded shapes",
    "corporate": "corporate, professional, trustworthy, stable, conservative colors",
    "organic": "organic, natural, flowing lines, earth tones, sustainable feel",
    "geometric": "geometric, abstract, mathematical precision, symmetrical",
    "hand-drawn": "hand-drawn, artisan, sketch-like, authentic, imperfect lines",
    "3d": "3D, dimensional, depth, shadows, isometric perspective",
    "abstract": "abstract mark, conceptual, symbolic, non-literal representation, artistic interpretation",
    "lettermark": "lettermark, single letter or initials, typographic, monogram style, distinctive character",
    "wordmark": "wordmark, logotype, custom typography, brand name as logo, distinctive lettering",
    "emblem": "emblem, badge, crest style, enclosed design, traditional, authoritative feel",
    "mascot": "mascot, character, friendly face, personified, memorable figure",
    "gradient": "gradient, color transition, vibrant, modern digital feel, smooth color flow",
    "lineart": "line art, single stroke, continuous line, elegant simplicity, wire-frame style",
    "negative-space": "negative space, clever use of white space, hidden meaning, dual imagery, optical illusion",
}

INDUSTRY_PROMPTS = {
    "tech": "technology company, digital, innovative, modern, circuit-like elements",
    "healthcare": "healthcare, medical, caring, trust, cross or heart symbol",
    "finance": "financial services, stable, trustworthy, growth, upward elements",
    "food": "food and beverage, appetizing, warm colors, welcoming",
    "fashion": "fashion brand, elegant, stylish, refined, artistic",
    "fitness": "fitness and sports, dynamic, energetic, powerful, movement",
    "eco": "eco-friendly, sustainable, natural, green, leaf or earth elements",
    "education": "education, knowledge, growth, learning, book or cap symbol",
    "real-estate": "real estate, property, home, roof or building silhouette",
    "creative": "creative agency, artistic, unique, expressive, colorful",
}


def enhance_prompt(base_prompt, style=None, industry=None, brand_name=None):
    """Enhance the logo prompt with style and industry modifiers"""
    prompt_parts = [base_prompt]

    if style and style in STYLE_MODIFIERS:
        prompt_parts.append(STYLE_MODIFIERS[style])

    if industry and industry in INDUSTRY_PROMPTS:
        prompt_parts.append(INDUSTRY_PROMPTS[industry])

    if brand_name:
        prompt_parts.insert(0, f"Logo for '{brand_name}':")

    combined = ", ".join(prompt_parts)
    return LOGO_PROMPT_TEMPLATE.format(prompt=combined)


class _SafeRedirectHandler(HTTPRedirectHandler):
    """Reject redirects to non-public or non-HTTPS destinations."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_public_https_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _validate_public_https_url(url):
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Provider returned an invalid media URL")

    hostname = parsed.hostname.lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith(
        (".localhost", ".local", ".internal")
    ):
        raise ValueError("Provider media URL used a local hostname")

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return
    else:
        if not ip.is_global:
            raise ValueError("Provider media URL used a non-public address")


def _json_request(
    url, api_key, method="GET", payload=None, api_key_header="Authorization"
):
    if api_key_header == "Authorization":
        auth_value = f"Bearer {api_key}"
    elif api_key_header == "x-api-key":
        auth_value = api_key
    else:
        raise ValueError("Unsupported API key header")

    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            api_key_header: auth_value,
            "Accept": "application/json",
            "User-Agent": HTTP_USER_AGENT,
            **({"Content-Type": "application/json"} if body is not None else {}),
        },
    )
    try:
        with build_opener(_SafeRedirectHandler()).open(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Provider request failed ({exc.code}): {detail[:300]}"
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Provider request failed: {exc}") from exc


def _atlas_prediction_data(response):
    if not isinstance(response, dict):
        raise TypeError("Atlas Cloud returned an invalid response")
    if response.get("code") not in (None, 0, 200):
        raise RuntimeError(response.get("message") or "Atlas Cloud request failed")
    data = response.get("data")
    if not isinstance(data, dict):
        raise TypeError("Atlas Cloud response did not include prediction data")
    return data


def _download_atlas_image(url, output_path):
    _download_image(url, output_path, "image provider")


def _download_image(url, output_path, provider_name):
    _validate_public_https_url(url)
    request = Request(
        url,
        headers={"Accept": "image/*", "User-Agent": HTTP_USER_AGENT},
    )
    try:
        with build_opener(_SafeRedirectHandler()).open(
            request, timeout=120
        ) as response:
            content_type = response.headers.get_content_type()
            if not content_type.startswith("image/"):
                raise RuntimeError(
                    f"{provider_name} output is not an image ({content_type})"
                )
            image_data = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Unable to download {provider_name} image: {exc}") from exc

    if not image_data:
        raise RuntimeError(f"{provider_name} returned an empty image")
    with open(output_path, "wb") as output_file:
        output_file.write(image_data)


def _generate_with_atlas(prompt, output_path, aspect_ratio, api_key, model):
    if not api_key:
        raise RuntimeError("ATLASCLOUD_API_KEY not set")

    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
    }
    response = _json_request(
        f"{ATLAS_API_BASE}/model/generateImage",
        api_key,
        method="POST",
        payload=payload,
    )
    data = _atlas_prediction_data(response)
    prediction_id = data.get("id")
    if not prediction_id:
        raise RuntimeError("Atlas Cloud did not return a prediction ID")

    for poll_number in range(ATLAS_MAX_POLLS + 1):
        status = str(data.get("status", "")).lower()
        if status == "completed":
            outputs = data.get("outputs")
            if (
                not isinstance(outputs, list)
                or not outputs
                or not isinstance(outputs[0], str)
            ):
                raise RuntimeError("Atlas Cloud completed without an image URL")
            _download_atlas_image(outputs[0], output_path)
            return
        if status in {"failed", "timeout", "canceled", "cancelled"}:
            raise RuntimeError(data.get("error") or f"Atlas Cloud prediction {status}")
        if poll_number == ATLAS_MAX_POLLS:
            break
        time.sleep(ATLAS_POLL_INTERVAL)
        data = _atlas_prediction_data(
            _json_request(
                f"{ATLAS_API_BASE}/model/prediction/{prediction_id}",
                api_key,
            )
        )

    raise RuntimeError("Atlas Cloud prediction timed out while polling")


def _muapi_response_objects(response):
    """Return the response and common MuAPI envelopes without guessing fields."""
    if not isinstance(response, dict):
        raise TypeError("MuAPI returned an invalid response")

    objects = [response]
    for key in ("data", "output", "result"):
        value = response.get(key)
        if isinstance(value, dict) and value not in objects:
            objects.append(value)
    return objects


def _muapi_response_value(response, keys):
    for item in _muapi_response_objects(response):
        for key in keys:
            value = item.get(key)
            if value not in (None, ""):
                return value
    return None


def _muapi_error(response):
    value = _muapi_response_value(response, ("error", "message", "detail"))
    if isinstance(value, str):
        return value[:300]
    return "MuAPI request failed"


def _muapi_result_url(response):
    """Return the documented result URL from the creation response."""
    for item in _muapi_response_objects(response):
        urls = item.get("urls")
        if not isinstance(urls, dict) or "get" not in urls:
            continue

        result_url = urls.get("get")
        if not isinstance(result_url, str) or not result_url:
            raise RuntimeError(
                "MuAPI creation response did not include a valid HTTPS result URL"
            )
        try:
            _validate_public_https_url(result_url)
        except ValueError as exc:
            raise RuntimeError(
                "MuAPI creation response did not include a valid HTTPS result URL"
            ) from exc
        return result_url

    raise RuntimeError(
        "MuAPI creation response did not include a valid HTTPS result URL"
    )


def _muapi_output_url(response):
    for item in _muapi_response_objects(response):
        outputs = item.get("outputs")
        if isinstance(outputs, list):
            for output in outputs:
                if isinstance(output, str) and output.startswith("https://"):
                    return output
                if isinstance(output, dict):
                    for key in ("url", "image_url"):
                        value = output.get(key)
                        if isinstance(value, str) and value.startswith("https://"):
                            return value
    raise RuntimeError("MuAPI completed without an HTTPS image URL")


def _download_muapi_image(url, output_path):
    _download_image(url, output_path, "MuAPI")


def _generate_with_muapi(prompt, output_path, aspect_ratio, api_key, model):
    if not api_key:
        raise RuntimeError("MUAPI_API_KEY not set")
    if model not in MUAPI_MODELS:
        raise RuntimeError(
            f"Unsupported MuAPI logo model: {model}. "
            f"Choose one of: {', '.join(MUAPI_MODELS)}"
        )

    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
    }
    response = _json_request(
        f"{MUAPI_API_BASE}/{model}",
        api_key,
        method="POST",
        payload=payload,
        api_key_header="x-api-key",
    )
    request_id = _muapi_response_value(response, ("request_id", "id"))
    if not isinstance(request_id, str) or not request_id:
        raise RuntimeError("MuAPI did not return a request ID")
    result_url = _muapi_result_url(response)

    data = response
    for poll_number in range(MUAPI_MAX_POLLS + 1):
        status = _muapi_response_value(data, ("status",))
        normalized_status = str(status or "").lower()
        if normalized_status in {"completed", "succeeded", "success"}:
            _download_muapi_image(_muapi_output_url(data), output_path)
            return
        if normalized_status in {
            "failed",
            "error",
            "timeout",
            "canceled",
            "cancelled",
        }:
            raise RuntimeError(f"MuAPI generation {normalized_status}: {_muapi_error(data)}")
        if poll_number == MUAPI_MAX_POLLS:
            break

        time.sleep(MUAPI_POLL_INTERVAL)
        data = _json_request(
            result_url,
            api_key,
            api_key_header="x-api-key",
        )

    raise RuntimeError("MuAPI prediction timed out while polling")


def _generate_with_gemini(prompt, output_path, aspect_ratio, use_pro):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError(
            "google-genai package not installed; run: pip install google-genai"
        ) from exc

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = GEMINI_PRO if use_pro else GEMINI_FLASH
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_LOW_AND_ABOVE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_LOW_AND_ABOVE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_LOW_AND_ABOVE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_LOW_AND_ABOVE",
                ),
            ],
        ),
    )

    for part in response.candidates[0].content.parts:
        if (
            hasattr(part, "inline_data")
            and part.inline_data
            and part.inline_data.mime_type.startswith("image/")
        ):
            with open(output_path, "wb") as output_file:
                output_file.write(part.inline_data.data)
            return
    raise RuntimeError("Gemini did not return an image")


def generate_logo(
    prompt,
    style=None,
    industry=None,
    brand_name=None,
    output_path=None,
    use_pro=False,
    aspect_ratio=None,
    provider="gemini",
    atlas_model=ATLAS_MODEL,
    muapi_model=MUAPI_MODEL,
):
    """Generate a logo using Gemini, Atlas Cloud, or MuAPI image generation.

    Args:
        aspect_ratio: Image aspect ratio. Options: "1:1", "16:9", "9:16", "4:3", "3:4"
                      Default is "1:1" (square) for logos.
    """

    # Enhance the prompt
    full_prompt = enhance_prompt(prompt, style, industry, brand_name)

    # Set aspect ratio (default to 1:1 for logos)
    ratio = aspect_ratio if aspect_ratio in ASPECT_RATIOS else DEFAULT_ASPECT_RATIO

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # noqa: DTZ005
        brand_slug = brand_name.lower().replace(" ", "_") if brand_name else "logo"
        output_path = f"{brand_slug}_{timestamp}.png"

    if provider == "atlas":
        model_label = f"Atlas Cloud ({atlas_model})"
    elif provider == "muapi":
        model_label = f"MuAPI ({muapi_model})"
    else:
        model_label = (
            "Nano Banana Pro (gemini-3-pro-image-preview)"
            if use_pro
            else "Nano Banana (gemini-2.5-flash-image)"
        )

    print(f"Generating logo with {model_label}...")
    print(f"Aspect ratio: {ratio}")
    print(f"Prompt: {full_prompt[:150]}...")
    print()

    try:
        if provider == "atlas":
            _generate_with_atlas(
                full_prompt,
                output_path,
                ratio,
                ATLASCLOUD_API_KEY,
                atlas_model,
            )
        elif provider == "muapi":
            _generate_with_muapi(
                full_prompt,
                output_path,
                ratio,
                MUAPI_API_KEY,
                muapi_model,
            )
        else:
            _generate_with_gemini(full_prompt, output_path, ratio, use_pro)

        print(f"Logo saved to: {output_path}")
        return output_path

    except Exception as exc:  # noqa: BLE001 - provider SDK errors are not standardized
        print(f"Error generating logo: {exc}")
        return None


def generate_batch(
    prompt,
    brand_name,
    count,
    output_dir,
    use_pro=False,
    brand_context=None,
    aspect_ratio=None,
    provider="gemini",
    atlas_model=ATLAS_MODEL,
    muapi_model=MUAPI_MODEL,
):
    """Generate multiple logo variants with different styles"""

    # Select appropriate styles for batch generation
    batch_styles = [
        ("minimalist", "Clean, simple geometric shape with minimal details"),
        ("modern", "Sleek gradient with tech-forward aesthetic"),
        ("geometric", "Abstract geometric patterns, mathematical precision"),
        ("gradient", "Vibrant color transitions, modern digital feel"),
        ("abstract", "Conceptual symbolic representation"),
        ("lettermark", "Stylized letter 'U' as monogram"),
        ("negative-space", "Clever use of negative space, hidden meaning"),
        ("lineart", "Single stroke continuous line design"),
        ("3d", "Dimensional design with depth and shadows"),
    ]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    results = []
    model_label = (
        f"Atlas Cloud ({atlas_model})"
        if provider == "atlas"
        else f"MuAPI ({muapi_model})"
        if provider == "muapi"
        else f"Nano Banana {'Pro' if use_pro else 'Flash'}"
    )
    ratio = aspect_ratio if aspect_ratio in ASPECT_RATIOS else DEFAULT_ASPECT_RATIO

    print(f"\n{'=' * 60}")
    print(f"  BATCH LOGO GENERATION: {brand_name}")
    print(f"  Model: {model_label}")
    print(f"  Aspect Ratio: {ratio}")
    print(f"  Variants: {count}")
    print(f"  Output: {output_dir}")
    print(f"{'=' * 60}\n")

    for i in range(min(count, len(batch_styles))):
        style_key, style_desc = batch_styles[i]

        # Build enhanced prompt with brand context
        enhanced_prompt = f"{prompt}, {style_desc}"
        if brand_context:
            enhanced_prompt = f"{brand_context}, {enhanced_prompt}"

        # Generate filename
        filename = f"{brand_name.lower().replace(' ', '_')}_{style_key}_{i + 1:02d}.png"
        output_path = os.path.join(output_dir, filename)

        print(f"[{i + 1}/{count}] Generating {style_key} variant...")

        result = generate_logo(
            prompt=enhanced_prompt,
            style=style_key,
            industry="tech",
            brand_name=brand_name,
            output_path=output_path,
            use_pro=use_pro,
            aspect_ratio=aspect_ratio,
            provider=provider,
            atlas_model=atlas_model,
            muapi_model=muapi_model,
        )

        if result:
            results.append(result)
            print(f"  ✓ Saved: {filename}\n")
        else:
            print(f"  ✗ Failed: {style_key}\n")

        # Rate limiting between requests
        if i < count - 1:
            time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"  BATCH COMPLETE: {len(results)}/{count} logos generated")
    print(f"{'=' * 60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate logos using Gemini, Atlas Cloud, or MuAPI"
    )
    parser.add_argument("--prompt", "-p", type=str, help="Logo description prompt")
    parser.add_argument("--brand", "-b", type=str, help="Brand name")
    parser.add_argument(
        "--style", "-s", choices=list(STYLE_MODIFIERS.keys()), help="Logo style"
    )
    parser.add_argument(
        "--industry", "-i", choices=list(INDUSTRY_PROMPTS.keys()), help="Industry type"
    )
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument(
        "--output-dir", type=str, help="Output directory for batch generation"
    )
    parser.add_argument(
        "--batch", type=int, help="Number of logo variants to generate (batch mode)"
    )
    parser.add_argument(
        "--brand-context", type=str, help="Additional brand context for prompts"
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use Nano Banana Pro (gemini-3-pro-image-preview) for professional quality",
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "atlas", "muapi"],
        default="gemini",
        help="Image provider (default: gemini)",
    )
    parser.add_argument(
        "--atlas-model",
        default=ATLAS_MODEL,
        help=f"Atlas Cloud image model (default: {ATLAS_MODEL})",
    )
    parser.add_argument(
        "--muapi-model",
        choices=MUAPI_MODELS,
        default=MUAPI_MODEL,
        help=f"MuAPI image model (default: {MUAPI_MODEL})",
    )
    parser.add_argument(
        "--aspect-ratio",
        "-r",
        choices=ASPECT_RATIOS,
        default=DEFAULT_ASPECT_RATIO,
        help=f"Image aspect ratio (default: {DEFAULT_ASPECT_RATIO} for logos)",
    )
    parser.add_argument(
        "--list-styles", action="store_true", help="List available styles"
    )
    parser.add_argument(
        "--list-industries", action="store_true", help="List available industries"
    )

    args = parser.parse_args()

    if args.provider != "gemini" and args.pro:
        parser.error(
            "--pro is only available with --provider gemini; "
            "use --muapi-model nano-banana-pro for MuAPI"
        )

    if args.list_styles:
        print("Available styles:")
        for style, desc in STYLE_MODIFIERS.items():
            print(f"  {style}: {desc[:60]}...")
        return

    if args.list_industries:
        print("Available industries:")
        for industry, desc in INDUSTRY_PROMPTS.items():
            print(f"  {industry}: {desc[:60]}...")
        return

    if not args.prompt and not args.brand:
        parser.error("Either --prompt or --brand is required")

    prompt = args.prompt or "professional logo"

    # Batch mode
    if args.batch:
        output_dir = (
            args.output_dir or f"./{args.brand.lower().replace(' ', '_')}_logos"
        )
        generate_batch(
            prompt=prompt,
            brand_name=args.brand or "Logo",
            count=args.batch,
            output_dir=output_dir,
            use_pro=args.pro,
            brand_context=args.brand_context,
            aspect_ratio=args.aspect_ratio,
            provider=args.provider,
            atlas_model=args.atlas_model,
            muapi_model=args.muapi_model,
        )
    else:
        generate_logo(
            prompt=prompt,
            style=args.style,
            industry=args.industry,
            brand_name=args.brand,
            output_path=args.output,
            use_pro=args.pro,
            aspect_ratio=args.aspect_ratio,
            provider=args.provider,
            atlas_model=args.atlas_model,
            muapi_model=args.muapi_model,
        )


if __name__ == "__main__":
    main()
