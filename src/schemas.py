import re
from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


Skill = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
]
NonBlankText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


ApplicationStatus = Literal[
    "APPLIED",
    "IN_REVIEW",
    "SHORTLISTED",
    "INTERVIEW",
    "OFFER",
    "HIRED",
    "REJECTED",
    "WITHDRAWN",
]


class OpeningCreate(BaseModel):
    title: Annotated[NonBlankText, Field(min_length=2, max_length=160)]
    description: str = Field(default="", max_length=20_000)
    required_skills: list[Skill] = Field(min_length=1, max_length=100)
    preferred_skills: list[Skill] = Field(default_factory=list, max_length=100)
    minimum_education: str | None = Field(default=None, max_length=160)
    minimum_years_experience: float | None = Field(default=None, ge=0, le=80)


class OpeningUpdate(BaseModel):
    title: Annotated[NonBlankText, Field(min_length=2, max_length=160)] | None = None
    description: str | None = Field(default=None, max_length=20_000)
    required_skills: list[Skill] | None = Field(default=None, min_length=1, max_length=100)
    preferred_skills: list[Skill] | None = Field(default=None, max_length=100)
    minimum_education: str | None = Field(default=None, max_length=160)
    minimum_years_experience: float | None = Field(default=None, ge=0, le=80)
    status: Literal["OPEN", "CLOSED"] | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, value: Any) -> Any:
        if isinstance(value, dict):
            null_fields = [
                field
                for field in (
                    "title",
                    "description",
                    "required_skills",
                    "preferred_skills",
                    "status",
                )
                if field in value and value[field] is None
            ]
            if null_fields:
                raise ValueError(
                    f"Fields cannot be null: {', '.join(null_fields)}."
                )
        return value


class OpeningResponse(BaseModel):
    opening_id: str
    title: str
    description: str
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_education: str | None = None
    minimum_years_experience: float | None = None
    status: str
    created_at: str
    updated_at: str


class JobDescriptionParseRequest(BaseModel):
    description: str = Field(min_length=1, max_length=20_000)


class JobDescriptionParseResponse(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_education: str | None
    minimum_years_experience: float | None
    evidence: dict[str, list[str]]
    warnings: list[str]
    method: Literal["explicit_heading_rules_v1"]
    human_confirmation_required: Literal[True] = True


class CandidateCreate(BaseModel):
    name: Annotated[NonBlankText, Field(max_length=160)]
    email: str | None = Field(default=None, max_length=320)
    opening_id: str = Field(min_length=1, max_length=80)
    skills: list[Skill] = Field(default_factory=list, max_length=100)
    resume_text: str = Field(default="", max_length=200_000)
    location: str | None = Field(default=None, max_length=160)
    relocation_willingness: bool | None = None
    work_mode_preference: Literal["ONSITE", "HYBRID", "REMOTE"] | None = None
    availability_date: str | None = Field(default=None, max_length=10)

    @field_validator("availability_date")
    @classmethod
    def validate_availability_date(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("availability_date must use YYYY-MM-DD.") from exc
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", value
        ):
            raise ValueError("Enter a valid email address.")
        return value


class CandidateUpdate(BaseModel):
    name: Annotated[NonBlankText, Field(max_length=160)] | None = None
    email: str | None = Field(default=None, max_length=320)
    skills: list[Skill] | None = Field(default=None, max_length=100)
    application_status: ApplicationStatus | None = None
    location: str | None = Field(default=None, max_length=160)
    relocation_willingness: bool | None = None
    work_mode_preference: Literal["ONSITE", "HYBRID", "REMOTE"] | None = None
    availability_date: str | None = Field(default=None, max_length=10)

    @field_validator("availability_date")
    @classmethod
    def validate_availability_date(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("availability_date must use YYYY-MM-DD.") from exc
        return value

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, value: Any) -> Any:
        if isinstance(value, dict):
            null_fields = [
                field
                for field in ("name", "skills", "application_status")
                if field in value and value[field] is None
            ]
            if null_fields:
                raise ValueError(
                    f"Fields cannot be null: {', '.join(null_fields)}."
                )
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", value
        ):
            raise ValueError("Enter a valid email address.")
        return value


