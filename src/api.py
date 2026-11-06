import logging
import secrets
import sqlite3
import uuid
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)

from . import database
from .auth import (
    SESSION_COOKIE_NAME,
    SESSION_LIFETIME_SECONDS,
    authentication_is_configured,
    is_configured_recruiter,
    require_recruiter,
    verify_recruiter_credentials,
)
from .errors import ATSAPIError, InvalidResumeError
from .jobs import create_job, get_job, update_job
from .schemas import (
    CandidateCreate,
    CandidateResponse,
    CandidateUpdate,
    JobStatusResponse,
    OpeningCreate,
    OpeningResponse,
    OpeningUpdate,
    ParseRequest,
    ParseResponse,
    PersistedShortlistRequest,
    RecruiterLoginRequest,
    RecruiterSessionResponse,
    ResumeUploadResponse,
    ScoreRequest,
    ScoreResponse,
    ShortlistRequest,
    ShortlistResponse,
    ShortlistedCandidate,
    ScreeningReportRequest,
    ScreeningReportResponse,
)
from .services import (
    calculate_candidate_match,
    parse_resume,
    shortlist_candidates,
)


logger = logging.getLogger(__name__)

system_router = APIRouter(
    prefix="/api/v1",
    tags=["System"],
)

router = APIRouter(
    prefix="/api/v1",
    tags=["ATS"],
    dependencies=[Depends(require_recruiter)],
)

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
MAX_RESUME_BYTES = 5 * 1024 * 1024


def _opening_or_404(opening_id: str) -> dict:
    opening = database.get_opening(opening_id)
    if opening is None:
        raise HTTPException(status_code=404, detail="Job opening not found.")
    return opening


def _candidate_or_404(candidate_id: str) -> dict:
    candidate = database.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate


@system_router.post("/auth/session", response_model=RecruiterSessionResponse)
def create_recruiter_session(
    credentials: RecruiterLoginRequest,
    request: Request,
    response: Response,
) -> RecruiterSessionResponse:
    if not authentication_is_configured():
        raise HTTPException(
            status_code=503,
            detail="Recruiter authentication is not configured.",
        )

    client_host = request.client.host if request.client else "unknown"
    attempt_key = database.recruiter_login_key(client_host, credentials.username)
    if database.recruiter_login_blocked(attempt_key):
        raise HTTPException(
            status_code=429,
            detail="Too many sign-in attempts. Try again in 15 minutes.",
            headers={"Retry-After": "900"},
        )

    authenticated_username = verify_recruiter_credentials(
        credentials.username, credentials.password
    )
    if authenticated_username is None:
        if database.record_recruiter_login_failure(attempt_key):
            raise HTTPException(
                status_code=429,
                detail="Too many sign-in attempts. Try again in 15 minutes.",
                headers={"Retry-After": "900"},
            )
        raise HTTPException(
            status_code=401,
            detail="Valid recruiter credentials are required.",
        )

    database.clear_recruiter_login_attempts(attempt_key)
    token = secrets.token_urlsafe(32)
    expires_at = database.create_recruiter_session(
        token, authenticated_username, SESSION_LIFETIME_SECONDS
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_LIFETIME_SECONDS,
        expires=SESSION_LIFETIME_SECONDS,
        path="/api/v1",
        secure=urlsplit(str(request.base_url)).scheme == "https",
        httponly=True,
        samesite="strict",
    )
    return RecruiterSessionResponse(
        authenticated=True,
        username=authenticated_username,
        expires_at=expires_at,
    )


@system_router.get("/auth/session", response_model=RecruiterSessionResponse)
def get_recruiter_session(
    request: Request,
) -> RecruiterSessionResponse:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    username = database.get_recruiter_session(token) if token else None
    expires_at = database.get_recruiter_session_expiry(token) if token else None
    if username is None or expires_at is None or not is_configured_recruiter(username):
        return RecruiterSessionResponse(authenticated=False)
    return RecruiterSessionResponse(
        authenticated=True,
        username=username,
        expires_at=expires_at,
    )


