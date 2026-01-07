"""
Document processing protocols for RAG ingestion.

Design: Open/Closed principle - add new formats by implementing
DocumentProcessor, not by modifying existing code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from langchain_core.documents import Document


@dataclass
class ProcessedDocument:
    """Result of document processing."""

    documents: list[Document]
    source_file: str
    page_count: int | None = None
    error: str | None = None


@runtime_checkable
class DocumentProcessor(Protocol):
    """Protocol for document processors."""

    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the file."""
        ...

    def process(self, file_path: Path) -> ProcessedDocument:
        """Process the document and return LangChain documents."""
        ...


class BaseDocumentProcessor(ABC):
    """Base class for document processors with common functionality."""

    @abstractmethod
    def supported_extensions(self) -> set[str]:
        """Return set of supported file extensions."""
        ...

    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the file."""
        return file_path.suffix.lower() in self.supported_extensions()

    @abstractmethod
    def process(self, file_path: Path) -> ProcessedDocument:
        """Process the document and return LangChain documents."""
        ...
