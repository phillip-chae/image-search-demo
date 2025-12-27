from celery import Celery
from celery.result import AsyncResult
from logging import getLogger
from uuid_extensions import uuid7str
from typing import cast

from shared.storage.s3 import S3
from shared.constant import INGEST_BUCKET
from ingestworker.task import INGEST_TASK
from . import StorageUploadError, CeleryTaskError

logger = getLogger(__name__)

class IngestService:
        
    def __init__(
        self, 
        storage: S3,
        celery: Celery
    ):
        if not storage.check_connection(INGEST_BUCKET):
            storage.create_bucket(INGEST_BUCKET)

        self.storage = storage
        self.celery = celery

    async def create_ingest(
        self, 
        file: bytes, 
        file_name: str
    ) -> str:
        """Create an ingest task to process the given file."""

        key = uuid7str()

        if not self.storage.upload(INGEST_BUCKET, file, key):
            logger.error("failed to upload file to storage", extra={
                "key": key, 
                "bucket": INGEST_BUCKET    
            })
            raise StorageUploadError("failed to upload file to storage")

        try:
            result = cast(AsyncResult, self.celery.send_task(
                INGEST_TASK,
                args=[key],
            ))

        except Exception as e:
            logger.error("failed to create ingest task", exc_info=e)
            raise CeleryTaskError("failed to create ingest task") from e

        logger.info(f"Ingest task created with id: {result.id}")
        return cast(str, result.id)
    
    async def read_ingest(self, task_id: str) -> dict | None:
        """Read the status of an ingest task by its ID."""
        self.celery.AsyncResult
        try:
            result = cast(AsyncResult, self.celery.AsyncResult(task_id))

        except Exception as e:
            logger.error("failed to read ingest task", exc_info=e)
            raise CeleryTaskError("failed to read ingest task") from e

        if not result:
            return None

        response = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.successful() else None,
            "error": str(result.result) if result.failed() else None,
        }

        return response