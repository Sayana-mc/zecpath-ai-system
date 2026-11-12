import hashlib
import json
import logging
import secrets
import sqlite3
import uuid
from pathlib import Path
from typing import Any
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
from pydantic import BaseModel

try:
    from . import database
except ImportError:
    from src import database
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
    HRInterviewSessionCreate,
    HRInterviewSessionResponse,
    HRInterviewSessionStatusUpdate,
    HRInterviewQuestionResponse,
    HRInterviewAnswerSubmit,
    HRInterviewFollowUpSubmit,
    HRInterviewFollowUpResponse,
    HRCommunicationEvaluationResponse,
    HRBehavioralSignalsResponse,
    HRAptitudeEvaluationResponse,
    HRInterviewScoreResponse,
    HRInterviewReportResponse,
    HRInterviewDecisionRequest,
    TechnicalInterviewSessionCreate,
    TechnicalInterviewSessionResponse,
    TechnicalInterviewQuestionResponse,
    TechnicalInterviewAnswerSubmit,
    TechnicalInterviewResponseResult,
    TechnicalInterviewCompleteResponse,
    MachineTestAssignmentCreate,
    MachineTestAssignmentResponse,
    MachineTestSubmissionCreate,
    MachineTestSubmissionResponse,
    CandidateIntegrityRecordCreate,
    CandidateIntegrityRecordResponse,
    CandidateBehavioralRecordCreate,
    CandidateBehavioralRecordResponse,
    CrossRoundEvaluationRequest,
    CrossRoundEvaluationResponse,
    FinalRecommendationRequest,
    FinalRecommendationResponse,
    FinalRecommendationDecisionRequest,
    HiringIntelligenceReportResponse,
    AuditEventResponse,
    AuditVerificationResponse,
    CandidateCoachingResponse,
    SimulationRunRequest,
    SimulationRunResponse,
    BenchmarkComparisonRequest,
    BenchmarkComparisonResponse,
    BatchResumeProcessRequest,
    BatchResumeProcessResponse,
    MonitoringLogEventRequest,
    MonitoringDashboardResponse,
    MonitoringAlertItem,
    DecisionAuditLogResponse,
)
from .observability import observability, read_jsonl
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
from .hr_interview_engine import hr_interview_engine
from .hr_interview_pipeline import hr_interview_pipeline
from .hr_scoring_engine import hr_scoring_engine
from .hr_summary_generator import hr_summary_generator
from .technical_interview_engine import technical_interview_engine
from .technical_scoring_engine import score_technical_answer
from .machine_test_engine import machine_test_engine
from .integrity_engine import integrity_engine
from .behavioral_ai_engine import behavioral_ai_engine
from .cross_round_scoring_engine import cross_round_scoring_engine
from .final_recommendation_engine import recommend_candidate
from .hiring_intelligence_report_generator import (
    generate_candidate_hiring_report,
    render_report_html,
    render_report_markdown,
)
from .optimization_engine import optimization_engine
from .security_governance import security_governance
from .simulation_pipeline import system_simulation_pipeline
from .coaching_engine import coaching_engine
from .batch_processing import batch_process_resumes, run_scalability_benchmark


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


@router.post("/ats/score", response_model=ScoreResponse)
def ats_score(request: ScoreRequest) -> ScoreResponse:
    """Day 16 ATS API demonstration endpoint."""
    return score_candidate(request)


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


class ATSShortlistRequest(BaseModel):
    job_id: str
    minimum_score: float = 0.0


@router.post("/ats/shortlist", response_model=ShortlistResponse)
def ats_shortlist(request: ATSShortlistRequest) -> ShortlistResponse:
    """Day 16 ATS shortlist endpoint."""
    persisted_req = PersistedShortlistRequest(minimum_score=request.minimum_score)
    return shortlist_opening(request.job_id, persisted_req)


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


@router.post(
    "/screening/pipeline/sessions",
    response_model=dict,
    status_code=201,
)
def create_screening_pipeline_session(request: ScreeningSessionCreate) -> dict:
    """Pipeline alias for creating a screening session."""
    return create_screening_session_full(request)


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
    question_id: str = Form(...),
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


# ---------------------------------------------------------------------------
# Days 33–40: AI HR Interview Routes
# ---------------------------------------------------------------------------

@router.post(
    "/hr-interviews",
    response_model=HRInterviewSessionResponse,
    status_code=201,
)
def create_hr_interview(payload: HRInterviewSessionCreate) -> HRInterviewSessionResponse:
    _candidate_or_404(payload.candidate_id)
    _opening_or_404(payload.opening_id)
    try:
        created = hr_interview_engine.create_interview_session(
            candidate_id=payload.candidate_id,
            opening_id=payload.opening_id,
            experience_level=payload.experience_level or "FRESHER",
            role_type=payload.role_type or "NON_TECHNICAL",
        )
        return HRInterviewSessionResponse(**created["session"])
    except Exception as exc:
        logger.exception("Failed to create HR interview")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/hr-interviews",
    response_model=list[HRInterviewSessionResponse],
)
def list_hr_interviews(
    candidate_id: str | None = None, status: str | None = None
) -> list[HRInterviewSessionResponse]:
    sessions = database.list_hr_interview_sessions(candidate_id=candidate_id, status=status)
    return [HRInterviewSessionResponse(**s) for s in sessions]