class CandidateResponse(BaseModel):
    candidate_id: str
    name: str
    email: str | None
    opening_id: str
    skills: list[str]
    resume_text: str
    resume_data: dict[str, Any]
    resume_filename: str | None
    application_status: str
    score: float | None
    score_evidence: dict[str, Any] | None
    location: str | None = None
    relocation_willingness: bool | None = None
    work_mode_preference: str | None = None
    availability_date: str | None = None
    created_at: str
    updated_at: str


class ResumeUploadResponse(BaseModel):
    job_id: str
    filename: str
    candidate_id: str | None = None
    status: str
    message: str


class ParseRequest(BaseModel):
    job_id: str


class ParseResponse(BaseModel):
    job_id: str
    status: str
    parsed_text: str
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    message: str


class ScoreRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=80)
    candidate_id: str


class ScoreResponse(BaseModel):
    job_id: str
    candidate_id: str
    score: float
    evidence: dict[str, Any]
    job_title: str
    candidate_name: str
    extracted_skills: list[str]
    matching_required_skills: list[str]
    missing_required_skills: list[str]
    education_details: list[dict[str, Any]]
    experience_details: dict[str, Any]
    components: dict[str, Any]
    ranking: int
    human_review_required: bool = True
    status: str
    message: str


class ShortlistRequest(BaseModel):
    candidates: list[dict[str, Any]]
    minimum_score: float = Field(default=60.0, ge=0.0, le=100.0)


class ShortlistedCandidate(BaseModel):
    candidate_id: str
    score: float
    rank: int


class ShortlistResponse(BaseModel):
    job_id: str
    status: str
    shortlisted_count: int
    candidates: list[ShortlistedCandidate]
    human_review_required: bool = True
    simulation_only: bool = False
    message: str


class PersistedShortlistRequest(BaseModel):
    minimum_score: float = Field(default=60.0, ge=0.0, le=100.0)


class ATSShortlistRequest(BaseModel):
    job_id: str
    minimum_score: float = Field(default=60.0, ge=0.0, le=100.0)



ScreeningIntent = Literal[
    "skills",
    "experience",
    "availability",
    "salary_expectation",
]


class ScreeningAnswerRequest(BaseModel):
    question_id: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)
    ]
    question: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)
    ]
    answer: str = Field(max_length=10_000)
    expected_intent: ScreeningIntent


class ScreeningReportRequest(BaseModel):
    answers: list[ScreeningAnswerRequest] = Field(min_length=1, max_length=20)


class ScreeningReportResponse(BaseModel):
    report_id: str
    candidate_id: str
    opening_id: str
    created_at: str
    method: Literal["day25_keyword_and_regex_rules"]
    answers: list[dict[str, Any]]
    review_flags: list[str]
    human_review_required: Literal[True] = True


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] | None = None


class RecruiterLoginRequest(BaseModel):
    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)
    ]
    password: Annotated[str, StringConstraints(min_length=1, max_length=1024)]


class RecruiterSessionResponse(BaseModel):
    authenticated: bool
    username: str | None = None
    expires_at: float | None = None


class EligibilityLocationRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed_locations: list[
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    ] = Field(default_factory=list, max_length=100)
    work_mode: Literal["ONSITE", "HYBRID", "REMOTE"] | None = None
    remote_allowed: bool = False
    relocation_required: bool = False
    latest_start_date: str | None = Field(default=None, max_length=10)


class EligibilityDecisionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manual_review_on_missing_data: bool = True


class EligibilityConfigurationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minimum_ats_score: float | None = Field(default=None, ge=0, le=100)
    mandatory_skills: list[Skill] = Field(default_factory=list, max_length=100)
    minimum_experience_years: float | None = Field(default=None, ge=0, le=80)
    maximum_experience_years: float | None = Field(default=None, ge=0, le=80)
    location_rules: EligibilityLocationRules = Field(default_factory=EligibilityLocationRules)
    decision_policy: EligibilityDecisionPolicy = Field(default_factory=EligibilityDecisionPolicy)

    @model_validator(mode="after")
    def validate_experience_range(self) -> "EligibilityConfigurationRequest":
        if (
            self.minimum_experience_years is not None
            and self.maximum_experience_years is not None
            and self.minimum_experience_years > self.maximum_experience_years
        ):
            raise ValueError("Minimum experience cannot exceed maximum experience.")
        return self

    @field_validator("mandatory_skills")
    @classmethod
    def validate_unique_skills(cls, value: list[str]) -> list[str]:
        normalized = [skill.casefold() for skill in value]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Mandatory skills must be unique.")
        return value

    @model_validator(mode="after")
    def validate_location_rules(self) -> "EligibilityConfigurationRequest":
        if self.location_rules.latest_start_date is not None:
            try:
                date.fromisoformat(self.location_rules.latest_start_date)
            except ValueError as exc:
                raise ValueError("latest_start_date must use YYYY-MM-DD.") from exc
        if (
            self.location_rules.relocation_required
            and not self.location_rules.allowed_locations
        ):
            raise ValueError(
                "Relocation can only be required when allowed locations are configured."
            )
        return self


class EligibilityConfigurationResponse(BaseModel):
    opening_id: str
    version: int
    configuration: EligibilityConfigurationRequest
    created_at: str
    updated_at: str


class EligibilityEvaluationRequest(BaseModel):
    opening_id: str = Field(min_length=1, max_length=80)


class EligibilityEvaluationResponse(BaseModel):
    evaluation_id: str
    candidate_id: str
    opening_id: str
    status: Literal["ELIGIBLE", "REVIEW", "REJECTED"]
    ats_score: float | None
    rules: dict[str, Any]
    mandatory_skills_matched: list[str]
    mandatory_skills_missing: list[str]
    experience_result: dict[str, Any]
    location_result: dict[str, Any]
    availability_result: dict[str, Any]
    missing_information: list[str]
    review_reasons: list[str]
    decision_explanation: str
    configuration_version: int
    evaluated_at: str
    human_review_required: Literal[True] = True


class ScreeningQuestionResponse(BaseModel):
    question_id: str
    role_id: str
    role_label: str
    category: str
    question_text: str
    expected_answer_type: str
    mandatory: bool
    scoring_importance: str
    display_order: int
    language: str
    is_active: bool
    version: int
    translations: dict[str, Any]
    follow_up_eligible: bool


class ScreeningSessionCreate(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=80)
    opening_id: str = Field(min_length=1, max_length=80)
    language: str = Field(default="en", min_length=2, max_length=16)
    source: Literal["MANUAL", "RECRUITER", "IMPORT"] = "MANUAL"


class ScreeningSessionStatusUpdate(BaseModel):
    status: Literal["IN_PROGRESS", "INTERRUPTED", "COMPLETED", "CANCELLED"]


class TranscriptSegmentCreate(BaseModel):
    segment_id: str | None = Field(default=None, min_length=1, max_length=80)
    question_id: str | None = Field(default=None, min_length=1, max_length=80)
    speaker: Literal["CANDIDATE", "RECRUITER", "AI", "SYSTEM", "FOLLOW_UP"]
    text: str = Field(max_length=20_000)
    start_time: datetime | None = None
    end_time: datetime | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    language: str | None = Field(default=None, min_length=2, max_length=16)
    source: Literal["MANUAL", "RECRUITER", "IMPORT", "SPEECH_RECOGNITION"] = "MANUAL"
    sequence_number: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_times(self) -> "TranscriptSegmentCreate":
        if self.start_time and self.start_time.tzinfo is None:
            raise ValueError("start_time must include a timezone.")
        if self.end_time and self.end_time.tzinfo is None:
            raise ValueError("end_time must include a timezone.")
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("end_time cannot precede start_time.")
        return self


