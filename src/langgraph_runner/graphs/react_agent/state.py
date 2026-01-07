"""
State for ReAct agent.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


@dataclass
class AgentState:
    """State for ReAct agent."""

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    is_last_step: bool = field(default=False)
    tool_called: bool = field(default=False)
