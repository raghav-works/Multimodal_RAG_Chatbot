import base64
import io

from PIL import Image
import requests


OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_VISION_MODEL = "llava:latest"
MAX_IMAGE_SIZE = (1024, 1024)
OLLAMA_TIMEOUT = 300


def _prepare_image(image_bytes: bytes) -> str:
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail(MAX_IMAGE_SIZE)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")


def answer_image_question(image_bytes: bytes, question: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": DEFAULT_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": question,
                "images": [_prepare_image(image_bytes)],
            }
        ],
        "stream": False,
    }
    response = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")
    data = response.json()
    return data.get("message", {}).get("content", "").strip()
