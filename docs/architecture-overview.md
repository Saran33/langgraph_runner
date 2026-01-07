# Architecture Overview: Modular Graph Framework

This document provides a technical overview of the LangGraph Runner framework architecture, focusing on its modular design and adherence to SOLID principles.

## Executive Summary

LangGraph Runner is a **pluggable graph execution framework** built on LangGraph that enables defining, composing, and running AI workflow graphs through a unified interface. The architecture follows SOLID principles to enable extensibility without modification, allowing new graph types to be added as independent modules that automatically integrate with the CLI and services.

**Core Design Philosophy:**
- Protocol-based abstractions over concrete implementations
- Self-registering graphs via factory functions
- Dependency injection throughout
- Composition over inheritance
- Async-first design

---

## Architectural Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI / API Layer                             │
│                    (main.py, controllers)                           │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                        Service Layer                                │
│                   (ChatService, IngestionService)                   │
│  - Orchestrates graph execution                                     │
│  - Controller-agnostic                                              │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                     Graph Registry Layer                            │
│                        (registry.py)                                │
│  - Maps graph names → factory functions                             │
│  - Enables runtime graph discovery                                  │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                     Graph Runners Layer                             |
│              (PregelRunner implementations)                         |
│  - Bridges ChatRequest/Response ↔ Graph State                       |
│  - Each graph provides its own runner                               |
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                    Graph Definitions Layer                          |
│               (StateGraph, nodes, edges)                            |
│  - LangGraph StateGraph construction                                |
│  - Node factories with dependency injection                         |
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                  Infrastructure Layer                               |
│          (LLMs, VectorStores, Checkpointers)                        │
│  - LangChain abstractions (BaseChatModel, VectorStore)              |
│  - External service integrations                                    |
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Abstractions

### 1. PregelRunner Protocol

The central abstraction enabling the pluggable architecture. All graph runners implement this protocol:

```python
@runtime_checkable
class PregelRunner(Protocol):
    """Protocol for graph execution."""

    @property
    def name(self) -> str: ...

    def invoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse: ...
    async def ainvoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse: ...
    async def astream(self, request: ChatRequest, thread_id: str = "default") -> AsyncIterator[str]: ...
```

**Location:** `src/langgraph_runner/graphs/base/runner.py`

**Key Benefits:**
- Structural typing (duck typing) - any class with matching methods works
- Runtime checkable for validation
- Decouples graphs from the framework

### 2. Base State Hierarchy

Minimal base states that graphs can extend:

```python
@dataclass
class BaseGraphInputState:
    """External interface for graph input."""
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)

@dataclass
class BaseGraphState(BaseGraphInputState):
    """Internal state for graph execution."""
    is_last_step: bool = field(default=False)
```

**Location:** `src/langgraph_runner/graphs/base/state.py`

**Design Principle:** Only include fields common to all graphs. Graph-specific fields belong in graph-specific states.

### 3. Base Configuration

Type-safe configuration with runtime extraction:

```python
@dataclass(kw_only=True)
class BaseGraphConfig:
    """Base configuration shared by all graphs."""
    model_id: str = field(default=settings.MODEL_ID)
    temperature: float = field(default=settings.DEFAULT_TEMPERATURE)

    @classmethod
    def from_runnable_config(cls, config: RunnableConfig | None = None) -> GraphConfigType:
        """Factory method to create config from LangGraph RunnableConfig."""
```

**Location:** `src/langgraph_runner/graphs/base/config.py`

---

## SOLID Principles in Practice

### Single Responsibility Principle (SRP)

Each component has one clear responsibility:

| Component | Responsibility |
|-----------|----------------|
| `ChatService` | Orchestrates chat interactions |
| `PregelRunner` | Executes graph, bridges interfaces |
| `IngestionService` | Orchestrates document ingestion |
| `DocumentProcessor` | Processes individual document types |
| Node factories | Single node logic (classify, retrieve, synthesize) |

**Example:** Node factories in `src/langgraph_runner/graphs/jpm_rag/nodes/`:
- `create_classify_node()` - Classification only
- `create_retrieval_nodes()` - Retrieval only
- `create_synthesis_node()` - Synthesis only

### Open/Closed Principle (OCP)

The architecture is **open for extension** (new graphs) but **closed for modification** (existing code unchanged).

