"""
Shared utilities for langgraph_runner.
"""

from collections.abc import Sequence

from langchain_core.messages import AnyMessage


def extract_last_human_message(messages: Sequence[AnyMessage]) -> str:
    """
    Extract text content from the last human message.

    Handles both simple string content and multimodal content (list of str/dict).
    """
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            content = msg.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts = [
                    part if isinstance(part, str) else part.get("text", "")
                    for part in content
                ]
                return " ".join(filter(None, text_parts))
    return ""
