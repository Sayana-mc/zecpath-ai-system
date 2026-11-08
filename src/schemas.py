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