"""
ReAct agent graph builder.
"""

from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode

from langgraph_runner.graphs.react_agent.config import ReActAgentConfig
from langgraph_runner.graphs.react_agent.state import AgentState
from langgraph_runner.models import load_chat_model


def _create_call_model(tools: list[BaseTool]):
    """Create the model-calling node."""

    async def call_model(state: AgentState, config: RunnableConfig) -> dict:
        """Call the LLM powering the agent."""
        cfg = ReActAgentConfig.from_runnable_config(config)

        model = load_chat_model(cfg.model_id, temperature=cfg.temperature)

        # Handle tool binding with optional tool_choice filtering
        if tools:
            if not state.tool_called and cfg.tool_choice:
                # First invocation with tool_choice: filter to only the chosen tool
                # This reduces unnecessary context passed to the model
                bound_tools = [t for t in tools if t.name == cfg.tool_choice]
                model = model.bind_tools(bound_tools, tool_choice=cfg.tool_choice)
            else:
                # No forced tool choice, bind all tools
                model = model.bind_tools(tools)

        messages = [SystemMessage(content=cfg.system_prompt), *state.messages]
        response = await model.ainvoke(messages, config)

        # Handle the case when it's the last step and the model still wants to use a tool
        if state.is_last_step and response.tool_calls:
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="I couldn't complete the request in the available steps.",
                    )
                ]
            }

        # If the response has tool calls, mark that a tool will be called
        # This prevents future forced tool choices to avoid infinite loops
        result: dict[str, list[AIMessage] | bool] = {"messages": [response]}
        if response.tool_calls:
            result["tool_called"] = True

        return result

    return call_model


def _route_model_output(state: AgentState) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    Routes to tools if the model made tool calls, otherwise ends.
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(f"Expected AIMessage, got {type(last_message).__name__}")
    if not last_message.tool_calls:
        return "__end__"
    return "tools"


def build_react_agent(
    tools: list[BaseTool],
    checkpointer: BaseCheckpointSaver | None = None,
):
    """
    Build a ReAct agent graph.

    Args:
        tools: Tools the agent can use
        checkpointer: For conversation memory and HITL support
    """
    builder = StateGraph(AgentState, context_schema=ReActAgentConfig)

    builder.add_node("agent", _create_call_model(tools))
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", _route_model_output)
    builder.add_edge("tools", "agent")

    graph = builder.compile(checkpointer=checkpointer)
    graph.name = "react_agent"
    return graph
