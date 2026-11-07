import re
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
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


class CandidateCreate(BaseModel):
    name: Annotated[NonBlankText, Field(max_length=160)]
    email: str | None = Field(default=None, max_length=320)
    opening_id: str = Field(min_length=1, max_length=80)
    skills: list[Skill] = Field(default_factory=list, max_length=100)
    resume_text: str = Field(default="", max_length=200_000)

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