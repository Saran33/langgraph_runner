"""
Retrieval node implementations for Send pattern.
"""

from typing import TypedDict

import structlog

from langgraph_runner.graphs.jpm_rag.state import RetrievalResult
from langgraph_runner.retrieval.retriever import FilteredRetriever

logger = structlog.stdlib.get_logger(__name__)


class RetrievalInput(TypedDict):
    """Input from Send - contains the query for this retrieval."""

    query: str


def create_retrieval_nodes(retriever: FilteredRetriever):
    """
    Factory to create retrieval nodes with injected retriever.

    Returns tuple of (retrieve_forecast, retrieve_mid_year).
    """

    async def retrieve_forecast(state: RetrievalInput) -> dict:
        """Retrieve from forecast document only."""
        query = state["query"]
        await logger.adebug("retrieval_query", doc_type="forecast", query=query)
        results_with_scores = await retriever.retrieve_with_scores(
            query, doc_type="forecast"
        )
        docs = [doc for doc, _ in results_with_scores]
        await logger.adebug(
            "retrieval_results",
            doc_type="forecast",
            num_chunks=len(docs),
            pages=[
                doc.metadata.get("page_number", doc.metadata.get("page"))
                for doc in docs
            ],
            distances=[round(score, 3) for _, score in results_with_scores],
        )
        return {"results": [RetrievalResult(source="forecast", documents=docs)]}

    async def retrieve_mid_year(state: RetrievalInput) -> dict:
        """Retrieve from mid-year document only."""
        query = state["query"]
        await logger.adebug("retrieval_query", doc_type="mid_year", query=query)
        results_with_scores = await retriever.retrieve_with_scores(
            query, doc_type="mid_year"
        )
        docs = [doc for doc, _ in results_with_scores]
        await logger.adebug(
            "retrieval_results",
            doc_type="mid_year",
            num_chunks=len(docs),
            pages=[
                doc.metadata.get("page_number", doc.metadata.get("page"))
                for doc in docs
            ],
            distances=[round(score, 3) for _, score in results_with_scores],
        )
        return {"results": [RetrievalResult(source="mid_year", documents=docs)]}

    return retrieve_forecast, retrieve_mid_year