class TranscriptSegmentResponse(BaseModel):
    segment_id: str
    session_id: str
    question_id: str | None
    speaker: str
    raw_text: str
    normalized_text: str
    start_time: str | None
    end_time: str | None
    confidence: float | None
    language: str | None
    source: str
    processing_version: str
    sequence_number: int
    created_at: str
    updated_at: str


class ScreeningInteractionCreate(BaseModel):
    question_id: str = Field(min_length=1, max_length=80)
    candidate_answer: str | None = Field(default=None, max_length=20_000)
    answer_type: str | None = Field(default=None, max_length=40)
    validation_status: Literal["PENDING", "VALID", "INVALID", "SKIPPED", "UNANSWERED"] = "PENDING"
    display_order: int = Field(ge=1)
    follow_up_to: str | None = Field(default=None, max_length=80)


class ScreeningInteractionResponse(BaseModel):
    interaction_id: str
    session_id: str
    question_id: str
    candidate_answer: str | None
    answer_type: str | None
    validation_status: str
    display_order: int
    follow_up_to: str | None
    created_at: str
    updated_at: str


class ScreeningSessionResponse(BaseModel):
    session_id: str
    candidate_id: str
    opening_id: str
    status: str
    language: str
    started_at: str
    completed_at: str | None
    source: str
    version: int
    created_at: str
    updated_at: str


class ScreeningTranscriptResponse(BaseModel):
    session: ScreeningSessionResponse
    segments: list[TranscriptSegmentResponse]
    interactions: list[ScreeningInteractionResponse]


class ScreeningAudioUploadResponse(BaseModel):
    audio_id: str
    session_id: str
    question_id: str | None
    status: str
    message: str


class ScreeningAudioStatusResponse(BaseModel):
    audio_id: str
    session_id: str
    question_id: str | None
    file_path: str
    file_size_bytes: int
    duration_seconds: float | None
    mime_type: str
    source: str
    status: str
    created_at: str
    updated_at: str


class ScreeningTranscriptCreate(BaseModel):
    audio_id: str | None = Field(default=None, min_length=1, max_length=80)
    question_id: str | None = Field(default=None, min_length=1, max_length=80)
    raw_text: str = Field(max_length=50_000)
    cleaned_text: str = Field(max_length=50_000)
    language: str | None = Field(default=None, min_length=2, max_length=16)
    language_probability: float | None = Field(default=None, ge=0, le=1)
    partial_answer: bool = False
    segment_count: int = Field(default=0, ge=0)
    processing_version: str = "stt-v1"


class ScreeningTranscriptDetailResponse(BaseModel):
    transcript_id: str
    session_id: str
    audio_id: str | None
    question_id: str | None
    raw_text: str
    cleaned_text: str
    language: str | None
    language_probability: float | None
    partial_answer: bool
    segment_count: int
    processing_version: str
    created_at: str
    updated_at: str


class ScreeningAnswerCreate(BaseModel):
    transcript_id: str | None = Field(default=None, min_length=1, max_length=80)
    question_id: str = Field(min_length=1, max_length=80)
    question_text: str = Field(max_length=5_000)
    expected_intent: str = Field(min_length=1, max_length=80)
    detected_intent: str | None = Field(default=None, max_length=80)
    answer_status: Literal["VALID", "INVALID", "PARTIAL", "VAGUE", "OFF_TOPIC", "UNCLEAR", "MISSING"]
    raw_answer: str = Field(max_length=50_000)
    cleaned_answer: str = Field(max_length=50_000)
    extracted_information: dict[str, Any] = Field(default_factory=dict)
    intent_confidence: float | None = Field(default=None, ge=0, le=1)
    needs_clarification: bool = False
    is_off_topic: bool = False


class ScreeningAnswerResponse(BaseModel):
    answer_id: str
    session_id: str
    transcript_id: str | None
    question_id: str
    question_text: str
    expected_intent: str
    detected_intent: str | None
    answer_status: str
    raw_answer: str
    cleaned_answer: str
    extracted_information: dict[str, Any]
    intent_confidence: float | None
    needs_clarification: bool
    is_off_topic: bool
    created_at: str
    updated_at: str


