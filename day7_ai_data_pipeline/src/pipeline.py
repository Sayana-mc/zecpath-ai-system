from src.metadata import create_metadata


def create_pipeline_record(
    candidate_id,
    job_id,
    model_version="v1.0"
):
    return create_metadata(
        candidate_id=candidate_id,
        job_id=job_id,
        model_version=model_version
    )