@router.get(
    "/hr-interviews/{interview_id}",
    response_model=HRInterviewSessionResponse,
)
def get_hr_interview(interview_id: str) -> HRInterviewSessionResponse:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    return HRInterviewSessionResponse(**session)


@router.get(
    "/hr-interviews/{interview_id}/status",
    response_model=dict,
)
def get_hr_interview_status(interview_id: str) -> dict:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    return hr_interview_pipeline.get_session_status(interview_id)


@router.post(
    "/hr-interviews/{interview_id}/start",
    response_model=HRInterviewSessionResponse,
)
def start_hr_interview(interview_id: str) -> HRInterviewSessionResponse:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    questions = database.list_hr_interview_questions(interview_id)
    first_q_id = questions[0]["question_id"] if questions else None
    updated = database.update_hr_interview_session_status(
        interview_id,
        status="IN_PROGRESS",
        current_phase="INTRODUCTION",
        current_question_id=first_q_id,
    )
    return HRInterviewSessionResponse(**updated)


@router.post(
    "/hr-interviews/{interview_id}/pause",
    response_model=HRInterviewSessionResponse,
)
def pause_hr_interview(interview_id: str) -> HRInterviewSessionResponse:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    updated = hr_interview_pipeline.pause_session(interview_id)
    return HRInterviewSessionResponse(**updated)


@router.post(
    "/hr-interviews/{interview_id}/resume",
    response_model=HRInterviewSessionResponse,
)
def resume_hr_interview(interview_id: str) -> HRInterviewSessionResponse:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    updated = hr_interview_pipeline.resume_session(interview_id)
    return HRInterviewSessionResponse(**updated)


@router.get(
    "/hr-interviews/{interview_id}/questions",
    response_model=list[HRInterviewQuestionResponse],
)
def get_hr_interview_questions(interview_id: str) -> list[HRInterviewQuestionResponse]:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    questions = database.list_hr_interview_questions(interview_id)
    return [HRInterviewQuestionResponse(**q) for q in questions]


@router.post(
    "/hr-interviews/{interview_id}/answers",
    response_model=dict,
)
def submit_hr_interview_answer(
    interview_id: str, payload: HRInterviewAnswerSubmit
) -> dict:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    result = hr_interview_pipeline.process_answer(
        interview_id=interview_id,
        question_id=payload.question_id,
        answer_text=payload.answer_text,
    )
    return result


@router.post(
    "/hr-interviews/{interview_id}/follow-ups",
    response_model=HRInterviewFollowUpResponse,
    status_code=201,
)
def submit_hr_interview_followup(
    interview_id: str, payload: HRInterviewFollowUpSubmit
) -> HRInterviewFollowUpResponse:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    saved = hr_interview_pipeline.process_followup(
        interview_id=interview_id,
        parent_question_id=payload.parent_question_id,
        followup_type=payload.followup_type,
        followup_question=payload.followup_question,
        candidate_response=payload.candidate_response,
    )
    return HRInterviewFollowUpResponse(**saved)


@router.post(
    "/hr-interviews/{interview_id}/complete",
    response_model=dict,
)
def complete_hr_interview(interview_id: str) -> dict:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    completed = hr_interview_pipeline.complete_session(interview_id)
    return completed


@router.get(
    "/hr-interviews/{interview_id}/evaluation",
    response_model=dict,
)
def get_hr_interview_evaluation(interview_id: str) -> dict:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    score = database.get_hr_interview_score(interview_id)
    if not score:
        score = hr_scoring_engine.calculate_comprehensive_hr_score(interview_id)
    comm = database.get_hr_communication_evaluations(interview_id)
    signals = database.get_hr_behavioral_signals(interview_id)
    apt = database.list_hr_aptitude_evaluations(interview_id)
    return {
        "score": score,
        "communication": comm,
        "signals": signals,
        "aptitude": apt,
    }


@router.get(
    "/hr-interviews/{interview_id}/report",
)
def get_hr_interview_report(
    interview_id: str, format: str | None = None
):
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    report = database.get_hr_interview_report_by_interview(interview_id)
    if not report:
        report = hr_summary_generator.generate_and_save_report(interview_id)
    if format == "html":
        return Response(content=report["html_report"], media_type="text/html")
    return report


@router.get(
    "/hr-interviews/candidates/{candidate_id}/reports",
    response_model=list[HRInterviewReportResponse],
)
def list_candidate_hr_reports(candidate_id: str) -> list[HRInterviewReportResponse]:
    _candidate_or_404(candidate_id)
    reports = database.list_hr_interview_reports_for_candidate(candidate_id)
    return [HRInterviewReportResponse(**r) for r in reports]


@router.post(
    "/hr-interviews/{interview_id}/decision",
    response_model=HRInterviewReportResponse,
)
def record_hr_interview_decision(
    interview_id: str, payload: HRInterviewDecisionRequest
) -> HRInterviewReportResponse:
    session = database.get_hr_interview_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="HR interview session not found.")
    updated = database.update_hr_interview_decision(
        interview_id=interview_id,
        decision=payload.decision,
        notes=payload.notes,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="HR interview report not found to update decision.")
    return HRInterviewReportResponse(**updated)