@system_router.delete("/auth/session", status_code=204)
def delete_recruiter_session(
    request: Request,
    response: Response,
    _: str = Depends(require_recruiter),
) -> Response:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        database.revoke_recruiter_session(token)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/api/v1",
        secure=urlsplit(str(request.base_url)).scheme == "https",
        httponly=True,
        samesite="strict",
    )
    response.status_code = 204
    return response


def _check_candidate_application(data: CandidateCreate) -> None:
    opening = _opening_or_404(data.opening_id)
    if opening["status"] != "OPEN":
        raise HTTPException(
            status_code=409,
            detail="Applications cannot be submitted to a closed job opening.",
        )


def process_resume_job(
    job_id: str,
    file_path: str,
    filename: str,
    candidate_id: str | None,
) -> None:
    """Extract and persist resume text; never treat parser failure as success."""
    path = Path(file_path)
    try:
        update_job(job_id, "PROCESSING")
        parsed_text = parse_resume(file_path)
        if candidate_id and not database.save_candidate_resume(
            candidate_id, filename, parsed_text
        ):
            raise InvalidResumeError(
                "The candidate record was removed before resume processing completed."
            )
        update_job(
            job_id,
            "COMPLETED",
            result={
                "candidate_id": candidate_id,
                "parsed_text": parsed_text,
            },
        )
        job = database.get_processing_job(job_id)
        if job and job["status"] == "COMPLETED":
            logger.info("Resume processing completed: %s", job_id)
        else:
            logger.info("Resume processing result was not retained: %s", job_id)
    except InvalidResumeError as exc:
        logger.info("Resume processing rejected: %s (%s)", job_id, exc.message)
        update_job(job_id, "FAILED", error=exc.message)
    except Exception:
        logger.exception("Resume processing failed: %s", job_id)
        update_job(
            job_id,
            "FAILED",
            error="Resume processing failed due to an internal error.",
        )
    finally:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logger.exception("Could not remove temporary resume file for job %s", job_id)


@system_router.get("/health")
def health_check() -> dict[str, str | bool]:
    try:
        database.check_database()
    except sqlite3.Error:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail="The application database is unavailable.",
        ) from None
    return {
        "status": "healthy",
        "service": "ZecPath ATS API",
        "version": "1.0.0",
        "authentication_configured": authentication_is_configured(),
    }


@router.post("/openings", response_model=OpeningResponse, status_code=201)
def create_opening(request: OpeningCreate) -> dict:
    try:
        data = request.model_dump()
        data["opening_id"] = str(uuid.uuid4())
        return database.create_opening(data)
    except Exception:
        logger.exception("Could not create job opening")
        raise HTTPException(
            status_code=500, detail="Could not save the job opening."
        ) from None


@router.get("/openings", response_model=list[OpeningResponse])
def list_openings(status: str | None = None) -> list[dict]:
    if status not in (None, "OPEN", "CLOSED"):
        raise HTTPException(status_code=422, detail="Status must be OPEN or CLOSED.")
    return database.list_openings(status)


@router.get("/openings/{opening_id}", response_model=OpeningResponse)
def get_opening(opening_id: str) -> dict:
    return _opening_or_404(opening_id)


@router.patch("/openings/{opening_id}", response_model=OpeningResponse)
def patch_opening(opening_id: str, request: OpeningUpdate) -> dict:
    _opening_or_404(opening_id)
    updates = request.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="Provide at least one field to update.")
    opening = database.update_opening(opening_id, updates)
    if opening is None:
        raise HTTPException(status_code=404, detail="Job opening not found.")
    return opening


@router.delete("/openings/{opening_id}", status_code=204)
def remove_opening(opening_id: str) -> Response:
    if not database.delete_opening(opening_id):
        raise HTTPException(status_code=404, detail="Job opening not found.")
    return Response(status_code=204)


@router.post("/candidates", response_model=CandidateResponse, status_code=201)
def create_candidate(request: CandidateCreate) -> dict:
    _check_candidate_application(request)
    data = request.model_dump()
    data["candidate_id"] = str(uuid.uuid4())
    if data["email"] is not None:
        data["email"] = data["email"].casefold()
    try:
        return database.create_candidate(data)
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="A candidate with this email has already applied to this opening.",
            ) from None
        logger.exception("Could not create candidate application")
        raise HTTPException(
            status_code=500, detail="Could not save the candidate application."
        ) from None