class ScreeningQuestionScoreCreate(BaseModel):
    answer_id: str = Field(min_length=1, max_length=80)
    question_id: str = Field(min_length=1, max_length=80)
    clarity_score: int = Field(ge=0, le=5)
    relevance_score: int = Field(ge=0, le=5)
    completeness_score: int = Field(ge=0, le=5)
    consistency_score: int = Field(ge=0, le=5)
    weighted_score: float
    normalized_score: float
    explanation: str
    human_review_required: bool = False
    scoring_version: str = "screening-v1"


class ScreeningQuestionScoreResponse(BaseModel):
    score_id: str
    session_id: str
    answer_id: str
    question_id: str
    clarity_score: int
    relevance_score: int
    completeness_score: int
    consistency_score: int
    weighted_score: float
    normalized_score: float
    explanation: str
    human_review_required: bool
    scoring_version: str
    created_at: str
    updated_at: str


class ScreeningAggregateScoreResponse(BaseModel):
    aggregate_id: str
    session_id: str
    candidate_id: str
    overall_score: float
    score_status: Literal["PROVISIONAL", "FINAL", "REVIEW_REQUIRED"]
    questions_evaluated: int
    questions_answered: int
    questions_missing: int
    human_review_required: bool
    scoring_version: str
    created_at: str
    updated_at: str


class BehavioralAnalysisCreate(BaseModel):
    answer_id: str | None = Field(default=None, min_length=1, max_length=80)
    sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED", "UNCERTAIN"] | None = None
    sentiment_score: float | None = Field(default=None, ge=-100, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=100)
    hesitation_count: int = Field(default=0, ge=0)
    uncertainty_count: int = Field(default=0, ge=0)
    contradiction_detected: bool = False
    contradiction_details: str | None = None
    response_length_category: Literal["SHORT", "MEDIUM", "LONG"] | None = None
    words_per_minute: float | None = None
    pace_category: Literal["FAST", "NORMAL", "SLOW", "UNKNOWN"] | None = None
    processing_version: str = "behavioral-v1"


class BehavioralAnalysisResponse(BaseModel):
    analysis_id: str
    session_id: str
    answer_id: str | None
    sentiment: str | None
    sentiment_score: float | None
    confidence_score: float | None
    hesitation_count: int
    uncertainty_count: int
    contradiction_detected: bool
    contradiction_details: str | None
    response_length_category: str | None
    words_per_minute: float | None
    pace_category: str | None
    processing_version: str
    created_at: str
    updated_at: str


class ScreeningReportFullCreate(BaseModel):
    candidate_id: str
    opening_id: str
    report_json: dict[str, Any]
    html_report: str | None = None
    pdf_report: bytes | None = None


class ScreeningReportFullResponse(BaseModel):
    report_id: str
    session_id: str
    candidate_id: str
    opening_id: str
    report_json: dict[str, Any]
    html_report: str | None
    version: int
    status: str
    created_at: str
    updated_at: str


# ============================================================================
# HR INTERVIEW SUBSYSTEM (DAYS 33-40) SCHEMAS
# ============================================================================

class HRInterviewSessionCreate(BaseModel):
    candidate_id: str
    opening_id: str
    experience_level: Literal["FRESHER", "EXPERIENCED"] = "FRESHER"
    role_type: Literal["TECHNICAL", "NON_TECHNICAL"] = "NON_TECHNICAL"
    recruiter_id: str | None = None


class HRInterviewSessionResponse(BaseModel):
    interview_id: str
    candidate_id: str
    opening_id: str
    status: str
    current_phase: str
    current_question_id: str | None
    experience_level: str
    role_type: str
    recruiter_id: str | None
    created_at: str
    updated_at: str


class HRInterviewSessionStatusUpdate(BaseModel):
    status: Literal["CREATED", "IN_PROGRESS", "PAUSED", "COMPLETED", "CANCELLED", "FAILED"]
    current_phase: Literal["CREATED", "INTRODUCTION", "CORE_HR_QUESTIONS", "ROLE_BASED_EVALUATION", "CLOSING", "COMPLETED"] | None = None
    current_question_id: str | None = None


