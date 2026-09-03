from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    job_id: str
    filename: str
    status: str
    message: str


class ParseRequest(BaseModel):
    job_id: str


class ParseResponse(BaseModel):
    job_id: str
    status: str
    parsed_text: str
    message: str


class ScoreRequest(BaseModel):
    job_id: str
    candidate_id: str
    job_id_reference: Optional[str] = None


class ScoreResponse(BaseModel):
    job_id: str
    candidate_id: str
    score: float
    status: str
    message: str


class ShortlistRequest(BaseModel):
    job_id: str
    candidates: List[Dict[str, Any]]
    minimum_score: float = Field(default=60.0, ge=0.0, le=100.0)


class ShortlistedCandidate(BaseModel):
    candidate_id: str
    score: float
    rank: int


class ShortlistResponse(BaseModel):
    job_id: str
    status: str
    shortlisted_count: int
    candidates: List[ShortlistedCandidate]
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None