import numpy as np
import requests

from core import settings


class EmbeddingClient:
    def __init__(self, timeout=60):
        self.timeout = timeout

    def health(self) -> dict:
        response = requests.get(settings.EMBEDDING_URL_HEALTH, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def embed(self, texts: list[str]) -> np.ndarray:
        response = requests.post(
            settings.EMBEDDING_URL_EMBED,
            json={"inputs": texts},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return np.asarray(data["embeddings"], dtype="float32")
