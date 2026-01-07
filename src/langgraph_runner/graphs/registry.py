"""
Graph runner registry.

Maps graph names to factory functions that create fully-wired runners.
This decouples graph instantiation from the service/controller layers.
"""

from collections.abc import Callable

from langgraph_runner.graphs.base.runner import PregelRunner

# Registry maps graph names to factory functions
REGISTRY: dict[str, Callable[[], PregelRunner]] = {}


def register(name: str, factory: Callable[[], PregelRunner]) -> None:
    """Register a graph factory function."""
    REGISTRY[name] = factory


def get_runner(name: str) -> PregelRunner:
    """Get a fully-wired runner instance by name."""
    if name not in REGISTRY:
        available = ", ".join(REGISTRY.keys()) or "(none)"
        raise ValueError(f"Unknown graph: {name}. Available: {available}")
    return REGISTRY[name]()


def list_graphs() -> list[str]:
    """List available graph names."""
    return list(REGISTRY.keys())