class HRInterviewQuestionResponse(BaseModel):
    question_id: str
    interview_id: str
    category: str
    question_text: str
    role_type: str
    experience_level: str
    difficulty: str
    expected_answer_criteria: str | None = None
    evaluation_parameters: dict[str, Any] | None = None
    follow_up_eligibility: bool = True
    question_order: int = 0
    active_status: bool = True
    created_at: str


class HRInterviewAnswerSubmit(BaseModel):
    question_id: str
    answer_text: str


class HRInterviewAnswerResponse(BaseModel):
    response_id: str
    interview_id: str
    question_id: str
    raw_response: str
    cleaned_response: str
    quality: str
    follow_up_eligible: bool
    follow_up_count: int
    created_at: str
    updated_at: str


class HRInterviewFollowUpSubmit(BaseModel):
    parent_question_id: str
    followup_type: Literal["clarification", "deepening", "example_based", "scenario_based"]
    followup_question: str
    candidate_response: str


class HRInterviewFollowUpResponse(BaseModel):
    followup_id: str
    interview_id: str
    parent_question_id: str
    followup_type: str
    followup_question: str
    candidate_response: str | None
    difficulty_level: str
    created_at: str
    updated_at: str


class HRCommunicationEvaluationResponse(BaseModel):
    evaluation_id: str
    interview_id: str
    response_id: str | None
    fluency_score: float
    grammar_score: float
    vocabulary_score: float
    clarity_score: float
    structure_score: float
    filler_control_score: float
    total_communication_score: float
    fillers_detected: list[str]
    evidence: list[str]
    created_at: str


class HRBehavioralSignalsResponse(BaseModel):
    signal_id: str
    interview_id: str
    response_id: str | None
    hesitation_count: int
    pause_count: int
    uncertainty_count: int
    repeated_word_count: int
    sentiment: str
    sentiment_score: float
    stress_score: float
    confidence_score: float
    contradiction_detected: bool
    contradiction_reason: str | None
    disclaimer: str
    created_at: str


class HRAptitudeEvaluationResponse(BaseModel):
    aptitude_id: str
    interview_id: str
    question_id: str
    category: str
    candidate_answer: str
    logic_score: float
    clarity_score: float
    problem_solving_score: float
    decision_making_score: float
    communication_score: float
    overall_score: float
    evaluation_details: dict[str, Any]
    created_at: str


class HRInterviewScoreResponse(BaseModel):
    score_id: str
    interview_id: str
    candidate_id: str
    relevance_score: float
    communication_score: float
    confidence_score: float
    consistency_score: float
    overall_hr_score: float
    score_status: str
    breakdown: dict[str, Any]
    human_review_required: bool
    created_at: str
    updated_at: str


class HRInterviewReportResponse(BaseModel):
    report_id: str
    interview_id: str
    candidate_id: str
    opening_id: str
    report_json: dict[str, Any]
    html_report: str | None
    version: int
    recruiter_decision: str | None
    recruiter_notes: str | None
    created_at: str
    updated_at: str


class HRInterviewDecisionRequest(BaseModel):
    decision: Literal["PROCEED", "HOLD", "REJECT", "MANUAL_REVIEW"]
    notes: str | None = None


# ---------------------------------------------------------------------------
# Days 41–52: Technical Interview, Machine Test, Integrity & Final Recommendation
# ---------------------------------------------------------------------------


class TechnicalInterviewSessionCreate(BaseModel):
    candidate_id: str
    opening_id: str
    target_role: str | None = None
    experience_level: str | None = None


class TechnicalInterviewQuestionResponse(BaseModel):
    question_id: str
    session_id: str
    question_text: str
    topic: str
    question_type: str
    difficulty: str
    sequence_order: int
    expected_criteria: list[str] = Field(default_factory=list)
    created_at: str


class TechnicalInterviewSessionResponse(BaseModel):
    session_id: str
    candidate_id: str
    opening_id: str
    target_role: str
    experience_level: str
    status: str
    current_stage: str
    total_questions: int
    overall_score: float
    rubric_breakdown: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class TechnicalInterviewAnswerSubmit(BaseModel):
    question_id: str
    answer_text: str


