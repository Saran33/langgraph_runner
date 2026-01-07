"""
Memory infrastructure factories (checkpointers, stores).

Provides factory functions to create checkpointer instances based on configuration.
"""

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from langgraph_runner.config import settings


def create_checkpointer(
    checkpointer_type: str | None = None,
) -> BaseCheckpointSaver:
    """
    Create a checkpointer based on configuration.

    Args:
        checkpointer_type: Override for settings.CHECKPOINTER_TYPE.
            Options: "memory", "postgres"

    Returns:
        A configured checkpointer instance.
    """
    checkpointer_type = checkpointer_type or settings.CHECKPOINTER_TYPE

    match checkpointer_type:
        case "memory":
            return MemorySaver()
        case "postgres":
            from langgraph.checkpoint.postgres import (  # type: ignore[import]
                PostgresSaver,
            )

            if not settings.POSTGRES_URI:
                raise ValueError(
                    "POSTGRES_URI is required when CHECKPOINTER_TYPE=postgres"
                )
            return PostgresSaver.from_conn_string(settings.POSTGRES_URI)
        case _:
            raise ValueError(f"Unknown checkpointer type: {checkpointer_type}")
