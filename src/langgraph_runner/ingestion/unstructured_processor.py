"""
Unstructured.io-based document processor.

Provides high-quality extraction with OCR, table detection, and multi-format support.
"""

from pathlib import Path

from langchain_core.documents import Document
from langchain_unstructured import UnstructuredLoader

from langgraph_runner.ingestion.protocols import BaseDocumentProcessor, ProcessedDocument


class UnstructuredProcessor(BaseDocumentProcessor):
    """Process documents using Unstructured.io for high-quality extraction."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".html", ".md", ".txt"}

    def __init__(self, strategy: str = "auto"):
        """
        Args:
            strategy: Extraction strategy - "fast", "hi_res", "ocr_only", "auto"
        """
        self._strategy = strategy

    def supported_extensions(self) -> set[str]:
        return self.SUPPORTED_EXTENSIONS

    def process(self, file_path: Path) -> ProcessedDocument:
        """Process document with Unstructured extraction."""
        if not file_path.exists():
            return ProcessedDocument(
                documents=[],
                source_file=file_path.name,
                error=f"File not found: {file_path}",
            )

        try:
            strategy = self._get_strategy(file_path)
            loader = UnstructuredLoader(
                file_path=str(file_path),
                strategy=strategy,
            )

            documents = loader.load()
            page_count = self._extract_page_count(documents)

            return ProcessedDocument(
                documents=documents,
                source_file=file_path.name,
                page_count=page_count,
            )

        except Exception as e:
            return ProcessedDocument(
                documents=[],
                source_file=file_path.name,
                error=str(e),
            )

    def _get_strategy(self, file_path: Path) -> str:
        """Select extraction strategy based on file type."""
        if self._strategy != "auto":
            return self._strategy
        # PDFs benefit from hi_res for tables and OCR
        return "hi_res" if file_path.suffix.lower() == ".pdf" else "fast"

    def _extract_page_count(self, docs: list[Document]) -> int | None:
        """Extract page count from document metadata."""
        page_numbers = {
            doc.metadata.get("page_number")
            for doc in docs
            if doc.metadata.get("page_number") is not None
        }
        return max(page_numbers) if page_numbers else None