class TechnicalInterviewResponseResult(BaseModel):
    response_id: str
    session_id: str
    question_id: str
    raw_answer: str
    score: float
    depth_level: str
    parameter_scores: dict[str, Any] = Field(default_factory=dict)
    feedback: str
    created_at: str


class TechnicalInterviewCompleteResponse(BaseModel):
    session_id: str
    status: str
    overall_score: float
    rubric_breakdown: dict[str, Any]
    total_questions: int
    completed_at: str


class MachineTestAssignmentCreate(BaseModel):
    candidate_id: str
    opening_id: str
    task_type: Literal["coding", "debugging", "file_based", "mini_system_design"]
    task_id: str | None = None
    title: str | None = None
    description: str | None = None
    time_limit_minutes: int = 60


class MachineTestAssignmentResponse(BaseModel):
    assignment_id: str
    candidate_id: str
    opening_id: str
    task_type: str
    task_id: str
    title: str
    description: str
    time_limit_minutes: int
    status: str
    assigned_at: str
    completed_at: str | None = None


class MachineTestSubmissionCreate(BaseModel):
    code_content: str
    language: str = "python"
    time_spent_minutes: float = 0.0


class MachineTestSubmissionResponse(BaseModel):
    submission_id: str
    assignment_id: str
    code_content: str
    language: str
    time_spent_minutes: float
    total_score: float
    rubric_scores: dict[str, Any]
    execution_details: dict[str, Any]
    status: str
    submitted_at: str


class CandidateIntegrityRecordCreate(BaseModel):
    session_id: str
    round_type: str
    has_consent: bool = True
    events: list[dict[str, Any]] = Field(default_factory=list)


class CandidateIntegrityRecordResponse(BaseModel):
    record_id: str
    candidate_id: str
    session_id: str
    round_type: str
    has_consent: bool
    total_risk_points: int
    risk_level: str
    requires_human_review: bool
    events: list[dict[str, Any]] = Field(default_factory=list)
    review_flags: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str


class CandidateBehavioralRecordCreate(BaseModel):
    session_id: str
    round_type: str
    has_consent: bool = True
    observations: list[dict[str, Any]] = Field(default_factory=list)


class CandidateBehavioralRecordResponse(BaseModel):
    record_id: str
    candidate_id: str
    session_id: str
    round_type: str
    has_consent: bool
    consistency_index: float
    requires_human_review: bool
    observations: list[dict[str, Any]] = Field(default_factory=list)
    disclaimer: str
    created_at: str


class CrossRoundEvaluationRequest(BaseModel):
    opening_id: str | None = None
    target_role: str | None = None
    round_scores: dict[str, float] | None = None
    role_weights: dict[str, float] | None = None
    missing_strategy: Literal["exclude_and_renormalize", "strict_zero", "flag_review"] = "exclude_and_renormalize"


class CrossRoundEvaluationResponse(BaseModel):
    evaluation_id: str
    candidate_id: str
    opening_id: str
    target_role: str
    hiring_fit_percentage: float
    round_scores: dict[str, Any]
    effective_weights: dict[str, Any]
    completed_rounds: int
    missing_rounds: list[str]
    anomalies: list[str]
    created_at: str


class FinalRecommendationRequest(BaseModel):
    opening_id: str | None = None
    target_role: str | None = None
    session_id: str | None = None
    evidence_quality: float = 85.0
    data_consistency: float = 85.0
    custom_rules: dict[str, Any] | None = None


class FinalRecommendationResponse(BaseModel):
    recommendation_id: str
    candidate_id: str
    opening_id: str
    target_role: str
    decision: Literal["SELECTED", "HOLD_REVIEW", "REJECTED"]
    score: float
    confidence: float
    confidence_interpretation: str = "Evidence completeness indicator; not a probability of job success."
    completed_rounds: int
    expected_rounds: int
    reasons: list[str]
    risk_factors: dict[str, Any]
    recruiter_decision: Literal["PENDING_REVIEW", "APPROVED", "OVERRIDDEN", "REJECTED"]
    recruiter_notes: str | None = None
    created_at: str
    updated_at: str