@router.get("/candidates", response_model=list[CandidateResponse])
def list_candidates(
    opening_id: str | None = None,
    application_status: str | None = None,
) -> list[dict]:
    allowed_statuses = {
        "APPLIED",
        "IN_REVIEW",
        "SHORTLISTED",
        "INTERVIEW",
        "OFFER",
        "HIRED",
        "REJECTED",
        "WITHDRAWN",
    }
    if application_status is not None and application_status not in allowed_statuses:
        raise HTTPException(status_code=422, detail="Unsupported application status.")
    if opening_id is not None:
        _opening_or_404(opening_id)
    return database.list_candidates(opening_id, application_status)


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str) -> dict:
    return _candidate_or_404(candidate_id)


@router.patch("/candidates/{candidate_id}", response_model=CandidateResponse)
def patch_candidate(candidate_id: str, request: CandidateUpdate) -> dict:
    _candidate_or_404(candidate_id)
    updates = request.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="Provide at least one field to update.")
    if updates.get("email") is not None:
        updates["email"] = updates["email"].casefold()
    try:
        candidate = database.update_candidate(candidate_id, updates)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A candidate with this email has already applied to this opening.",
        ) from None
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate


@router.delete("/candidates/{candidate_id}", status_code=204)
def remove_candidate(candidate_id: str) -> Response:
    if not database.delete_candidate(candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return Response(status_code=204)


@router.post(
    "/candidates/{candidate_id}/screening-reports",
    response_model=ScreeningReportResponse,
    status_code=201,
)
def create_screening_report(
    candidate_id: str, request: ScreeningReportRequest
) -> dict:
    candidate = _candidate_or_404(candidate_id)
    from day25_answer_intent_engine.src.answer_understanding_engine import (
        AnswerUnderstandingEngine,
    )

    engine = AnswerUnderstandingEngine()
    answers = []
    review_flags = []
    for submitted_answer in request.answers:
        understanding = engine.understand(
            submitted_answer.answer,
            expected_intent=submitted_answer.expected_intent,
        )
        answer = {
            "question_id": submitted_answer.question_id,
            "question": submitted_answer.question,
            "answer": submitted_answer.answer,
            "expected_intent": submitted_answer.expected_intent,
            "detected_intent": understanding["intent"],
            "status": understanding["answer_status"],
            "extracted_information": understanding["extracted_information"],
        }
        answers.append(answer)
        if answer["status"] != "valid":
            review_flags.append(
                f"{answer['question_id']}: answer status is {answer['status']}."
            )
        if answer["detected_intent"] != answer["expected_intent"]:
            review_flags.append(
                f"{answer['question_id']}: detected intent differs from the selected question type."
            )

    report = {
        "report_id": str(uuid.uuid4()),
        "candidate_id": candidate_id,
        "opening_id": candidate["opening_id"],
        "created_at": database.current_timestamp(),
        "method": "day25_keyword_and_regex_rules",
        "answers": answers,
        "review_flags": list(dict.fromkeys(review_flags)),
        "human_review_required": True,
    }
    database.save_screening_report(report)
    return report


@router.get(
    "/candidates/{candidate_id}/screening-reports",
    response_model=list[ScreeningReportResponse],
)
def list_screening_reports(candidate_id: str) -> list[dict]:
    _candidate_or_404(candidate_id)
    return database.list_screening_reports(candidate_id)


@router.post("/resumes/upload", response_model=ResumeUploadResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    candidate_id: str | None = Form(default=None),
) -> ResumeUploadResponse:
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if extension not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported resume format. Use PDF, DOCX, or TXT.",
        )
    if candidate_id is not None:
        _candidate_or_404(candidate_id)

    content = await file.read(MAX_RESUME_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded resume is empty.")
    if len(content) > MAX_RESUME_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Resume exceeds the 5 MiB upload limit.",
        )

    job_id = str(uuid.uuid4())
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / f"{job_id}{extension}"
    try:
        destination.write_bytes(content)
        create_job(filename, candidate_id, job_id)
    except OSError:
        destination.unlink(missing_ok=True)
        logger.exception("Could not store uploaded resume")
        raise HTTPException(
            status_code=500, detail="Could not store the uploaded resume."
        ) from None
    except Exception:
        destination.unlink(missing_ok=True)
        logger.exception("Could not register uploaded resume")
        raise HTTPException(
            status_code=500, detail="Could not queue the uploaded resume."
        ) from None

    background_tasks.add_task(
        process_resume_job,
        job_id,
        str(destination),
        filename,
        candidate_id,
    )
    logger.info("Resume uploaded and queued: %s", job_id)
    return ResumeUploadResponse(
        job_id=job_id,
        filename=filename,
        candidate_id=candidate_id,
        status="QUEUED",
        message="Resume accepted for processing.",
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: str) -> dict:
    try:
        return get_job(job_id)
    except ATSAPIError as exc:
        raise HTTPException(
            status_code=404,
            detail={"error": exc.error_code, "message": exc.message},
        ) from None


