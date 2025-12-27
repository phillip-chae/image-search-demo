from dependency_injector.wiring import inject, Provide
from celery import Task
import time
from io import BytesIO

from shared.storage.s3 import S3
from shared.constant import INGEST_BUCKET
from shared.logger import get_logger
from shared.model.index import IndexResponse
from ingestworker.container import Container
from ingestworker.main import app
from ingestworker.service.ingest import IngestService
from . import QUEUE, INGEST_TASK

logger = get_logger(__name__)

class StorageError(Exception):
    """Custom exception for storage-related errors."""
    pass

class IngestError(Exception):
    """Custom exception for ingest-related errors."""
    pass

@app.task(queue=QUEUE, name=INGEST_TASK, bind=True, pydantic=True)
@inject
def ingest_task(
    self: Task, # In case we need to access task info or do retries
    key: str,
    file_name: str,
    # Dependency Injection
    s3: S3 = Provide[Container.s3],
    ingest_service: IngestService = Provide[Container.ingest_service]) -> IndexResponse:
    """Ingest task to process data and send to index service."""

    t = time.time()
    resp = IndexResponse()

    try:
        image_bytes = s3.download(INGEST_BUCKET, key)
        if not image_bytes:
            logger.error("failed to download image from storage", extra={
                "key": key, 
                "bucket": INGEST_BUCKET    
            })
            raise StorageError("failed to download image from storage")
        
        if response := ingest_service.ingest(BytesIO(image_bytes), file_name):
            resp = response

        if resp.detail:
            raise IngestError(resp.detail)
    
    except Exception as e:
        logger.error("failed to ingest data, deleting image from storage", exc_info=e, extra={
            "key": key,
            "bucket": INGEST_BUCKET
        })
        if not s3.delete(INGEST_BUCKET, key):
            logger.error("failed to delete image from storage after ingest failure", extra={
                "key": key,
                "bucket": INGEST_BUCKET
            })

        resp.detail = str(e)

    finally:
        resp.elapsed_time = time.time() - t
    
    return resp
        