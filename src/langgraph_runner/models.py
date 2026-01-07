"""
Model loading utilities.

Provides factory functions to load chat models based on model ID.
"""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from langgraph_runner.config import settings


def load_chat_model(
    model_id: str | None = None,
    temperature: float | None = None,
    **kwargs,
) -> BaseChatModel:
    """
    Load a chat model by ID.

    Args:
        model_id: Model identifier (e.g., "gpt-5", "gpt-5-mini").
            If None, uses settings.MODEL_ID.
        temperature: Model temperature. If None, uses settings.DEFAULT_TEMPERATURE.

    Returns:
        A configured chat model instance.
    """
    model_id = model_id or settings.MODEL_ID
    temperature = (
        temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
    )

    return init_chat_model(
        model_id, temperature=temperature, api_key=settings.OPENAI_API_KEY, **kwargs
    )
