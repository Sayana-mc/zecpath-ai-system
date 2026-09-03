from datetime import datetime, timezone


def create_metadata(
    candidate_id,
    job_id,
    model_version,
):
    """
    Create standardized metadata for AI pipeline records.

    Parameters:
        candidate_id (str): Unique candidate identifier.
        job_id (str): Unique job description identifier.
        model_version (str): Version of the AI/model pipeline.

    Returns:
        dict: Standardized metadata object.
    """

    if not candidate_id:
        raise ValueError("candidate_id is required")

    if not job_id:
        raise ValueError("job_id is required")

    if not model_version:
        raise ValueError("model_version is required")

    return {
        "candidate_id": str(candidate_id),
        "job_id": str(job_id),
        "model_version": str(model_version),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }