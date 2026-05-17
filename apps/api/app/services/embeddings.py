import hashlib
import math
import re
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 48) -> None:
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
        _ = text
        raise NotImplementedError("Ollama embeddings adapter will call local /api/embeddings in provider phase.")


class MistralEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        _ = text
        raise NotImplementedError("Mistral embeddings adapter requires server-only API key in provider phase.")


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions do not match")
    return sum(a * b for a, b in zip(left, right))


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector
    return [value / magnitude for value in vector]