# ---------------------------------------------------------------------------
# Days 46–47: Technical Interview Routes
# ---------------------------------------------------------------------------

@router.post(
    "/technical-interviews",
    response_model=TechnicalInterviewSessionResponse,
    status_code=201,
)
def create_technical_interview(payload: TechnicalInterviewSessionCreate) -> TechnicalInterviewSessionResponse:
    cand = _candidate_or_404(payload.candidate_id)
    op = _opening_or_404(payload.opening_id)
    target_role = payload.target_role or op.get("title", "Software Engineer")
    exp_level = payload.experience_level or "mid"
    sess = database.create_technical_interview_session(
        candidate_id=payload.candidate_id,
        opening_id=payload.opening_id,
        target_role=target_role,
        experience_level=exp_level,
    )
    questions = technical_interview_engine.generate_questions(
        target_role=target_role,
        experience_level=exp_level,
        skills=cand.get("skills", []),
    )
    for idx, q in enumerate(questions, start=1):
        database.save_technical_interview_question(
            session_id=sess["session_id"],
            question_text=q["question_text"],
            topic=q.get("topic", "Core Engineering"),
            question_type=q.get("question_type", "conceptual"),
            difficulty=q.get("difficulty", "medium"),
            sequence_order=idx,
            expected_criteria=q.get("expected_criteria", []),
        )
    database.update_technical_interview_session(sess["session_id"], total_questions=len(questions))
    return TechnicalInterviewSessionResponse(**database.get_technical_interview_session(sess["session_id"]))


@router.get(
    "/technical-interviews",
    response_model=list[TechnicalInterviewSessionResponse],
)
def list_technical_interviews(candidate_id: str | None = None) -> list[TechnicalInterviewSessionResponse]:
    sessions = database.list_technical_interview_sessions(candidate_id=candidate_id)
    return [TechnicalInterviewSessionResponse(**s) for s in sessions]


@router.get(
    "/technical-interviews/{session_id}",
    response_model=TechnicalInterviewSessionResponse,
)
def get_technical_interview(session_id: str) -> TechnicalInterviewSessionResponse:
    sess = database.get_technical_interview_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Technical interview session not found.")
    return TechnicalInterviewSessionResponse(**sess)


@router.post(
    "/technical-interviews/{session_id}/start",
    response_model=TechnicalInterviewSessionResponse,
)
def start_technical_interview(session_id: str) -> TechnicalInterviewSessionResponse:
    sess = database.get_technical_interview_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Technical interview session not found.")
    updated = database.update_technical_interview_session(session_id, status="IN_PROGRESS", current_stage="STAGE_QUESTION_1")
    return TechnicalInterviewSessionResponse(**updated)


@router.get(
    "/technical-interviews/{session_id}/questions",
    response_model=list[TechnicalInterviewQuestionResponse],
)
def get_technical_interview_questions(session_id: str) -> list[TechnicalInterviewQuestionResponse]:
    sess = database.get_technical_interview_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Technical interview session not found.")
    questions = database.list_technical_interview_questions(session_id)
    return [TechnicalInterviewQuestionResponse(**q) for q in questions]


@router.post(
    "/technical-interviews/{session_id}/answers",
    response_model=TechnicalInterviewResponseResult,
)
def submit_technical_interview_answer(
    session_id: str, payload: TechnicalInterviewAnswerSubmit
) -> TechnicalInterviewResponseResult:
    sess = database.get_technical_interview_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Technical interview session not found.")
    questions = database.list_technical_interview_questions(session_id)
    matching_q = next((q for q in questions if q["question_id"] == payload.question_id), None)
    expected_criteria = matching_q.get("expected_criteria", []) if matching_q else []
    q_type = matching_q.get("question_type", "conceptual") if matching_q else "conceptual"

    score_result = score_technical_answer(
        answer_text=payload.answer_text,
        expected_criteria=expected_criteria,
        question_type=q_type,
    )
    saved = database.save_technical_interview_response(
        session_id=session_id,
        question_id=payload.question_id,
        raw_answer=payload.answer_text,
        score=score_result["score"],
        depth_level=score_result.get("depth_level", "moderate"),
        parameter_scores=score_result.get("parameter_scores", {}),
        feedback=score_result.get("feedback", ""),
    )
    return TechnicalInterviewResponseResult(**saved)


@router.get(
    "/technical-interviews/{session_id}/answers",
    response_model=list[TechnicalInterviewResponseResult],
)
def list_technical_interview_answers(session_id: str) -> list[TechnicalInterviewResponseResult]:
    sess = database.get_technical_interview_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Technical interview session not found.")
    answers = database.list_technical_interview_responses(session_id)
    return [TechnicalInterviewResponseResult(**a) for a in answers]


