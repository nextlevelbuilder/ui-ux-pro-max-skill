import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch

MODULE_PATH = Path(__file__).parents[1] / "generate.py"
SPEC = importlib.util.spec_from_file_location("logo_generate", MODULE_PATH)
logo_generate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(logo_generate)


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


if __name__ == "__main__":
    unittest.main()
