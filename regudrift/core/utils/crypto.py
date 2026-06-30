import hashlib
import json
import re
from typing import Any, Dict, Optional


def normalize_text(text: str) -> str:
    """
    Standardizes whitespace, strips trailing spaces, and lowercase-converts text 
    to make hash calculations highly resilient to minor layout drifts.
    """
    # Replace multiple spaces/newlines/tabs with a single space
    cleaned = re.sub(r"\s+", " ", text)
    return cleaned.strip().lower()


def generate_chunk_hash(
    content: str,
    document_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a deterministic SHA-256 hash acting as an idempotent identifier 
    for document chunks.
    
    Args:
        content: The text segment of the chunk.
        document_id: The unique identifier of the parent document.
        metadata: Optional hierarchical info (e.g. Chapter, Section) to anchor the hash.
        
    Returns:
        A deterministic hexadecimal SHA-256 hash string.
    """
    normalized_content = normalize_text(content)
    
    # Construct standard deterministic payload
    payload = {
        "content_hash": hashlib.sha256(normalized_content.encode("utf-8")).hexdigest(),
        "document_id": document_id
    }
    
    # Deteminisitically incorporate metadata keys if provided
    if metadata:
        # Standardize keys by sorting them to preserve hash stability
        sorted_meta = {k: metadata[k] for k in sorted(metadata.keys()) if metadata[k] is not None}
        payload["metadata"] = sorted_meta
        
    # Serialize to deterministic JSON string
    serialized_payload = json.dumps(payload, sort_keys=True)
    
    # Calculate final SHA-256
    return hashlib.sha256(serialized_payload.encode("utf-8")).hexdigest()