@router.post(
    "/technical-interviews/{session_id}/complete",
    response_model=TechnicalInterviewCompleteResponse,
)
def complete_technical_interview(session_id: str) -> TechnicalInterviewCompleteResponse:
    sess = database.get_technical_interview_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Technical interview session not found.")
    responses = database.list_technical_interview_responses(session_id)
    if responses:
        avg_score = round(sum(r["score"] for r in responses) / len(responses), 2)
    else:
        avg_score = 0.0

    rubric_breakdown = {
        "total_responses": len(responses),
        "average_score": avg_score,
        "shallow_count": sum(1 for r in responses if r.get("depth_level") == "shallow"),
        "moderate_count": sum(1 for r in responses if r.get("depth_level") == "moderate"),
        "deep_count": sum(1 for r in responses if r.get("depth_level") == "deep"),
    }
    database.update_technical_interview_session(
        session_id=session_id,
        status="COMPLETED",
        current_stage="COMPLETED",
        overall_score=avg_score,
        rubric_breakdown=rubric_breakdown,
    )
    now = database._now()
    return TechnicalInterviewCompleteResponse(
        session_id=session_id,
        status="COMPLETED",
        overall_score=avg_score,
        rubric_breakdown=rubric_breakdown,
        total_questions=len(responses),
        completed_at=now,
    )


# ---------------------------------------------------------------------------
# Day 50: Machine Test Routes
# ---------------------------------------------------------------------------

@router.post(
    "/machine-tests/assignments",
    response_model=MachineTestAssignmentResponse,
    status_code=201,
)
def create_machine_test(payload: MachineTestAssignmentCreate) -> MachineTestAssignmentResponse:
    _candidate_or_404(payload.candidate_id)
    _opening_or_404(payload.opening_id)
    task = machine_test_engine.assign_task(
        task_type=payload.task_type,
        task_id=payload.task_id,
    )
    created = database.create_machine_test_assignment(
        candidate_id=payload.candidate_id,
        opening_id=payload.opening_id,
        task_type=payload.task_type,
        task_id=task.get("task_id", payload.task_id or "MT_001"),
        title=payload.title or task.get("title", "Technical Coding Challenge"),
        description=payload.description or task.get("description", ""),
        time_limit_minutes=payload.time_limit_minutes,
    )
    return MachineTestAssignmentResponse(**created)


@router.get(
    "/machine-tests/assignments",
    response_model=list[MachineTestAssignmentResponse],
)
def list_machine_tests(candidate_id: str | None = None) -> list[MachineTestAssignmentResponse]:
    assignments = database.list_machine_test_assignments(candidate_id=candidate_id)
    return [MachineTestAssignmentResponse(**a) for a in assignments]


@router.get(
    "/machine-tests/assignments/{assignment_id}",
    response_model=MachineTestAssignmentResponse,
)
def get_machine_test(assignment_id: str) -> MachineTestAssignmentResponse:
    assignment = database.get_machine_test_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Machine test assignment not found.")
    return MachineTestAssignmentResponse(**assignment)


@router.post(
    "/machine-tests/assignments/{assignment_id}/submit",
    response_model=MachineTestSubmissionResponse,
)
def submit_machine_test(
    assignment_id: str, payload: MachineTestSubmissionCreate
) -> MachineTestSubmissionResponse:
    assignment = database.get_machine_test_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Machine test assignment not found.")

    eval_result = machine_test_engine.evaluate_submission(
        task_type=assignment["task_type"],
        code=payload.code_content,
        time_spent_minutes=payload.time_spent_minutes,
        time_limit_minutes=assignment["time_limit_minutes"],
    )
    now = database._now()
    saved = database.save_machine_test_submission(
        assignment_id=assignment_id,
        code_content=payload.code_content,
        language=payload.language,
        time_spent_minutes=payload.time_spent_minutes,
        total_score=eval_result["total_score"],
        rubric_scores=eval_result.get("rubric_scores", {}),
        execution_details=eval_result.get("execution_details", {}),
    )
    database.update_machine_test_assignment_status(assignment_id, status="EVALUATED", completed_at=now)
    return MachineTestSubmissionResponse(**saved)


@router.get(
    "/machine-tests/assignments/{assignment_id}/submissions",
    response_model=list[MachineTestSubmissionResponse],
)
def list_machine_test_submissions(assignment_id: str) -> list[MachineTestSubmissionResponse]:
    assignment = database.get_machine_test_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Machine test assignment not found.")
    submissions = database.list_machine_test_submissions(assignment_id)
    return [MachineTestSubmissionResponse(**s) for s in submissions]


# ---------------------------------------------------------------------------
# Days 48–49: Integrity & Behavioral Records Routes
# ---------------------------------------------------------------------------

@router.post(
    "/candidates/{candidate_id}/integrity-records",
    response_model=CandidateIntegrityRecordResponse,
    status_code=201,
)
def record_candidate_integrity(
    candidate_id: str, payload: CandidateIntegrityRecordCreate
) -> CandidateIntegrityRecordResponse:
    _candidate_or_404(candidate_id)
    evaluated = integrity_engine.evaluate_events(
        events=payload.events,
        has_consent=payload.has_consent,
    )
    saved = database.save_candidate_integrity_record(
        candidate_id=candidate_id,
        session_id=payload.session_id,
        round_type=payload.round_type,
        has_consent=payload.has_consent,
        total_risk_points=evaluated["total_risk_points"],
        risk_level=evaluated["risk_level"],
        requires_human_review=evaluated["requires_human_review"],
        events=payload.events,
        review_flags=evaluated.get("review_flags", []),
    )
    return CandidateIntegrityRecordResponse(**saved)


