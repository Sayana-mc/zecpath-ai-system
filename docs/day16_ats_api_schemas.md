# Day 16 — ATS API Schemas

This document describes the Pydantic request/response schemas used by the ATS API endpoints. All schemas are defined in `src/schemas.py`.

## Common Types

```python
Skill = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
```

## Job Opening Schemas

### OpeningCreate
```python
class OpeningCreate(BaseModel):
    title: Annotated[NonBlankText, Field(min_length=2, max_length=160)]
    description: str = Field(default="", max_length=20_000)
    required_skills: list[Skill] = Field(min_length=1, max_length=100)
    preferred_skills: list[Skill] = Field(default_factory=list, max_length=100)
    minimum_education: str | None = Field(default=None, max_length=160)
    minimum_years_experience: float | None = Field(default=None, ge=0, le=80)
```

### OpeningUpdate
```python
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
        # Rejects explicit null for required fields
```

### OpeningResponse
```python
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
```

## Job Description Parsing

### JobDescriptionParseRequest
```python
class JobDescriptionParseRequest(BaseModel):
    description: str = Field(min_length=1, max_length=20_000)
```

### JobDescriptionParseResponse
```python
class JobDescriptionParseResponse(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_education: str | None
    minimum_years_experience: float | None
    evidence: dict[str, list[str]]
    warnings: list[str]
    method: Literal["explicit_heading_rules_v1"]
    human_confirmation_required: Literal[True] = True
```

## Candidate Schemas

### CandidateCreate
```python
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
        # Validates YYYY-MM-DD format
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        # Validates email format
```

### CandidateUpdate
```python
class CandidateUpdate(BaseModel):
    name: Annotated[NonBlankText, Field(max_length=160)] | None = None
    email: str | None = Field(default=None, max_length=320)
    skills: list[Skill] | None = Field(default=None, max_length=100)
    application_status: ApplicationStatus | None = None
    location: str | None = Field(default=None, max_length=160)
    relocation_willingness: bool | None = None
    work_mode_preference: Literal["ONSITE", "HYBRID", "REMOTE"] | None = None
    availability_date: str | None = Field(default=None, max_length=10)
```

### CandidateResponse
```python
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
```

## Resume Processing

### ResumeUploadResponse
```python
class ResumeUploadResponse(BaseModel):
    job_id: str
    filename: str
    candidate_id: str | None = None
    status: str
    message: str
```

### ParseRequest
```python
class ParseRequest(BaseModel):
    job_id: str
```

### ParseResponse
```python
class ParseResponse(BaseModel):
    job_id: str
    status: str
    parsed_text: str
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    message: str
```

## ATS Scoring

### ScoreRequest
```python
class ScoreRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=80)
    candidate_id: str
```

### ScoreResponse
```python
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
```

## Shortlisting

### ShortlistRequest (Demo)
```python
class ShortlistRequest(BaseModel):
    candidates: list[dict[str, Any]]
    minimum_score: float = Field(default=60.0, ge=0.0, le=100.0)
```

### ShortlistedCandidate
```python
class ShortlistedCandidate(BaseModel):
    candidate_id: str
    score: float
    rank: int
```

### ShortlistResponse
```python
class ShortlistResponse(BaseModel):
    job_id: str
    status: str
    shortlisted_count: int
    candidates: list[ShortlistedCandidate]
    human_review_required: bool = True
    simulation_only: bool = False
    message: str
```

### PersistedShortlistRequest
```python
class PersistedShortlistRequest(BaseModel):
    minimum_score: float = Field(default=60.0, ge=0.0, le=100.0)
```

## Screening Questions

### ScreeningIntent
```python
ScreeningIntent = Literal["skills", "experience", "availability", "salary_expectation"]
```

### ScreeningQuestionResponse
```python
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
    created_at: str
    updated_at: str
    follow_up_eligible: bool
    translations: dict[str, Any]
```

## Screening Reports

### ScreeningAnswerRequest
```python
class ScreeningAnswerRequest(BaseModel):
    question_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    answer: str = Field(max_length=10_000)
    expected_intent: ScreeningIntent
```

### ScreeningReportRequest
```python
class ScreeningReportRequest(BaseModel):
    answers: list[ScreeningAnswerRequest] = Field(min_length=1, max_length=20)
```

### ScreeningReportResponse
```python
class ScreeningReportResponse(BaseModel):
    report_id: str
    candidate_id: str
    opening_id: str
    created_at: str
    method: Literal["day25_keyword_and_regex_rules"]
    answers: list[dict[str, Any]]
    review_flags: list[str]
    human_review_required: Literal[True] = True
```

## Job Processing

