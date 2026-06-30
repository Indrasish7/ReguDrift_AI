import asyncio
import io
import re
from typing import Any, BinaryIO, Dict, List, Optional
from pydantic import BaseModel, Field

# Try to import pypdf safely, fallback to manual parsing if unavailable
try:
    import pypdf
except ImportError:
    pypdf = None

from regudrift.core.utils.crypto import generate_chunk_hash


class DocumentChunk(BaseModel):
    """
    Schema representing an individual, semantically rich segment of a document.
    """
    id: str = Field(..., description="Deterministic SHA-256 chunk hash.")
    content: str = Field(..., description="The raw textual content of the chunk.")
    document_id: str = Field(..., description="Foreign key reference to the parent document.")
    chunk_index: int = Field(..., description="Sequence index of the chunk in the document.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Enriched metadata including parent hierarchy (Chapter/Section/Clause) and page references."
    )


class ParsedDocument(BaseModel):
    """
    Enriched, parsed schema of an entire document containing structured sub-chunks.
    """
    document_id: str = Field(..., description="Unique document ID (e.g., UUID or filename-based).")
    filename: str = Field(..., description="Original name of the ingested file.")
    chunks: List[DocumentChunk] = Field(..., description="List of generated document chunks.")


class LegalHierarchyState:
    """
    Tracks the active hierarchical state (Chapter, Section, Article, Clause) 
    as we traverse a legal or regulatory document.
    """
    def __init__(self):
        self.chapter: Optional[str] = None
        self.section: Optional[str] = None
        self.article: Optional[str] = None
        self.clause: Optional[str] = None

    def update(self, line: str) -> bool:
        """
        Scans a line for legal structural headers and updates active hierarchy.
        Returns True if a header was found and updated, False otherwise.
        """
        stripped = line.strip()
        
        # Regex patterns for matching regulatory structures
        # 1. Chapter (e.g., "CHAPTER II: REGULATORY OVERSIGHT" or "Chap 3")
        chapter_match = re.match(
            r"^\s*(?:CHAPTER|CHAP\.|CH\.)\s+([A-Z0-9]+)[\s:.-]+(.*)$", 
            stripped, 
            re.IGNORECASE
        )
        if chapter_match:
            self.chapter = f"Chapter {chapter_match.group(1)}: {chapter_match.group(2).strip()}"
            self.section = None
            self.article = None
            self.clause = None
            return True

        # 2. Section (e.g., "Section 4.2 - Data Privacy Boundaries" or "Sec. 1.1")
        section_match = re.match(
            r"^\s*(?:SECTION|SEC\.)\s+(\d+(?:\.\d+)*)[\s:.-]+(.*)$", 
            stripped, 
            re.IGNORECASE
        )
        if section_match:
            self.section = f"Section {section_match.group(1)}: {section_match.group(2).strip()}"
            self.article = None
            self.clause = None
            return True

        # 3. Article (e.g., "Article 12: Idempotency Requirements" or "Art. 4")
        article_match = re.match(
            r"^\s*(?:ARTICLE|ART\.)\s+(\d+|[A-Z0-9]+)[\s:.-]+(.*)$", 
            stripped, 
            re.IGNORECASE
        )
        if article_match:
            self.article = f"Article {article_match.group(1)}: {article_match.group(2).strip()}"
            self.clause = None
            return True

        # 4. Clause/Sub-section (e.g., "(a) Any provider must..." or "2.3.a")
        clause_match = re.match(
            r"^\s*\(([a-z]|\d+)\)\s+(.*)$", 
            stripped
        )
        if clause_match:
            self.clause = f"Clause ({clause_match.group(1)})"
            return True

        return False

    def get_path_string(self) -> str:
        """
        Compiles the hierarchy track into a unified path string.
        """
        parts = []
        if self.chapter:
            parts.append(self.chapter)
        if self.section:
            parts.append(self.section)
        if self.article:
            parts.append(self.article)
        if self.clause:
            parts.append(self.clause)
        
        return " > ".join(parts) if parts else "Root"


