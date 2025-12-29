
BUILD_TIME := $(shell date +%Y-%m-%dT%T%z)
GIT_REV := $(shell git rev-parse --short HEAD)
PROJ_ROOT_DIR := $(dir $(realpath $(MKFILE_DIR)))

include ${PROJ_ROOT_DIR}version

# ======================================================
# Docker Inits
.PHONY: docker-init
docker-init:
	docker volume create demo-minio || true && \
	docker volume create demo-milvus-etcd || true && \
	docker volume create demo-milvus || true && \
	docker volume create demo-redis || true && \
	docker network create demo-network || true

# ======================================================
# Swagger (Swaggo)

.PHONY: swagger-cdnapi
swagger-cdnapi:
	cd cdnapi && \
	$$(go env GOPATH)/bin/swag init -g main.go \
		-o docs \
		-d cmd/cdnapid,handler/api,router,service,config,model &&\
	cd ..

# ======================================================
# Docker Builds

INGESTAPI_NAME := ingestapi
.PHONY: docker-build-ingestapi
docker-build-ingestapi:
	docker build . -f docker/Dockerfile.${INGESTAPI_NAME} -t demo/${INGESTAPI_NAME}:${VER} \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--build-arg GIT_REV=$(GIT_REV) \
		--build-arg NAME=$(INGESTAPI_NAME) \
		--build-arg VER=$(VER)

INGESTWORKER_NAME := ingestworker
.PHONY: docker-build-ingestworker
docker-build-ingestworker:
	docker build . -f docker/Dockerfile.${INGESTWORKER_NAME} -t demo/${INGESTWORKER_NAME}:${VER} \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--build-arg GIT_REV=$(GIT_REV) \
		--build-arg NAME=$(INGESTWORKER_NAME) \
		--build-arg VER=$(VER)

.PHONY: docker-build-ingestworker-cpu
docker-build-ingestworker-cpu:
	docker buildx build . -f docker/Dockerfile.${INGESTWORKER_NAME}.cpu \
		-t demo/${INGESTWORKER_NAME}:${VER}-cpu \
		--platform linux/amd64 \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--build-arg GIT_REV=$(GIT_REV) \
		--build-arg NAME=$(INGESTWORKER_NAME) \
		--build-arg VER=$(VER)

SEARCHAPI_NAME := searchapi
.PHONY: docker-build-searchapi
docker-build-searchapi:
	docker build . -f docker/Dockerfile.${SEARCHAPI_NAME} -t demo/${SEARCHAPI_NAME}:${VER} \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--build-arg GIT_REV=$(GIT_REV) \
		--build-arg NAME=$(SEARCHAPI_NAME) \
		--build-arg VER=$(VER)

.PHONY: docker-build-searchapi-cpu
docker-build-searchapi-cpu:
	docker buildx build . -f docker/Dockerfile.${SEARCHAPI_NAME}.cpu \
		-t demo/${SEARCHAPI_NAME}:${VER}-cpu \
		--platform linux/amd64 \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--build-arg GIT_REV=$(GIT_REV) \
		--build-arg NAME=$(SEARCHAPI_NAME) \
		--build-arg VER=$(VER)

CDNAPINAME := cdnapi
.PHONY: docker-build-cdnapi
docker-build-cdnapi: swagger-cdnapi
	docker build . -f docker/Dockerfile.${CDNAPINAME} -t demo/${CDNAPINAME}:${VER} \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--build-arg GIT_REV=$(GIT_REV) \
		--build-arg NAME=$(CDNAPINAME) \
		--build-arg VER=$(VER)

.PHONY: docker-build
docker-build: docker-build-ingestapi docker-build-ingestworker docker-build-searchapi docker-build-cdnapi

.PHONY: docker-build-cpu
docker-build-cpu: docker-build-ingestworker-cpu docker-build-searchapi-cpu docker-build-ingestapi docker-build-cdnapi

# ======================================================
# Docker Compose
.PHONY: docker-compose-up
docker-compose-up:
	export IMAGE_TAG=${VER} && \
	docker-compose up -d
		
.PHONY: docker-compose-down
docker-compose-down:
	export IMAGE_TAG=${VER} && \
	docker-compose down 

