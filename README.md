# Image Search Demo

This repository demonstrates a production-grade microservice architecture for image ingestion + indexing, plus a text-query search API that returns matching images. It’s intended as a portfolio showcase of modern Python/Go service design, dependency injection, configuration management, and containerization.

## 🏗️ Architecture Overview

The system is designed as a distributed pipeline:

*   **`ingestapi`**: A FastAPI-based entry point that accepts data and dispatches tasks. It handles request validation and queues jobs for asynchronous processing.
*   **`ingestworker`**: A Celery worker that consumes tasks from the queue (Redis). It handles heavy lifting, data transformation, and storage operations.
*   **`searchapi`**: A FastAPI service that converts text queries into embeddings and performs vector search (Milvus) to return matching image IDs.
*   **`cdnapi`**: A Go (Gin) service that serves raw image bytes by image ID (backed by object storage).
*   **`shared`**: A core library containing common utilities, configuration schemas, and shared domain logic to ensure consistency across services.

Supporting infrastructure (via Docker Compose): Redis (queue), Milvus + etcd (vector DB), and MinIO (object storage).

## 🧩 Code Patterns & Design Choices

### Dependency Injection (DI)
The project utilizes the `dependency-injector` library to manage component lifecycles and dependencies.
*   **Declarative Containers**: Services and resources are defined in `container.py` using `containers.DeclarativeContainer`.
*   **Wiring**: The `container.wire()` method is used to inject dependencies into FastAPI routers and Celery tasks, keeping business logic decoupled from infrastructure concerns.
*   **Singleton Pattern**: Heavy resources (like Storage clients or Database connections) are managed as Singletons to ensure efficient resource usage.

### Configuration Management
Configuration is handled via `pydantic-settings` with custom extensions for YAML support.
*   **Type Safety**: All configurations are defined as Pydantic models (`BaseConfig`), ensuring type safety and validation at startup.
*   **Hierarchical Loading**: The `BaseConfig` class in `shared/config` implements a custom source to load from YAML files (`conf/*.yaml`) while allowing overrides via environment variables (using `__` as a nested delimiter).
*   **Centralized Config**: Shared configuration logic resides in the `shared` library, promoting code reuse.

### Project Layout
The repository follows a monorepo-style structure:
*   **`shared/`**: Contains reusable code (logging, storage adapters, config logic).
*   **`service_name/`**: Each service has its own directory with a standard structure (`api/`, `service/`, `config/`, `container.py`).
*   **`conf/`**: Centralized location for service configuration files.

## 🐳 Docker Optimizations

The Dockerfiles are engineered for speed, security, and minimal footprint:

*   **Package Manager (`uv`)**: We use `uv` (by Astral) instead of pip/poetry for lightning-fast dependency resolution and installation.
*   **Multi-Stage Builds**:
    *   **Builder Stage**: Compiles dependencies and creates a virtual environment. It uses `RUN --mount=type=cache` to cache `uv` artifacts, significantly speeding up re-builds.
    *   **Final Stage**: A pristine `python:3.13-slim` image where only the pre-built `.venv` and application code are copied.
*   **Layer Caching**: Dependencies are installed (`uv sync --no-install-project`) *before* copying the source code. This ensures that changing application code does not invalidate the dependency layer.
*   **Bytecode Compilation**: The `--compile-bytecode` flag is used during installation to improve container startup time.
*   **Security**: Minimal runtime dependencies are installed, and apt caches are cleaned up (`rm -rf /var/lib/apt/lists/*`) to reduce attack surface and image size.

## 🚀 Todo / Roadmap

The following components and features are planned for implementation:

- [x] **Minimal Frontend**: Static search page (Nginx) that calls `searchapi` then renders images from `cdnapi`.
- [ ] **Frontend (Full UI)**: Develop a richer UI (React/Next.js) for interacting with the ingestion and search APIs.
- [ ] **Observability Stack**:
    -   Deploy **Grafana** for visualization.
    -   Configure **Loki** for log aggregation.
    -   Set up **Prometheus** for metrics collection.
    -   Implement **Grafana Alloy** for telemetry data forwarding.
- [ ] **Orchestration**:
    - [x]  **Docker Compose**: Bring up the core stack (Redis, Milvus, MinIO, APIs) with a single command.
    -   **Kubernetes**: Develop a production-ready **Helm Chart** to demonstrate Kubernetes deployment skills, including ingress, scaling policies, and resource limits.

## 🚀 Running Locally (Docker)

Bring up the stack:

1. Create required Docker volumes/network:
    - `make docker-init`
2. Start services:
    - `docker compose up -d --build`

Useful local ports (default compose):

- `ingestapi`: `http://localhost:8000`
- `searchapi`: `http://localhost:8001`
- `cdnapi`: `http://localhost:8002`
- `frontend`: `http://localhost:3000`

## 🔎 Minimal Search Frontend

This repo includes a small static search page served by an Nginx container. It avoids browser CORS issues by reverse-proxying API calls through the same origin:

- UI: `http://localhost:3000`
- Search request (proxied to `searchapi`): `GET /api/v1/image/search?text=...`
- Images (proxied to `cdnapi`): `GET /images/{image_id}`

Start it with:

- `docker compose up -d --build frontend`
