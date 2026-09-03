from __future__ import annotations

import json
import re
from pathlib import Path

from .ats.scoring_engine import generate_candidate_score


# ============================================================
# PROJECT PATHS
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
DAY13_ROOT = CURRENT_DIR.parent

PROJECT_ROOT = DAY13_ROOT.parent

DAY9_ROOT = PROJECT_ROOT / "day9_skill_extraction"
DAY10_ROOT = PROJECT_ROOT / "day10_experience_relevance"
DAY11_ROOT = PROJECT_ROOT / "day11_education_certification"
DAY12_ROOT = PROJECT_ROOT / "day12_semantic_matching"

DAY9_INPUT = DAY9_ROOT / "input"

DAY10_OUTPUT = (
    DAY10_ROOT
    / "output"
    / "structured"
)

DAY11_OUTPUT = (
    DAY11_ROOT
    / "output"
    / "structured"
)

DAY12_OUTPUT = (
    DAY12_ROOT
    / "output"
    / "matches"
)

OUTPUT_DIR = (
    DAY13_ROOT
    / "output"
    / "scores"
)


# ============================================================
# HELPERS
# ============================================================

def normalize_name(value):
    """
    Normalize file/candidate names so that
    upstream files can be matched reliably.
    """

    if value is None:
        return ""

    value = str(value)

    value = value.lower()

    value = value.replace(".pdf", "")
    value = value.replace(".json", "")

    value = re.sub(r"[^a-z0-9]+", " ", value)

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def load_json(path, warn=True):
    """
    Safely load a JSON file.
    """

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as exc:

        if warn:
            print(
                f"[WARNING] Could not read "
                f"{path.name}: {exc}"
            )

        return None


def find_json_by_name(folder, source_file):
    """
    Find a JSON file inside a folder using
    normalized filename matching.
    """

    if not folder.exists():
        return None

    target = normalize_name(source_file)

    for path in folder.rglob("*.json"):

        if normalize_name(path.name) == target:
            return path

        if normalize_name(path.stem) == target:
            return path

    return None


def get_candidate_name(source_file):
    """
    Convert resume filename into candidate name.
    """

    name = Path(source_file).stem

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()


# ============================================================
# DAY 9 - SKILL DATA
# ============================================================

def extract_skills_from_day9(data):
    """
    Extract skills from Day 9 resume JSON.
    """

    if not isinstance(data, dict):
        return []

    segmentation = data.get(
        "segmentation",
        {}
    )

    if not isinstance(segmentation, dict):
        return []

    sections = segmentation.get(
        "sections",
        {}
    )

    if not isinstance(sections, dict):
        return []

    skills_text = sections.get(
        "SKILLS",
        ""
    )

    if isinstance(skills_text, list):

        return [
            str(skill).strip()
            for skill in skills_text
            if str(skill).strip()
        ]

    if not isinstance(
        skills_text,
        str
    ):
        return []

    skills = []

    for line in skills_text.splitlines():

        line = line.strip()

        line = re.sub(
            r"^[•●▪▸\-*]+\s*",
            "",
            line
        )

        if line:
            skills.append(line)

    return skills


# ============================================================
# DAY 10 - EXPERIENCE DATA
# ============================================================

def extract_experience_score(data):
    """
    Extract experience relevance score
    from Day 10 structured JSON.
    """

    if not isinstance(data, dict):
        return 0.0

    analysis = data.get(
        "experience_analysis",
        {}
    )

    if not isinstance(
        analysis,
        dict
    ):
        return 0.0

    relevance = analysis.get(
        "relevance_analysis",
        {}
    )

    if not isinstance(
        relevance,
        dict
    ):
        return 0.0

    score = relevance.get(
        "relevance_score",
        0.0
    )

    try:
        return float(score)

    except (
        TypeError,
        ValueError
    ):
        return 0.0


# ============================================================
# DAY 12 - SEMANTIC DATA
# ============================================================