@router.get(
    "/candidates/{candidate_id}/integrity-records",
    response_model=list[CandidateIntegrityRecordResponse],
)
def list_candidate_integrity(candidate_id: str) -> list[CandidateIntegrityRecordResponse]:
    _candidate_or_404(candidate_id)
    records = database.get_candidate_integrity_records(candidate_id)
    return [CandidateIntegrityRecordResponse(**r) for r in records]


@router.post(
    "/candidates/{candidate_id}/behavioral-records",
    response_model=CandidateBehavioralRecordResponse,
    status_code=201,
)
def record_candidate_behavioral(
    candidate_id: str, payload: CandidateBehavioralRecordCreate
) -> CandidateBehavioralRecordResponse:
    _candidate_or_404(candidate_id)
    eval_result = behavioral_ai_engine.evaluate_observations(
        observations=payload.observations,
        has_consent=payload.has_consent,
    )
    saved = database.save_candidate_behavioral_record(
        candidate_id=candidate_id,
        session_id=payload.session_id,
        round_type=payload.round_type,
        has_consent=payload.has_consent,
        consistency_index=eval_result["consistency_index"],
        requires_human_review=eval_result["requires_human_review"],
        observations=payload.observations,
        disclaimer=eval_result["disclaimer"],
    )
    return CandidateBehavioralRecordResponse(**saved)


@router.get(
    "/candidates/{candidate_id}/behavioral-records",
    response_model=list[CandidateBehavioralRecordResponse],
)
def list_candidate_behavioral(candidate_id: str) -> list[CandidateBehavioralRecordResponse]:
    _candidate_or_404(candidate_id)
    records = database.get_candidate_behavioral_records(candidate_id)
    return [CandidateBehavioralRecordResponse(**r) for r in records]


# ---------------------------------------------------------------------------
# Day 41 & 51 + Day 42: Cross-Round Unified Scoring Routes
# ---------------------------------------------------------------------------

@router.post(
    "/candidates/{candidate_id}/cross-round-evaluation",
    response_model=CrossRoundEvaluationResponse,
    status_code=201,
)
def evaluate_cross_round_scoring(
    candidate_id: str, payload: CrossRoundEvaluationRequest
) -> CrossRoundEvaluationResponse:
    cand = _candidate_or_404(candidate_id)
    op_id = payload.opening_id or cand.get("opening_id", "default_opening")
    target_role = payload.target_role or "software_engineer"

    scores = dict(payload.round_scores or {})
    if not scores:
        if cand.get("score") is not None:
            scores["ats"] = float(cand["score"])
        screening_sessions = database.list_screening_sessions(candidate_id)
        if screening_sessions:
            reports = database.list_screening_reports_full(screening_sessions[0]["session_id"])
            if reports:
                scores["screening"] = float(reports[0]["report_json"].get("overall_score", 75.0))
        hr_sessions = database.list_hr_interview_sessions(candidate_id=candidate_id)
        if hr_sessions:
            hr_sc = database.get_hr_interview_score(hr_sessions[0]["interview_id"])
            if hr_sc:
                scores["hr_interview"] = float(hr_sc["overall_hr_score"])
        tech_sessions = database.list_technical_interview_sessions(candidate_id=candidate_id)
        if tech_sessions and tech_sessions[0]["overall_score"]:
            scores["technical_interview"] = float(tech_sessions[0]["overall_score"])
        mt_assigns = database.list_machine_test_assignments(candidate_id=candidate_id)
        if mt_assigns:
            subs = database.list_machine_test_submissions(mt_assigns[0]["assignment_id"])
            if subs:
                scores["machine_test"] = float(subs[0]["total_score"])

    unified = cross_round_scoring_engine.calculate_unified_fit(
        round_scores=scores,
        target_role=target_role,
        role_weights=payload.role_weights,
        missing_strategy=payload.missing_strategy,
    )
    saved = database.save_cross_round_evaluation(
        candidate_id=candidate_id,
        opening_id=op_id,
        target_role=target_role,
        hiring_fit_percentage=unified["hiring_fit_percentage"],
        round_scores=scores,
        effective_weights=unified["effective_weights"],
        completed_rounds=unified["completed_rounds_count"],
        missing_rounds=unified["missing_rounds"],
        anomalies=unified["anomalies"],
    )
    return CrossRoundEvaluationResponse(**saved)


@router.get(
    "/candidates/{candidate_id}/cross-round-evaluation",
    response_model=list[CrossRoundEvaluationResponse],
)
def list_candidate_cross_round_evaluations(candidate_id: str) -> list[CrossRoundEvaluationResponse]:
    _candidate_or_404(candidate_id)
    evals = database.list_cross_round_evaluations(candidate_id)
    return [CrossRoundEvaluationResponse(**e) for e in evals]


# ---------------------------------------------------------------------------
# Day 52: Final Recommendation AI Routes
# ---------------------------------------------------------------------------