### JobStatusResponse
```python
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
```

## Error Handling

### ErrorResponse
```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] | None = None
```

## Authentication

### RecruiterLoginRequest
```python
class RecruiterLoginRequest(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    password: Annotated[str, StringConstraints(min_length=1, max_length=1024)]
```

### RecruiterSessionResponse
```python
class RecruiterSessionResponse(BaseModel):
    authenticated: bool
    username: str | None = None
    expires_at: float | None = None
```

## Eligibility Schemas

### EligibilityLocationRules
```python
class EligibilityLocationRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    allowed_locations: list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]] = Field(default_factory=list, max_length=100)
    work_mode: Literal["ONSITE", "HYBRID", "REMOTE"] | None = None
    remote_allowed: bool = False
    relocation_required: bool = False
    latest_start_date: str | None = Field(default=None, max_length=10)
```

### EligibilityDecisionPolicy
```python
class EligibilityDecisionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    manual_review_on_missing_data: bool = True
```

### EligibilityConfigurationRequest
```python
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
        # Validates minimum_experience_years <= maximum_experience_years
    
    @field_validator("mandatory_skills")
    @classmethod
    def validate_unique_skills(cls, value: list[str]) -> list[str]:
        # Validates uniqueness (case-insensitive)
    
    @model_validator(mode="after")
    def validate_location_rules(self) -> "EligibilityConfigurationRequest":
        # Validates latest_start_date format and relocation logic
```

### EligibilityConfigurationResponse
```python
class EligibilityConfigurationResponse(BaseModel):
    opening_id: str
    version: int
    configuration: EligibilityConfigurationRequest
    created_at: str
    updated_at: str
```

### EligibilityEvaluationRequest
```python
class EligibilityEvaluationRequest(BaseModel):
    opening_id: str = Field(min_length=1, max_length=80)
```

### EligibilityEvaluationResponse
```python
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
```

## Transcript Schemas

### ScreeningSessionCreate
```python
class ScreeningSessionCreate(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=80)
    opening_id: str = Field(min_length=1, max_length=80)
    language: str = Field(default="en", min_length=2, max_length=16)
    source: Literal["MANUAL", "RECRUITER", "IMPORT"] = "MANUAL"
```

### ScreeningSessionStatusUpdate
```python
class ScreeningSessionStatusUpdate(BaseModel):
    status: Literal["IN_PROGRESS", "INTERRUPTED", "COMPLETED", "CANCELLED"]
```

### TranscriptSegmentCreate
```python
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
        # Validates timezone-aware timestamps and end_time >= start_time
```

### TranscriptSegmentResponse
```python
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
```

### ScreeningInteractionCreate
```python
class ScreeningInteractionCreate(BaseModel):
    question_id: str = Field(min_length=1, max_length=80)
    candidate_answer: str | None = Field(default=None, max_length=20_000)
    answer_type: str | None = Field(default=None, max_length=40)
    validation_status: Literal["PENDING", "VALID", "INVALID", "SKIPPED", "UNANSWERED"] = "PENDING"
    display_order: int = Field(ge=1)
    follow_up_to: str | None = Field(default=None, max_length=80)
```

### ScreeningInteractionResponse
```python
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
```

### ScreeningSessionResponse
```python
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
```

### ScreeningTranscriptResponse
```python
class ScreeningTranscriptResponse(BaseModel):
    session: ScreeningSessionResponse
    segments: list[TranscriptSegmentResponse]
    interactions: list[ScreeningInteractionResponse]
```

## Application Status Enum

```python
ApplicationStatus = Literal[
    "APPLIED", "IN_REVIEW", "SHORTLISTED", "INTERVIEW",
    "OFFER", "HIRED", "REJECTED", "WITHDRAWN"
]
```

## Validation Rules Summary

| Schema | Key Validations |
|--------|-----------------|
| OpeningCreate | Required skills non-empty, title 2-160 chars |
| CandidateCreate | Email format, availability_date ISO format, opening_id required |
| EligibilityConfigurationRequest | Experience range valid, unique mandatory skills, location rules consistent |
| TranscriptSegmentCreate | Timezone-aware timestamps, sequence increasing, confidence 0-1 |
| ScreeningQuestionResponse | All required fields, valid enums, translation structure |

## JSON Schema Files

Formal JSON Schema files are available in `docs/schemas/`:
- `screening_question.schema.json` — Screening question structure
- `screening_transcript.schema.json` — Full transcript with session, segments, interactions
- `resume_schema.json` — Resume data structure
- `job_description_schema.json` — Parsed JD structure
- `skill_schema.json` — Skill normalization output
- `experience_schema.json` — Experience extraction output