def extract_semantic_matches(data):
    """
    Extract Day 12 semantic matching results.
    """

    if not isinstance(data, dict):
        return []

    matches = data.get(
        "matches",
        []
    )

    if not isinstance(
        matches,
        list
    ):
        return []

    return matches


# ============================================================
# EDUCATION DATA
# ============================================================

def extract_education_score(data):
    """
    Extract education alignment score
    from Day 11 data when available.
    """

    if not isinstance(data, dict):
        return 0.0

    academic_profile = data.get("academic_profile", {})

    if isinstance(academic_profile, dict):
        relevance = academic_profile.get("education_relevance", {})

        if isinstance(relevance, dict):
            try:
                return float(relevance.get("score", 0.0))
            except (TypeError, ValueError):
                return 0.0

    possible_keys = [
        "education_alignment",
        "education_score",
        "alignment_score",
    ]

    for key in possible_keys:

        if key in data:

            try:
                return float(
                    data[key]
                )

            except (
                TypeError,
                ValueError
            ):
                pass

    nested_keys = [
        "education_analysis",
        "education",
        "certification_analysis",
    ]

    for parent_key in nested_keys:

        parent = data.get(
            parent_key
        )

        if not isinstance(
            parent,
            dict
        ):
            continue

        for key in possible_keys:

            if key in parent:

                try:
                    return float(
                        parent[key]
                    )

                except (
                    TypeError,
                    ValueError
                ):
                    pass

    return 0.0


# ============================================================
# SKILL MATCH
# ============================================================

def calculate_skill_match(
    resume_skills,
    job_title,
    job_data=None,
):
    """
    Calculate skill match score.

    If structured job skills are available,
    compare resume skills with job skills.

    Otherwise use role-related keyword matching.
    """

    if not resume_skills:
        return 0.0

    resume_text = " ".join(
        resume_skills
    ).lower()

    # --------------------------------------------------------
    # Try to obtain job skills
    # --------------------------------------------------------

    job_skills = []

    if isinstance(
        job_data,
        dict
    ):

        possible_keys = [
            "skills",
            "required_skills",
            "technical_skills",
            "job_skills",
        ]

        for key in possible_keys:

            value = job_data.get(
                key
            )

            if isinstance(
                value,
                list
            ):

                job_skills.extend(
                    str(item)
                    for item in value
                )

            elif isinstance(
                value,
                str
            ):

                job_skills.extend(
                    value.split(",")
                )

    # --------------------------------------------------------
    # If job skills are available
    # --------------------------------------------------------

    if job_skills:

        normalized_job_skills = [
            str(skill).strip().lower()
            for skill in job_skills
            if str(skill).strip()
        ]

        if normalized_job_skills:

            matched = 0

            for skill in normalized_job_skills:

                if skill in resume_text:
                    matched += 1

            return (
                matched
                / len(normalized_job_skills)
            ) * 100

    # --------------------------------------------------------
    # Role keyword fallback
    # --------------------------------------------------------

    role_keywords = {

        "data analyst": [
            "python",
            "sql",
            "excel",
            "power bi",
            "tableau",
            "pandas",
            "numpy",
            "statistics",
            "data analysis",
        ],

        "python developer": [
            "python",
            "sql",
            "git",
            "api",
            "fastapi",
            "django",
            "flask",
        ],

        "machine learning engineer": [
            "python",
            "machine learning",
            "scikit learn",
            "tensorflow",
            "pytorch",
            "numpy",
            "pandas",
        ],

        "graphic designer": [
            "figma",
            "photoshop",
            "illustrator",
            "indesign",
            "typography",
            "branding",
            "motion graphics",
        ],

        "hr executive": [
            "recruitment",
            "human resources",
            "hr",
            "talent acquisition",
            "employee relations",
            "payroll",
        ],
    }

    role = str(
        job_title
    ).strip().lower()

    keywords = role_keywords.get(
        role,
        []
    )

    if not keywords:
        return 0.0

    matched = 0

    for keyword in keywords:

        if keyword in resume_text:
            matched += 1

    return (
        matched
        / len(keywords)
    ) * 100


