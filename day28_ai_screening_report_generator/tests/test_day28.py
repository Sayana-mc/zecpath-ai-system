import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day28_ai_screening_report_generator"
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)


from report_builder import ScreeningReportBuilder
from report_formatter import RecruiterReportFormatter


def load_data():

    input_file = (
        PROJECT_ROOT
        / "day28_ai_screening_report_generator"
        / "input"
        / "screening_input.json"
    )

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def test_key_answers():

    data = load_data()

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    assert len(
        report["key_answers"]
    ) == 4


def test_strengths():

    data = load_data()

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    assert len(
        report["strengths"]
    ) > 0


def test_risks():

    data = load_data()

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    assert len(
        report["risks"]
    ) > 0


def test_missing_data():

    data = load_data()

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    assert isinstance(
        report["missing_data"],
        list
    )


def test_salary_highlight():

    data = load_data()

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    assert (
        report["highlights"]
        ["salary_expectation"]
        == 4.0
    )


def test_availability_highlight():

    data = load_data()

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    assert (
        report["highlights"]
        ["availability"]
        == "immediate"
    )


def test_recruiter_report():

    data = load_data()

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    formatter = RecruiterReportFormatter(
        report
    )

    text = formatter.format_text()

    assert "AI SCREENING REPORT" in text
    assert "KEY HIGHLIGHTS" in text
    assert "STRENGTHS" in text
    assert "RISKS" in text
    assert "MISSING DATA" in text