# ReguDrift AI - Enterprise Development Standards

This document establishes the official enterprise-wide design principles, coding standards, and architectural patterns for the **ReguDrift AI** application. All modules, interfaces, and implementations must strictly adhere to these standards.

---

## 1. Core Architectural Pillars

### 1.1 Asynchronous-First Design
*   **Event Loop Integrity**: The main execution thread must never be blocked by CPU-bound or synchronous I/O operations.
*   **Thread Offloading**: Any synchronous library (e.g., `pypdf` for PDF parsing, `faiss` for CPU-bound similarity search, standard synchronous file writes) must be offloaded to a thread pool using `asyncio.to_thread` or a dedicated `ThreadPoolExecutor`.
*   **Async Network Clients**: All HTTP/gRPC network traffic (e.g., calls to Gemini APIs, Qdrant cluster connections, external tools) must utilize async clients (e.g., `httpx.AsyncClient` or `AsyncQdrantClient`).

### 1.2 Strict Type-Hinting & Schema Validation
*   **Static Typing**: Every function, variable, and class must have explicit type-hints under PEP 484/585. Use `typing` and `typing_extensions` where necessary.
*   **Data Validation Layer**: Leverage **Pydantic V2** (`pydantic` and `pydantic-settings`) for payload and configuration parsing.
*   **No Raw Dicts in Domain logic**: Use Pydantic models for structured business data instead of raw dictionaries to guarantee type safety and automated validation.

### 1.3 Immutable and Idempotent Operations
*   **Deterministic Keying**: Every chunk ingested must generate a deterministic, collision-resistant identifier (SHA-256) based on its normalized text content and parent document attributes. This ensures ingestion idempotency and prevents double-indexing.
*   **State Integrity**: Agents must progress through immutable state changes. Every transition must yield a new validated state model, which is saved or serialized.

---

## 2. Directory Structure Conventions

A clean, domain-driven structure is required for a scalable production service:

```
regudrift/
├── __init__.py
├── main.py                  # FastAPI Application Entrypoint
├── api/                     # API Routing & Dependency Injection
│   ├── __init__.py
│   ├── dependencies.py      # Core DI providers (clients, services)
│   └── v1/
│       ├── __init__.py
│       ├── router.py        # Version 1 root router
│       └── endpoints/       # Specific API endpoints
│           ├── __init__.py
│           ├── ingestion.py
│           ├── vector.py
│           └── agent.py
├── core/                    # Core Business Logic & Infrastructure
│   ├── __init__.py
│   ├── config.py            # Pydantic Settings layer
│   ├── errors.py            # Enterprise-wide Exception system
│   ├── logging.py           # Structured JSON/Console logging setup
│   ├── utils/
│   │   ├── __init__.py
│   │   └── crypto.py        # Cryptographic/Hashing utilities
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── parser.py        # Async Document streams & parsing
│   ├── vector/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract Retrieval Interfaces
│   │   ├── faiss_service.py # Local CPU-bound Vector Retrieval
│   │   └── qdrant_service.py# Cloud/Production Vector Retrieval
│   └── agent/
│       ├── __init__.py
│       ├── schemas.py       # Pydantic state & validation schemas
│       └── orchestrator.py  # Planner-Executor orchestration loop
└── tests/                   # Strict unit & integration tests
```

---

## 3. Error Handling and Exceptions

*   **Global Exception Handler**: FastAPI must have custom middleware/handlers to catch all standard internal exceptions (`ReguDriftException`) and map them to HTTP 4xx/5xx responses with structured JSON bodies.
*   **No Bare Excepts**: Never use `except:`. Always catch specific exceptions (e.g., `ValueError`, `HTTPStatusError`) and log them with full stack traces in debug environments.
*   **Error Schemas**: Standardized error response model:
    ```python
    class ErrorResponse(BaseModel):
        code: str          # e.g., "RETRIEVAL_ERROR"
        detail: str        # Human-readable message
        timestamp: str     # ISO format
        meta: dict = {}    # Optional debugging context
    ```

---

## 4. Configuration and Environment Management

*   **Pydantic Settings**: All configurations are managed via a single class inheriting from `BaseSettings` (from `pydantic-settings`).
*   **Environment Variables**: Raw `os.environ` should never be queried directly in the business logic; access configurations strictly through the dependency-injected Settings object.
*   **Secret Masking**: Secrets must be stored as `SecretStr` to prevent accidental logging.

---

## 5. Structured Logging Guidelines

*   **JSON Logging in Production**: Logs must be structured (key-value pairs) to allow easy indexing by log aggregation services (ELK, Datadog).
*   **Context Propagation**: Log statements in async contexts should propagate a unique `request_id` or `trace_id` down the event loop.
*   **Level Adherence**:
    *   `INFO`: High-level flow tracing (e.g., "Document parsed, 42 chunks generated").
    *   `DEBUG`: Granular details (e.g., specific hashes, similarity search scores).
    *   `WARNING`: Recoverable errors (e.g., connection retry, fallback to local vector search).
    *   `ERROR`: Failure of operations requiring immediate attention (e.g., Gemini API key rejection).