**Adding a new graph requires:**
1. Create graph module with `PregelRunner` implementation
2. Call `register()` in `__init__.py`
3. Import module in CLI

**No modification needed to:**
- Registry
- ChatService
- CLI
- Existing graphs

```python
# New graph self-registers on import
# src/langgraph_runner/graphs/my_graph/__init__.py
from langgraph_runner.graphs.registry import register
from langgraph_runner.graphs.my_graph.runner import MyRunner

register("my_graph", lambda: MyRunner())
```

### Liskov Substitution Principle (LSP)

All `PregelRunner` implementations are substitutable:

```python
runner1 = get_runner("jpm_rag")        # JPMRagRunner
runner2 = get_runner("jpm_react_agent") # ReactAgentRunner

# Both work identically with ChatService
service1 = ChatService(runner1)
service2 = ChatService(runner2)
```

### Interface Segregation Principle (ISP)

Interfaces are minimal and focused:

**Base config includes only universal fields:**
```python
@dataclass
class BaseGraphConfig:
    model_id: str    # All graphs need a model
    temperature: float  # All graphs use temperature
```

**Graph-specific configs add their own fields:**
```python
@dataclass
class RAGGraphConfig(BaseGraphConfig):
    classification_model_id: str  # Only RAG needs this

@dataclass
class ReActAgentConfig(BaseGraphConfig):
    system_prompt: str  # Only ReAct needs this
```

### Dependency Inversion Principle (DIP)

High-level modules depend on abstractions:

```python
class ChatService:
    def __init__(self, runner: PregelRunner):  # Depends on protocol
        self._runner = runner

class IngestionService:
    def __init__(self, processor: DocumentProcessor, vectorstore: VectorStore):
        self._processor = processor  # Depends on protocol
```

Low-level modules implement abstractions:
```python
class JPMRagRunner(PregelRunner): ...
class UnstructuredProcessor(BaseDocumentProcessor): ...
```

---

## Key Design Patterns

### 1. Registry Pattern

Central discovery mechanism for graphs:

```python
# src/langgraph_runner/graphs/registry.py
REGISTRY: dict[str, Callable[[], PregelRunner]] = {}

def register(name: str, factory: Callable[[], PregelRunner]) -> None:
    """Register a graph factory function."""
    REGISTRY[name] = factory

def get_runner(name: str) -> PregelRunner:
    """Get a fully-wired runner instance by name."""
    return REGISTRY[name]()
```

**Benefits:**
- Late binding of graph implementations
- Dynamic discovery via imports
- No hardcoded graph lists

### 2. Factory Pattern

Each graph provides a factory function that wires dependencies:

```python
def _create_runner() -> JPMRagRunner:
    """Factory wires all dependencies."""
    retriever = _get_retriever()
    return JPMRagRunner(retriever)

register("jpm_rag", _create_runner)
```

### 3. Closure-Based Dependency Injection

Node factories capture dependencies in closures:

```python
def create_retrieval_nodes(retriever: FilteredRetriever):
    """Factory captures retriever in closure."""

    async def retrieve_forecast(state: RetrievalInput) -> dict:
        # retriever available from closure
        results = await retriever.retrieve_with_scores(query, doc_type="forecast")
        return {"results": results}

    return retrieve_forecast, ...
```

### 4. Composition Pattern

Graphs can compose other graphs as tools:

```python
# JPM RAG exposed as a tool
@tool
async def search_jpm_documents(query: str) -> str:
    result = await get_graph().ainvoke(RAGGraphInputState(query=query))
    return result["answer"]

# ReAct agent uses RAG as a tool
agent = build_react_agent(tools=[search_jpm_documents], ...)
```

**Location:** `src/langgraph_runner/graphs/jpm_react_agent/__init__.py`

---

## Module Structure

### Graph Module Template

Every graph follows a consistent structure:

```
src/langgraph_runner/graphs/{graph_name}/
├── __init__.py      # Registration: register("name", factory)
├── config.py        # GraphConfig extends BaseGraphConfig
├── state.py         # GraphState extends BaseGraphState
├── graph.py         # build_graph() function
├── runner.py        # Runner implements PregelRunner
├── prompts.py       # Graph-specific prompts
├── setup.py         # Optional: one-time setup (ingestion, etc.)
└── nodes/           # Node implementations
    ├── __init__.py
    ├── node1.py     # create_node1() factory
    └── node2.py     # create_node2() factory
```

