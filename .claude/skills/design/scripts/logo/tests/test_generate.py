import base64
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch

MODULE_PATH = Path(__file__).parents[1] / "generate.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("logo_generate", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


logo_generate = _load_module()

JPEG = b"\xff\xd8\xff\xe0jpeg-bytes"
PNG = b"\x89PNG\r\n\x1a\npng-bytes"


def _image_response(mime_type, data):
    part = SimpleNamespace(inline_data=SimpleNamespace(mime_type=mime_type, data=data))
    return SimpleNamespace(
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))]
    )


def _fake_genai(client):
    """sys.modules entries for an offline google.genai whose Client is client."""
    types = ModuleType("google.genai.types")
    types.GenerateContentConfig = types.ImageConfig = types.SafetySetting = dict
    genai = ModuleType("google.genai")
    genai.Client = lambda api_key: client
    genai.types = types
    google = ModuleType("google")
    google.genai = genai
    return {"google": google, "google.genai": genai, "google.genai.types": types}


class AtlasGenerationTests(unittest.TestCase):
    @patch.object(logo_generate, "_download_atlas_image")
    @patch.object(logo_generate.time, "sleep")
    @patch.object(logo_generate, "_json_request")
    def test_atlas_submits_once_and_polls_until_completed(
        self, json_request, sleep, download
    ):
        json_request.side_effect = [
            {"code": 200, "data": {"id": "pred-123", "status": "created"}},
            {"code": 200, "data": {"id": "pred-123", "status": "processing"}},
            {
                "code": 200,
                "data": {
                    "id": "pred-123",
                    "status": "completed",
                    "outputs": ["https://media.example.com/logo.png"],
                },
            },
        ]

        logo_generate._generate_with_atlas(
            "logo prompt", "logo.png", "1:1", "atlas-key", "atlas/model"
        )

        self.assertEqual(json_request.call_count, 3)
        self.assertEqual(
            json_request.call_args_list[0],
            call(
                f"{logo_generate.ATLAS_API_BASE}/model/generateImage",
                "atlas-key",
                method="POST",
                payload={
                    "model": "atlas/model",
                    "prompt": "logo prompt",
                    "aspect_ratio": "1:1",
                },
            ),
        )
        self.assertEqual(
            json_request.call_args_list[1:],
            [
                call(
                    f"{logo_generate.ATLAS_API_BASE}/model/prediction/pred-123",
                    "atlas-key",
                ),
                call(
                    f"{logo_generate.ATLAS_API_BASE}/model/prediction/pred-123",
                    "atlas-key",
                ),
            ],
        )
        self.assertEqual(sleep.call_count, 2)
        download.assert_called_once_with(
            "https://media.example.com/logo.png", "logo.png"
        )

    @patch.object(logo_generate, "_json_request")
    def test_atlas_does_not_retry_generation_post(self, json_request):
        json_request.side_effect = RuntimeError("network error")

        with self.assertRaisesRegex(RuntimeError, "network error"):
            logo_generate._generate_with_atlas(
                "logo prompt", "logo.png", "1:1", "atlas-key", "atlas/model"
            )

        json_request.assert_called_once()

    @patch.object(logo_generate, "_validate_public_https_url")
    @patch.object(logo_generate, "build_opener")
    def test_media_download_never_forwards_api_key(self, build_opener, validate):
        class Headers:
            @staticmethod
            def get_content_type():
                return "image/png"

        class Response:
            headers = Headers()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            @staticmethod
            def read():
                return b"png-bytes"

        build_opener.return_value.open.return_value = Response()

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "logo.png"
            logo_generate._download_atlas_image(
                "https://media.example.com/logo.png", output
            )
            self.assertEqual(output.read_bytes(), b"png-bytes")

        request = build_opener.return_value.open.call_args.args[0]
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertNotIn("authorization", headers)
        self.assertEqual(headers["accept"], "image/*")
        self.assertEqual(headers["user-agent"], logo_generate.HTTP_USER_AGENT)
        validate.assert_called_once_with("https://media.example.com/logo.png")

    def test_atlas_requires_api_key(self):
        with self.assertRaisesRegex(RuntimeError, "ATLASCLOUD_API_KEY not set"):
            logo_generate._generate_with_atlas(
                "logo prompt", "logo.png", "1:1", None, "atlas/model"
            )

    def test_media_url_rejects_private_addresses(self):
        with self.assertRaisesRegex(ValueError, "non-public address"):
            logo_generate._validate_public_https_url("https://127.0.0.1/logo.png")

        with self.assertRaisesRegex(ValueError, "local hostname"):
            logo_generate._validate_public_https_url("https://assets.local/logo.png")