@router.post(
    "/candidates/{candidate_id}/final-recommendation",
    response_model=FinalRecommendationResponse,
    status_code=201,
)
def generate_candidate_final_recommendation(
    candidate_id: str, payload: FinalRecommendationRequest
) -> FinalRecommendationResponse:
    cand = _candidate_or_404(candidate_id)
    op_id = payload.opening_id or cand.get("opening_id", "default_opening")
    target_role = payload.target_role or "Software Engineer"
    session_id = payload.session_id or f"sess_{candidate_id}"

    cross_evals = database.list_cross_round_evaluations(candidate_id)
    if cross_evals:
        last_eval = cross_evals[0]
        unified_score = last_eval["hiring_fit_percentage"]
        round_scores = last_eval["round_scores"]
        completed_rounds = last_eval["completed_rounds"]
    else:
        unified_score = float(cand.get("score") or 75.0)
        round_scores = {"ats": unified_score}
        completed_rounds = 1

    integrity_records = database.get_candidate_integrity_records(candidate_id)
    integrity_flagged = any(r["risk_level"] == "HIGH" or r["requires_human_review"] for r in integrity_records)
    integrity_evidence = []
    for r in integrity_records:
        for f in r.get("review_flags", []):
            integrity_evidence.append(str(f))

    behav_records = database.get_candidate_behavioral_records(candidate_id)
    behav_flagged = any(r["consistency_index"] < 50.0 or r["requires_human_review"] for r in behav_records)
    behav_evidence = [obs.get("note", "Inconsistent observation") for r in behav_records for obs in r.get("observations", []) if obs.get("impact") == "negative"]

    assessment_status = "COMPLETE" if completed_rounds >= 3 else "INCOMPLETE"

    assessment_payload = {
        "candidate_id": candidate_id,
        "session_id": session_id,
        "target_role": target_role,
        "assessment_status": assessment_status,
        "unified_score": unified_score,
        "completed_rounds": completed_rounds,
        "expected_rounds": 5,
        "evidence_quality": payload.evidence_quality,
        "data_consistency": payload.data_consistency,
        "rounds": round_scores,
        "risk_factors": {
            "integrity": {
                "flag": integrity_flagged,
                "evidence": integrity_evidence if integrity_flagged else [],
                "source": "Integrity Monitoring Subsystem",
            },
            "behavior": {
                "flag": behav_flagged,
                "evidence": behav_evidence if behav_flagged else [],
                "source": "Behavioral Signals Subsystem",
            },
        },
    }

    rec_result = recommend_candidate(assessment_payload, rules=payload.custom_rules)
    saved = database.save_final_recommendation(
        candidate_id=candidate_id,
        opening_id=op_id,
        target_role=target_role,
        decision=rec_result["decision"],
        score=rec_result["score"],
        confidence=rec_result["confidence"],
        completed_rounds=completed_rounds,
        expected_rounds=5,
        reasons=rec_result["explanation"]["reasons"],
        risk_factors=rec_result["risk_factors"],
    )
    return FinalRecommendationResponse(**saved)


@router.get(
    "/candidates/{candidate_id}/final-recommendation",
    response_model=list[FinalRecommendationResponse],
)
def list_candidate_final_recommendations(candidate_id: str) -> list[FinalRecommendationResponse]:
    _candidate_or_404(candidate_id)
    recs = database.list_final_recommendations(candidate_id=candidate_id)
    return [FinalRecommendationResponse(**r) for r in recs]


