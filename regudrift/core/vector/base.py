from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel, Field

from regudrift.core.ingestion.parser import DocumentChunk


class SearchResult(BaseModel):
    """
    Standardized payload wrapping a matched document chunk and its relevance score.
    """
    chunk: DocumentChunk = Field(..., description="The matched document segment.")
    score: float = Field(..., description="Retrieval similarity distance (e.g., Cosine/L2).")


class BaseVectorService(ABC):
    """
    Abstract Base Class establishing standard async contracts for retrieval backends.
    Allows transparent runtime swapping between FAISS and Qdrant clusters.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """
        Performs startup checks, opens connection pools, or ensures collections/indices
        are active and prepped.
        """
        pass

    @abstractmethod
    async def add_documents(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        Indexes a series of processed document chunks along with their corresponding 
        vector embeddings.
        
        Args:
            chunks: List of structured DocumentChunk entities.
            embeddings: Parallel matrix of floating-point embeddings (dimensions must match configuration).
            
        Returns:
            A list of successfully indexed deterministic chunk IDs.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Performs a vector search to locate the nearest neighbors to a query embedding.
        
        Args:
            query_vector: Embedding representing the search query.
            limit: Maximum count of matches to return.
            
        Returns:
            A sorted list of SearchResult models containing matching chunks and scores.
        """
        pass

    @abstractmethod
    async def delete_documents(self, chunk_ids: List[str]) -> None:
        """
        Permanently expunges matching document chunks from the retrieval index by ID.
        
        Args:
            chunk_ids: List of SHA-256 chunk IDs to remove.
        """
        pass
class VectorServiceError(Exception):
    """Base exception for all vector database retrieval or ingestion issues."""
    pass
