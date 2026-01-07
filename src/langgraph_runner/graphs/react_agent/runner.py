"""
Runner for ReAct agent.
"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from langgraph_runner.graphs.base.runner import ChatRequest, ChatResponse, PregelRunner
from langgraph_runner.graphs.react_agent.config import ReActAgentConfig
from langgraph_runner.graphs.react_agent.state import AgentState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


class ReactAgentRunner(PregelRunner):
    """Runner for ReAct agent graphs."""

    def __init__(self, graph: "CompiledStateGraph", system_prompt: str):
        self._graph = graph
        self._system_prompt = system_prompt

    @property
    def name(self) -> str:
        return self._graph.name

    def _parse_messages(self, request: ChatRequest) -> list:
        """Parse ChatRequest messages into LangChain message types."""
        messages = []
        for msg in request.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] in ("assistant", "ai"):
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def _build_runnable_config(
        self, request: ChatRequest, thread_id: str
    ) -> RunnableConfig:
        """Build RunnableConfig from ChatRequest."""
        config = ReActAgentConfig(
            model_id=request.model_id,
            temperature=request.temperature,
            system_prompt=self._system_prompt,
        )
        configurable = config.to_dict()
        configurable["thread_id"] = thread_id
        return RunnableConfig(configurable=configurable)

    def invoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse:
        messages = self._parse_messages(request)
        config = self._build_runnable_config(request, thread_id)
        result = self._graph.invoke(AgentState(messages=messages), config)
        return ChatResponse(content=result["messages"][-1].content)

    async def ainvoke(
        self, request: ChatRequest, thread_id: str = "default"
    ) -> ChatResponse:
        messages = self._parse_messages(request)
        config = self._build_runnable_config(request, thread_id)
        result = await self._graph.ainvoke(AgentState(messages=messages), config)
        return ChatResponse(content=result["messages"][-1].content)

    async def astream(
        self, request: ChatRequest, thread_id: str = "default"
    ) -> AsyncIterator[str]:
        messages = self._parse_messages(request)
        config = self._build_runnable_config(request, thread_id)

        async for msg, metadata in self._graph.astream(
            AgentState(messages=messages),
            config,
            stream_mode="messages",
        ):
            if metadata.get("langgraph_node") == "agent":  # type: ignore[union-attr]
                content = getattr(msg, "content", "")
                if content:
                    yield content
