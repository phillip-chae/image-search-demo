from celery import Celery
from celery.signals import worker_process_init
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from ingestworker.config import service_name, cfg
from ingestworker.container import Container
from ingestworker.task import task_routes

logger = logging.getLogger(__name__)

app = Celery(
    service_name,
    broker=cfg.redis.url,
    backend=cfg.redis.url,
    include = [
        "ingestworker.task.ingest",
    ]
)

app.conf.update(task_routes = task_routes)

container = Container()
container.wire(packages=[
    "ingestworker.task",
    "ingestworker.service",
])

@worker_process_init.connect
def init_svcs(**kwargs):
    """Initialize services in worker process. Before task execution."""
    logger.info("preloading services in worker process")
    _ = container.ingest_service()
    logger.info("services preloaded successfully")


def init():
    from ingestworker import project_root
    from pathlib import Path
    from shared.model.index import INDEX_BUCKET
    from shared.storage.s3 import S3
    from ingestworker.repo.image import ImageRepository

    # Initialize storage
    s3 = S3(cfg.s3)
    if not s3.check_connection(INDEX_BUCKET):
        s3.create_bucket(INDEX_BUCKET)

    # Initialize dbs
    ImageRepository.init(cfg.milvus_db)

    # Add sample data ingestion
    svc = container.ingest_service()
    sample_images = Path(project_root / "data" / "train").rglob("*.JPEG")
    for img_path in sample_images:
        logger.info(f"pre-ingesting sample image: {img_path}")
        svc.ingest(img_path, img_path.name)

if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Ingest Worker")
    parser.add_argument("--init", action="store_true", help="Pre-ingest sample data and exit")
    args = parser.parse_args()
    if args.init:
        init()
    print("Exiting ingest worker. Do not start it directly; use 'celery -A ingestworker.main worker --loglevel=info'")
    sys.exit(0)