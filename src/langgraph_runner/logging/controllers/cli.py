"""
CLI-specific logging adapter.

Provides context binding for CLI chat sessions and commands.
"""

import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from langgraph_runner.logging.context import bind_context, logging_context


def set_cli_session_context(graph_name: str, session_id: str | None = None) -> None:
    """Set context for a CLI chat session."""
    bind_context(
        graph_name=graph_name,
        session_id=session_id or str(uuid.uuid4()),
        controller="cli",
    )


@contextmanager
def cli_command_context(command: str) -> Iterator[None]:
    """Context manager for CLI command execution."""
    with logging_context(command=command):
        yield
