"""
Logging context management using structlog contextvars.

Provides controller-agnostic context propagation for request IDs and session context.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import structlog


def bind_context(**kwargs: Any) -> None:
    """Bind key-value pairs to the current logging context."""
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()


def get_context() -> dict[str, Any]:
    """Get current context variables."""
    return structlog.contextvars.get_contextvars()


@contextmanager
def logging_context(**kwargs: Any) -> Iterator[None]:
    """Context manager that adds context for the duration of the scope."""
    old_context = get_context().copy()
    try:
        bind_context(**kwargs)
        yield
    finally:
        clear_context()
        bind_context(**old_context)
