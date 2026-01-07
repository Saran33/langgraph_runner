"""
CLI entry point for chat.

Generic controller that works with any registered graph.
Graph-specific setup (ingestion, etc.) is in each graph module's setup.py.
"""

# ruff: noqa: T201
import argparse
import asyncio
import sys

import langgraph_runner.graphs.jpm_rag  # Import to trigger registration
import langgraph_runner.graphs.jpm_react_agent  # noqa: F401  # Import to trigger registration
from langgraph_runner.config import settings
from langgraph_runner.graphs.registry import get_runner, list_graphs
from langgraph_runner.logging import configure_logging, get_logger
from langgraph_runner.logging.controllers.cli import (
    cli_command_context,
    set_cli_session_context,
)
from langgraph_runner.services.chat import ChatService

logger = get_logger(__name__)

DEFAULT_GRAPH = settings.DEFAULT_GRAPH


async def _stream_response(service: ChatService, message: str) -> None:
    """Stream a response with immediate feedback."""
    async for chunk in service.astream_chat(
        message,
        model_id=settings.MODEL_ID,
        temperature=settings.DEFAULT_TEMPERATURE,
    ):
        print(chunk, end="", flush=True)
    print("\n")


def cmd_chat(args: argparse.Namespace) -> None:
    """Start an interactive chat session with streaming."""
    with cli_command_context("chat"):
        runner = get_runner(args.graph)
        service = ChatService(runner)
        set_cli_session_context(graph_name=args.graph)

        logger.info("chat_session_started", graph=args.graph)
        print(f"Chat with {service.graph_name} graph")
        print("Type 'quit' to end the session\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit"):
                    print("Goodbye!")
                    break

                print("\nAssistant:\n", end="", flush=True)
                asyncio.run(_stream_response(service, user_input))

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                logger.exception("chat_error", error=str(e))
                print(f"\nError: {e}\n")


def cmd_ask(args: argparse.Namespace) -> None:
    """Ask a single question with streaming response."""
    with cli_command_context("ask"):
        set_cli_session_context(graph_name=args.graph)
        logger.info(
            "ask_command", graph=args.graph, question_preview=args.question[:80]
        )
        runner = get_runner(args.graph)
        service = ChatService(runner)
        print("Assistant: ", end="", flush=True)
        asyncio.run(_stream_response(service, args.question))


def cmd_list(_args: argparse.Namespace) -> None:
    """List available graphs."""
    graphs = list_graphs()
    if not graphs:
        print("No graphs registered.")
        return

    print("Available graphs:")
    for g in graphs:
        default_marker = " (default)" if g == DEFAULT_GRAPH else ""
        print(f"  - {g}{default_marker}")


def main() -> None:
    configure_logging()

    parser = argparse.ArgumentParser(
        description="LangGraph Runner CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat
  uv run python -m langgraph_runner chat

  # Ask a single question
  uv run python -m langgraph_runner ask "What stocks were highlighted?"

  # List available graphs
  uv run python -m langgraph_runner list

  # Use specific graph
  uv run python -m langgraph_runner --graph jpm_rag chat
""",
    )
    parser.add_argument(
        "--graph",
        "-g",
        default=DEFAULT_GRAPH,
        help=f"Graph to use (default: {DEFAULT_GRAPH})",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # chat command
    subparsers.add_parser("chat", help="Interactive chat mode")

    # ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a single question")
    ask_parser.add_argument("question", help="The question to ask")

    # list command
    subparsers.add_parser("list", help="List available graphs")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        "chat": cmd_chat,
        "ask": cmd_ask,
        "list": cmd_list,
    }

    try:
        commands[args.command](args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)


if __name__ == "__main__":
    main()