# ============================================================
# JOB DATA DISCOVERY
# ============================================================

JOB_DATA_CACHE = {}


def find_job_data(job_id):
    """
    Search project JSON files for a matching job ID.

    This is intentionally flexible because job files
    may be stored in different folders.
    """

    cache_key = str(job_id).strip()

    if cache_key in JOB_DATA_CACHE:
        return JOB_DATA_CACHE[cache_key]

    for path in PROJECT_ROOT.rglob(
        "*.json"
    ):

        # Avoid generated output folders
        if any(
            part in {
                "output",
                ".venv",
                "__pycache__",
                ".pytest_cache",
            }
            for part in path.parts
        ):
            continue

        # The Day 4 folder contains empty placeholder JSON files. They are
        # not usable data records, so ignore them during job discovery.
        if path.stat().st_size == 0:
            continue

        data = load_json(path, warn=False)

        if isinstance(
            data,
            dict
        ):

            if str(
                data.get("job_id", "")
            ).strip() == str(
                job_id
            ).strip():

                JOB_DATA_CACHE[cache_key] = data
                return data

            jobs = data.get(
                "jobs"
            )

            if isinstance(
                jobs,
                list
            ):

                for job in jobs:

                    if not isinstance(
                        job,
                        dict
                    ):
                        continue

                    if str(
                        job.get(
                            "job_id",
                            ""
                        )
                    ).strip() == str(
                        job_id
                    ).strip():

                        JOB_DATA_CACHE[cache_key] = job
                        return job

    JOB_DATA_CACHE[cache_key] = {}
    return {}


# ============================================================
# MAIN SCORING PIPELINE
# ============================================================

