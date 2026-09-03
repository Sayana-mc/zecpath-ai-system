import logging
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)

from .errors import ATSAPIError
from .jobs import create_job, get_job, update_job
from .schemas import (
    JobStatusResponse,
    ParseResponse,
    ResumeUploadResponse,
    ScoreRequest,
    ScoreResponse,
    ShortlistRequest,
    ShortlistResponse,
)
from .services import (
    calculate_score,
    parse_resume,
    shortlist_candidates,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["ATS"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def process_resume_job(job_id: str, file_path: str) -> None:
    """Process an uploaded resume asynchronously."""

    try:
        update_job(job_id, "PROCESSING")

        parsed_text = parse_resume(file_path)

        update_job(
            job_id,
            "COMPLETED",
            result={
                "parsed_text": parsed_text,
            },
        )

        logger.info("Resume processing completed: %s", job_id)

    except Exception as exc:
        logger.exception("Resume processing failed: %s", job_id)

        update_job(
            job_id,
            "FAILED",
            error=str(exc),
        )


@router.get("/health")
def health_check():
    """API health endpoint."""

    return {
        "status": "healthy",
        "service": "ZecPath ATS API",
        "version": "1.0.0",
    }


@router.post(
    "/resumes/upload",
    response_model=ResumeUploadResponse,
)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a resume and create an asynchronous processing job."""

    allowed_extensions = {".pdf", ".docx", ".txt"}

    extension = Path(file.filename or "").suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported resume format. Use PDF, DOCX, or TXT.",
        )

    job_id = create_job(file.filename or "resume")

    destination = UPLOAD_DIR / f"{job_id}{extension}"

    content = await file.read()
    destination.write_bytes(content)

    background_tasks.add_task(
        process_resume_job,
        job_id,
        str(destination),
    )

    logger.info(
        "Resume uploaded. job_id=%s filename=%s",
        job_id,
        file.filename,
    )

    return ResumeUploadResponse(
        job_id=job_id,
        filename=file.filename or "resume",
        status="QUEUED",
        message="Resume uploaded and queued for processing.",
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
)
def job_status(job_id: str):
    """Get asynchronous processing status."""

    try:
        job = get_job(job_id)

        return JobStatusResponse(
            job_id=job["job_id"],
            status=job["status"],
            result=job["result"],
            error=job["error"],
        )

    except ATSAPIError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "error": exc.error_code,
                "message": exc.message,
            },
        )


@router.post(
    "/resumes/parse",
    response_model=ParseResponse,
)
def parse_resume_endpoint(request: dict):
    """Parse a previously uploaded resume."""

    job_id = request.get("job_id")

    if not job_id:
        raise HTTPException(
            status_code=400,
            detail="job_id is required.",
        )

    try:
        job = get_job(job_id)

        result = job.get("result") or {}

        return ParseResponse(
            job_id=job_id,
            status=job["status"],
            parsed_text=result.get("parsed_text", ""),
            message="Resume parsing result retrieved.",
        )

    except ATSAPIError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "error": exc.error_code,
                "message": exc.message,
            },
        )


@router.post(
    "/candidates/score",
    response_model=ScoreResponse,
)
def score_candidate(request: ScoreRequest):
    """Score a candidate."""

    candidate = {
        "candidate_id": request.candidate_id,
        "score": 0,
    }

    score = calculate_score(candidate)

    return ScoreResponse(
        job_id=request.job_id,
        candidate_id=request.candidate_id,
        score=score,
        status="SCORED",
        message="Candidate scoring completed.",
    )


@router.post(
    "/candidates/shortlist",
    response_model=ShortlistResponse,
)
def shortlist(request: ShortlistRequest):
    """Shortlist candidates above the configured score threshold."""

    candidates = shortlist_candidates(
        request.candidates,
        request.minimum_score,
    )

    return ShortlistResponse(
        job_id=request.job_id,
        status="SHORTLISTED",
        shortlisted_count=len(candidates),
        candidates=candidates,
        message="Candidate shortlisting completed.",
    )