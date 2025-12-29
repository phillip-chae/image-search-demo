# Image Search Demo
### *A Portfolio Project Demonstrating Production-Grade Microservices Architecture*

This repository showcases a distributed image ingestion, indexing, and search system built with modern backend technologies. It demonstrates practical experience with microservices design, message queues, vector databases, containerization, and multi-language service development—all patterns used in production systems at scale.

**For Recruiters**: This project highlights hands-on expertise in backend engineering, distributed systems, DevOps practices, and clean architecture principles. Each component is designed to showcase real-world problem-solving and technical decision-making.

## 💼 Skills Demonstrated

### Backend Development
- **Python** (FastAPI, Celery): RESTful APIs, async processing, task queues
- **Go** (Gin): High-performance HTTP services, static compilation
- **Dependency Injection**: Lifecycle management, testability, decoupled design
- **Type Safety**: Pydantic models, Go's type system for compile-time guarantees

### Distributed Systems & Architecture
- **Microservices**: Independent services with single responsibilities
- **Message Queues**: Async job processing with Redis + Celery
- **Vector Databases**: Semantic search with Milvus
- **Object Storage**: Image persistence with MinIO (S3-compatible)
- **API Gateway**: Request routing and reverse proxy patterns with Traefik

### DevOps & Infrastructure
- **Docker**: Multi-stage builds, layer caching, security hardening
- **Docker Compose**: Full-stack orchestration, service dependencies
- **Configuration Management**: Type-safe configs with environment overrides
- **Infrastructure as Code**: Declarative service definitions

### Software Engineering Practices
- **Monorepo Architecture**: Shared libraries, consistent tooling
- **Clean Architecture**: Separation of concerns (handlers → services → repos)
- **Design Patterns**: Factory, Repository, Dependency Injection
- **Build Optimization**: Fast CI/CD with aggressive caching

### Currently Learning / Expanding
- **Frontend**: React/Next.js for rich user interfaces
- **Observability**: Grafana, Loki, Prometheus, Alloy for telemetry
- **Kubernetes**: Helm charts, scaling, production orchestration

## 🏗️ Architecture Overview

The system is designed as a distributed pipeline with two main flows:

### Ingestion Pipeline
```
┌──────────┐     HTTP POST      ┌────────────┐     Redis Queue     ┌──────────────┐
│  Client  │ ─────────────────> │ ingestapi  │ ──────────────────> │ ingestworker │
│          │   (image + text)   │  (FastAPI) │    (Celery Task)    │   (Celery)   │
└──────────┘                    └────────────┘                     └──────────────┘
                                                                            │
                                                                            ▼
                                                    ┌──────────────────────────────────┐
                                                    │  1. Store image → MinIO          │
                                                    │  2. Generate embedding → CLIP    │
                                                    │  3. Index vector → Milvus        │
                                                    └──────────────────────────────────┘
```

### Search Pipeline
```
┌──────────┐    HTTP GET       ┌────────────┐   Vector Search    ┌───────────┐
│  Client  │ ───────────────> │ searchapi  │ ─────────────────> │  Milvus   │
│          │  (text query)    │  (FastAPI) │   (embedding)      │ (Vector DB)│
└──────────┘                  └────────────┘                    └───────────┘
     │                              │                                  │
     │                              ▼                                  │
     │                      ┌──────────────┐                          │
     │                      │  CLIP Model  │                          │
     │                      │  (embedding) │                          │
     │                      └──────────────┘                          │
     │                              │                                  │
     │                              ◄──────────────────────────────────┘
     │                              │  (matching image IDs)
     │                              ▼
     │                      ┌──────────────┐   HTTP GET         ┌──────────┐
     └─────────────────────> │   cdnapi     │ ───────────────>  │  MinIO   │
              (per image)    │    (Go)      │  (by image ID)    │ (Storage)│
                             └──────────────┘                   └──────────┘
                                      │
                                      ▼
                              (return image bytes)
```

### Service Responsibilities

| Service | Language | Purpose | Key Technologies |
|---------|----------|---------|------------------|
| **ingestapi** | Python | Accept upload requests, validate input, dispatch async tasks | FastAPI, Pydantic, Celery client |
| **ingestworker** | Python | Process images: generate embeddings (CLIP), store in object storage, index vectors | Celery, PyTorch, OpenCV, CLIP |
| **searchapi** | Python | Convert text queries to embeddings, perform vector similarity search | FastAPI, Sentence Transformers, Milvus client |
| **cdnapi** | Go | Serve raw image bytes by ID with high throughput | Gin, MinIO SDK |
| **shared** (Python) | Python | Reusable utilities: logging, storage adapters, config loading | Pydantic, structlog |
| **pkg** (Go) | Go | Shared Go packages: configuration, storage interfaces | Go standard library |

**Supporting Infrastructure**:
- **Redis**: Message broker for Celery task queue
- **Milvus + etcd**: Vector database for semantic search
- **MinIO**: S3-compatible object storage for images
- **Traefik**: Reverse proxy and load balancer