@router.post("/resumes/parse", response_model=ParseResponse)
def parse_resume_endpoint(request: ParseRequest) -> ParseResponse:
    try:
        job = get_job(request.job_id)
    except ATSAPIError as exc:
        raise HTTPException(
            status_code=404,
            detail={"error": exc.error_code, "message": exc.message},
        ) from None
    if job["status"] != "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail={
                "status": job["status"],
                "message": job["error"] or "Resume parsing has not completed.",
            },
        )
    parsed_text = (job.get("result") or {}).get("parsed_text", "")
    if not parsed_text:
        raise HTTPException(
            status_code=410,
            detail="Extracted resume text is no longer available.",
        )
    return ParseResponse(
        job_id=request.job_id,
        status=job["status"],
        parsed_text=parsed_text,
        message="Resume text extracted successfully.",
    )


@router.post("/candidates/score", response_model=ScoreResponse)
def score_candidate(request: ScoreRequest) -> ScoreResponse:
    candidate = _candidate_or_404(request.candidate_id)
    opening = _opening_or_404(request.job_id)
    if candidate["opening_id"] != request.job_id:
        raise HTTPException(
            status_code=409,
            detail="Candidate application does not belong to this job opening.",
        )
    try:
        score, evidence = calculate_candidate_match(candidate, opening)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    if not database.save_candidate_score(request.candidate_id, score, evidence):
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return ScoreResponse(
        job_id=request.job_id,
        candidate_id=request.candidate_id,
        score=score,
        evidence=evidence,
        human_review_required=True,
        status="SCORED",
        message="Exact required-skill overlap calculated; human review is required.",
    )


@router.post(
    "/openings/{opening_id}/shortlist",
    response_model=ShortlistResponse,
)
def shortlist_opening(
    opening_id: str,
    request: PersistedShortlistRequest,
) -> ShortlistResponse:
    _opening_or_404(opening_id)
    candidates = [
        candidate
        for candidate in database.list_candidates(opening_id)
        if candidate["score"] is not None
        and candidate["score"] >= request.minimum_score
    ]
    candidates.sort(key=lambda candidate: (-candidate["score"], candidate["name"]))
    ranked = [
        ShortlistedCandidate(
            candidate_id=candidate["candidate_id"],
            score=candidate["score"],
            rank=rank,
        )
        for rank, candidate in enumerate(candidates, start=1)
    ]
    return ShortlistResponse(
        job_id=opening_id,
        status="REVIEW_SUGGESTIONS_READY",
        shortlisted_count=len(ranked),
        candidates=ranked,
        human_review_required=True,
        simulation_only=False,
        message="Ranked from saved candidate scores. Confirm every decision through human review.",
    )


@router.post("/candidates/shortlist", response_model=ShortlistResponse)
def shortlist_demo(request: ShortlistRequest) -> ShortlistResponse:
    """Keep the original score-list helper, explicitly labelled as non-persistent demo data."""
    try:
        candidates = [
            ShortlistedCandidate(**candidate)
            for candidate in shortlist_candidates(
                request.candidates, request.minimum_score
            )
        ]
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return ShortlistResponse(
        job_id="caller-supplied-demo",
        status="SIMULATION_ONLY",
        shortlisted_count=len(candidates),
        candidates=candidates,
        human_review_required=True,
        simulation_only=True,
        message="Uses caller-supplied scores only; no saved candidate records were read or changed.",
    )
