"""
Filtered retriever for document type filtering.

This is a thin wrapper that adds doc_type filtering on top of Chroma.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document


class FilteredRetriever:
    """Retriever with document type filtering and score thresholding."""

    def __init__(
        self,
        vectorstore: Chroma,
        k: int = 5,
        max_distance: float | None = None,
    ):
        self._vectorstore = vectorstore
        self._k = k
        self._max_distance = max_distance  # Lower distance = more similar

    async def retrieve(self, query: str, doc_type: str | None = None) -> list[Document]:
        """
        Retrieve documents, optionally filtered by type and score.

        Args:
            query: The search query
            doc_type: Filter by document type ("forecast", "mid_year", or None for all)

        Returns:
            List of matching documents
        """
        filter_dict = None
        if doc_type and doc_type != "both":
            filter_dict = {"doc_type": doc_type}

        # Use score-based retrieval if threshold is set
        if self._max_distance is not None:
            results = await self._vectorstore.asimilarity_search_with_score(
                query=query,
                k=self._k,
                filter=filter_dict,
            )
            # Filter by distance threshold (lower = more similar)
            return [doc for doc, distance in results if distance <= self._max_distance]

        return await self._vectorstore.asimilarity_search(
            query=query,
            k=self._k,
            filter=filter_dict,
        )

    async def retrieve_with_scores(
        self, query: str, doc_type: str | None = None
    ) -> list[tuple[Document, float]]:
        """
        Retrieve documents with similarity scores.

        Args:
            query: The search query
            doc_type: Filter by document type

        Returns:
            List of (document, score) tuples
        """
        filter_dict = None
        if doc_type and doc_type != "both":
            filter_dict = {"doc_type": doc_type}

        return await self._vectorstore.asimilarity_search_with_score(
            query=query,
            k=self._k,
            filter=filter_dict,
        )
