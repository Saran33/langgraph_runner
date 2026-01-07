"""
Runner for direct JPM RAG graph invocation.
"""

from collections.abc import AsyncIterator

from langchain_core.runnables import RunnableConfig

from langgraph_runner.graphs.base.runner import ChatRequest, ChatResponse, PregelRunner
from langgraph_runner.graphs.jpm_rag.config import RAGGraphConfig
from langgraph_runner.graphs.jpm_rag.graph import build_graph
from langgraph_runner.graphs.jpm_rag.state import RAGGraphInputState
from langgraph_runner.retrieval.retriever import FilteredRetriever


class JPMRagRunner(PregelRunner):
    """
    Runner for direct RAG graph invocation (no agent wrapper).

    Use this when you want simple query -> answer without conversation.
    """

    def __init__(self, retriever: FilteredRetriever | None = None):
        self._graph = build_graph(retriever)

    @property
    def name(self) -> str:
        return self._graph.name

    def _build_runnable_config(self, request: ChatRequest) -> RunnableConfig:
        """Build RunnableConfig from ChatRequest."""
        config = RAGGraphConfig(
            model_id=request.model_id,
            temperature=request.temperature,
        )
        return RunnableConfig(configurable=config.to_dict())

    def _build_input_state(self, request: ChatRequest) -> RAGGraphInputState:
        """Extract query from messages and build input state."""
        # Extract query from last user message
        query = ""
        for msg in reversed(request.messages):
            if msg.get("role") == "user":
                query = msg["content"]
                break
        return RAGGraphInputState(query=query)

    def invoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse:
        input_state = self._build_input_state(request)
        config = self._build_runnable_config(request)
        result = self._graph.invoke(input_state, config=config)
        return ChatResponse(content=result["answer"])

    async def ainvoke(
        self, request: ChatRequest, thread_id: str = "default"
    ) -> ChatResponse:
        input_state = self._build_input_state(request)
        config = self._build_runnable_config(request)
        result = await self._graph.ainvoke(input_state, config=config)
        return ChatResponse(content=result["answer"])

    async def astream(
        self, request: ChatRequest, thread_id: str = "default"
    ) -> AsyncIterator[str]:
        input_state = self._build_input_state(request)
        config = self._build_runnable_config(request)

        async for msg_chunk, metadata in self._graph.astream(
            input_state, config, stream_mode="messages"
        ):
            # Only stream from the synthesis node, skip classify and retrieval nodes
            node_name = metadata.get("langgraph_node", "")  # type: ignore[union-attr]
            if node_name != "synthesize":
                continue
            # msg_chunk is an AIMessageChunk with .content attribute
            content = getattr(msg_chunk, "content", "")
            if content:
                yield content
