from pathlib import Path
from typing import BinaryIO

from shared.storage.s3 import S3
from shared.logger import get_logger
from shared.hash.phash import Phasher
from shared.model.index import IndexItem, IndexResponse, INDEX_BUCKET
from ingestworker.repo.image import ImageRepository

logger = get_logger(__name__)

class IngestService:
    def __init__(
        self,
        repo: ImageRepository,
        s3: S3,
    ):
        from shared.ai.encode import ClipEncoder
        from magic import Magic
        self.repo = repo
        self.s3 = s3
        self.mime_magic = Magic(mime=True)
        self.encoder = ClipEncoder()
        self.phasher = Phasher()
    
    def ingest(
        self, 
        image_file: str | Path | BinaryIO, 
        file_name: str
    ) -> IndexResponse:
        resp = IndexResponse()

        try:
            if isinstance(image_file, (str, Path)):
                file = open(image_file, "rb")
                should_close = True
            else:
                file = image_file
                should_close = False
            try:
                embedding = self.encoder.encode_image(file)
                phash = self._calculate_phash(file)
                image_bytes = file.read()
                
            finally:
                if should_close:
                    file.close()

            data = IndexItem(
                id=phash,
                file_name=file_name,
                vector=embedding
            )
            logger.debug("Ingested data prepared", extra={
                "phash": phash,
                "file_name": file_name
            })
            # Because no interaction with other dbs and data types are necessary, I handle the storing in the same function;
            # in real implementation, I would separate them with a separate indexing application/service
            ids = self.repo.create([data])
            # In real implementation, I would determine image type based on magic, and mark the metadata to the object
            self.s3.upload(INDEX_BUCKET, image_bytes, phash, extra_args={
                "ContentType": self.mime_magic.from_buffer(image_bytes)
            })
            
            logger.debug("data indexed successfully", extra={
                "phash": phash,
                "file_name": file_name,
                "ids": ids
            })
        except Exception as e:
            logger.error("failed to ingest data", exc_info=e)
            resp.detail = str(e)
            
        finally:
            return resp
    
    def _calculate_phash(self, image_file: BinaryIO) -> str:
        image_file.seek(0)
        phash = self.phasher(image_file)
        image_file.seek(0)
        return phash

    