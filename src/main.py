import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from . import database
from .api import router, system_router
from .logging_config import configure_logging


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.initialize_database()
    interrupted = database.fail_interrupted_processing_jobs()
    if interrupted:
        logger.warning("Marked %s interrupted resume job(s) as failed", interrupted)
    yield


app = FastAPI(
    title="ZecPath ATS API",
    description=(
        "Local recruiter workflow API for job openings, candidate applications, "
        "resume extraction, transparent skill matching, and human-reviewed shortlists."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(system_router)
app.include_router(router)


@app.get("/", tags=["System"])
def root() -> HTMLResponse:
    page = Path(__file__).resolve().parents[1] / "static" / "index.html"
    return HTMLResponse(page.read_text(encoding="utf-8"))