SHELL=/bin/bash
APP_NAME=langgraph_runner
SRC_DIR=src

DEFAULT_GRAPH?=jpm_react_agent

# =============================================================================
# Development Setup
# =============================================================================

sync:
	@uv sync --all-extras --dev --no-cache

pre-commit-install: sync
	@uv run pre-commit install

pre-commit-run:
	@uv run pre-commit run --all-files

# =============================================================================
# Linting & Type Checking
# =============================================================================

ruff:
	@uv run ruff format ${SRC_DIR}/
	@uv run ruff check ${SRC_DIR}/ --fix

ruff-check:
	@uv run ruff check ${SRC_DIR}/

mypy:
	@uv run mypy ${SRC_DIR}/

lint: ruff mypy

# =============================================================================
# Testing
# =============================================================================

test:
	@uv run pytest

test-cov:
	@uv run pytest --cov=${SRC_DIR}/${APP_NAME} --cov-report=term-missing

# =============================================================================
# CLI Commands
# =============================================================================

list:
	@uv run python -m langgraph_runner list

chat:
	@uv run python -m langgraph_runner --graph ${DEFAULT_GRAPH} chat

# Usage: make ask Q="Your question here"
ask:
	@uv run python -m langgraph_runner --graph ${DEFAULT_GRAPH} ask "${Q}"

# Usage: make stream Q="Your question here"
stream:
	@uv run python -m langgraph_runner --graph ${DEFAULT_GRAPH} stream "${Q}"

.PHONY: sync pre-commit-install pre-commit-run \
        ruff ruff-check mypy lint \
        test test-cov \
        list chat ask stream
