import asyncio
import json
import os
from typing import Dict, List, Optional
import numpy as np

# Try to import faiss safely, fallback to manual mock index if unavailable
try:
    import faiss
except ImportError:
    faiss = None

from regudrift.config.settings import settings
from regudrift.core.ingestion.parser import DocumentChunk
from regudrift.core.vector.base import BaseVectorService, SearchResult, VectorServiceError


class LocalFAISSService(BaseVectorService):
    """
    Local testing vector database utilizing FAISS (CPU edition).
    Performs fully thread-offloaded Cosine/Dot Product similarity indexing.
    Serializes index state and parallel chunk metadata mapping to disk.
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
        
        # In-memory storage
        self.index: Optional[Any] = None
        self.chunks_map: Dict[str, DocumentChunk] = {}  # Map: str(id_int) -> DocumentChunk
        self.id_to_hash_map: Dict[int, str] = {}        # Map: id_int -> chunk_hash_sha256
        self.hash_to_id_map: Dict[str, int] = {}        # Map: chunk_hash_sha256 -> id_int
        self.current_id = 0
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Loads the FAISS index from disk if it exists, otherwise creates a fresh one.
        Offloads all I/O and index allocation to threads.
        """
        if faiss is None:
            raise VectorServiceError(
                "FAISS library is not installed. Please install faiss-cpu to use LocalFAISSService."
            )

        async with self._lock:
            await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        """Synchronous part of initialization running in a thread."""
        os.makedirs(self.index_dir, exist_ok=True)

        if os.path.exists(self.index_file) and os.path.exists(self.chunks_file):
            try:
                # Load FAISS index binary
                raw_index = faiss.read_index(self.index_file)
                # Wrap it inside an IDMap if not already to support removal of IDs
                if not isinstance(raw_index, faiss.IndexIDMap):
                    self.index = faiss.IndexIDMap(raw_index)
                else:
                    self.index = raw_index

                # Load parallel chunk metadata dictionary
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
                # Fallback to fresh instantiation if file is corrupted
                self._create_fresh_index()
        else:
            self._create_fresh_index()

    def _create_fresh_index(self) -> None:
        """Instantiates a new FAISS Inner Product Index with ID Map mapping."""
        # IndexFlatIP handles cosine similarity when vectors are L2-normalized
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
        """
        L2-normalizes embeddings and adds them deterministic-mapped to the FAISS index.
        Saves changes to disk immediately. Runs offloaded to worker threads.
        """
        if not chunks or not embeddings:
            return []

        if len(chunks) != len(embeddings):
            raise VectorServiceError("Chunks and embeddings lists must be of identical length.")

        async with self._lock:
            added_ids = await asyncio.to_thread(self._add_documents_sync, chunks, embeddings)
            return added_ids

    def _add_documents_sync(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Synchronous execution of document insertion and index serialization."""
        vector_matrix = np.array(embeddings, dtype=np.float32)
        
        # Apply L2-normalization for Cosine similarity search compatibility
        faiss.normalize_L2(vector_matrix)
        
        ids_to_add = []
        added_hashes = []

        for idx, chunk in enumerate(chunks):
            # Check if this chunk is already indexed to ensure idempotency
            if chunk.id in self.hash_to_id_map:
                # Retrieve existing ID to overwrite
                target_id = self.hash_to_id_map[chunk.id]
                # FAISS remove_ids takes an array
                self.index.remove_ids(np.array([target_id], dtype=np.int64))
            else:
                target_id = self.current_id
                self.current_id += 1
            
            ids_to_add.append(target_id)
            self.chunks_map[str(target_id)] = chunk
            self.id_to_hash_map[target_id] = chunk.id
            self.hash_to_id_map[chunk.id] = target_id
            added_hashes.append(chunk.id)

        # Ingest to FAISS index with explicit mapped IDs
        ids_vector = np.array(ids_to_add, dtype=np.int64)
        self.index.add_with_ids(vector_matrix, ids_vector)

        # Serialize modifications to storage immediately
        self._save_to_disk_sync()
        return added_hashes

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Executes an offloaded similarity search against the local FAISS index.
        """
        async with self._lock:
            # Prevent empty search calls on uninitialized index
            if self.index is None or self.index.ntotal == 0:
                return []
            
            results = await asyncio.to_thread(self._search_sync, query_vector, limit)
            return results

    def _search_sync(self, query_vector: List[float], limit: int) -> List[SearchResult]:
        """Synchronous CPU FAISS search query offloaded to thread."""
        query_matrix = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(query_matrix)
        
        # Perform K-Nearest Neighbors search
        # D: distances (cosine similarity score), I: matched integer IDs
        D, I = self.index.search(query_matrix, limit)
        
        search_results = []
        # Parse output buffers
        for score, int_id in zip(D[0], I[0]):
            if int_id == -1:
                continue  # Out of matches
                
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
        """
        Removes documents by chunk hashes from the index and serializes state changes.
        """
        async with self._lock:
            if self.index is None or not chunk_ids:
                return
                
            await asyncio.to_thread(self._delete_documents_sync, chunk_ids)

    def _delete_documents_sync(self, chunk_ids: List[str]) -> None:
        """Synchronously filters and purges matching indices."""
        ids_to_purge = []
        for hash_id in chunk_ids:
            if hash_id in self.hash_to_id_map:
                target_id = self.hash_to_id_map[hash_id]
                ids_to_purge.append(target_id)
                
                # Clear references in maps
                del self.chunks_map[str(target_id)]
                del self.id_to_hash_map[target_id]
                del self.hash_to_id_map[hash_id]

        if ids_to_purge:
            purge_vector = np.array(ids_to_purge, dtype=np.int64)
            self.index.remove_ids(purge_vector)
            self._save_to_disk_sync()

    def _save_to_disk_sync(self) -> None:
        """Synchronously serializes index structures and hash mappings to disk."""
        faiss.write_index(self.index, self.index_file)
        
        # Export dictionaries containing DocumentChunk model exports
        payload = {
            "chunks_map": {k: v.model_dump() for k, v in self.chunks_map.items()},
            "id_to_hash_map": {str(k): v for k, v in self.id_to_hash_map.items()},
            "hash_to_id_map": self.hash_to_id_map,
            "current_id": self.current_id
        }
        with open(self.chunks_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
