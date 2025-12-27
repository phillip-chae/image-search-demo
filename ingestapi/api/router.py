from fastapi import APIRouter

from .v1.routes import ingest

router = APIRouter()
router.include_router(ingest.router)