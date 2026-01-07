"""
Document ingestion service.

Orchestrates document processing and indexing using injected dependencies.
"""

from pathlib import Path

import structlog
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from langgraph_runner.ingestion.chunker import chunk_documents
from langgraph_runner.ingestion.protocols import DocumentProcessor

logger = structlog.stdlib.get_logger(__name__)

# Metadata fields to preserve in vector store.
# ChromaDB only accepts str, int, float, bool, or None values.
# Complex types (dicts, lists, numpy arrays) from PDF extraction are dropped.
ALLOWED_METADATA_FIELDS = frozenset({
    # Document identification
    "source",
    "filename",
    # Page/position tracking
    "page_number",
    "page",
    "start_index",
    "chunk_id",
    # Custom catalog metadata
    "doc_type",
    "doc_name",
    "date_context",
    # Element type from unstructured
    "category",
    "element_id",
})


def _sanitize_metadata(doc: Document) -> Document:
    """
    Filter document metadata to only include allowed fields with simple types.

    ChromaDB only accepts metadata values that are str, int, float, bool, or None.
    Complex types like dicts, lists, or numpy arrays are dropped.
    """
    sanitized = {}
    for key, value in doc.metadata.items():
        if key not in ALLOWED_METADATA_FIELDS:
            continue
        # Only keep simple types that ChromaDB accepts
        if isinstance(value, (str, int, float, bool)) or value is None:
            sanitized[key] = value
        # Convert numpy numeric types to Python types
        elif hasattr(value, "item"):  # numpy scalar
            sanitized[key] = value.item()

    return Document(page_content=doc.page_content, metadata=sanitized)


class IngestionService:
    """Service for ingesting documents into a vector store."""

    def __init__(
        self,
        processor: DocumentProcessor,
        vectorstore: VectorStore,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self._processor = processor
        self._vectorstore = vectorstore
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def ingest_file(
        self,
        file_path: Path,
        metadata: dict | None = None,
    ) -> int:
        """
        Ingest a single file.

        Args:
            file_path: Path to the document
            metadata: Additional metadata to attach to all chunks

        Returns:
            Number of chunks indexed
        """
        if not self._processor.can_process(file_path):
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        result = self._processor.process(file_path)
        if result.error:
            raise RuntimeError(f"Processing failed: {result.error}")

        # Enrich with caller-provided metadata
        if metadata:
            for doc in result.documents:
                doc.metadata.update(metadata)

        chunks = chunk_documents(
            result.documents,
            self._chunk_size,
            self._chunk_overlap,
        )

        # Sanitize metadata to only include allowed fields with simple types
        sanitized_chunks = [_sanitize_metadata(chunk) for chunk in chunks]

        self._vectorstore.add_documents(sanitized_chunks)
        return len(sanitized_chunks)

    def ingest_directory(
        self,
        directory: Path,
        metadata_catalog: dict[str, dict] | None = None,
    ) -> int:
        """
        Ingest all supported files from a directory.

        Args:
            directory: Directory containing documents
            metadata_catalog: Mapping of filename -> metadata dict

        Returns:
            Total number of chunks indexed
        """
        metadata_catalog = metadata_catalog or {}
        total_chunks = 0

        for file_path in sorted(directory.iterdir()):
            if not file_path.is_file():
                continue
            if not self._processor.can_process(file_path):
                continue

            metadata = metadata_catalog.get(file_path.name, {})
            chunks = self.ingest_file(file_path, metadata)
            total_chunks += chunks
            logger.info(
                "file_ingested",
                filename=file_path.name,
                chunks=chunks,
            )

        return total_chunks
