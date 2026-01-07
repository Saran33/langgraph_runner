"""
State for JPM RAG router graph.

Simple query-based state for stateless RAG execution.
Uses Send API pattern with Classification and RetrievalResult.
"""

import operator
from dataclasses import dataclass, field
from typing import Annotated, Literal

from langchain_core.documents import Document


@dataclass
class Classification:
    """A routing decision for a specific source."""

    source: Literal["forecast", "mid_year"]
    query: str


@dataclass
class RetrievalResult:
    """Result from a retrieval node."""

    source: Literal["forecast", "mid_year"]
    documents: list[Document]


@dataclass
class RAGGraphInputState:
    """Input state for RAG graph - same as base for chat interface."""

    query: str


@dataclass
class RAGGraphState(RAGGraphInputState):
    """
    State for the stateless RAG router.

    Simple query in, answer out. Uses Send API for parallel retrieval.
    """

    # Routing results from classify node
    classifications: list[Classification] = field(default_factory=list)

    # Retrieved documents - uses operator.add to merge from parallel Send
    results: Annotated[list[RetrievalResult], operator.add] = field(
        default_factory=list
    )

    # Final synthesized answer
    answer: str = field(default="")