def process_resume(
    resume_path
):
    """
    Process one resume through the
    Day 9 → Day 10 → Day 12 → Day 13 pipeline.
    """

    source_file = resume_path.name

    candidate_name = get_candidate_name(
        source_file
    )

    # --------------------------------------------------------
    # Load Day 9
    # --------------------------------------------------------

    day9_path = find_json_by_name(
        DAY9_INPUT,
        source_file
    )

    day9_data = (
        load_json(day9_path)
        if day9_path
        else {}
    )

    resume_skills = (
        extract_skills_from_day9(
            day9_data
        )
    )

    # --------------------------------------------------------
    # Load Day 10
    # --------------------------------------------------------

    day10_path = find_json_by_name(
        DAY10_OUTPUT,
        source_file
    )

    day10_data = (
        load_json(day10_path)
        if day10_path
        else {}
    )

    experience_score = (
        extract_experience_score(
            day10_data
        )
    )

    # --------------------------------------------------------
    # Load Day 11 education data
    # --------------------------------------------------------

    day11_path = find_json_by_name(
        DAY11_OUTPUT,
        source_file
    )

    day11_data = (
        load_json(day11_path)
        if day11_path
        else {}
    )

    education_score = (
        extract_education_score(
            day11_data
        )
    )

    # --------------------------------------------------------
    # Load Day 12
    # --------------------------------------------------------

    day12_path = find_json_by_name(
        DAY12_OUTPUT,
        source_file
    )

    day12_data = (
        load_json(day12_path)
        if day12_path
        else {}
    )

    semantic_matches = (
        extract_semantic_matches(
            day12_data
        )
    )

    # --------------------------------------------------------
    # Process every job
    # --------------------------------------------------------

    results = []

    for match in semantic_matches:

        if not isinstance(
            match,
            dict
        ):
            continue

        job_id = match.get(
            "job_id",
            ""
        )

        job_title = match.get(
            "job_title",
            ""
        )

        # ----------------------------------------------------
        # Semantic score
        # ----------------------------------------------------

        semantic_score = match.get(
            "similarity_score",
            0.0
        )

        try:
            semantic_score = float(
                semantic_score
            )

        except (
            TypeError,
            ValueError
        ):
            semantic_score = 0.0

        # ----------------------------------------------------
        # Job data
        # ----------------------------------------------------

        job_data = find_job_data(
            job_id
        )

        # ----------------------------------------------------
        # Skill score
        # ----------------------------------------------------

        skill_score = calculate_skill_match(
            resume_skills=resume_skills,
            job_title=job_title,
            job_data=job_data,
        )

        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Generate final score
        # ----------------------------------------------------

        score = generate_candidate_score(

            candidate_name=(
                candidate_name
            ),

            job_id=job_id,

            job_title=job_title,

            skill_match=skill_score,

            experience_relevance=(
                experience_score
            ),

            education_alignment=(
                education_score
            ),

            semantic_similarity=(
                semantic_score
            ),
        )

        results.append(
            score
        )

    return {
        "source_file": source_file,
        "status": "success",
        "matches": results,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "# DAY 13 - ATS SCORING ENGINE"
    )
    print()

    print(
        f"Project root  : {PROJECT_ROOT}"
    )

    # --------------------------------------------------------
    # Find resumes
    # --------------------------------------------------------

    resumes = list(
        DAY9_ROOT.rglob("*.pdf")
    )

    # If PDFs are not inside Day 9,
    # use Day 9 JSON files as source records.
    if not resumes:

        resumes = list(
            DAY9_INPUT.glob(
                "*.json"
            )
        )

    print(
        f"Resumes found : {len(resumes)}"
    )

    # --------------------------------------------------------
    # Job count from Day 12
    # --------------------------------------------------------

    job_ids = set()

    if DAY12_OUTPUT.exists():

        for path in DAY12_OUTPUT.glob(
            "*.json"
        ):

            data = load_json(
                path
            )

            if not isinstance(
                data,
                dict
            ):
                continue

            for match in data.get(
                "matches",
                []
            ):

                if isinstance(
                    match,
                    dict
                ):

                    job_id = match.get(
                        "job_id"
                    )

                    if job_id:
                        job_ids.add(
                            job_id
                        )

    print(
        f"Jobs found    : {len(job_ids)}"
    )
    print()

    # --------------------------------------------------------
    # Check upstream paths
    # --------------------------------------------------------

    print(
        f"Day 10 path   : {DAY10_OUTPUT}"
    )

    print(
        "Day 10 status : "
        + (
            "FOUND"
            if DAY10_OUTPUT.exists()
            else "NOT FOUND"
        )
    )

    print()

    print(
        f"Day 12 path   : {DAY12_OUTPUT}"
    )

    print(
        "Day 12 status : "
        + (
            "FOUND"
            if DAY12_OUTPUT.exists()
            else "NOT FOUND"
        )
    )

    print(
        "====================="
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    processed = 0
    errors = 0

    # --------------------------------------------------------
    # Process resumes
    # --------------------------------------------------------

    for source in resumes:

        try:

            # If source is PDF, find corresponding
            # Day 9 JSON.
            if source.suffix.lower() == ".pdf":

                result = process_resume(
                    source
                )

            else:

                # Day 9 JSON fallback
                pdf_name = (
                    source.stem
                    + ".pdf"
                )

                fake_pdf = (
                    source.parent
                    / pdf_name
                )

                result = process_resume(
                    fake_pdf
                )

            output_name = (
                source.stem
                + ".json"
            )

            output_path = (
                OUTPUT_DIR
                / output_name
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    result,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            print(
                f"[SUCCESS] {output_name}"
            )

            processed += 1

        except Exception as exc:

            errors += 1

            print(
                f"[ERROR] {source.name}: {exc}"
            )

    print(
        "==========================================="
    )

    print(
        f"Processed     : {processed}"
    )

    print(
        f"Errors        : {errors}"
    )

    print(
        f"Output folder : {OUTPUT_DIR}"
    )

    print(
        "ATS scoring completed successfully."
    )

    print(
        "==========================================="
    )


if __name__ == "__main__":
    main()
