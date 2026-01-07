"""
Protocol for graph runners.

This is our ONLY custom protocol - LangChain doesn't provide this abstraction.
All graph runners must implement this interface to work with the chat service.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class ChatRequest:
    """Standard chat request for all graphs."""

    messages: list[dict[str, str]]
    model_id: str
    temperature: float = 0.0


@dataclass
class ChatResponse:
    """Standard chat response from all graphs."""

    content: str


@runtime_checkable
class PregelRunner(Protocol):
    """
    Protocol for graph execution.

    All graph runners implement this interface, enabling:
    - Registry pattern for graph selection
    - Dependency injection in services
    - Consistent CLI/API interface across graph types
    """

    @property
    def name(self) -> str:
        """Return the graph name for identification."""
        ...

    def invoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse:
        """Execute the graph synchronously."""
        ...

    async def ainvoke(
        self, request: ChatRequest, thread_id: str = "default"
    ) -> ChatResponse:
        """Execute the graph asynchronously."""
        ...

    async def astream(
        self, request: ChatRequest, thread_id: str = "default"
    ) -> AsyncIterator[str]:
        """Stream the graph execution."""
        raise NotImplementedError
        if False:
            yield {}
