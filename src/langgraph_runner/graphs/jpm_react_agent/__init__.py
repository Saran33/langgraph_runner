"""
JPM React Agent - Composite of react_agent + jpm_rag blocks.

This is a conversational agent that uses the JPM RAG tool for document search.
"""

from langgraph.checkpoint.base import BaseCheckpointSaver

from langgraph_runner.graphs.jpm_rag.tool import search_jpm_documents
from langgraph_runner.graphs.react_agent import ReactAgentRunner, build_react_agent
from langgraph_runner.graphs.registry import register
from langgraph_runner.memory import create_checkpointer

SYSTEM_PROMPT = """You are a helpful assistant for analyzing J.P. Morgan investment documents.

Use the search_jpm_documents tool when you need information about:
- 2025 market predictions and investment themes
- Mid-year 2025 performance and results
- Stock analysis and portfolio recommendations

For greetings, clarifications, or questions about previous responses, respond directly.
Always cite sources when providing financial information."""


def _create_runner(
    checkpointer: BaseCheckpointSaver | None = None,
) -> ReactAgentRunner:
    """Create the JPM React Agent runner.

    Args:
        checkpointer: Optional checkpointer for conversation memory.
            If None, uses the default from settings.CHECKPOINTER_TYPE.
    """
    if checkpointer is None:
        checkpointer = create_checkpointer()

    agent = build_react_agent(
        tools=[search_jpm_documents],
        checkpointer=checkpointer,
    )
    agent.name = "jpm_react_agent"

    return ReactAgentRunner(agent, system_prompt=SYSTEM_PROMPT)


# Register in catalogue
register("jpm_react_agent", _create_runner)