class RegulatoryClauseChunker:
    """
    Sliding-window text chunker built explicitly for structured regulatory texts.
    Maintains hierarchical state tracking to inject full legal context to all chunks.
    """
    def __init__(
        self,
        max_chunk_words: int = 250,
        overlap_words: int = 50
    ):
        self.max_chunk_words = max_chunk_words
        self.overlap_words = overlap_words

    def chunk_document(self, text: str, document_id: str) -> List[DocumentChunk]:
        """
        Splits the regulatory text into overlapping windows, constantly updating
        and attaching the active Chapter/Section hierarchy.
        """
        lines = text.split("\n")
        hierarchy = LegalHierarchyState()
        
        # We will parse the text into logical blocks (each block has a hierarchy state)
        blocks: List[Dict[str, Any]] = []
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            hierarchy.update(line_str)
            blocks.append({
                "text": line_str,
                "hierarchy": hierarchy.get_path_string(),
                "chapter": hierarchy.chapter,
                "section": hierarchy.section,
                "article": hierarchy.article,
                "clause": hierarchy.clause,
            })

        chunks: List[DocumentChunk] = []
        chunk_idx = 0
        
        # Apply sliding window logic across the blocks
        i = 0
        while i < len(blocks):
            current_window: List[Dict[str, Any]] = []
            word_count = 0
            
            # Form a window of blocks
            j = i
            while j < len(blocks) and word_count < self.max_chunk_words:
                block = blocks[j]
                words = len(block["text"].split())
                word_count += words
                current_window.append(block)
                j += 1
            
            if not current_window:
                break
                
            # Synthesize chunk contents
            chunk_content = "\n".join([b["text"] for b in current_window])
            
            # The context is taken from the dominant or starting block hierarchy
            primary_block = current_window[0]
            metadata = {
                "parent_hierarchy": primary_block["hierarchy"],
                "chapter": primary_block["chapter"],
                "section": primary_block["section"],
                "article": primary_block["article"],
                "clause": primary_block["clause"],
            }
            
            # Calculate deterministic ID
            chunk_id = generate_chunk_hash(chunk_content, document_id, metadata)
            
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    content=chunk_content,
                    document_id=document_id,
                    chunk_index=chunk_idx,
                    metadata=metadata
                )
            )
            chunk_idx += 1
            
            # Advance index with overlap
            # Find how many blocks correspond to overlap_words
            overlap_count = 0
            overlap_word_sum = 0
            k = j - 1
            while k >= i and overlap_word_sum < self.overlap_words:
                overlap_word_sum += len(blocks[k]["text"].split())
                overlap_count += 1
                k -= 1
                
            # Prevent infinite loops in case of a single massive block
            step = max(1, (j - i) - overlap_count)
            i += step
            
        return chunks


def parse_txt_stream(stream: io.StringIO, document_id: str) -> str:
    """
    Synchronously extracts text from a standard TXT IO stream.
    """
    return stream.read()


def _parse_pdf_bytes_sync(pdf_bytes: bytes) -> str:
    """
    CPU-bound synchronous PDF text extraction.
    Uses pypdf for extraction, with raw-text regex scanning fallbacks.
    """
    text_buffer = []
    
    if pypdf is not None:
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # Enrich with inline page boundary markers
                    text_buffer.append(f"\n[Page {i + 1}]\n")
                    text_buffer.append(page_text)
            return "".join(text_buffer)
        except Exception as e:
            # Fallback below if library throws unexpected format errors
            pass

    # Basic layout fallback for unstructured PDF content
    # Decodes standard postscript-like chunks where legible
    clean_text = []
    for line in pdf_bytes.decode("utf-8", errors="ignore").split("\n"):
        cleaned = re.sub(r"[^\x20-\x7E]+", "", line).strip()
        if len(cleaned) > 10:
            clean_text.append(cleaned)
    return "\n".join(clean_text)


class DocumentParser:
    """
    Production-grade document parser. Feeds streaming binary or text buffers,
    offloads CPU-heavy actions to threads, and executes sliding-window legal chunking.
    """
    def __init__(self, max_chunk_words: int = 250, overlap_words: int = 50):
        self.chunker = RegulatoryClauseChunker(
            max_chunk_words=max_chunk_words,
            overlap_words=overlap_words
        )

    async def parse_pdf(self, pdf_stream: bytes, document_id: str, filename: str) -> ParsedDocument:
        """
        Asynchronously parses PDF file streams.
        Offloads the heavy PDF reading tasks to an executor thread to preserve event loop integrity.
        """
        # Run the CPU-bound PDF parser in a background thread
        raw_text = await asyncio.to_thread(_parse_pdf_bytes_sync, pdf_stream)
        
        # Segment using legal chunker
        chunks = self.chunker.chunk_document(raw_text, document_id)
        
        # Tag each chunk with metadata about page number if we injected inline markers
        active_page = 1
        for chunk in chunks:
            # Check if this chunk is located after a specific page marker
            page_markers = re.findall(r"\[Page (\d+)\]", chunk.content)
            if page_markers:
                active_page = int(page_markers[-1])
            chunk.metadata["page_number"] = active_page
            
        return ParsedDocument(
            document_id=document_id,
            filename=filename,
            chunks=chunks
        )

    async def parse_txt(self, text_content: str, document_id: str, filename: str) -> ParsedDocument:
        """
        Asynchronously parses raw text strings or TXT streams.
        """
        chunks = self.chunker.chunk_document(text_content, document_id)
        for chunk in chunks:
            chunk.metadata["page_number"] = 1  # Standard single-page document boundary
            
        return ParsedDocument(
            document_id=document_id,
            filename=filename,
            chunks=chunks
        )
