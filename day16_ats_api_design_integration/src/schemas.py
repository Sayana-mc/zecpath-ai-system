from typing import List, Optional
from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ParsingResponse(BaseModel):
    job_id: str
    status: str
    candidate_id: Optional[str] = None
    parsed_text: Optional[str] = None


class ScoringRequest(BaseModel):
    candidate_id: str
    job_id: str
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0


class ScoringResponse(BaseModel):
    job_id: str
    candidate_id: str
    score: float
    status: str


class ShortlistRequest(BaseModel):
    job_id: str
    candidate_ids: List[str]


class ShortlistResponse(BaseModel):
    job_id: str
    shortlisted_candidates: List[str]
    count: int


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None