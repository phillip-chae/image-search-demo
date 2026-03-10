# Image Search Demo

Portfolio project that demonstrates a production-style image ingestion and semantic search pipeline using Python, Go, and containerized microservices.

## What This Project Shows

- End-to-end backend system design across API, async processing, storage, and search layers
- Practical microservices patterns: service boundaries, shared libraries, and independent scaling concerns
- ML-powered semantic search using vector embeddings and Milvus
- DevOps fundamentals: Docker multi-stage builds, Compose orchestration, and config-driven services

## System Overview

Two core flows drive the platform:

1. Ingestion flow
- `ingestapi` accepts image upload requests
- Jobs are queued through Redis/Celery
- `ingestworker` generates embeddings, stores image objects, and indexes vectors

2. Search flow
- `searchapi` converts text queries to embeddings and retrieves nearest matches from Milvus
- `cdnapi` serves matching image bytes from object storage

## Service Map

| Service | Language | Responsibility |
|---|---|---|
| `ingestapi` | Python (FastAPI) | Validate requests and enqueue ingestion jobs |
| `ingestworker` | Python (Celery) | Process images, generate embeddings, index/search metadata |
| `searchapi` | Python (FastAPI) | Execute text-to-vector semantic search |
| `cdnapi` | Go (Gin) | Serve image content efficiently by image ID |

Supporting infrastructure: Redis (queue), Milvus (vector DB), MinIO (object storage), Traefik (gateway/proxy).

## Technology Stack

- Backend: Python (FastAPI, Celery), Go (Gin)
- ML/Search: CLIP/Sentence Transformers, Milvus
- Storage: MinIO (S3-compatible)
- Messaging: Redis
- Infra: Docker, Docker Compose, Traefik

## Local Run (Docker)

1. Initialize local Docker resources:
- `make docker-init`
2. Build and start the stack:
- `docker compose up -d --build`

Default local endpoints:

- Frontend: `http://localhost:3000`
- Ingest API: `http://localhost:8000`
- Search API: `http://localhost:8001`
- CDN API: `http://localhost:8002`

## Why This Is Useful In A Portfolio

- Demonstrates clean layered architecture (`api/handler -> service -> repo`)
- Shows cross-language service development (Python + Go) in one system
- Reflects practical trade-offs of distributed systems (async workflows, storage/search separation)
- Highlights reproducible local environments and deployment-ready containerization

## Contact

Phillip Chae
- LinkedIn: https://www.linkedin.com/in/phillip-chae-13b1651b1/
- GitHub: https://github.com/phillip-chae
- Email: msc694@nyu.edu

This project is intended as a technical portfolio demonstration and is not production-ready.
