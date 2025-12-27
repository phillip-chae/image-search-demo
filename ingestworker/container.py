from dependency_injector import containers, providers

from shared.storage.s3 import S3

from ingestworker.config import cfg
from ingestworker.repo.image import ImageRepository
from ingestworker.service.ingest import IngestService

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    s3: providers.Provider[S3] = providers.Singleton(
        S3,
        cfg=cfg.s3
    )

    repo: providers.Provider[ImageRepository] = providers.Singleton(
        ImageRepository,
        cfg=cfg.milvus_db
    )

    ingest_service = providers.Singleton(
        IngestService,
        repo=repo,
        s3=s3,
    )