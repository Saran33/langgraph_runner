"""
Document chunking using LangChain's TextSplitter.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunker(chunk_size: int = 1000, chunk_overlap: int = 200):
    """Create a configured text splitter."""
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        add_start_index=True,
    )


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Split documents into chunks with metadata."""
    splitter = create_chunker(chunk_size, chunk_overlap)
    chunks = splitter.split_documents(documents)

    # Add chunk metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return chunks