class FinalRecommendationDecisionRequest(BaseModel):
    recruiter_decision: Literal["APPROVED", "OVERRIDDEN", "REJECTED"]
    notes: str | None = None


# ============================================================================
# Days 53-60: Reporting, Security, Simulation, Coaching & Scalability Schemas
# ============================================================================

class HiringIntelligenceReportResponse(BaseModel):
    report_id: str
    candidate_id: str
    opening_id: str
    version: int
    report_title: str
    unified_hiring_fit_score: float | None = None
    evaluation_summary: dict[str, Any]
    strengths: list[str]
    weaknesses_and_skill_gaps: list[str]
    missing_evaluation_evidence: list[str]
    risk_indicators: list[dict[str, Any]]
    final_recommendation: dict[str, Any]
    recruiter_decision_workflow: dict[str, Any]
    disclaimer: str
    created_at: str


class AuditEventResponse(BaseModel):
    event_id: str
    event_type: str
    actor_id: str
    subject_id: str
    details: dict[str, Any]
    previous_hash: str
    event_hash: str
    created_at: str


class AuditVerificationResponse(BaseModel):
    verified: bool
    event_count: int
    status: str
    tampered_at_index: int | None = None
    event_id: str | None = None
    expected_hash: str | None = None
    stored_hash: str | None = None


class CandidateCoachingResponse(BaseModel):
    coaching_id: str
    candidate_id: str
    target_role: str
    identified_skill_gaps: list[str]
    recommended_preparation: list[str]
    practice_questions: list[str]
    governance_guardrails: dict[str, Any]
    disclaimer: str
    created_at: str


class SimulationRunRequest(BaseModel):
    candidate: dict[str, Any]
    opening: dict[str, Any]


class SimulationRunResponse(BaseModel):
    candidate_id: str
    opening_id: str
    unified_fit_score: float
    ai_recommendation: str
    report_id: str | None = None
    stage_statuses: dict[str, str]
    stage_timings_ms: dict[str, float]
    total_execution_ms: float
    pipeline_success: bool


class BenchmarkComparisonRequest(BaseModel):
    simulations: list[dict[str, Any]]
    human_evaluations: list[dict[str, Any]]


class BenchmarkComparisonResponse(BaseModel):
    total_evaluated: int
    decision_alignment_rate_percent: float
    average_score_gap: float
    max_score_gap: float
    comparisons: list[dict[str, Any]]


class BatchResumeProcessRequest(BaseModel):
    resumes: list[dict[str, Any]]
    batch_size: int = 4
    max_concurrency: int = 2


class BatchResumeProcessResponse(BaseModel):
    total_submitted: int
    successful_count: int
    failure_count: int
    cache_hits: int
    cache_hit_rate: float
    results: list[dict[str, Any]]
    failures: list[dict[str, Any]]


# Day 61: Observability & Monitoring Schemas
# ---------------------------------------------------------------------------


class MonitoringLogEventRequest(BaseModel):
    event_type: Literal["api_request", "model_run", "error", "decision_audit"]
    payload: dict[str, Any]


class MonitoringAlertItem(BaseModel):
    rule: str
    severity: Literal["WARNING", "HIGH", "CRITICAL"]
    message: str
    value: float
    timestamp: str


class MonitoringDashboardResponse(BaseModel):
    generated_at: str
    service: str
    operational_metrics: dict[str, Any]
    ai_model_metrics: dict[str, Any]
    recruitment_decisions: dict[str, Any]
    recent_errors: list[dict[str, Any]]
    ai_quality_guidance: str


class DecisionAuditLogResponse(BaseModel):
    event_id: str
    timestamp: str
    event_type: str
    candidate_ref: str
    opening_ref: str | None = None
    decision: str
    reason: str
    actor: str
    model_version: str
    human_reviewed: bool
