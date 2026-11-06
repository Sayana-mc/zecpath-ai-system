import uuid
from typing import Any

from .database import (
    create_processing_job,
    get_processing_job,
    update_processing_job,
)
from .errors import JobNotFoundError


def create_job(
    filename: str,
    candidate_id: str | None = None,
    job_id: str | None = None,
) -> str:
    """Create a new asynchronous processing job."""

    job_id = job_id or str(uuid.uuid4())
    create_processing_job(job_id, filename, candidate_id)
    return job_id


def update_job(
    job_id: str,
    status: str,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    """Update asynchronous job state."""

    if not update_processing_job(job_id, status, result, error):
        raise JobNotFoundError(job_id)


def get_job(job_id: str) -> dict[str, Any]:
    """Return job status."""

    job = get_processing_job(job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    return job