### Existing Graph Implementations

| Graph | Type | Description |
|-------|------|-------------|
| `jpm_rag` | Stateless RAG | Document routing + retrieval + synthesis |
| `react_agent` | Building Block | Reusable ReAct agent pattern |
| `jpm_react_agent` | Composite | ReAct agent with JPM RAG as tool |

---

## Dependency Injection Patterns

### 1. Configuration-Based Injection

LangGraph's `context_schema` passes config through the graph:

```python
builder = StateGraph(
    RAGGraphState,
    input_schema=RAGGraphInputState,
    context_schema=RAGGraphConfig  # DI via context
)

# Nodes extract config at runtime
async def classify(state: RAGGraphState, config: RunnableConfig) -> dict:
    cfg = RAGGraphConfig.from_runnable_config(config)
    llm = load_chat_model(cfg.model_id)
```

### 2. Constructor Injection

Graph builders accept dependencies:

```python
def build_graph(retriever: FilteredRetriever | None = None):
    if retriever is None:
        retriever = _get_default_retriever()

    retrieve_nodes = create_retrieval_nodes(retriever)
```

### 3. Factory Registration

Registry stores factories, not instances:

```python
register("jpm_rag", lambda: JPMRagRunner())  # Factory stored
runner = get_runner("jpm_rag")  # Factory called, fresh instance
```

---

## Async Architecture

The framework is async-first:

- All graph nodes are async functions
- Services support both sync and async execution
- Streaming support via `astream()` method
- Logging context propagation via `contextvars`

```python
async def ainvoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse:
    result = await self._graph.ainvoke(input_state, config=config)
    return ChatResponse(content=result["answer"])

async def astream(self, request: ChatRequest, thread_id: str = "default") -> AsyncIterator[str]:
    async for chunk in self._runner.astream(request, thread_id=thread_id):
        yield chunk
```

---

## Extending the Framework

### Adding a New Graph

1. **Create module structure:**
```bash
mkdir -p src/langgraph_runner/graphs/my_graph/nodes
touch src/langgraph_runner/graphs/my_graph/{__init__,config,state,graph,runner,prompts}.py
```

2. **Define state (extend base):**
```python
# state.py
@dataclass
class MyGraphState(BaseGraphState):
    custom_field: str = ""
```

3. **Define config (extend base):**
```python
# config.py
@dataclass(kw_only=True)
class MyGraphConfig(BaseGraphConfig):
    custom_setting: int = 10
```

4. **Implement runner (follow protocol):**
```python
# runner.py
class MyRunner(PregelRunner):
    @property
    def name(self) -> str: ...
    def invoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse: ...
    async def ainvoke(self, request: ChatRequest, thread_id: str = "default") -> ChatResponse: ...
    async def astream(self, request: ChatRequest, thread_id: str = "default") -> AsyncIterator[str]: ...
```

5. **Register in `__init__.py`:**
```python
from langgraph_runner.graphs.registry import register
from .runner import MyRunner

register("my_graph", lambda: MyRunner())
```

6. **Import in main.py:**
```python
import langgraph_runner.graphs.my_graph  # Triggers registration
```

7. **Use:**
```bash
uv run python -m langgraph_runner --graph my_graph chat
```

### Adding a New Document Processor

Implement the `DocumentProcessor` protocol:

```python
class MyProcessor(BaseDocumentProcessor):
    def supported_extensions(self) -> set[str]:
        return {".xyz"}

    def process(self, file_path: Path) -> ProcessedDocument:
        # Custom processing
        return ProcessedDocument(documents=[...], source_file=file_path.name)
```

Use with existing ingestion:
```python
service = IngestionService(MyProcessor(), vectorstore)
```

---

## Summary

The LangGraph Runner architecture achieves extensibility through:

1. **Protocol-based design:** `PregelRunner` enables any graph type
2. **Registry pattern:** Graphs self-register, no central modification
3. **SOLID principles:** Single responsibility, open/closed, substitutability
4. **Dependency injection:** Configuration and factories enable testability
5. **Composition:** Graphs can use other graphs as tools
6. **Minimal base classes:** Only truly shared functionality in base

This design allows the framework to scale to many graph types while maintaining code quality, testability, and developer experience.
