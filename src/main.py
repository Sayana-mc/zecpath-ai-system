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


tags_metadata = [
    {
        "name": "Screening Questions",
        "description": "Standardized HR screening question repository, role-based question filtering, and multilingual question templates.",
    },
    {
        "name": "Screening Sessions",
        "description": "Candidate screening session lifecycle, pipeline creation, session status tracking, and conversation start.",
    },
    {
        "name": "Candidate Answers",
        "description": "Candidate verbal and text answer ingestion, segment tagging, and conversational dialog interactions.",
    },
    {
        "name": "Audio and Transcription",
        "description": "Candidate voice audio upload, speech-to-text processing, Whisper model transcription, and transcript cleaning.",
    },
    {
        "name": "Intent and Information Extraction",
        "description": "Natural language intent classification, entity extraction (skills, experience, notice period, salary), and answer validation.",
    },
    {
        "name": "Screening Evaluation",
        "description": "4-factor scoring rubric (Clarity, Relevance, Completeness, Consistency), behavioral indicators, and session completion.",
    },
    {
        "name": "Screening Reports",
        "description": "Recruiter-ready candidate screening reports, structured answer analysis, strengths, risks, and recommendations.",
    },
    {
        "name": "HR Interview Engine",
        "description": "AI HR interview session management, role/experience-based question bank generation, and conversation state machine.",
    },
    {
        "name": "HR Dynamic Follow-Up",
        "description": "Adaptive follow-up question triggers, completeness checks, deepening inquiries, and repetition control.",
    },
    {
        "name": "HR Communication & Behavioral Evaluation",
        "description": "Multi-factor communication fluency, grammar, vocabulary, filler penalties, hesitation tracking, and ethical safeguards.",
    },
    {
        "name": "HR Interview Scoring & Reports",
        "description": "4-factor scoring rubric, aptitude evaluation, 11-section recruiter report generation, HTML export, and hiring decisions.",
    },
    {
        "name": "ATS",
        "description": "Applicant Tracking System core: job openings, candidate ingestion, resume upload, parsing, and shortlisting.",
    },
    {
        "name": "System",
        "description": "System health checks, recruiter authentication session management, and metrics.",
    },
]

app = FastAPI(
    title="ZecPath AI Screening & Hiring System API",
    description=(
        "Production-grade local recruiter workflow API for ATS resume screening, "
        "interactive AI candidate screening, multi-factor scoring, and verifiable hiring audits."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
    )
    for path, methods in openapi_schema.get("paths", {}).items():
        if "/screening" in path or "screening-reports" in path or "/hr-interviews" in path:
            for op in methods.values():
                if isinstance(op, dict) and "tags" in op:
                    op["tags"] = [t for t in op["tags"] if t != "ATS"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", tags=["System"])
def root() -> HTMLResponse:
    page = Path(__file__).resolve().parents[1] / "static" / "index.html"
    return HTMLResponse(page.read_text(encoding="utf-8"))