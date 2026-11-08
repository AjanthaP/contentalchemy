from io import BytesIO

import requests
from PIL import Image

from src.agents.image_generator import StableDiffusionGenerator


def _png_bytes() -> bytes:
    image = Image.new("RGB", (1, 1))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return buffered.getvalue()


def test_hugging_face_generator_uses_supported_default_and_bearer_token(monkeypatch):
    generator = StableDiffusionGenerator("hf_test_token")
    response = requests.Response()
    response.status_code = 200
    response._content = _png_bytes()
    captured = {}

    def fake_post(url, *, headers, json):
        captured.update(url=url, headers=headers, payload=json)
        return response

    monkeypatch.setattr("src.agents.image_generator.requests.post", fake_post)

    result = generator.generate("A dog")

    assert generator.model == "stabilityai/stable-diffusion-3-medium-diffusers"
    assert captured["url"] == (
        "https://router.huggingface.co/hf-inference/models/"
        "stabilityai/stable-diffusion-3-medium-diffusers"
    )
    assert captured["headers"]["Authorization"] == "Bearer hf_test_token"
    assert result["success"] is True
    assert result["image_base64"]


def test_hugging_face_generator_includes_http_error_details(monkeypatch):
    generator = StableDiffusionGenerator("hf_test_token")
    response = requests.Response()
    response.status_code = 410
    response._content = b'{"error":"Model is not supported by this provider"}'
    response.url = generator.endpoint

    def fake_post(*args, **kwargs):
        return response

    monkeypatch.setattr("src.agents.image_generator.requests.post", fake_post)

    result = generator.generate("A dog")

    assert result["success"] is False
    assert "HTTP 410" in result["error"]
    assert "Model is not supported by this provider" in result["error"]
