import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from src.resume_analysis import extract_resume_data


SCHEMA_DIR = Path(__file__).resolve().parents[1] / "docs" / "schemas"
RESUME_DIR = (
    Path(__file__).resolve().parents[1]
    / "datasets"
    / "test"
    / "resumes"
)


def load_schemas():
    return {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in SCHEMA_DIR.glob("*.json")
    }


def test_day_four_schemas_are_valid_and_validate_synthetic_examples():
    schemas = load_schemas()
    resources = [
        (schema["$id"], Resource.from_contents(schema))
        for schema in schemas.values()
    ]
    registry = Registry().with_resources(resources)

    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)

    examples = {
        "skill_schema.json": {
            "skill": "Python",
            "category": "technical",
            "source": "SKILLS",
            "match_type": "exact",
            "confidence": 0.9,
        },
        "experience_schema.json": {
            "job_title": "Software Engineer",
            "company": "Synthetic Example",
            "start_date": "2022-01-01",
            "end_date": "2024-12-01",
            "duration_months": 36,
        },
        "job_description_schema.json": {
            "opening_id": "synthetic-job",
            "title": "Data Analyst",
            "description": "Analyze synthetic data.",
            "required_skills": ["SQL"],
            "preferred_skills": [],
            "status": "OPEN",
        },
        "resume_schema.json": {
            "extraction_method": "synthetic-test",
            "skills": ["Python"],
            "skill_details": [
                {
                    "skill": "Python",
                    "category": "technical",
                    "source": "SKILLS",
                    "match_type": "exact",
                    "confidence": 0.9,
                }
            ],
            "education": [],
            "certifications": [],
            "experience": [
                {
                    "job_title": "Software Engineer",
                    "company": "Synthetic Example",
                    "start_date": "2022-01-01",
                    "end_date": "2024-12-01",
                    "duration_months": 36,
                }
            ],
            "experience_years": 3,
            "sections": {"sections": {"SKILLS": "Python"}, "detected_headings": []},
        },
    }

    for filename, example in examples.items():
        validator = Draft202012Validator(
            schemas[filename],
            registry=registry,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        )
        assert validator.is_valid(example), (
            filename,
            list(validator.iter_errors(example)),
        )

    resume_validator = Draft202012Validator(
        schemas["resume_schema.json"],
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    for resume_file in RESUME_DIR.glob("resume_*.txt"):
        profile = extract_resume_data(resume_file.read_text(encoding="utf-8"))
        assert resume_validator.is_valid(profile), (
            resume_file.name,
            list(resume_validator.iter_errors(profile)),
        )


def test_screening_question_dataset_matches_schema():
    dataset_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "screening"
        / "hr_screening_questions.json"
    )
    question_schema = load_schemas()["screening_question.schema.json"]
    validator = Draft202012Validator(
        question_schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    assert len(dataset["questions"]) == 17
    for question in dataset["questions"]:
        assert validator.is_valid(question), (
            question.get("question_id"),
            list(validator.iter_errors(question)),
        )
