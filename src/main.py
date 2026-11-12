import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

try:
    from . import database
except ImportError:
    from src import database
from .api import router, system_router
from .logging_config import configure_logging
from .observability import observability


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


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000.0
    path = request.url.path
    if path.startswith("/api/"):
        observability.log_api_request(
            endpoint=path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
    return response


app.include_router(system_router)
app.include_router(router)


@app.get("/", tags=["System"])
def root() -> HTMLResponse:
    page = Path(__file__).resolve().parents[1] / "static" / "index.html"
    return HTMLResponse(page.read_text(encoding="utf-8"))