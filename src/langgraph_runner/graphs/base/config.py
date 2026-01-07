"""
Base configuration for all graphs.

Design Note: Only include configuration that is truly common to ALL graph types.
"""

from dataclasses import dataclass, field, fields
from typing import TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config

from langgraph_runner.config import settings

GraphConfigType = TypeVar("GraphConfigType", bound="BaseGraphConfig")


@dataclass(kw_only=True)
class BaseGraphConfig:
    """
    Base configuration shared by all graphs.

    Contains only the minimal configuration required by any graph.
    """

    model_id: str = field(
        default=settings.MODEL_ID,
        metadata={"description": "The LLM model identifier"},
    )
    temperature: float = field(
        default=settings.DEFAULT_TEMPERATURE,
        metadata={"description": "Sampling temperature"},
    )

    @classmethod
    def from_runnable_config(
        cls: type[GraphConfigType],
        config: RunnableConfig | None = None,
    ) -> GraphConfigType:
        """
        Factory method to create config from LangGraph RunnableConfig.

        This bridges the gap between LangGraph's config system and our typed config.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

    def to_dict(self) -> dict:
        """Convert config to dictionary for RunnableConfig."""
        return {f.name: getattr(self, f.name) for f in fields(self)}
