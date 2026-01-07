# LangGraph Runner Framework

A modular, extensible framework for building and running AI workflow graphs using LangGraph. The architecture follows SOLID principles with a pluggable graph registry, enabling new graph types to be added without modifying existing code.

## Features

- **Pluggable Graph Architecture** - Registry pattern enables adding new graph types as independent modules
- **Protocol-Based Design** - `PregelRunner` protocol allows any graph implementation to integrate seamlessly
- **Smart Document Routing** - Built-in RAG capabilities with automatic query classification and routing
- **Streaming Support** - Real-time streaming responses for better UX
- **Async-First** - Full async/await support throughout
- **Conversation Memory** - Optional checkpointer integration for multi-turn conversations

## Architecture

The framework is organized into layers that separate concerns and enable extensibility:

```
                    ┌─────────────────────────────────────────┐
                    │              CLI / API                  │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────-┐
                    │         Graph Registry & Services        │
                    │  ┌─────────────────────────────────────┐ │
                    │  │     Pluggable Graph Runners         │ │
                    │  │  ┌───────────────────────────────┐  │ │
                    │  │  │   Any PregelRunner impl       │  │ │
                    │  │  └───────────────────────────────┘  │ │
                    │  └─────────────────────────────────────┘ │
                    │                    │                     │
                    │  Uses LangChain types directly:          │
                    │  • BaseChatModel (LLM)                   │
                    │  • VectorStore                           │
                    │  • BaseLoader                            │
                    │  • TextSplitter                          │
                    │  • Embeddings                            │
                    └─────────────────┬───────────────────────-┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────▼────────┐           ┌────────▼────────┐          ┌────────▼────────┐
│  Unstructured  │           │    Chroma       │          │   ChatOpenAI    │
│  (langchain-   │           │  (LangChain)    │          │   (LangChain)   │
│  unstructured) │           │                 │          │                 │
└────────────────┘           └─────────────────┘          └─────────────────┘
```

## Included Graph Implementations

The framework ships with example graph implementations demonstrating different patterns:

| Graph | Type | Description |
|-------|------|-------------|
| `jpm_rag` | Stateless RAG | Document routing, retrieval, and synthesis with citations |
| `jpm_react_agent` | Conversational Agent | ReAct agent that uses `jpm_rag` as a tool, with conversation memory |

These serve as reference implementations showing how to build graphs following the framework patterns.

## Prerequisites

### System Dependencies

Unstructured.io requires system-level dependencies for PDF processing:

**macOS:**
```bash
brew install poppler tesseract
```

**Ubuntu/Debian:**
```bash
apt-get install poppler-utils tesseract-ocr
```

### Python & Package Manager

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Clone repository
git clone <repository-url>
cd langgraph_runner

# Install dependencies
make sync

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

## Quick Start

### 1. Setup a Graph (Example: jpm_rag)

Some graphs require one-time setup (e.g., document ingestion):

```bash
# Add PDF documents to data/pdfs/
# Expected files for jpm_rag:
#   - outlook-2025-building-on-strength.pdf
#   - mid-year-outlook-2025.pdf

# Run graph-specific setup
rm -rf data/chroma_db  # Optional: clear existing DB
uv run python -m langgraph_runner.graphs.jpm_rag.setup
```

### 2. Run Any Graph

```bash
# List available graphs
make list

# Interactive chat with default graph
make chat

# Use a specific graph
make chat DEFAULT_GRAPH=jpm_rag

# Single question
make ask Q="What stocks were highlighted in the 2025 forecast?"

# Streaming response
make stream Q="Compare forecast vs reality for tech stocks"
```

## Adding New Graphs

The framework uses a registry pattern for extensibility. To add a new graph:

### 1. Create Module Structure

```
src/langgraph_runner/graphs/your_graph/
├── __init__.py        # Registration
├── config.py          # Extend BaseGraphConfig
├── state.py           # Extend BaseGraphState
├── graph.py           # build_graph() function
├── runner.py          # Implement PregelRunner
├── prompts.py         # Graph-specific prompts
├── setup.py           # Optional: one-time setup
└── nodes/             # Node implementations
```

### 2. Implement the PregelRunner Protocol

```python
# runner.py
from langgraph_runner.graphs.base.runner import PregelRunner, ChatRequest, ChatResponse

class YourRunner(PregelRunner):
    @property
    def name(self) -> str:
        return "your_graph"

    def invoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse:
        # Implementation
        pass

    async def ainvoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse:
        # Async implementation
        pass

    async def astream(self, request: ChatRequest, thread_id: str = "default") -> AsyncIterator[str]:
        # Streaming implementation
        pass
```

### 3. Register the Graph

```python
# __init__.py
from langgraph_runner.graphs.registry import register
from .runner import YourRunner

register("your_graph", lambda: YourRunner())
```

### 4. Import in Main

```python
# main.py - add import to trigger registration
import langgraph_runner.graphs.your_graph
```

### 5. Use Your Graph

```bash
# Setup (if needed)
uv run python -m langgraph_runner.graphs.your_graph.setup

# Chat
uv run python -m langgraph_runner --graph your_graph chat
```

See `docs/architecture-overview.md` for detailed architecture documentation.

## Development

```bash
make sync          # Install dependencies
make lint          # Run ruff + mypy
make ruff          # Format and lint with ruff
make mypy          # Run type checker
make test          # Run tests
make test-cov      # Run tests with coverage
```

## Configuration

Environment variables (set in `.env`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `MODEL_ID` | No | `gpt-4o` | Default LLM model |
| `DEFAULT_TEMPERATURE` | No | `0.0` | Sampling temperature |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model |
| `RETRIEVAL_K` | No | `5` | Number of documents to retrieve |
| `CHUNK_SIZE` | No | `1000` | Document chunk size |
| `CHUNK_OVERLAP` | No | `200` | Chunk overlap |
| `DEFAULT_GRAPH` | No | `jpm_react_agent` | Default graph for CLI |

## Documentation

- `docs/architecture-overview.md` - Technical overview of modular design and SOLID principles
- `docs/implementation-tickets/` - Individual feature implementation details

## License

MIT
