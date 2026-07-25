import asyncio
import json
import logging
import os
from typing import Dict, List, Optional
import numpy as np

from regudrift.config.settings import settings
from regudrift.core.ingestion.parser import DocumentChunk
from regudrift.core.vector.base import BaseVectorService, SearchResult, VectorServiceError

logger = logging.getLogger("regudrift.core.vector.faiss_service")

# Try to import faiss safely, fallback to pure python in-memory cosine engine if unavailable
try:
    import faiss
except Exception as e:
    logger.warning(f"FAISS import unavailable ({e}). Falling back to pure Python in-memory vector store.")
    faiss = None


class InMemoryVectorStore:
    """
    Lightweight, zero-dependency pure Python vector engine fallback.
    Performs cosine similarity search using numpy.
    Used seamlessly in serverless container environments where C++ FAISS binaries are omitted.
    """
    def __init__(self, dimension: int = settings.EMBEDDING_DIMENSION):
        self.dimension = dimension
        self.vectors: List[np.ndarray] = []
        self.ids: List[int] = []
        self.chunks_map: Dict[str, DocumentChunk] = {}
        self.id_to_hash_map: Dict[int, str] = {}
        self.hash_to_id_map: Dict[str, int] = {}
        self.current_id = 0

    def add_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> List[str]:
        added_hashes = []
        for chunk, emb in zip(chunks, embeddings):
            chunk_hash = chunk.chunk_hash
            vec = np.array(emb, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
                
            if chunk_hash in self.hash_to_id_map:
                existing_id = self.hash_to_id_map[chunk_hash]
                for idx, int_id in enumerate(self.ids):
                    if int_id == existing_id:
                        self.vectors[idx] = vec
                        break
                self.chunks_map[str(existing_id)] = chunk
            else:
                new_id = self.current_id
                self.current_id += 1
                self.ids.append(new_id)
                self.vectors.append(vec)
                self.chunks_map[str(new_id)] = chunk
                self.id_to_hash_map[new_id] = chunk_hash
                self.hash_to_id_map[chunk_hash] = new_id
            added_hashes.append(chunk_hash)
        return added_hashes

    def search(self, query_vector: List[float], limit: int) -> List[SearchResult]:
        if not self.vectors:
            return []
            
        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm
            
        matrix = np.array(self.vectors, dtype=np.float32)
        scores = np.dot(matrix, q_vec)
        
        top_indices = np.argsort(scores)[::-1][:limit]
        results = []
        for idx in top_indices:
            int_id = self.ids[idx]
            score = float(scores[idx])
            str_id = str(int_id)
            if str_id in self.chunks_map:
                results.append(SearchResult(chunk=self.chunks_map[str_id], score=score))
        return results

    def delete_documents(self, chunk_ids: List[str]) -> None:
        for chunk_hash in chunk_ids:
            if chunk_hash in self.hash_to_id_map:
                target_id = self.hash_to_id_map[chunk_hash]
                if target_id in self.ids:
                    idx = self.ids.index(target_id)
                    del self.ids[idx]
                    del self.vectors[idx]
                if str(target_id) in self.chunks_map:
                    del self.chunks_map[str(target_id)]
                if target_id in self.id_to_hash_map:
                    del self.id_to_hash_map[target_id]
                del self.hash_to_id_map[chunk_hash]


class LocalFAISSService(BaseVectorService):
    """
    Local vector database supporting both FAISS C++ indexing and a pure Python in-memory fallback.
    Serializes index state and parallel chunk metadata mapping to disk when possible.
    """

    def __init__(
        self,
        index_dir: str = settings.FAISS_INDEX_PATH,
        dimension: int = settings.EMBEDDING_DIMENSION
    ):
        self.index_dir = index_dir
        self.dimension = dimension
        
        # Files for serialization
        self.index_file = os.path.join(index_dir, "index.faiss")
        self.chunks_file = os.path.join(index_dir, "chunks.json")
        
        # Storage implementations
        self.use_fallback = (faiss is None)
        self.fallback_store = InMemoryVectorStore(dimension) if self.use_fallback else None
        
        self.index = None
        self.chunks_map: Dict[str, DocumentChunk] = {}
        self.id_to_hash_map: Dict[int, str] = {}
        self.hash_to_id_map: Dict[str, int] = {}
        self.current_id = 0
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Initializes FAISS if available, or boots the in-memory fallback vector store.
        """
        async with self._lock:
            if self.use_fallback:
                logger.info("Operating in-memory vector retrieval mode.")
                return
                
            await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        """Synchronous part of initialization running in a thread."""
        try:
            os.makedirs(self.index_dir, exist_ok=True)

            if os.path.exists(self.index_file) and os.path.exists(self.chunks_file):
                try:
                    raw_index = faiss.read_index(self.index_file)
                    if not isinstance(raw_index, faiss.IndexIDMap):
                        self.index = faiss.IndexIDMap(raw_index)
                    else:
                        self.index = raw_index

                    with open(self.chunks_file, "r", encoding="utf-8") as f:
                        serialized_data = json.load(f)
                        
                    self.chunks_map = {
                        k: DocumentChunk(**v) for k, v in serialized_data.get("chunks_map", {}).items()
                    }
                    self.id_to_hash_map = {
                        int(k): v for k, v in serialized_data.get("id_to_hash_map", {}).items()
                    }
                    self.hash_to_id_map = serialized_data.get("hash_to_id_map", {})
                    self.current_id = serialized_data.get("current_id", 0)
                except Exception as e:
                    logger.warning(f"Failed loading FAISS cache from disk: {e}. Creating fresh index.")
                    self._create_fresh_index()
            else:
                self._create_fresh_index()
        except Exception as e:
            logger.warning(f"FAISS initialization error: {e}. Switching to in-memory fallback store.")
            self.use_fallback = True
            self.fallback_store = InMemoryVectorStore(self.dimension)

    def _create_fresh_index(self) -> None:
        """Instantiates a new FAISS Inner Product Index with ID Map mapping."""
        flat_index = faiss.IndexFlatIP(self.dimension)
        self.index = faiss.IndexIDMap(flat_index)
        self.chunks_map = {}
        self.id_to_hash_map = {}
        self.hash_to_id_map = {}
        self.current_id = 0

    async def add_documents(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ) -> List[str]:
        if not chunks or not embeddings:
            return []

        async with self._lock:
            if self.use_fallback or self.index is None:
                return self.fallback_store.add_documents(chunks, embeddings)
                
            return await asyncio.to_thread(self._add_documents_sync, chunks, embeddings)

    def _add_documents_sync(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ) -> List[str]:
        matrix = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(matrix)
        
        assigned_ids = []
        added_hashes = []
        
        for idx, chunk in enumerate(chunks):
            chunk_hash = chunk.chunk_hash
            
            if chunk_hash in self.hash_to_id_map:
                existing_id = self.hash_to_id_map[chunk_hash]
                target_id = existing_id
                self.index.remove_ids(np.array([target_id], dtype=np.int64))
            else:
                target_id = self.current_id
                self.current_id += 1
                
            assigned_ids.append(target_id)
            added_hashes.append(chunk_hash)
            
            self.chunks_map[str(target_id)] = chunk
            self.id_to_hash_map[target_id] = chunk_hash
            self.hash_to_id_map[chunk_hash] = target_id

        ids_vector = np.array(assigned_ids, dtype=np.int64)
        self.index.add_with_ids(matrix, ids_vector)
        
        try:
            self._save_to_disk_sync()
        except Exception as e:
            logger.warning(f"Could not persist FAISS index to disk: {e}")
            
        return added_hashes

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[SearchResult]:
        if not query_vector:
            return []

        async with self._lock:
            if self.use_fallback or self.index is None:
                return self.fallback_store.search(query_vector, limit)
                
            return await asyncio.to_thread(self._search_sync, query_vector, limit)

    def _search_sync(self, query_vector: List[float], limit: int) -> List[SearchResult]:
        query_matrix = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(query_matrix)
        
        D, I = self.index.search(query_matrix, limit)
        
        search_results = []
        for score, int_id in zip(D[0], I[0]):
            if int_id == -1:
                continue
                
            str_id = str(int_id)
            if str_id in self.chunks_map:
                search_results.append(
                    SearchResult(
                        chunk=self.chunks_map[str_id],
                        score=float(score)
                    )
                )
                
        return search_results

    async def delete_documents(self, chunk_ids: List[str]) -> None:
        async with self._lock:
            if self.use_fallback or self.index is None:
                self.fallback_store.delete_documents(chunk_ids)
                return
                
            if not chunk_ids:
                return
                
            await asyncio.to_thread(self._delete_documents_sync, chunk_ids)

    def _delete_documents_sync(self, chunk_ids: List[str]) -> None:
        ids_to_purge = []
        for hash_id in chunk_ids:
            if hash_id in self.hash_to_id_map:
                target_id = self.hash_to_id_map[hash_id]
                ids_to_purge.append(target_id)
                
                if str(target_id) in self.chunks_map:
                    del self.chunks_map[str(target_id)]
                if target_id in self.id_to_hash_map:
                    del self.id_to_hash_map[target_id]
                del self.hash_to_id_map[hash_id]

        if ids_to_purge:
            purge_vector = np.array(ids_to_purge, dtype=np.int64)
            self.index.remove_ids(purge_vector)
            try:
                self._save_to_disk_sync()
            except Exception as e:
                logger.warning(f"Could not save deleted state to disk: {e}")

    def _save_to_disk_sync(self) -> None:
        faiss.write_index(self.index, self.index_file)
        payload = {
            "chunks_map": {k: v.model_dump() for k, v in self.chunks_map.items()},
            "id_to_hash_map": {str(k): v for k, v in self.id_to_hash_map.items()},
            "hash_to_id_map": self.hash_to_id_map,
            "current_id": self.current_id
        }
        with open(self.chunks_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
