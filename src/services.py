import re
from pathlib import Path
from typing import Any
from zipfile import BadZipFile

from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from ats_engine.ats_scorer import calculate_ats_score
from .errors import InvalidResumeError


def _unique_skills(skills: list[str]) -> list[str]:
    unique = {}
    for skill in skills:
        unique.setdefault(skill.strip().casefold(), skill.strip())
    return list(unique.values())


def parse_resume(file_path: str) -> str:
    """Extract text from a supported resume format without retaining its file."""

    path = Path(file_path)

    if not path.exists():
        raise InvalidResumeError("Resume file does not exist.")

    try:
        extension = path.suffix.lower()
        if extension == ".txt":
            text = path.read_text(encoding="utf-8")
        elif extension == ".pdf":
            reader = PdfReader(str(path))
            if reader.is_encrypted and not reader.decrypt(""):
                raise InvalidResumeError("Password-protected PDF files are not supported.")
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif extension == ".docx":
            document = Document(str(path))
            paragraphs = [paragraph.text for paragraph in document.paragraphs]
            table_text = [
                cell.text
                for table in document.tables
                for row in table.rows
                for cell in row.cells
            ]
            text = "\n".join(paragraphs + table_text)
        else:
            raise InvalidResumeError(
                "Unsupported resume format. Use PDF, DOCX, or TXT."
            )
    except InvalidResumeError:
        raise
    except (
        BadZipFile,
        PackageNotFoundError,
        PdfReadError,
        UnicodeDecodeError,
        OSError,
        ValueError,
    ) as exc:
        raise InvalidResumeError(
            "The resume file is unreadable or has an invalid format."
        ) from exc

    text = text.strip()
    if not text:
        raise InvalidResumeError("No readable text was found in the resume.")
    return text


def calculate_score(candidate: dict[str, Any]) -> float:
    """Score explicit candidate skills against a job's required skills."""
    candidate_skills = candidate.get("skills", [])
    required_skills = candidate.get("required_skills", [])
    if not isinstance(candidate_skills, list) or not isinstance(required_skills, list):
        raise ValueError("Candidate and required skills must be lists.")
    return calculate_ats_score(candidate_skills, required_skills)


def calculate_candidate_match(
    candidate: dict[str, Any], opening: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    """Calculate exact skill overlap and return the evidence used by the score."""
    required_skills = _unique_skills(opening["required_skills"])
    profile_skills = candidate.get("skills", [])
    resume_text = candidate.get("resume_text", "")

    if not profile_skills and not resume_text.strip():
        raise ValueError("Candidate must provide skills or a readable resume before scoring.")

    normalized_profile_skills = _unique_skills(profile_skills)
    resume_evidence = []
    for skill in required_skills:
        match = re.search(
            r"(?<![a-z0-9])" + re.escape(skill.casefold()) + r"(?![a-z0-9])",
            resume_text.casefold(),
        )
        if match:
            start = max(0, match.start() - 60)
            end = min(len(resume_text), match.end() + 60)
            resume_evidence.append(
                {"skill": skill, "excerpt": resume_text[start:end]}
            )
    detected_resume_skills = [item["skill"] for item in resume_evidence]
    evidence_skills = list(dict.fromkeys(normalized_profile_skills + detected_resume_skills))
    matched_skills = [
        skill
        for skill in required_skills
        if skill.casefold() in {item.casefold() for item in evidence_skills}
    ]
    missing_skills = [
        skill for skill in required_skills if skill not in matched_skills
    ]
    score = calculate_score(
        {"skills": evidence_skills, "required_skills": required_skills}
    )
    return score, {
        "method": "exact_required_skill_overlap",
        "human_review_required": True,
        "required_skills": required_skills,
        "matched_required_skills": matched_skills,
        "missing_required_skills": missing_skills,
        "profile_skills": normalized_profile_skills,
        "resume_evidence_skills": detected_resume_skills,
        "resume_evidence": resume_evidence,
    }


def shortlist_candidates(
    candidates: list[dict[str, Any]],
    minimum_score: float = 60.0,
) -> list[dict[str, Any]]:
    """Rank caller-supplied scores for an explicitly labelled demo operation."""

    processed = []

    for candidate in candidates:
        score = candidate.get("score")
        if not isinstance(score, (int, float)):
            raise ValueError("Every candidate must include a numeric score.")
        score = round(max(0.0, min(100.0, float(score))), 2)

        if score >= minimum_score:
            processed.append(
                {
                    "candidate_id": str(candidate["candidate_id"]),
                    "score": score,
                }
            )

    processed.sort(
        key=lambda candidate: candidate["score"],
        reverse=True,
    )

    for rank, candidate in enumerate(processed, start=1):
        candidate["rank"] = rank

    return processed