@router.post(
    "/final-recommendations/{recommendation_id}/decision",
    response_model=FinalRecommendationResponse,
)
def update_final_recommendation_recruiter_decision(
    recommendation_id: str, payload: FinalRecommendationDecisionRequest
) -> FinalRecommendationResponse:
    rec = database.get_final_recommendation(recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Final recommendation not found.")
    updated = database.update_final_recommendation_decision(
        recommendation_id=recommendation_id,
        recruiter_decision=payload.recruiter_decision,
        recruiter_notes=payload.notes,
    )
    security_governance.log_audit_event(
        event_type="RECRUITER_DECISION_UPDATED",
        actor_id="recruiter",
        subject_id=rec["candidate_id"],
        details={
            "recommendation_id": recommendation_id,
            "decision": payload.recruiter_decision,
            "notes": payload.notes,
        },
    )
    return FinalRecommendationResponse(**updated)


# ============================================================================
# Days 53-60: Hiring Intelligence Reports, Security, Simulation, Coaching & Batching
# ============================================================================

@router.post(
    "/candidates/{candidate_id}/hiring-intelligence-report",
    response_model=HiringIntelligenceReportResponse,
    status_code=201,
)
def generate_hiring_intelligence_report_endpoint(
    candidate_id: str, request: Request
) -> HiringIntelligenceReportResponse:
    cand = _candidate_or_404(candidate_id)
    recruiter_id = request.cookies.get(SESSION_COOKIE_NAME, "recruiter_session")
    report = generate_candidate_hiring_report(
        candidate_id=candidate_id,
        recruiter_id=recruiter_id,
        save_to_db=True,
    )
    security_governance.log_audit_event(
        event_type="HIRING_REPORT_GENERATED",
        actor_id=recruiter_id,
        subject_id=candidate_id,
        details={"report_id": report.get("report_id"), "version": report.get("version", 1)},
    )
    return HiringIntelligenceReportResponse(**report)


@router.get(
    "/candidates/{candidate_id}/hiring-intelligence-report",
    response_model=HiringIntelligenceReportResponse,
)
def get_latest_hiring_intelligence_report_endpoint(
    candidate_id: str,
) -> HiringIntelligenceReportResponse:
    _candidate_or_404(candidate_id)
    report_record = database.get_latest_hiring_intelligence_report(candidate_id)
    if not report_record:
        report_data = generate_candidate_hiring_report(candidate_id, save_to_db=True)
        return HiringIntelligenceReportResponse(**report_data)
    rep = dict(report_record["report_json"])
    rep["report_id"] = report_record["report_id"]
    rep["version"] = report_record["version"]
    rep["created_at"] = report_record["created_at"]
    return HiringIntelligenceReportResponse(**rep)


@router.get(
    "/candidates/{candidate_id}/hiring-intelligence-report/history",
    response_model=list[HiringIntelligenceReportResponse],
)
def get_hiring_intelligence_report_history_endpoint(
    candidate_id: str,
) -> list[HiringIntelligenceReportResponse]:
    _candidate_or_404(candidate_id)
    records = database.list_hiring_intelligence_reports(candidate_id)
    results = []
    for r in records:
        rep = dict(r["report_json"])
        rep["report_id"] = r["report_id"]
        rep["version"] = r["version"]
        rep["created_at"] = r["created_at"]
        results.append(HiringIntelligenceReportResponse(**rep))
    return results


@router.get("/hiring-intelligence-reports/{report_id}/html")
def get_hiring_intelligence_report_html_endpoint(report_id: str) -> Response:
    record = database.get_hiring_intelligence_report(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Hiring report not found.")
    return Response(content=record["html_content"], media_type="text/html")


@router.get("/candidates/{candidate_id}/hiring-intelligence-report/html")
def get_candidate_hiring_intelligence_report_html_endpoint(candidate_id: str) -> Response:
    record = database.get_latest_hiring_intelligence_report(candidate_id)
    if not record:
        generate_candidate_hiring_report(candidate_id, save_to_db=True)
        record = database.get_latest_hiring_intelligence_report(candidate_id)
    if not record:
        raise HTTPException(status_code=404, detail="Hiring report not found for candidate.")
    return Response(content=record["html_content"], media_type="text/html")


@router.get("/hiring-intelligence-reports/{report_id}/markdown")
def get_hiring_intelligence_report_markdown_endpoint(report_id: str) -> Response:
    record = database.get_hiring_intelligence_report(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Hiring report not found.")
    return Response(content=record["markdown_content"], media_type="text/markdown")


@router.get("/candidates/{candidate_id}/hiring-intelligence-report/markdown")
def get_candidate_hiring_intelligence_report_markdown_endpoint(candidate_id: str) -> Response:
    record = database.get_latest_hiring_intelligence_report(candidate_id)
    if not record:
        generate_candidate_hiring_report(candidate_id, save_to_db=True)
        record = database.get_latest_hiring_intelligence_report(candidate_id)
    if not record:
        raise HTTPException(status_code=404, detail="Hiring report not found for candidate.")
    return Response(content=record["markdown_content"], media_type="text/markdown")


@router.get("/audit/events", response_model=list[AuditEventResponse])
def get_audit_events_endpoint(
    limit: int = 100,
    event_type: str | None = None,
    subject_id: str | None = None,
) -> list[AuditEventResponse]:
    events = database.list_audit_events(limit=limit, event_type=event_type, subject_id=subject_id)
    return [AuditEventResponse(**e) for e in events]


@router.get("/audit/verify", response_model=AuditVerificationResponse)
def verify_audit_trail_endpoint() -> AuditVerificationResponse:
    res = database.verify_audit_log_integrity()
    return AuditVerificationResponse(**res)


@router.post(
    "/candidates/{candidate_id}/coaching",
    response_model=CandidateCoachingResponse,
    status_code=201,
)
def generate_candidate_coaching_endpoint(
    candidate_id: str,
) -> CandidateCoachingResponse:
    cand = _candidate_or_404(candidate_id)
    opening = database.get_opening(cand["opening_id"]) if cand.get("opening_id") else None
    target_role = opening.get("title") if opening else "Software Engineer"
    coaching = coaching_engine.generate_candidate_coaching(
        candidate_id=candidate_id,
        target_role=target_role,
        save_to_db=True,
    )
    return CandidateCoachingResponse(**coaching)


@router.get(
    "/candidates/{candidate_id}/coaching",
    response_model=CandidateCoachingResponse,
)
def get_candidate_coaching_endpoint(candidate_id: str) -> CandidateCoachingResponse:
    _candidate_or_404(candidate_id)
    record = database.get_latest_coaching_record(candidate_id)
    if not record:
        coaching = coaching_engine.generate_candidate_coaching(
            candidate_id=candidate_id,
            save_to_db=True,
        )
        return CandidateCoachingResponse(**coaching)
    return CandidateCoachingResponse(
        coaching_id=record["coaching_id"],
        candidate_id=record["candidate_id"],
        target_role=record["target_role"],
        identified_skill_gaps=record["identified_skill_gaps"],
        recommended_preparation=record["recommended_preparation"],
        practice_questions=record["practice_questions"],
        governance_guardrails={
            "influences_hiring_status": False,
            "emotion_detection_enabled": False,
            "automatic_rejection_enabled": False,
            "human_recruiter_decision_only": True,
        },
        disclaimer="Candidate coaching suggestions are developmental aids and do not affect hiring status.",
        created_at=record["created_at"],
    )


@router.post("/simulation/run", response_model=SimulationRunResponse, status_code=201)
def run_simulation_endpoint(payload: SimulationRunRequest) -> SimulationRunResponse:
    result = system_simulation_pipeline.simulate_candidate_pipeline(
        candidate_data=payload.candidate,
        opening_data=payload.opening,
    )
    return SimulationRunResponse(**result)


@router.post("/simulation/benchmark", response_model=BenchmarkComparisonResponse)
def compare_benchmark_endpoint(payload: BenchmarkComparisonRequest) -> BenchmarkComparisonResponse:
    comparison = system_simulation_pipeline.compare_ai_vs_human_evaluations(
        simulation_results=payload.simulations,
        human_evaluations=payload.human_evaluations,
    )
    return BenchmarkComparisonResponse(**comparison)


@router.post("/resumes/batch-process", response_model=BatchResumeProcessResponse)
async def batch_process_resumes_endpoint(payload: BatchResumeProcessRequest) -> BatchResumeProcessResponse:
    def _extract_skills(item: dict[str, Any]) -> dict[str, Any]:
        text = item.get("text", "").lower()
        skills = [s for s in ["python", "fastapi", "sql", "docker", "aws", "react"] if s in text]
        return {"extracted_skills": skills, "status": "EXTRACTED"}

    result = await batch_process_resumes(
        resumes=payload.resumes,
        process_fn=_extract_skills,
        batch_size=payload.batch_size,
        max_concurrency=payload.max_concurrency,
    )
    return BatchResumeProcessResponse(**result)


# ---------------------------------------------------------------------------
# Day 61: Observability & Monitoring Endpoints
# ---------------------------------------------------------------------------


@router.get("/monitoring/dashboard", response_model=MonitoringDashboardResponse)
def get_monitoring_dashboard_endpoint(
    recruiter: dict = Depends(require_recruiter),
) -> MonitoringDashboardResponse:
    summary = observability.get_dashboard_summary()
    return MonitoringDashboardResponse(**summary)


@router.get("/monitoring/alerts", response_model=list[MonitoringAlertItem])
def get_monitoring_alerts_endpoint(
    recruiter: dict = Depends(require_recruiter),
) -> list[MonitoringAlertItem]:
    active_alerts = observability.evaluate_alerts()
    return [MonitoringAlertItem(**a) for a in active_alerts]


@router.get("/monitoring/decision-audit", response_model=list[DecisionAuditLogResponse])
def get_decision_audit_logs_endpoint(
    limit: int = 50,
    recruiter: dict = Depends(require_recruiter),
) -> list[DecisionAuditLogResponse]:
    events = read_jsonl(observability.log_dir / "decision_audit.jsonl", max_records=limit)
    return [DecisionAuditLogResponse(**e) for e in events]


@router.post("/monitoring/log-event", status_code=201)
def log_observability_event_endpoint(
    payload: MonitoringLogEventRequest,
    recruiter: dict = Depends(require_recruiter),
) -> dict[str, Any]:
    event_type = payload.event_type
    p = payload.payload
    if event_type == "api_request":
        res = observability.log_api_request(
            endpoint=p.get("endpoint", "/custom"),
            method=p.get("method", "GET"),
            status_code=int(p.get("status_code", 200)),
            duration_ms=float(p.get("duration_ms", 10.0)),
            correlation_id=p.get("correlation_id"),
            user_ref=p.get("user_ref", recruiter.get("username")),
        )
    elif event_type == "model_run":
        res = observability.log_model_run(
            model_name=p.get("model_name", "custom_model"),
            model_version=p.get("model_version", "1.0"),
            task=p.get("task", "custom_task"),
            duration_ms=float(p.get("duration_ms", 50.0)),
            success=bool(p.get("success", True)),
            input_ref=p.get("input_ref"),
        )
    elif event_type == "error":
        res = observability.log_error(
            component=p.get("component", "system"),
            error_type=p.get("error_type", "GenericError"),
            safe_message=p.get("safe_message", "Error logged"),
        )
    elif event_type == "decision_audit":
        res = observability.log_decision_audit(
            candidate_ref=p.get("candidate_ref", ""),
            opening_ref=p.get("opening_ref"),
            decision=p.get("decision", "REVIEW_REQUIRED"),
            reason=p.get("reason", "Logged via API"),
            actor=p.get("actor", recruiter.get("username", "recruiter")),
            model_version=p.get("model_version", "v1.0"),
            human_reviewed=bool(p.get("human_reviewed", True)),
        )
    else:
        raise HTTPException(status_code=400, detail="Unknown event type.")
    return {"status": "LOGGED", "record": res}


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
