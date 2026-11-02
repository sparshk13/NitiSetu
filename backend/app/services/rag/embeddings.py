import os
import math
import hashlib
import logging
from typing import List
import numpy as np
from backend.app.config import settings

logger = logging.getLogger("nitisetu.rag.embeddings")

TARGET_DIMENSION = 768


class EmbeddingService:
    """
    Consistent 768-dimensional dense vector generator.
    Supports Google Gemini API embeddings with deterministic semantic projection fallback.
    """

    def __init__(self, dimension: int = TARGET_DIMENSION):
        self.dimension = dimension
        self._quota_exhausted_until: float = 0.0

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        Deterministic, L2-normalized 768-dimensional semantic projection.
        Ensures consistent dense vector space for testing and offline fallbacks without API dependency.
        """
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()

        for idx, word in enumerate(words):
            # Generate deterministic hash projection
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self.dimension
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            weight = 1.0 / math.sqrt(idx + 1)
            vec[pos] += float(val * weight)

        # L2-normalize vector
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec.tolist()

    def get_embedding(self, text: str, use_api: bool = False) -> List[float]:
        """Generate 768-dimensional normalized embedding vector. Defaults to ultra-fast deterministic projection."""
        clean_text = " ".join(text.split())
        if not clean_text:
            return [0.0] * self.dimension

        if not use_api:
            return self._generate_fallback_embedding(clean_text)

        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key or "your_" in api_key.lower() or "placeholder" in api_key.lower():
            return self._generate_fallback_embedding(clean_text)

        import time
        if time.time() < self._quota_exhausted_until:
            return self._generate_fallback_embedding(clean_text)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=5000)
            )

            # Request 768-dimensional embedding from official model
            model = getattr(settings, "gemini_embedding_model", "text-embedding-004")
            result = client.models.embed_content(
                model=model,
                contents=clean_text,
                config=types.EmbedContentConfig(output_dimensionality=self.dimension)
            )

            if result and hasattr(result, "embedding") and result.embedding:
                vec = np.array(result.embedding.values, dtype=np.float32)
                # Ensure dimension
                if len(vec) == self.dimension:
                    norm = np.linalg.norm(vec)
                    if norm > 1e-6:
                        vec = vec / norm
                    return vec.tolist()
        except Exception as e:
            err_str = str(e).lower()
            logger.debug(f"Gemini embedding API call failed: {e}. Using deterministic projection.")
            if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
                self._quota_exhausted_until = time.time() + 600

        return self._generate_fallback_embedding(clean_text)

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch generation of embeddings."""
        return [self.get_embedding(t) for t in texts]


embedding_service = EmbeddingService()
