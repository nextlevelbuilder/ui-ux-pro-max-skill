"""Tests for tailwind_config_gen.py"""

from pathlib import Path

import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tailwind_config_gen import TailwindConfigGenerator


class TestTailwindConfigGenerator:
    """Test TailwindConfigGenerator class."""

    def test_init_default_typescript(self):
        """Test initialization with default settings."""
        generator = TailwindConfigGenerator()
        assert generator.typescript is True
        assert generator.framework == "react"

    def test_init_javascript(self):
        """Test initialization for JavaScript config."""
        generator = TailwindConfigGenerator(typescript=False)
        assert generator.typescript is False

    def test_init_framework(self):
        """Test initialization with different frameworks."""
        for framework in ["react", "vue", "svelte", "nextjs"]:
            generator = TailwindConfigGenerator(framework=framework)
            assert generator.framework == framework

    def test_default_output_path_typescript(self):
        """Test default output path for TypeScript."""
        generator = TailwindConfigGenerator(typescript=True)
        assert generator.output_path.name == "tailwind.config.ts"

    def test_default_output_path_javascript(self):
        """Test default output path for JavaScript."""
        generator = TailwindConfigGenerator(typescript=False)
        assert generator.output_path.name == "tailwind.config.js"

    def test_custom_output_path(self, tmp_path):
        """Test custom output path."""
        custom_path = tmp_path / "custom-config.ts"
        generator = TailwindConfigGenerator(output_path=custom_path)
        assert generator.output_path == custom_path

    def test_base_config_structure(self):
        """Test base configuration structure."""
        generator = TailwindConfigGenerator()
        config = generator.config

        assert "darkMode" in config
        assert "content" in config
        assert "theme" in config
        assert "plugins" in config
        assert "extend" in config["theme"]

    def test_default_content_paths_react(self):
        """Test default content paths for React."""
        generator = TailwindConfigGenerator(framework="react")
        paths = generator.config["content"]

        assert any("src/**/*.{js,jsx,ts,tsx}" in p for p in paths)
        assert any("index.html" in p for p in paths)

    def test_default_content_paths_nextjs(self):
        """Test default content paths for Next.js."""
        generator = TailwindConfigGenerator(framework="nextjs")
        paths = generator.config["content"]

        assert any("app/**" in p for p in paths)
        assert any("pages/**" in p for p in paths)
        assert any("components/**" in p for p in paths)

    def test_default_content_paths_vue(self):
        """Test default content paths for Vue."""
        generator = TailwindConfigGenerator(framework="vue")
        paths = generator.config["content"]

        assert any("vue" in p for p in paths)

    def test_add_colors(self):
        """Test adding custom colors."""
        generator = TailwindConfigGenerator()
        colors = {
            "brand": "#3b82f6",
            "accent": "#8b5cf6"
        }
        generator.add_colors(colors)

        assert "colors" in generator.config["theme"]["extend"]
        assert generator.config["theme"]["extend"]["colors"]["brand"] == "#3b82f6"
        assert generator.config["theme"]["extend"]["colors"]["accent"] == "#8b5cf6"

    def test_add_colors_multiple_times(self):
        """Test adding colors multiple times."""
        generator = TailwindConfigGenerator()

        generator.add_colors({"brand": "#3b82f6"})
        generator.add_colors({"accent": "#8b5cf6"})

        colors = generator.config["theme"]["extend"]["colors"]
        assert "brand" in colors
        assert "accent" in colors

    def test_add_color_palette(self):
        """Test adding full color palette."""
        generator = TailwindConfigGenerator()
        generator.add_color_palette("brand", "#3b82f6")

        brand = generator.config["theme"]["extend"]["colors"]["brand"]

        assert isinstance(brand, dict)
        assert "50" in brand
        assert "500" in brand
        assert "950" in brand
        assert "var(--color-brand" in brand["500"]

    def test_add_fonts(self):
        """Test adding custom fonts."""
        generator = TailwindConfigGenerator()
        fonts = {
            "sans": ["Inter", "system-ui", "sans-serif"],
            "display": ["Playfair Display", "serif"]
        }
        generator.add_fonts(fonts)

        font_family = generator.config["theme"]["extend"]["fontFamily"]
        assert font_family["sans"] == ["Inter", "system-ui", "sans-serif"]
        assert font_family["display"] == ["Playfair Display", "serif"]

    def test_add_spacing(self):
        """Test adding custom spacing."""
        generator = TailwindConfigGenerator()
        spacing = {
            "18": "4.5rem",
            "navbar": "4rem"
        }
        generator.add_spacing(spacing)

        spacing_config = generator.config["theme"]["extend"]["spacing"]
        assert spacing_config["18"] == "4.5rem"
        assert spacing_config["navbar"] == "4rem"

    def test_add_breakpoints(self):
        """Test adding custom breakpoints."""
        generator = TailwindConfigGenerator()
        breakpoints = {
            "3xl": "1920px",
            "tablet": "768px"
        }
        generator.add_breakpoints(breakpoints)

        screens = generator.config["theme"]["extend"]["screens"]
        assert screens["3xl"] == "1920px"
        assert screens["tablet"] == "768px"

    def test_add_plugins(self):
        """Test adding plugins."""
        generator = TailwindConfigGenerator()
        plugins = ["@tailwindcss/typography", "@tailwindcss/forms"]
        generator.add_plugins(plugins)

        assert "@tailwindcss/typography" in generator.config["plugins"]
        assert "@tailwindcss/forms" in generator.config["plugins"]

    def test_add_plugins_no_duplicates(self):
        """Test that adding same plugin twice doesn't duplicate."""
        generator = TailwindConfigGenerator()
        generator.add_plugins(["@tailwindcss/typography"])
        generator.add_plugins(["@tailwindcss/typography"])

        count = generator.config["plugins"].count("@tailwindcss/typography")
        assert count == 1

    def test_recommend_plugins(self):
        """Test plugin recommendations."""
        generator = TailwindConfigGenerator()
        recommendations = generator.recommend_plugins()

        assert isinstance(recommendations, list)
        assert "tailwindcss-animate" in recommendations

    def test_recommend_plugins_nextjs(self):
        """Test plugin recommendations for Next.js."""
        generator = TailwindConfigGenerator(framework="nextjs")
        recommendations = generator.recommend_plugins()

        assert "@tailwindcss/typography" in recommendations

    def test_generate_typescript_config(self):
        """Test generating TypeScript configuration."""
        generator = TailwindConfigGenerator(typescript=True)
        config = generator.generate_config_string()

        assert "import type { Config } from 'tailwindcss'" in config
        assert "const config: Config" in config
        assert "export default config" in config

    def test_generate_javascript_config(self):
        """Test generating JavaScript configuration."""
        generator = TailwindConfigGenerator(typescript=False)
        config = generator.generate_config_string()

        assert "module.exports" in config
        assert "@type" in config

    def test_generate_config_with_colors(self):
        """Test generating config with custom colors."""
        generator = TailwindConfigGenerator()
        generator.add_colors({"brand": "#3b82f6"})
        config = generator.generate_config_string()

        assert "colors" in config
        assert "brand" in config

    def test_generate_config_with_plugins(self):
        """Test generating config with plugins."""
        generator = TailwindConfigGenerator()
        generator.add_plugins(["tailwindcss-animate"])
        config = generator.generate_config_string()

        assert "plugins:" in config
        assert "require('tailwindcss-animate')" in config

    def test_validate_config_valid(self):
        """Test validating valid configuration."""
        generator = TailwindConfigGenerator()
        valid, message = generator.validate_config()

        assert valid is True

    def test_validate_config_no_content(self):
        """Test validating config with no content paths."""
        generator = TailwindConfigGenerator()
        generator.config["content"] = []

        valid, message = generator.validate_config()

        assert valid is False
        assert "No content paths" in message

    def test_validate_config_empty_theme(self):
        """Test validating config with empty theme extensions."""
        generator = TailwindConfigGenerator()
        # Default has empty theme.extend

        valid, message = generator.validate_config()

        assert valid is True
        assert "Warning" in message

    def test_write_config(self, tmp_path):
        """Test writing configuration to file."""
        output_path = tmp_path / "tailwind.config.ts"
        generator = TailwindConfigGenerator(output_path=output_path)

        success, message = generator.write_config()

        assert success is True
        assert output_path.exists()
        assert "written to" in message

    def test_write_config_creates_content(self, tmp_path):
        """Test that written config contains expected content."""
        output_path = tmp_path / "tailwind.config.ts"
        generator = TailwindConfigGenerator(output_path=output_path)
        generator.add_colors({"brand": "#3b82f6"})

        generator.write_config()

        content = output_path.read_text()
        assert "import type { Config }" in content
        assert "brand" in content

    def test_write_config_invalid_path(self):
        """Test writing config to invalid path."""
        generator = TailwindConfigGenerator(output_path=Path("/invalid/path/config.ts"))

        success, message = generator.write_config()

        assert success is False
        assert "Failed to write" in message

    def test_full_configuration_typescript(self, tmp_path):
        """Test generating complete TypeScript configuration."""
        output_path = tmp_path / "tailwind.config.ts"
        generator = TailwindConfigGenerator(
            typescript=True,
            framework="nextjs",
            output_path=output_path
        )

        # Add various customizations
        generator.add_colors({"brand": "#3b82f6", "accent": "#8b5cf6"})
        generator.add_fonts({"sans": ["Inter", "sans-serif"]})
        generator.add_spacing({"navbar": "4rem"})
        generator.add_breakpoints({"3xl": "1920px"})
        generator.add_plugins(["tailwindcss-animate"])

        success, _ = generator.write_config()
        assert success is True

        content = output_path.read_text()

        # Verify all customizations are present
        assert "brand" in content
        assert "accent" in content
        assert "Inter" in content
        assert "navbar" in content
        assert "3xl" in content
        assert "tailwindcss-animate" in content

    def test_full_configuration_javascript(self, tmp_path):
        """Test generating complete JavaScript configuration."""
        output_path = tmp_path / "tailwind.config.js"
        generator = TailwindConfigGenerator(
            typescript=False,
            framework="react",
            output_path=output_path
        )

        generator.add_colors({"primary": "#3b82f6"})
        generator.add_plugins(["@tailwindcss/forms"])

        success, _ = generator.write_config()
        assert success is True

        content = output_path.read_text()

        assert "module.exports" in content
        assert "primary" in content
        assert "@tailwindcss/forms" in content
