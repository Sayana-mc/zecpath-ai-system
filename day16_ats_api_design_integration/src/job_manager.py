from typing import Dict, Any
import uuid


JOBS: Dict[str, Dict[str, Any]] = {}


def create_job(job_type: str) -> str:
    job_id = str(uuid.uuid4())

    JOBS[job_id] = {
        "job_id": job_id,
        "job_type": job_type,
        "status": "QUEUED",
        "result": None,
        "error": None,
    }

    return job_id


def update_job(
    job_id: str,
    status: str,
    result: Any = None,
    error: str = None,
) -> None:

    if job_id not in JOBS:
        return

    JOBS[job_id]["status"] = status
    JOBS[job_id]["result"] = result
    JOBS[job_id]["error"] = error


def get_job(job_id: str):
    return JOBS.get(job_id)