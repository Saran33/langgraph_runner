# Project Guidelines

## Build & Development Commands
- **Install dependencies**: `make uv-sync`
- **Start required services**: `make compose-dependencies`
- **Run API server locally**: `make backend-run-local`
- **Run database migrations**: `make db-migrate`
- **Populate database**: `make db-populate`
- **Start with Docker**: `make compose-backend`

## Lint & Formatting
- **Run all linting, formatting, and type checks**: `make lint`
- **Format code**: `make ruff` or `uv run ruff format .`
- **Type check**: `make mypy` or `uv run mypy .`

## Testing
- **Run all unit tests**: `make test`
- **Run single test**: `uv run pytest tests/unit_tests/path/to/test_file.py::TestClass::test_method -vv`
- **Run with coverage**: Tests automatically include coverage with `--cov-report=term-missing:skip-covered`

## Code Style Guidelines
- **Line length**: 88 characters
- **Imports**: Use `isort` order (stdlib, third-party, first-party)
- **Types**: Use Python type hints for all functions and variables
- **Formatting**: Follow Ruff formatting rules
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Error handling**: Use custom exceptions from `app/exceptions/` when possible
- **Avoid**: Print statements, commented-out code, complex comprehensions
- **Testing**: Test all new features with pytest, use fixtures when appropriate

## Pre-commit
- **Install hooks**: `make pre-commit-install`
- **Run hooks**: `make pre-commit-run`

## Additional Notes
- Remember, we should NEVER be using the system Python. We are using `uv`. If a command is not in the Makefile, it should be run with `uv run <COMMAND>`.
- Never make any commits or stage changes. These will be reviewed by the team and we will commit them.
- We need to strictly adhere to SOLID principles and design patterns. The project makes widespread use of protocols and abstract classes.
- We use a custom logging library that is based on `structlog`. This is already set up in the project. We should use async logging where appropriate.
- We should seek to keep the code clear, concise, readable, and maintainable, avoiding fluff and complexity unless there is a good reason for it.
- We have tests in a `tests` directory (which contains both unit tests and "integration" test specs). We should aim for high test coverage.
- We prioritise integration tests that get the most "bang for our buck" in term of coverage and are more likely to catch bugs in practice.
- After making any code changes, run `make lint` to fix all linting errors. This should be done before reporting that a task is complete.
- When requesting permission to execute an action, please always try to explain your reasoning for what you hope to accomplish by the action (unless it is very obvious). This will help the user to better appraise your proposed action with an understanding of your intentions.
- Think carefully and only action the specific task you are given, using the most concise and elegant solution that changes as little code as possible.
- Strive for simplicity and clarity in your code, avoiding unnecessary complexity unless there is a performance or architectural reason.
- Strictly adhere to SOLID principles and DRY (Don't Repeat Yourself) principles.
- Try to refrain from removing comments unless relevant to the code change or if they are outdated or incorrect.
- Never add inline imports unless absolutely necessary for circular import resolution. Always place imports at the top of the file.
- NEVER add "backwards compatibility" code unless explicitly requested. We are not supporting legacy code and this will only add unnecessary complexity.
- There is no need for comments that are only relevant in the context of the current WIP branch. Only add comments if they will make sense in the context of main branch in future, for any developer examining the code when it is merged into main.
