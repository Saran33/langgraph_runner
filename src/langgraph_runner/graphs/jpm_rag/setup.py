"""
Setup script for J.P. Morgan RAG graph.

Run before chat to ingest documents into the vector store.
Usage: python -m langgraph_runner.graphs.jpm_rag.setup
"""

import structlog

from langgraph_runner.config import settings
from langgraph_runner.ingestion.service import IngestionService
from langgraph_runner.ingestion.unstructured_processor import UnstructuredProcessor
from langgraph_runner.logging import configure_logging
from langgraph_runner.retrieval.vectorstore import create_vectorstore

logger = structlog.stdlib.get_logger(__name__)

# Graph-specific metadata catalog
DOCUMENT_CATALOG = {
    "outlook-2025-building-on-strength.pdf": {
        "doc_type": "forecast",
        "doc_name": "J.P. Morgan Outlook 2025",
        "date_context": "January 2025",
    },
    "mid-year-outlook-2025.pdf": {
        "doc_type": "mid_year",
        "doc_name": "J.P. Morgan Mid-Year Outlook 2025",
        "date_context": "Mid-2025",
    },
}


def main():
    """Ingest J.P. Morgan PDF documents into the vector store."""
    configure_logging()

    logger.info("setup_started", graph="jpm_rag")
    logger.info("loading_documents", source_dir=str(settings.PDF_DIR))

    processor = UnstructuredProcessor(strategy="hi_res")
    vectorstore = create_vectorstore(settings.CHROMA_DIR)
    service = IngestionService(processor, vectorstore)

    total = service.ingest_directory(settings.PDF_DIR, DOCUMENT_CATALOG)
    logger.info(
        "setup_complete",
        total_chunks=total,
        chroma_dir=str(settings.CHROMA_DIR),
    )


if __name__ == "__main__":
    main()
