import hashlib
import json
import math
import re
from abc import ABC, abstractmethod
from urllib import error, request

from app.core.config import get_settings


class EmbeddingProviderError(RuntimeError):
    pass


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 768) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1.0
        return _normalize(vector)


class LocalOllamaEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        settings = get_settings()
        payload = {
            "model": settings.ollama_embedding_model,
            "input": text,
        }
        try:
            data = _post_ollama_json(f"{settings.ollama_base_url.rstrip('/')}/api/embed", payload)
        except EmbeddingProviderError:
            data = _post_ollama_json(
                f"{settings.ollama_base_url.rstrip('/')}/api/embeddings",
                {"model": settings.ollama_embedding_model, "prompt": text},
            )

        embedding = data.get("embedding")
        if embedding is None and isinstance(data.get("embeddings"), list) and data["embeddings"]:
            embedding = data["embeddings"][0]
        if not isinstance(embedding, list):
            raise EmbeddingProviderError("Ollama embedding response did not include an embedding vector")
        return _normalize([float(value) for value in embedding])


class MistralEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        settings = get_settings()
        if settings.mistral_api_key is None:
            raise EmbeddingProviderError("MISTRAL_API_KEY is not configured")
        payload = {
            "model": "mistral-embed",
            "input": [text],
        }
        http_request = request.Request(
            "https://api.mistral.ai/v1/embeddings",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {settings.mistral_api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(http_request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, error.HTTPError, json.JSONDecodeError) as exc:
            raise EmbeddingProviderError(f"Mistral embeddings unavailable: {exc.__class__.__name__}") from exc

        values = data.get("data", [{}])[0].get("embedding")
        if not isinstance(values, list):
            raise EmbeddingProviderError("Mistral embedding response did not include an embedding vector")
        return _normalize([float(value) for value in values])


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions do not match")
    return sum(a * b for a, b in zip(left, right))


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector
    return [value / magnitude for value in vector]


def _post_ollama_json(url: str, payload: dict[str, str]) -> dict:
    http_request = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with request.urlopen(http_request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, error.HTTPError, json.JSONDecodeError) as exc:
        raise EmbeddingProviderError(f"Ollama embeddings unavailable: {exc.__class__.__name__}") from exc
    if not isinstance(data, dict):
        raise EmbeddingProviderError("Ollama embeddings returned non-object JSON")
    return data