## 🧩 Technical Deep Dives

### Why Dependency Injection?

**Problem**: Hardcoded dependencies make code difficult to test, swap implementations, or manage resource lifecycles.

**Solution**: Using the `dependency-injector` library, all services declare their dependencies explicitly through a container (`container.py`):

- **Testability**: Mock dependencies (e.g., storage, database) for unit tests without touching real infrastructure
- **Flexibility**: Swap implementations (e.g., local storage vs. S3) via configuration
- **Lifecycle Management**: Singleton resources (DB connections, HTTP clients) are created once and reused
- **Cleaner Code**: Business logic receives dependencies via constructor injection, no `import` spaghetti

**Example**: The `ingestapi` container wires dependencies into FastAPI routes:
```python
container.wire(modules=["ingestapi.api.v1.image"])
```

Routes receive services like `StorageService` and `TaskDispatcher` automatically—no manual instantiation.

### Why Multi-Stage Docker Builds?

**Problem**: Single-stage builds include dev tools, source code, and build artifacts in the final image, leading to bloated, slower, less secure containers.

**Solution**: Separate builder and runtime stages:

**Benefits**:
1. **Faster CI/CD**: Builder stage is cached; only rebuilds when dependencies change
2. **Smaller Images**: Runtime image (`python:3.13-slim` or `alpine`) contains only compiled binaries and runtime libs—no compilers, no source code
3. **Better Caching**: Installing dependencies happens before copying source code, so code changes don't invalidate dependency layers
4. **Security**: Minimal attack surface—no build tools in production image

