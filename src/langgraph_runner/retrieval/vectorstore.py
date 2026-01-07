"""
ChromaDB vector store setup.

Uses LangChain's Chroma directly - no wrapper needed.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from langgraph_runner.config import settings


def create_vectorstore(
    persist_directory: Path,
    collection_name: str = "jpmorgan_rag",
    embedding_model: str | None = None,
) -> Chroma:
    """Create or load a ChromaDB vector store."""
    persist_directory.mkdir(parents=True, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model=embedding_model or settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
    )


def index_documents(vectorstore: Chroma, documents: list[Document]) -> list[str]:
    """Add documents to the vector store."""
    return vectorstore.add_documents(documents)
