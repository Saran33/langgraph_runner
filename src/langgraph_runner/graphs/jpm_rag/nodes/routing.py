"""
Routing with Send API for parallel execution.
"""

from langgraph.types import Send

from langgraph_runner.graphs.jpm_rag.state import RAGGraphState


def route_to_sources(state: RAGGraphState) -> list[Send]:
    """Fan out to sources based on classifications."""
    return [Send(c.source, {"query": c.query}) for c in state.classifications]
