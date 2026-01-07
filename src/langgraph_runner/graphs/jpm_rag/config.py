"""
Configuration for JPM RAG graph.
"""

from dataclasses import dataclass, field

from langgraph_runner.config import settings
from langgraph_runner.graphs.base.config import BaseGraphConfig


@dataclass(kw_only=True)
class RAGGraphConfig(BaseGraphConfig):
    """Configuration for the RAG graph."""

    classification_model_id: str = field(
        default_factory=lambda: settings.ROUTER_MODEL_ID,
    )
    classification_temperature: float = 0.0
