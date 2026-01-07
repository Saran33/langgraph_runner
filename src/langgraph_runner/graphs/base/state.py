"""
Base state definitions for all graphs.

Design Note: Only include fields that are truly common to ALL graph types.
For a chat-based interface, the minimal common state is messages.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


@dataclass
class BaseGraphInputState:
    """
    Narrower interface for graph input from the outside world.

    This represents what the CLI/API provides to the graph.
    Uses add_messages reducer for proper message accumulation.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )


@dataclass
class BaseGraphState(BaseGraphInputState):
    """
    Complete internal state for graph execution.

    Extends input state with internal tracking fields.
    Subclasses add domain-specific fields.
    """

    is_last_step: bool = field(default=False)