class MuapiGenerationTests(unittest.TestCase):
    @patch.object(logo_generate, "_download_muapi_image")
    @patch.object(logo_generate.time, "sleep")
    @patch.object(logo_generate, "_json_request")
    def test_muapi_submits_once_and_polls_until_completed(
        self, json_request, sleep, download
    ):
        json_request.side_effect = [
            {
                "id": "req-123",
                "status": "created",
                "output": {
                    "urls": {
                        "get": "https://api.muapi.ai/api/v1/results/req-123"
                    }
                },
            },
            {"id": "req-123", "status": "processing"},
            {
                "id": "req-123",
                "status": "completed",
                "output": {"outputs": ["https://media.example.com/logo.png"]},
            },
        ]

        logo_generate._generate_with_muapi(
            "logo prompt", "logo.png", "1:1", "muapi-key", "nano-banana"
        )

        self.assertEqual(json_request.call_count, 3)
        self.assertEqual(
            json_request.call_args_list[0],
            call(
                f"{logo_generate.MUAPI_API_BASE}/nano-banana",
                "muapi-key",
                method="POST",
                payload={"prompt": "logo prompt", "aspect_ratio": "1:1"},
                api_key_header="x-api-key",
            ),
        )
        self.assertEqual(
            json_request.call_args_list[1:],
            [
                call(
                    "https://api.muapi.ai/api/v1/results/req-123",
                    "muapi-key",
                    api_key_header="x-api-key",
                ),
                call(
                    "https://api.muapi.ai/api/v1/results/req-123",
                    "muapi-key",
                    api_key_header="x-api-key",
                ),
            ],
        )
        self.assertEqual(sleep.call_count, 2)
        download.assert_called_once_with(
            "https://media.example.com/logo.png", "logo.png"
        )

    @patch.object(logo_generate, "_json_request")
    def test_muapi_does_not_retry_generation_post(self, json_request):
        json_request.side_effect = RuntimeError("network error")

        with self.assertRaisesRegex(RuntimeError, "network error"):
            logo_generate._generate_with_muapi(
                "logo prompt", "logo.png", "1:1", "muapi-key", "nano-banana"
            )

        json_request.assert_called_once()

    def test_muapi_requires_key_and_known_model(self):
        with self.assertRaisesRegex(RuntimeError, "MUAPI_API_KEY not set"):
            logo_generate._generate_with_muapi(
                "logo prompt", "logo.png", "1:1", None, "nano-banana"
            )

        with self.assertRaisesRegex(RuntimeError, "Unsupported MuAPI logo model"):
            logo_generate._generate_with_muapi(
                "logo prompt", "logo.png", "1:1", "muapi-key", "unknown-model"
            )

    @patch.object(logo_generate, "build_opener")
    def test_muapi_uses_x_api_key_header(self, build_opener):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            @staticmethod
            def read():
                return b"{}"

        build_opener.return_value.open.return_value = Response()

        logo_generate._json_request(
            "https://api.muapi.ai/api/v1/nano-banana",
            "muapi-key",
            method="POST",
            payload={"prompt": "logo"},
            api_key_header="x-api-key",
        )

        request = build_opener.return_value.open.call_args.args[0]
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(headers["x-api-key"], "muapi-key")
        self.assertNotIn("authorization", headers)

    @patch.object(logo_generate, "_json_request")
    def test_muapi_reports_failed_prediction(self, json_request):
        json_request.side_effect = [
            {
                "request_id": "req-123",
                "output": {
                    "urls": {
                        "get": "https://api.muapi.ai/api/v1/results/req-123"
                    }
                },
            },
            {"status": "failed", "error": "invalid prompt"},
        ]

        with self.assertRaisesRegex(RuntimeError, "invalid prompt"):
            logo_generate._generate_with_muapi(
                "logo prompt", "logo.png", "1:1", "muapi-key", "nano-banana"
            )

    @patch.object(logo_generate, "_json_request")
    def test_muapi_requires_creation_result_url(self, json_request):
        json_request.return_value = {"request_id": "req-123", "status": "created"}

        with self.assertRaisesRegex(RuntimeError, "valid HTTPS result URL"):
            logo_generate._generate_with_muapi(
                "logo prompt", "logo.png", "1:1", "muapi-key", "nano-banana"
            )

        json_request.assert_called_once()

    @patch.object(logo_generate, "_json_request")
    def test_muapi_rejects_invalid_creation_result_url(self, json_request):
        json_request.return_value = {
            "request_id": "req-123",
            "status": "created",
            "output": {"urls": {"get": "http://api.muapi.ai/results/req-123"}},
        }

        with self.assertRaisesRegex(RuntimeError, "valid HTTPS result URL"):
            logo_generate._generate_with_muapi(
                "logo prompt", "logo.png", "1:1", "muapi-key", "nano-banana"
            )

        json_request.assert_called_once()


