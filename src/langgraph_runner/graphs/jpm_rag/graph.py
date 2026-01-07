"""
Stateless RAG router graph.
"""

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from langgraph_runner.config import settings
from langgraph_runner.graphs.jpm_rag.config import RAGGraphConfig
from langgraph_runner.graphs.jpm_rag.nodes.classify import create_classify_node
from langgraph_runner.graphs.jpm_rag.nodes.retrieval import create_retrieval_nodes
from langgraph_runner.graphs.jpm_rag.nodes.routing import route_to_sources
from langgraph_runner.graphs.jpm_rag.nodes.synthesis import create_synthesis_node
from langgraph_runner.graphs.jpm_rag.state import RAGGraphInputState, RAGGraphState
from langgraph_runner.retrieval.retriever import FilteredRetriever
from langgraph_runner.retrieval.vectorstore import create_vectorstore


@lru_cache(maxsize=1)
def _get_default_retriever() -> FilteredRetriever:
    """Lazily create default retriever."""
    vectorstore = create_vectorstore(settings.CHROMA_DIR)
    return FilteredRetriever(
        vectorstore,
        k=settings.RETRIEVAL_K,
        max_distance=settings.RETRIEVAL_MAX_DISTANCE,
    )


def build_graph(retriever: FilteredRetriever | None = None):
    """
    Build the stateless RAG router graph.

    Args:
        retriever: Optional retriever for testing. If None, uses default.
    """
    if retriever is None:
        retriever = _get_default_retriever()

    classify = create_classify_node()
    retrieve_forecast, retrieve_mid_year = create_retrieval_nodes(retriever)
    synthesize = create_synthesis_node()

    builder = StateGraph(
        RAGGraphState, input_schema=RAGGraphInputState, context_schema=RAGGraphConfig
    )

    builder.add_node("classify", classify)
    builder.add_node("forecast", retrieve_forecast)
    builder.add_node("mid_year", retrieve_mid_year)
    builder.add_node("synthesize", synthesize)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify", route_to_sources, ["forecast", "mid_year"]
    )
    builder.add_edge("forecast", "synthesize")
    builder.add_edge("mid_year", "synthesize")
    builder.add_edge("synthesize", END)

    graph = builder.compile()
    graph.name = "jpm_rag"
    return graph


@lru_cache(maxsize=1)
def get_graph():
    """Get the cached default graph instance."""
    return build_graph()
