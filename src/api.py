import hashlib
import json
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
    EligibilityConfigurationRequest,
    EligibilityConfigurationResponse,
    EligibilityEvaluationRequest,
    EligibilityEvaluationResponse,
    JobDescriptionParseRequest,
    JobDescriptionParseResponse,
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
    ScreeningInteractionCreate,
    ScreeningInteractionResponse,
    ScreeningQuestionResponse,
    ScreeningSessionCreate,
    ScreeningSessionResponse,
    ScreeningSessionStatusUpdate,
    ScreeningTranscriptResponse,
    TranscriptSegmentCreate,
    TranscriptSegmentResponse,
    ScreeningAudioUploadResponse,
    ScreeningAudioStatusResponse,
    ScreeningTranscriptCreate,
    ScreeningTranscriptDetailResponse,
    ScreeningAnswerCreate,
    ScreeningAnswerResponse,
    ScreeningQuestionScoreCreate,
    ScreeningQuestionScoreResponse,
    ScreeningAggregateScoreResponse,
    BehavioralAnalysisCreate,
    BehavioralAnalysisResponse,
    ScreeningReportFullCreate,
    ScreeningReportFullResponse,
)
from .services import (
    calculate_candidate_match,
    parse_resume,
    shortlist_candidates,
)
from .integrated_scoring import (
    ScoringModelUnavailableError,
    calculate_integrated_score,
)
from .resume_analysis import extract_resume_data
from .eligibility import evaluate_eligibility
from .screening_questions import get_questions, load_dataset
from .job_description_parser import parse_job_description
from .stt_integration import stt_integration
from .answer_understanding_integration import answer_understanding_integration
from .screening_scoring_integration import screening_scoring_integration
from .behavioral_analysis_integration import behavioral_analysis_integration
from .screening_report_integration import screening_report_integration
from .conversation_flow_integration import conversation_flow_integration
from .edge_case_integration import edge_case_integration
from .screening_pipeline import screening_pipeline


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
MAX_AUDIO_BYTES = 50 * 1024 * 1024
RESUME_MIME_TYPES = {
    ".pdf": {"application/pdf"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    },
    ".txt": {"text/plain"},
}


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


def _session_or_404(session_id: str) -> dict:
    session = database.get_screening_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Screening session not found.")
    return session


