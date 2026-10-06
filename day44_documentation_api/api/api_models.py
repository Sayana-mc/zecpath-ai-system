from typing import List

from pydantic import BaseModel, Field


class CandidateResponse(BaseModel):
    question_id: str
    response: str = Field(min_length=1)


class ScreeningRequest(BaseModel):
    candidate_id: str
    role: str
    responses: List[CandidateResponse]


class InterviewEvaluationRequest(BaseModel):
    candidate_id: str
    question_id: str
    question: str
    response: str = Field(min_length=1)


class ScoreComponents(BaseModel):
    relevance: float
    communication: float
    confidence: float
    consistency: float


class InterviewEvaluationResponse(BaseModel):
    candidate_id: str
    question_id: str
    status: str
    score: float
    components: ScoreComponents


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str