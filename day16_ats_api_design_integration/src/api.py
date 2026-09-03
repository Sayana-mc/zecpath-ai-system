import logging

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks

from .schemas import (
    ResumeUploadResponse,
    ParsingResponse,
    ScoringRequest,
    ScoringResponse,
    ShortlistRequest,
    ShortlistResponse,
    JobStatusResponse,
)

from .job_manager import (
    create_job,
    update_job,
    get_job,
)

from .services import (
    parse_resume,
    calculate_score,
    shortlist_candidates,
)


logger = logging.getLogger(__name__)

app = FastAPI(
    title="ZecPath ATS API",
    description="AI-powered Applicant Tracking System API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "application": "ZecPath ATS API",
        "version": "1.0.0",
        "status": "running",
    }


@app.post(
    "/api/v1/resumes/upload",
    response_model=ResumeUploadResponse,
)
async def upload_resume(
    file: UploadFile = File(...)
):

    job_id = create_job("resume_upload")

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded resume is empty",
            )

        update_job(
            job_id,
            "COMPLETED",
            {
                "filename": file.filename,
                "size": len(content),
            },
        )

        logger.info(
            "Resume uploaded: %s",
            file.filename,
        )

        return ResumeUploadResponse(
            job_id=job_id,
            status="COMPLETED",
            message="Resume uploaded successfully",
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Resume upload failed")

        update_job(
            job_id,
            "FAILED",
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Resume upload failed",
        )


@app.post(
    "/api/v1/resumes/parse",
    response_model=ParsingResponse,
)
async def parse_resume_endpoint(
    file: UploadFile = File(...)
):

    job_id = create_job("resume_parsing")

    try:
        content = await file.read()

        text = content.decode(
            "utf-8",
            errors="ignore",
        )

        result = parse_resume(text)

        update_job(
            job_id,
            "COMPLETED",
            result,
        )

        return ParsingResponse(
            job_id=job_id,
            status="COMPLETED",
            parsed_text=result["text"],
        )

    except Exception as exc:
        logger.exception("Resume parsing failed")

        update_job(
            job_id,
            "FAILED",
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Resume parsing failed",
        )


@app.post(
    "/api/v1/scoring",
    response_model=ScoringResponse,
)
def score_candidate(
    request: ScoringRequest,
):

    job_id = create_job("candidate_scoring")

    try:
        score = calculate_score(
            request.skills,
            request.experience_years,
        )

        result = {
            "candidate_id": request.candidate_id,
            "job_id": request.job_id,
            "score": score,
        }

        update_job(
            job_id,
            "COMPLETED",
            result,
        )

        return ScoringResponse(
            job_id=request.job_id,
            candidate_id=request.candidate_id,
            score=score,
            status="SCORED",
        )

    except Exception as exc:
        logger.exception("Candidate scoring failed")

        update_job(
            job_id,
            "FAILED",
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Candidate scoring failed",
        )


@app.post(
    "/api/v1/shortlist",
    response_model=ShortlistResponse,
)
def shortlist(
    request: ShortlistRequest,
):

    candidates = shortlist_candidates(
        request.candidate_ids
    )

    return ShortlistResponse(
        job_id=request.job_id,
        shortlisted_candidates=candidates,
        count=len(candidates),
    )


@app.get(
    "/api/v1/jobs/{job_id}",
    response_model=JobStatusResponse,
)
def job_status(job_id: str):

    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        result=job["result"],
        error=job["error"],
    )