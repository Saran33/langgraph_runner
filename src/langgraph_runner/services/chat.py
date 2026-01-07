"""
Chat service for orchestrating graph execution.

Works with any graph that implements the PregelRunner protocol.
"""

from collections.abc import AsyncIterator

from langgraph_runner.graphs.base.runner import ChatRequest, PregelRunner


class ChatService:
    """Service for chat interactions with graphs."""

    def __init__(self, runner: PregelRunner):
        """Initialize with a graph runner."""
        self._runner = runner

    @property
    def graph_name(self) -> str:
        """Return the name of the underlying graph."""
        return self._runner.name

    def chat(
        self, message: str, thread_id: str = "default", **kwargs
    ) -> str:
        """Send a message and get a response."""
        request = ChatRequest(
            messages=[{"role": "user", "content": message}],
            **kwargs,
        )
        response = self._runner.invoke(request, thread_id=thread_id)
        return response.content

    async def achat(
        self, message: str, thread_id: str = "default", **kwargs
    ) -> str:
        """Async version of chat."""
        request = ChatRequest(
            messages=[{"role": "user", "content": message}],
            **kwargs,
        )
        response = await self._runner.ainvoke(request, thread_id=thread_id)
        return response.content

    async def astream_chat(
        self, message: str, thread_id: str = "default", **kwargs
    ) -> AsyncIterator[str]:
        """Stream the response."""
        request = ChatRequest(
            messages=[{"role": "user", "content": message}],
            **kwargs,
        )
        async for chunk in self._runner.astream(request, thread_id=thread_id):
            yield chunk
