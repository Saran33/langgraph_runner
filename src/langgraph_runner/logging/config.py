"""
Structlog configuration for LangGraph Runner.

Provides structured logging with configurable output format (console/JSON).
"""

import logging
import sys
from logging import StreamHandler
from typing import TextIO

import structlog
from structlog.stdlib import BoundLogger
from structlog.typing import Processor

from langgraph_runner.config import settings

# Third-party modules that are noisy at INFO level - suppress to WARNING
NOISY_MODULES = ["httpx", "httpcore", "chromadb", "openai", "urllib3"]


class MessageIsNormal(logging.Filter):
    """Filter to route INFO/WARNING to stdout."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


def _get_log_level() -> int:
    """Convert string log level to logging constant."""
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    return levels.get(settings.LOG_LEVEL.lower(), logging.INFO)


def _create_handlers() -> list[StreamHandler[TextIO]]:
    """Create stdout/stderr handlers with proper filtering."""
    # INFO and WARNING to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(MessageIsNormal())

    # ERROR and CRITICAL to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    return [stdout_handler, stderr_handler]


def configure_logging(*, include_callsite_info: bool = False) -> None:
    """
    Configure structlog with shared processors and handlers.

    Args:
        include_callsite_info: Include filename, function name, and line number
            in log output. Defaults to False (less noisy for CLI usage).
    """
    log_level = _get_log_level()
    handlers = _create_handlers()

    shared_processors: list[Processor] = [
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.ExtraAdder(),
    ]

    # Include callsite info if explicitly requested or if DEBUG level
    if include_callsite_info or log_level == logging.DEBUG:
        shared_processors.insert(
            4,
            structlog.processors.CallsiteParameterAdder({
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }),
        )

    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if settings.JSON_LOGS
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    logging.basicConfig(format="%(message)s", level=log_level, handlers=handlers)

    # Suppress noisy third-party loggers - they log too much at INFO level
    for module in NOISY_MODULES:
        logging.getLogger(module).setLevel(logging.WARNING)

    for handler in handlers:
        handler.setFormatter(formatter)


def get_logger(name: str | None = None) -> BoundLogger:
    """Get a structured async logger instance."""
    return structlog.stdlib.get_logger(name)
