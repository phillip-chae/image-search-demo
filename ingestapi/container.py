from dependency_injector import containers, providers
from celery import Celery

from shared.storage.s3 import S3
from ingestapi.config import Config, conf_path, service_name
from ingestapi.service.ingest import IngestService

cfg = Config.from_yaml(conf_path)

def get_celery(broker_url: str) -> Celery:
    from ingestworker.task import QUEUE, task_routes
    return Celery(
        service_name,
        queue=QUEUE,
        broker=broker_url,
        backend=broker_url,
        task_routes=task_routes,
    )

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    storage: providers.Provider[S3] = providers.Singleton(
        S3,
        cfg=cfg.storage
    )

    celery: providers.Provider[Celery] = providers.Singleton(
        get_celery,
        broker_url=cfg.redis.url,
    )

    ingest_service = providers.Singleton(
        IngestService,
        storage=storage,
        celery=celery,
    )