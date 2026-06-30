import asyncio
from typing import List
from google import genai
from pydantic import BaseModel, Field

from regudrift.config.settings import settings


class AsyncEmbeddingGenerator:
    """
    Asynchronous utility executing text embedding generation via the Google GenAI SDK.
    Integrates connection configurations, explicit type checking, and concurrent batching.
    """

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL,
        batch_size: int = 100,
        max_concurrent_requests: int = 5
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # Initialize the modern GenAI Client utilizing settings' SecretStr securely
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY.get_secret_value()
        )

    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Sends a single batch of texts to the Gemini embedding engine asynchronously,
        wrapped with concurrency limits.
        """
        if not texts:
            return []

        async with self.semaphore:
            try:
                # Use client.aio for high-performance non-blocking async network I/O
                response = await self.client.aio.models.embed_content(
                    model=self.model_name,
                    contents=texts
                )
                
                # Extract float list vectors from GenAI response
                embeddings = []
                for emb in response.embeddings:
                    embeddings.append(emb.values)
                return embeddings
            except Exception as e:
                raise RuntimeError(
                    f"Gemini API Embedding generation failed for batch of size {len(texts)}: {e}"
                ) from e

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Processes a large list of text inputs, slicing them into standardized batches,
        resolving them concurrently under rate limit controls, and returning a unified matrix.
        
        Args:
            texts: List of normalized text payloads.
            
        Returns:
            A parallel list of embedding vectors (list of float lists, each with 768 dimensions).
        """
        if not texts:
            return []

        # Divide texts into chunks of size self.batch_size
        batches = [
            texts[i : i + self.batch_size]
            for i in range(0, len(texts), self.batch_size)
        ]
        
        # Execute all batches concurrently within our semaphore bounds
        tasks = [self._embed_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks)
        
        # Flatten the list of lists into a single linear matrix
        flat_embeddings = [emb for batch_result in results for emb in batch_result]
        return flat_embeddings