def _eligibility_fingerprint(
    candidate: dict, opening: dict, configuration_version: int
) -> str:
    inputs = {
        "candidate_id": candidate["candidate_id"],
        "candidate_updated_at": candidate["updated_at"],
        "score": candidate.get("score"),
        "score_evidence": candidate.get("score_evidence"),
        "opening_id": opening["opening_id"],
        "opening_updated_at": opening["updated_at"],
        "configuration_version": configuration_version,
    }
    return hashlib.sha256(
        json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _evaluate_and_persist_eligibility(
    candidate: dict, opening: dict, configuration_record: dict
) -> dict:
    fingerprint = _eligibility_fingerprint(
        candidate, opening, configuration_record["version"]
    )
    result = evaluate_eligibility(
        candidate=candidate,
        opening=opening,
        configuration=configuration_record["configuration"],
        configuration_version=configuration_record["version"],
        evaluation_id=str(uuid.uuid4()),
        evaluated_at=database.current_timestamp(),
    )
    database.save_eligibility_evaluation(result, fingerprint)
    return result


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
        resume_data = extract_resume_data(parsed_text)
        if candidate_id and not database.save_candidate_resume(
            candidate_id, filename, parsed_text, resume_data
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
                "resume_data": resume_data,
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


@router.post(
    "/openings/parse-description",
    response_model=JobDescriptionParseResponse,
)
def parse_opening_description(
    request: JobDescriptionParseRequest,
) -> dict:
    return parse_job_description(request.description)


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
    content_type = (file.content_type or "").casefold()
    if content_type and content_type != "application/octet-stream" and (
        content_type not in RESUME_MIME_TYPES[extension]
    ):
        raise HTTPException(
            status_code=400,
            detail="Resume file type does not match its filename extension.",
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
    resume_data = (job.get("result") or {}).get("resume_data", {})
    if not parsed_text:
        raise HTTPException(
            status_code=410,
            detail="Extracted resume text is no longer available.",
        )
    return ParseResponse(
        job_id=request.job_id,
        status=job["status"],
        parsed_text=parsed_text,
        extracted_data=resume_data,
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
        calculate_candidate_match(candidate, opening)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    try:
        score, evidence = calculate_integrated_score(candidate, opening)
    except ScoringModelUnavailableError as exc:
        logger.exception("Day 12 semantic model unavailable")
        raise HTTPException(status_code=503, detail=str(exc)) from None
    evidence["scored_at"] = database.current_timestamp()
    evidence["scoring_version"] = "day9-12-13-v1"
    if not database.save_candidate_score(request.candidate_id, score, evidence):
        raise HTTPException(status_code=404, detail="Candidate not found.")
    scored_candidates = [
        item
        for item in database.list_candidates(request.job_id)
        if item["score"] is not None
    ]
    scored_candidates.sort(key=lambda item: (-item["score"], item["name"]))
    ranking = next(
        (
            index
            for index, item in enumerate(scored_candidates, start=1)
            if item["candidate_id"] == request.candidate_id
        ),
        None,
    )
    if ranking is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return ScoreResponse(
        job_id=request.job_id,
        candidate_id=request.candidate_id,
        score=score,
        evidence=evidence,
        job_title=opening["title"],
        candidate_name=candidate["name"],
        extracted_skills=evidence["extracted_skills"],
        matching_required_skills=evidence["matching_required_skills"],
        missing_required_skills=evidence["missing_required_skills"],
        education_details=evidence["education_details"],
        experience_details=evidence["experience_details"],
        components=evidence["components"],
        ranking=ranking,
        human_review_required=True,
        status="SCORED",
        message=(
            "Day 9-13 ATS score calculated from available evidence; human review "
            "is required."
        ),
    )


@router.put(
    "/openings/{opening_id}/eligibility-config",
    response_model=EligibilityConfigurationResponse,
)
def save_opening_eligibility_configuration(
    opening_id: str, request: EligibilityConfigurationRequest
) -> dict:
    _opening_or_404(opening_id)
    record = database.save_eligibility_configuration(
        opening_id, request.model_dump(mode="json")
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Job opening not found.")
    return record


@router.get(
    "/openings/{opening_id}/eligibility-config",
    response_model=EligibilityConfigurationResponse,
)
def get_opening_eligibility_configuration(opening_id: str) -> dict:
    _opening_or_404(opening_id)
    record = database.get_eligibility_configuration(opening_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail="Eligibility configuration not found."
        )
    return record


@router.post(
    "/candidates/{candidate_id}/eligibility/evaluate",
    response_model=EligibilityEvaluationResponse,
    status_code=201,
)
def evaluate_candidate_eligibility(
    candidate_id: str, request: EligibilityEvaluationRequest
) -> dict:
    candidate = _candidate_or_404(candidate_id)
    opening = _opening_or_404(request.opening_id)
    if candidate["opening_id"] != opening["opening_id"]:
        raise HTTPException(
            status_code=409,
            detail="Candidate application does not belong to this job opening.",
        )
    configuration = database.get_eligibility_configuration(opening["opening_id"])
    if configuration is None:
        raise HTTPException(
            status_code=409,
            detail="Configure eligibility rules before evaluating a candidate.",
        )
    return _evaluate_and_persist_eligibility(candidate, opening, configuration)


@router.get(
    "/candidates/{candidate_id}/eligibility",
    response_model=EligibilityEvaluationResponse,
)
def get_candidate_eligibility(candidate_id: str, opening_id: str) -> dict:
    candidate = _candidate_or_404(candidate_id)
    opening = _opening_or_404(opening_id)
    if candidate["opening_id"] != opening["opening_id"]:
        raise HTTPException(
            status_code=409,
            detail="Candidate application does not belong to this job opening.",
        )
    configuration = database.get_eligibility_configuration(opening_id)
    if configuration is None:
        raise HTTPException(
            status_code=404, detail="Eligibility configuration not found."
        )
    fingerprint = _eligibility_fingerprint(
        candidate, opening, configuration["version"]
    )
    latest = database.get_latest_eligibility_evaluation(candidate_id, opening_id)
    if latest is None or latest.pop("_input_fingerprint", None) != fingerprint:
        return _evaluate_and_persist_eligibility(candidate, opening, configuration)
    return latest


@router.get("/screening/questions", response_model=list[ScreeningQuestionResponse])
def list_screening_questions(
    role_id: str | None = None,
    category: str | None = None,
    language: str = "en",
    mandatory: bool | None = None,
    active_only: bool = True,
) -> list[dict]:
    dataset = load_dataset()
    if role_id is not None and role_id not in dataset["roles"]:
        raise HTTPException(status_code=422, detail="Unsupported screening role.")
    normalized_category = category.upper().replace(" ", "_") if category else None
    if (
        normalized_category is not None
        and normalized_category not in dataset["categories"]
    ):
        raise HTTPException(status_code=422, detail="Unsupported question category.")
    try:
        return get_questions(
            role_id=role_id,
            category=category,
            language=language,
            mandatory=mandatory,
            active_only=active_only,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None


@router.post(
    "/screening/sessions",
    response_model=ScreeningSessionResponse,
    status_code=201,
)
def create_screening_session(request: ScreeningSessionCreate) -> dict:
    candidate = _candidate_or_404(request.candidate_id)
    _opening_or_404(request.opening_id)
    if candidate["opening_id"] != request.opening_id:
        raise HTTPException(
            status_code=409,
            detail="Candidate application does not belong to this job opening.",
        )
    return database.create_screening_session(
        {**request.model_dump(), "session_id": str(uuid.uuid4())}
    )


@router.get(
    "/screening/sessions/{session_id}",
    response_model=ScreeningTranscriptResponse,
)
def get_screening_transcript(session_id: str) -> dict:
    session = _session_or_404(session_id)
    return {
        "session": session,
        "segments": database.list_transcript_segments(session_id),
        "interactions": database.list_screening_interactions(session_id),
    }


@router.patch(
    "/screening/sessions/{session_id}",
    response_model=ScreeningSessionResponse,
)
def update_screening_session(
    session_id: str, request: ScreeningSessionStatusUpdate
) -> dict:
    session = _session_or_404(session_id)
    allowed_transitions = {
        "CREATED": {"IN_PROGRESS", "CANCELLED"},
        "IN_PROGRESS": {"INTERRUPTED", "COMPLETED", "CANCELLED"},
        "INTERRUPTED": {"IN_PROGRESS", "COMPLETED", "CANCELLED"},
    }
    if request.status not in allowed_transitions.get(session["status"], set()):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot change a {session['status']} session to {request.status}.",
        )
    return database.update_screening_session_status(session_id, request.status) or {}


@router.post(
    "/screening/sessions/{session_id}/segments",
    response_model=list[TranscriptSegmentResponse],
    status_code=201,
)
def add_transcript_segments(
    session_id: str, segments: list[TranscriptSegmentCreate]
) -> list[dict]:
    session = _session_or_404(session_id)
    if session["status"] not in {"IN_PROGRESS", "INTERRUPTED"}:
        raise HTTPException(
            status_code=409,
            detail="Start or resume the screening session before adding transcript segments.",
        )
    if not segments or len(segments) > 500:
        raise HTTPException(
            status_code=422, detail="Submit between 1 and 500 transcript segments."
        )
    existing_segments = database.list_transcript_segments(session_id)
    if existing_segments:
        expected_sequence = existing_segments[-1]["sequence_number"] + 1
        if segments[0].sequence_number != expected_sequence:
            raise HTTPException(
                status_code=409,
                detail=f"Transcript sequence must resume at {expected_sequence}.",
            )
    elif segments[0].sequence_number != 1:
        raise HTTPException(
            status_code=409,
            detail="Transcript sequence must begin at 1.",
        )
    if any(
        later.sequence_number <= earlier.sequence_number
        for earlier, later in zip(segments, segments[1:])
    ):
        raise HTTPException(
            status_code=422,
            detail="Transcript segments must be submitted in increasing sequence order.",
        )
    valid_question_ids = {
        item["question_id"] for item in load_dataset()["questions"]
    }
    submitted_ids: set[str] = set()
    submitted_sequences: set[int] = set()
    existing_sequences = {item["sequence_number"] for item in existing_segments}
    records = []
    for segment in segments:
        if segment.question_id and segment.question_id not in valid_question_ids:
            raise HTTPException(status_code=422, detail="Unknown screening question ID.")
        if segment.segment_id and segment.segment_id in submitted_ids:
            raise HTTPException(status_code=422, detail="Duplicate segment ID in request.")
        if (
            segment.sequence_number in submitted_sequences
            or segment.sequence_number in existing_sequences
        ):
            raise HTTPException(
                status_code=409, detail="Duplicate transcript sequence number."
            )
        segment_id = segment.segment_id or str(uuid.uuid4())
        submitted_ids.add(segment_id)
        submitted_sequences.add(segment.sequence_number)
        records.append(
            {
                **segment.model_dump(exclude={"segment_id"}),
                "segment_id": segment_id,
                "start_time": (
                    segment.start_time.isoformat() if segment.start_time else None
                ),
                "end_time": segment.end_time.isoformat() if segment.end_time else None,
            }
        )
    try:
        return database.save_transcript_segments(session_id, records)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Transcript segment ID or sequence number already exists.",
        ) from None


@router.post(
    "/screening/sessions/{session_id}/interactions",
    response_model=ScreeningInteractionResponse,
    status_code=201,
)
def add_screening_interaction(
    session_id: str, request: ScreeningInteractionCreate
) -> dict:
    session = _session_or_404(session_id)
    if session["status"] not in {"IN_PROGRESS", "INTERRUPTED"}:
        raise HTTPException(
            status_code=409,
            detail="Start or resume the screening session before adding interactions.",
        )
    question_ids = {item["question_id"] for item in load_dataset()["questions"]}
    if request.question_id not in question_ids:
        raise HTTPException(status_code=422, detail="Unknown screening question ID.")
    if request.follow_up_to:
        exists = any(
            item["interaction_id"] == request.follow_up_to
            for item in database.list_screening_interactions(session_id)
        )
        if not exists:
            raise HTTPException(status_code=422, detail="Unknown follow-up interaction.")
    try:
        return database.save_screening_interaction(
            session_id,
            {**request.model_dump(), "interaction_id": str(uuid.uuid4())},
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="An interaction already exists at that display order.",
        ) from None


@router.get(
    "/screening/sessions/{session_id}/interactions",
    response_model=list[ScreeningInteractionResponse],
)
def get_screening_interactions(session_id: str) -> list[dict]:
    _session_or_404(session_id)
    return database.list_screening_interactions(session_id)


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


@router.post(
    "/screening/sessions",
    response_model=dict,
    status_code=201,
)
def create_screening_session_full(request: ScreeningSessionCreate) -> dict:
    """Create a new screening session with questions."""
    session_data = screening_pipeline.create_screening_session(
        candidate_id=request.candidate_id,
        opening_id=request.opening_id,
        language=request.language,
    )
    return session_data


@router.get(
    "/screening/sessions/{session_id}/status",
    response_model=dict,
)
def get_screening_session_status(session_id: str) -> dict:
    """Get comprehensive screening session status."""
    return screening_pipeline.get_session_status(session_id)


@router.post(
    "/screening/sessions/{session_id}/start",
    response_model=dict,
)
def start_screening_session(session_id: str) -> dict:
    """Start the screening conversation flow."""
    _session_or_404(session_id)
    return conversation_flow_integration.start_session(session_id)


@router.post(
    "/screening/sessions/{session_id}/audio",
    response_model=ScreeningAudioUploadResponse,
    status_code=202,
)
async def upload_screening_audio(
    session_id: str,
    file: UploadFile = File(...),
    question_id: str | None = Form(default=None),
) -> ScreeningAudioUploadResponse:
    """Upload audio file for transcription."""
    _session_or_404(session_id)

    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if extension not in {".wav", ".mp3", ".m4a", ".ogg", ".flac"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format. Use WAV, MP3, M4A, OGG, or FLAC.",
        )

    content = await file.read(MAX_AUDIO_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded audio is empty.")
    if len(content) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio exceeds the {MAX_AUDIO_BYTES // (1024*1024)} MiB upload limit.",
        )

    mime_type = file.content_type or "audio/wav"
    return await stt_integration.upload_audio(
        session_id=session_id,
        file_bytes=content,
        filename=filename,
        mime_type=mime_type,
        question_id=question_id,
    )


@router.get(
    "/screening/audio/{audio_id}",
    response_model=ScreeningAudioStatusResponse,
)
def get_audio_status(audio_id: str) -> ScreeningAudioStatusResponse:
    """Get audio processing status."""
    try:
        return stt_integration.get_audio_status(audio_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.post(
    "/screening/audio/{audio_id}/transcribe",
    response_model=ScreeningTranscriptDetailResponse,
)
def transcribe_audio(audio_id: str) -> ScreeningTranscriptDetailResponse:
    """Process audio through STT and save transcript."""
    try:
        return stt_integration.process_audio(audio_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except Exception as exc:
        logger.exception("Transcription failed")
        raise HTTPException(status_code=500, detail="Transcription failed") from None


@router.get(
    "/screening/transcripts/{transcript_id}",
    response_model=ScreeningTranscriptDetailResponse,
)
def get_transcript(transcript_id: str) -> ScreeningTranscriptDetailResponse:
    """Get transcript by ID."""
    try:
        return stt_integration.get_transcript(transcript_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.post(
    "/screening/sessions/{session_id}/answers/text",
    response_model=dict,
)
def submit_text_answer(
    session_id: str,
    question_id: str,
    answer_text: str = Form(...),
) -> dict:
    """Submit text answer for a question."""
    _session_or_404(session_id)
    return screening_pipeline.process_text_response(
        session_id=session_id,
        question_id=question_id,
        text_answer=answer_text,
    )


@router.post(
    "/screening/sessions/{session_id}/complete",
    response_model=dict,
)
def complete_screening_session(session_id: str) -> dict:
    """Complete screening session and generate report."""
    _session_or_404(session_id)
    return screening_pipeline.complete_session(session_id)


@router.get(
    "/screening/sessions/{session_id}/report",
    response_model=ScreeningReportFullResponse,
)
def get_screening_report(session_id: str) -> ScreeningReportFullResponse:
    """Get screening report for session."""
    reports = database.list_screening_reports_full(session_id)
    if not reports:
        raise HTTPException(status_code=404, detail="No report found for this session.")
    return ScreeningReportFullResponse(**reports[0])


@router.get(
    "/screening/candidates/{candidate_id}/reports",
    response_model=list[ScreeningReportFullResponse],
)
def list_candidate_screening_reports(candidate_id: str) -> list[ScreeningReportFullResponse]:
    """List all screening reports for a candidate."""
    _candidate_or_404(candidate_id)
    sessions = database.list_screening_sessions(candidate_id)
    reports = []
    for session in sessions:
        session_reports = database.list_screening_reports_full(session["session_id"])
        reports.extend(session_reports)
    return [ScreeningReportFullResponse(**r) for r in reports]


@router.get(
    "/screening/questions/{role_id}",
    response_model=list[ScreeningQuestionResponse],
)
def get_questions_for_role(role_id: str, language: str = "en") -> list[dict]:
    """Get screening questions for a specific role."""
    questions = get_questions(role_id=role_id, language=language, active_only=True)
    return questions


def _candidate_or_404(candidate_id: str) -> dict:
    candidate = database.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate


def _session_or_404(session_id: str) -> dict:
    session = database.get_screening_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Screening session not found.")
    return session
