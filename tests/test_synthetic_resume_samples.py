from pathlib import Path

from src.resume_analysis import extract_resume_data


RESUME_DIR = (
    Path(__file__).resolve().parents[1]
    / "datasets"
    / "test"
    / "resumes"
)


def test_ten_synthetic_resume_samples_run_through_profile_extraction():
    resume_files = sorted(RESUME_DIR.glob("resume_*.txt"))

    assert len(resume_files) >= 10
    for resume_file in resume_files:
        profile = extract_resume_data(resume_file.read_text(encoding="utf-8"))
        assert profile["sections"]["sections"]
        assert isinstance(profile["skills"], list)
        assert isinstance(profile["education"], list)
        assert isinstance(profile["certifications"], list)
        assert isinstance(profile["experience"], list)
