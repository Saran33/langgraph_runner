"""JPM RAG block - stateless RAG graph."""

from langgraph_runner.graphs.jpm_rag.runner import JPMRagRunner
from langgraph_runner.graphs.registry import register

# Register for direct invocation
register("jpm_rag", lambda: JPMRagRunner())
