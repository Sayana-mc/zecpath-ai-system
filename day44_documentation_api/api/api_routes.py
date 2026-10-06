from fastapi import APIRouter

from .api_models import (
    HealthResponse,
    ScreeningRequest,
    InterviewEvaluationRequest,
    InterviewEvaluationResponse,
    ScoreComponents
)

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "service": "hr-interview-ai",
        "version": "1.0.0"
    }


@router.post("/screening")
def screening(request: ScreeningRequest):
    return {
        "candidate_id": request.candidate_id,
        "status": "completed",
        "message": "Screening request accepted",
        "response_count": len(request.responses)
    }


@router.post(
    "/interview/evaluate",
    response_model=InterviewEvaluationResponse
)
def evaluate_interview(request: InterviewEvaluationRequest):

    components = ScoreComponents(
        relevance=80,
        communication=80,
        confidence=80,
        consistency=80
    )

    return InterviewEvaluationResponse(
        candidate_id=request.candidate_id,
        question_id=request.question_id,
        status="completed",
        score=80,
        components=components
    )