import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from .errors import JobNotFoundError


JOBS: Dict[str, Dict[str, Any]] = {}


def create_job(filename: str) -> str:
    """Create a new asynchronous processing job."""

    job_id = str(uuid.uuid4())

    JOBS[job_id] = {
        "job_id": job_id,
        "filename": filename,
        "status": "QUEUED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result": None,
        "error": None,
    }

    return job_id


def update_job(
    job_id: str,
    status: str,
    result: Dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    """Update asynchronous job state."""

    if job_id not in JOBS:
        raise JobNotFoundError(job_id)

    JOBS[job_id]["status"] = status
    JOBS[job_id]["result"] = result
    JOBS[job_id]["error"] = error


def get_job(job_id: str) -> Dict[str, Any]:
    """Return job status."""

    if job_id not in JOBS:
        raise JobNotFoundError(job_id)

    return JOBS[job_id]