import asyncio
import uuid
from typing import List, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from regudrift.config.settings import settings
from regudrift.core.ingestion.parser import DocumentChunk
from regudrift.core.vector.base import BaseVectorService, SearchResult, VectorServiceError


class QdrantVectorService(BaseVectorService):
    """
    Production-scale Qdrant vector database retrieval provider.
    Establishes native async communication using AsyncQdrantClient.
    Saves document content alongside hierarchical metadata to support exact lookups.
    """

    def __init__(
        self,
        collection_name: str = settings.DEFAULT_COLLECTION_NAME,
        dimension: int = settings.EMBEDDING_DIMENSION
    ):
        self.collection_name = collection_name
        self.dimension = dimension
        
        # Instantiate AsyncQdrantClient pulling parameters strictly from settings
        api_key_str = (
            settings.QDRANT_API_KEY.get_secret_value()
            if settings.QDRANT_API_KEY
            else None
        )
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=api_key_str
        )

    def _hash_to_uuid(self, chunk_id_hash: str) -> str:
        """
        Deterministically converts a SHA-256 chunk hash into a valid UUIDv5 string 
        to comply with Qdrant's point identifier specifications.
        """
        # Namespace DNS serves as an arbitrary stable namespace
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id_hash))

    async def initialize(self) -> None:
        """
        Ensures target Qdrant collection is configured and active.
        Creates it if it does not already exist on the target cluster.
        """
        try:
            collections_response = await self.client.get_collections()
            collection_names = [col.name for col in collections_response.collections]
            
            if self.collection_name not in collection_names:
                # Cosine distance yields optimal results for legal text matching
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            raise VectorServiceError(
                f"Failed to initialize Qdrant collection '{self.collection_name}': {e}"
            ) from e

    async def add_documents(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        Upserts structured documents and vectors asynchronously to the Qdrant cluster.
        Injects the complete hierarchy metadata to enable precise filtered retrieval.
        """
        if not chunks or not embeddings:
            return []

        if len(chunks) != len(embeddings):
            raise VectorServiceError("Chunks and embeddings lists must be of identical length.")

        points = []
        added_hashes = []

        for chunk, embedding in zip(chunks, embeddings):
            # Create a deterministic UUID matching the SHA-256 hash
            point_uuid = self._hash_to_uuid(chunk.id)
            
            # Map standard payload and inject exact hierarchical keys
            payload = {
                "chunk_id": chunk.id,
                "content": chunk.content,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "parent_hierarchy": chunk.metadata.get("parent_hierarchy"),
                "chapter": chunk.metadata.get("chapter"),
                "section": chunk.metadata.get("section"),
                "article": chunk.metadata.get("article"),
                "clause": chunk.metadata.get("clause"),
                "page_number": chunk.metadata.get("page_number", 1)
            }
            
            points.append(
                PointStruct(
                    id=point_uuid,
                    vector=embedding,
                    payload=payload
                )
            )
            added_hashes.append(chunk.id)

        try:
            # Perform atomic async upsert
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return added_hashes
        except Exception as e:
            raise VectorServiceError(
                f"Failed to upsert points into Qdrant collection '{self.collection_name}': {e}"
            ) from e

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Performs a cosine similarity search against Qdrant, yielding SearchResult models.
        """
        try:
            scored_points = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            results = []
            for point in scored_points:
                payload = point.payload
                if not payload:
                    continue
                    
                # Reconstruct metadata dict
                metadata = {
                    "parent_hierarchy": payload.get("parent_hierarchy"),
                    "chapter": payload.get("chapter"),
                    "section": payload.get("section"),
                    "article": payload.get("article"),
                    "clause": payload.get("clause"),
                    "page_number": payload.get("page_number", 1)
                }
                
                # Reconstruct the original DocumentChunk object from payload
                chunk = DocumentChunk(
                    id=payload.get("chunk_id"),
                    content=payload.get("content"),
                    document_id=payload.get("document_id"),
                    chunk_index=payload.get("chunk_index"),
                    metadata=metadata
                )
                
                results.append(
                    SearchResult(
                        chunk=chunk,
                        score=float(point.score)
                    )
                )
            return results
        except Exception as e:
            raise VectorServiceError(
                f"Failed to search Qdrant collection '{self.collection_name}': {e}"
            ) from e

    async def delete_documents(self, chunk_ids: List[str]) -> None:
        """
        Removes points from the Qdrant collection asynchronously.
        """
        if not chunk_ids:
            return

        try:
            # Map SHA-256 hashes back to deterministic UUID point IDs
            point_uuids = [self._hash_to_uuid(cid) for cid in chunk_ids]
            
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_uuids
            )
        except Exception as e:
            raise VectorServiceError(
                f"Failed to delete points from Qdrant collection '{self.collection_name}': {e}"
            ) from e
