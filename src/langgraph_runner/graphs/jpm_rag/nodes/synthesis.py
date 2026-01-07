"""
Synthesis node.
"""

import structlog
from langchain_core.runnables import RunnableConfig

from langgraph_runner.graphs.jpm_rag.config import RAGGraphConfig
from langgraph_runner.graphs.jpm_rag.prompts import build_synthesis_messages
from langgraph_runner.graphs.jpm_rag.state import RAGGraphState
from langgraph_runner.models import load_chat_model

logger = structlog.stdlib.get_logger(__name__)


def create_synthesis_node():
    """Factory for synthesis node."""

    async def synthesize_node(state: RAGGraphState, config: RunnableConfig) -> dict:
        """Generate a cited answer from retrieved documents."""
        cfg = RAGGraphConfig.from_runnable_config(config)
        llm = load_chat_model(cfg.model_id, temperature=cfg.temperature)

        # Collect documents by source
        forecast_docs = []
        mid_year_docs = []
        for result in state.results:
            if result.source == "forecast":
                forecast_docs.extend(result.documents)
            elif result.source == "mid_year":
                mid_year_docs.extend(result.documents)

        await logger.adebug(
            "synthesis_input",
            query=state.query,
            forecast_chunks=len(forecast_docs),
            mid_year_chunks=len(mid_year_docs),
        )

        messages = build_synthesis_messages(state.query, forecast_docs, mid_year_docs)
        response = await llm.ainvoke(messages)

        await logger.adebug(
            "synthesis_output",
            answer_preview=response.content[:200] if response.content else "",
        )

        return {"answer": response.content}

    return synthesize_node