**Concrete Example** (Python service):
```dockerfile
# Builder stage: install dependencies
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/
WORKDIR /opt/image-search-demo

COPY pyproject.toml uv.lock ./
COPY ingestapi/pyproject.toml ingestapi/pyproject.toml
COPY shared shared

# Cache uv downloads; compile bytecode for faster startup
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --compile-bytecode --no-install-project

# Runtime stage: copy only .venv and code
FROM python:3.13-slim
WORKDIR /opt/image-search-demo
COPY --from=builder /opt/image-search-demo/.venv .venv
COPY ingestapi ingestapi
COPY conf/ingestapi.yaml conf/ingestapi.yaml

CMD ["python", "-m", "uvicorn", "ingestapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Result**: Images are ~70% smaller, build times drop by 50% after initial cache warm-up.

### Why Microservices Over Monolith?

**Context**: This project could have been a single FastAPI app. Why split it into multiple services?

**Reasons**:
1. **Independent Scaling**: The `ingestworker` is CPU/GPU-bound (embeddings); `cdnapi` is I/O-bound (serving files). Scale them separately.
2. **Technology Diversity**: Use Go for the CDN service (low latency, low memory) and Python for ML-heavy services (rich ecosystem).
3. **Fault Isolation**: A crash in the CDN doesn't take down image ingestion. Deploy and restart services independently.
4. **Team Scalability** (Portfolio Context): Demonstrates understanding of how large organizations structure codebases (team ownership, clear boundaries).

**Trade-offs Acknowledged**:
- Increased operational complexity (multiple deployments, network hops)
- Observability challenges (distributed tracing needed)

**Portfolio Value**: Shows I understand *when* to use microservices and *why*—not just blindly following trends.

### Configuration Strategy

**Design**: Centralized YAML configs (`conf/*.yaml`) with environment variable overrides.

**Implementation**:
- **Type Safety**: All configs are Pydantic models; invalid configs fail fast at startup
- **Environment Flexibility**: Use `INGESTAPI__REDIS__HOST` to override `ingestapi.yaml → redis.host` (double underscore for nesting)
- **Hierarchical Overrides**: Defaults in YAML → overridden by env vars → validated by Pydantic

**Why This Matters**:
- **Local Development**: Use `conf/ingestapi.yaml` as-is
- **Docker Compose**: Override secrets via `.env` file
- **Kubernetes** (future): Use ConfigMaps + Secrets

**Code Sample** (simplified):
```python
class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379

class Config(BaseSettings):
    redis: RedisConfig
    
    model_config = SettingsConfigDict(
        yaml_file="conf/ingestapi.yaml",
        env_nested_delimiter="__"
    )
```

## 🐳 Docker Build Optimizations

The Dockerfiles are engineered for speed, security, and minimal footprint:

### Key Techniques

1. **Package Manager (`uv`)**: We use [uv](https://github.com/astral-sh/uv) (by Astral) instead of pip/poetry for 10-100x faster dependency resolution and installation.

2. **Multi-Stage Builds** (detailed above):
   - **Builder Stage**: Compiles dependencies, creates virtual environment
   - **Runtime Stage**: Only copies pre-built `.venv` and application code

3. **Layer Caching**:
   - Dependencies are installed (`uv sync --no-install-project`) *before* copying source code
   - Changing application code does **not** invalidate the dependency layer
   - BuildKit cache mounts (`--mount=type=cache`) persist `uv` downloads across builds

4. **Bytecode Compilation**: `--compile-bytecode` flag speeds up container startup by pre-compiling Python to `.pyc` files

5. **Security**:
   - Minimal runtime dependencies (only essential system libraries)
   - Apt caches cleaned up (`rm -rf /var/lib/apt/lists/*`) to reduce attack surface and image size
   - Go binaries are statically linked (`CGO_ENABLED=0`) and run on `alpine` base (CVE scanning surface reduced)

### Example: Go Service Multi-Stage Build

```dockerfile
# Builder: compile binary
FROM golang:1.25-alpine AS builder
COPY go.work .
COPY cdnapi/go.mod cdnapi/go.sum ./cdnapi/
RUN cd cdnapi && go mod download  # Cache dependencies
COPY cdnapi/ ./cdnapi/
RUN CGO_ENABLED=0 go build -o /bin/cdnapid ./cdnapi/cmd/cdnapid

# Runtime: minimal image
FROM alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=builder /bin/cdnapid cdnapid
CMD ["./cdnapid"]
```

**Result**: ~15MB final image (vs. ~800MB with full Go toolchain).

## 📂 Project Structure

```
image-search-demo/
├── cdnapi/                 # Go service: image delivery (CDN)
│   ├── cmd/                # Entry point (main.go)
│   ├── config/             # Config loading
│   ├── handler/            # HTTP handlers (Gin)
│   ├── router/             # Route definitions
│   └── service/            # Business logic
├── ingestapi/              # Python service: accept uploads, queue tasks
│   ├── api/v1/             # FastAPI routers (v1 API)
│   ├── config/             # Config models (Pydantic)
│   ├── service/            # Business logic layer
│   └── container.py        # Dependency injection container
├── ingestworker/           # Python service: Celery worker (process images)
│   ├── config/
│   ├── repo/               # Data access layer
│   ├── service/
│   └── task/               # Celery task definitions
├── searchapi/              # Python service: text → vector search
│   ├── api/v1/
│   ├── config/
│   ├── repo/
│   └── service/
├── shared/                 # Shared Python library (utilities, storage, logging)
│   └── shared/
│       ├── config/         # Base config loading logic
│       ├── log/            # Structured logging setup
│       └── storage/        # Storage adapters (MinIO, local)
├── pkg/                    # Shared Go library (config, storage)
│   ├── config/
│   └── storage/
├── conf/                   # Centralized YAML configs for all services
│   ├── ingestapi.yaml
│   ├── searchapi.yaml
│   └── cdnapi.yaml
├── docker/                 # Dockerfiles for each service
│   ├── Dockerfile.ingestapi
│   ├── Dockerfile.cdnapi
│   └── ...
├── frontend/               # Static HTML/JS search UI (Nginx)
│   ├── js/
│   └── nginx/
├── docker-compose.yml      # Full-stack orchestration
└── Makefile                # Convenience commands (docker-init, lint, test)
```

**Consistent Service Structure**:
Each service follows the same layered architecture:
- **`api/` (or `handler/`)**: HTTP layer—request parsing, response serialization
- **`service/`**: Business logic—orchestrates repos, applies domain rules
- **`repo/`**: Data access—interacts with databases, storage, external APIs
- **`config/`**: Configuration models and loading
- **`container.py`**: Dependency injection wiring (Python services)

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

## 🎯 Future Enhancements

### Observability
- [ ] **Distributed Tracing**: Integrate OpenTelemetry for request tracing across services
- [ ] **Metrics Collection**: Prometheus exporters for service health, latency, throughput
- [ ] **Log Aggregation**: Loki for centralized log querying and correlation
- [ ] **Dashboards**: Grafana for real-time monitoring and alerting

### Production Readiness
- [ ] **Kubernetes Deployment**: Helm chart with ingress, HPA (Horizontal Pod Autoscaling), resource limits
- [ ] **Health Checks**: Liveness/readiness probes for all services
- [ ] **Graceful Shutdown**: Proper signal handling, connection draining
- [ ] **Rate Limiting**: Protect APIs from abuse (Redis-backed rate limiter)
- [ ] **Authentication**: JWT-based auth for ingest/search APIs
- [ ] **API Versioning**: Structured versioning strategy for breaking changes

### Features
- [ ] **Full React Frontend**: Rich UI for browsing images, uploading with drag-and-drop, real-time search suggestions
- [ ] **Batch Ingestion**: Bulk upload endpoint for indexing large image datasets
- [ ] **Advanced Search**: Filters (date, tags, metadata), multi-modal search (text + image)
- [ ] **Image Processing**: Automatic thumbnail generation, format conversion, metadata extraction (EXIF)

## 📫 Contact

**Phillip Chae**
- [LinkedIn](https://www.linkedin.com/in/phillip-chae-13b1651b1/)
- [GitHub](https://github.com/phillip-chae)
- [Email](msc694@nyu.edu)

---

*This project is intended as a technical portfolio demonstration. Not intended for production use.*