class UberllmGenerationTests(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.dir = Path(temp_dir.name)

    @staticmethod
    def _answer(data):
        return {"data": [{"b64_json": base64.b64encode(data).decode("ascii")}]}

    @patch.object(logo_generate, "_json_request")
    def test_uberllm_posts_once_and_saves_the_returned_image(self, json_request):
        json_request.return_value = self._answer(PNG)
        output = str(self.dir / "logo.png")

        saved = logo_generate._generate_with_uberllm(
            "logo prompt", output, "1:1", "uberllm-key", "vendor/model"
        )

        json_request.assert_called_once_with(
            f"{logo_generate.UBERLLM_API_BASE}/images/generations",
            "uberllm-key",
            method="POST",
            payload={
                "model": "vendor/model",
                "prompt": "logo prompt",
                "n": 1,
                "aspect_ratio": "1:1",
                "response_format": "b64_json",
            },
        )
        self.assertEqual(saved, output)
        self.assertEqual(Path(saved).read_bytes(), PNG)

    @patch.object(logo_generate, "_json_request")
    def test_uberllm_uses_the_extension_of_the_returned_type(self, json_request):
        json_request.return_value = self._answer(JPEG)

        with patch("sys.stdout", new_callable=io.StringIO):
            saved = logo_generate._generate_with_uberllm(
                "logo prompt", str(self.dir / "logo.png"), "1:1", "k", "m"
            )

        self.assertEqual(saved, str(self.dir / "logo.jpg"))
        self.assertFalse((self.dir / "logo.png").exists())

    @patch.object(logo_generate, "_json_request")
    def test_uberllm_rejects_missing_or_non_image_data(self, json_request):
        for answer, message in (
            ({"data": []}, "did not return an image"),
            ({"data": [{"b64_json": "not base64!"}]}, "invalid image data"),
            (self._answer(b"<html>"), "not a PNG, JPEG or WebP"),
        ):
            with self.subTest(message=message):
                json_request.return_value = answer
                with self.assertRaisesRegex(RuntimeError, message):
                    logo_generate._generate_with_uberllm(
                        "logo prompt", str(self.dir / "logo.png"), "1:1", "k", "m"
                    )
        self.assertEqual(list(self.dir.iterdir()), [])

    def test_uberllm_requires_api_key(self):
        with self.assertRaisesRegex(RuntimeError, "UBERLLM_API_KEY not set"):
            logo_generate._generate_with_uberllm(
                "logo prompt", "logo.png", "1:1", None, "vendor/model"
            )


class GeminiImageTypeTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        for patcher in (
            patch.dict(sys.modules, _fake_genai(self.client)),
            patch.object(logo_generate, "GEMINI_API_KEY", "test-key"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.dir = Path(temp_dir.name)

    def _generate(self, mime_type, data, requested_name):
        self.client.models.generate_content.return_value = _image_response(
            mime_type, data
        )
        return logo_generate._generate_with_gemini(
            "logo prompt", str(self.dir / requested_name), "1:1", use_pro=True
        )

    def test_jpeg_is_saved_with_jpg_extension(self):
        with patch("sys.stdout", new_callable=io.StringIO):
            saved = self._generate("image/jpeg", JPEG, "logo.png")

        self.assertEqual(saved, str(self.dir / "logo.jpg"))
        self.assertEqual(Path(saved).read_bytes(), JPEG)
        self.assertFalse((self.dir / "logo.png").exists())

    def test_matching_extension_keeps_requested_path(self):
        for mime_type, data, name in (
            ("image/png", PNG, "logo.png"),
            ("image/jpeg", JPEG, "logo.jpeg"),
            ("image/jpeg", JPEG, "logo.JPG"),
        ):
            with self.subTest(name=name):
                saved = self._generate(mime_type, data, name)
                self.assertEqual(saved, str(self.dir / name))
                self.assertEqual(Path(saved).read_bytes(), data)

    def test_unknown_image_type_keeps_requested_path(self):
        self.assertEqual(
            logo_generate._path_for_image_type("logo.png", "image/heic"), "logo.png"
        )

    def test_generate_logo_prints_and_returns_the_saved_path(self):
        self.client.models.generate_content.return_value = _image_response(
            "image/jpeg", JPEG
        )
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            saved = logo_generate.generate_logo(
                "test mark", output_path=str(self.dir / "logo.png"), use_pro=True
            )

        self.assertEqual(saved, str(self.dir / "logo.jpg"))
        self.assertIn(f"Logo saved to: {saved}", stdout.getvalue())

    def test_pro_requests_the_configured_pro_model(self):
        self._generate("image/png", PNG, "logo.png")

        self.assertEqual(
            self.client.models.generate_content.call_args.kwargs["model"],
            logo_generate.GEMINI_PRO,
        )


class GeminiModelIdTests(unittest.TestCase):
    def test_pro_defaults_to_the_ga_model(self):
        with patch.dict(os.environ):
            os.environ.pop("GEMINI_PRO_IMAGE_MODEL", None)
            module = _load_module()

        self.assertEqual(module.GEMINI_PRO, "gemini-3-pro-image")

    def test_model_ids_can_be_overridden_from_the_environment(self):
        with patch.dict(
            os.environ,
            {"GEMINI_FLASH_IMAGE_MODEL": "flash-next", "GEMINI_PRO_IMAGE_MODEL": "pro-next"},
        ):
            module = _load_module()

        self.assertEqual(module.GEMINI_FLASH, "flash-next")
        self.assertEqual(module.GEMINI_PRO, "pro-next")


class ExitStatusTests(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.dir = Path(temp_dir.name)

    def _run_main(self, *args):
        with patch.object(sys, "argv", ["generate.py", *args]), patch(
            "sys.stdout", new_callable=io.StringIO
        ):
            logo_generate.main()

    def test_failed_single_request_exits_1(self):
        client = Mock()
        client.models.generate_content.side_effect = RuntimeError(
            "429 RESOURCE_EXHAUSTED"
        )
        with patch.dict(sys.modules, _fake_genai(client)), patch.object(
            logo_generate, "GEMINI_API_KEY", "test-key"
        ), self.assertRaises(SystemExit) as raised:
            self._run_main("--prompt", "test mark", "--output", str(self.dir / "logo.png"))

        self.assertEqual(raised.exception.code, 1)

    @patch.object(logo_generate.time, "sleep")
    @patch.object(logo_generate, "generate_logo", return_value=None)
    def test_batch_with_no_logos_exits_1(self, generate_logo, sleep):
        with self.assertRaises(SystemExit) as raised:
            self._run_main(
                "--brand", "Demo", "--batch", "2", "--output-dir", str(self.dir)
            )

        self.assertEqual(raised.exception.code, 1)
        self.assertEqual(generate_logo.call_count, 2)

    @patch.object(logo_generate.time, "sleep")
    @patch.object(
        logo_generate, "generate_logo", side_effect=[None, "demo_modern_02.png"]
    )
    def test_partial_batch_exits_0(self, generate_logo, sleep):
        self._run_main("--brand", "Demo", "--batch", "2", "--output-dir", str(self.dir))

        self.assertEqual(generate_logo.call_count, 2)

    def test_list_styles_exits_0(self):
        self._run_main("--list-styles")


if __name__ == "__main__":
    unittest.main()
