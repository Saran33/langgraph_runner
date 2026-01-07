"""
Expose JPM RAG graph as a tool for composition.
"""

from langchain_core.tools import tool

from langgraph_runner.graphs.jpm_rag.graph import get_graph
from langgraph_runner.graphs.jpm_rag.state import RAGGraphInputState


@tool
async def search_jpm_documents(query: str) -> str:
    """Search J.P. Morgan Outlook and Mid-Year documents.

    Use this tool to find information about:
    - 2025 market predictions and investment themes (from Outlook 2025)
    - Actual mid-year 2025 performance and results (from Mid-Year Outlook)
    - Stock analysis, sector recommendations, and portfolio strategies
    - Comparisons between predictions and actual outcomes

    Args:
        query: The question to search for in J.P. Morgan documents.

    Returns:
        A synthesized answer with citations from the relevant documents.
    """
    result = await get_graph().ainvoke(RAGGraphInputState(query=query))
    return result["answer"]
