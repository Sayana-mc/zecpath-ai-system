import json
from pathlib import Path

from .embedding_engine import EmbeddingEngine
from .similarity_engine import (
    cosine_similarity,
    similarity_label,
)
from .text_builder import (
    build_resume_text,
    build_job_text,
)


def load_json(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def match_resume_to_job(
    resume,
    job,
    embedding_engine
):
    resume_text = build_resume_text(
        resume
    )

    job_text = build_job_text(
        job
    )

    resume_embedding = (
        embedding_engine.encode(
            resume_text
        )
    )

    job_embedding = (
        embedding_engine.encode(
            job_text
        )
    )

    score = cosine_similarity(
        resume_embedding,
        job_embedding
    )

    return {
        "resume_file": resume.get(
            "source_file",
            ""
        ),
        "job_id": job.get(
            "job_id",
            ""
        ),
        "job_title": job.get(
            "job_title",
            ""
        ),
        "similarity_score": round(
            score,
            4
        ),
        "match_level": similarity_label(
            score
        ),
    }


def process_all_matches(
    resume_dir,
    job_dir,
    output_dir
):
    resume_dir = Path(resume_dir)
    job_dir = Path(job_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    embedding_engine = (
        EmbeddingEngine()
    )

    resumes = list(
        resume_dir.glob("*.json")
    )

    jobs = list(
        job_dir.glob("*.json")
    )

    results = []

    for resume_file in resumes:

        resume = load_json(
            resume_file
        )

        resume_results = []

        for job_file in jobs:

            job = load_json(
                job_file
            )

            result = match_resume_to_job(
                resume,
                job,
                embedding_engine
            )

            resume_results.append(
                result
            )

        resume_results.sort(
            key=lambda item:
            item["similarity_score"],
            reverse=True
        )

        output = {
            "source_file": resume.get(
                "source_file",
                resume_file.name
            ),
            "status": "success",
            "matches": resume_results
        }

        output_path = (
            output_dir /
            resume_file.name
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output,
                file,
                indent=4,
                ensure_ascii=False
            )

        results.append(output)

    return results