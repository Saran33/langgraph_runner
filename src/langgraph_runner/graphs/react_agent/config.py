"""
Configuration for ReAct agent.
"""

from dataclasses import dataclass, field

from langgraph_runner.graphs.base.config import BaseGraphConfig


@dataclass(kw_only=True)
class ReActAgentConfig(BaseGraphConfig):
    """Configuration for the ReAct agent."""

    system_prompt: str = field(
        default="You are a helpful assistant.",
        metadata={"description": "System prompt for the agent"},
    )
    tool_choice: str | None = field(
        default=None,
        metadata={
            "description": "Force a specific tool on first invocation. "
            "Set to tool name to reduce context by only binding that tool."
        },
    )
