"""
Classification node using structured output.
"""

from typing import Literal, cast

import structlog
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from langgraph_runner.graphs.jpm_rag.config import RAGGraphConfig
from langgraph_runner.graphs.jpm_rag.prompts import CLASSIFY_SYSTEM
from langgraph_runner.graphs.jpm_rag.state import Classification, RAGGraphState
from langgraph_runner.models import load_chat_model

logger = structlog.stdlib.get_logger(__name__)


class ClassificationSchema(BaseModel):
    """Schema for a single classification with retrieval-optimized query."""

    source: Literal["forecast", "mid_year"] = Field(
        description="The document source to search"
    )
    query: str = Field(
        description=(
            "Retrieval-optimized search query. MUST NOT contain document names like "
            "'Outlook 2025' or 'Mid-Year'. Focus on keywords: stock names, sectors, "
            "themes, metrics. Example: 'AI stocks equities technology recommendations'"
        )
    )


class ClassificationResult(BaseModel):
    """Structured output for classifier."""

    classifications: list[ClassificationSchema] = Field(
        description="Sources to query with retrieval-optimized sub-questions"
    )


def create_classify_node():
    """Factory for classification node."""

    async def classify(state: RAGGraphState, config: RunnableConfig) -> dict:
        """Classify the query and determine which sources to search."""
        cfg = RAGGraphConfig.from_runnable_config(config)
        llm = load_chat_model(
            cfg.classification_model_id, temperature=cfg.classification_temperature
        )

        result = cast(
            ClassificationResult,
            await llm.with_structured_output(ClassificationResult).ainvoke([
                {"role": "system", "content": CLASSIFY_SYSTEM},
                {"role": "user", "content": state.query},
            ]),
        )

        # Convert schema to state dataclass
        classifications = [
            Classification(source=c.source, query=c.query)
            for c in result.classifications
        ]

        await logger.adebug(
            "classification_result",
            sources=[c.source for c in classifications],
            sub_queries={c.source: c.query for c in classifications},
        )

        return {"classifications": classifications}

    return classify
