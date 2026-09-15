import sys
from pathlib import Path


# ============================================================
# PROJECT PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day25_answer_intent_engine"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))


# ============================================================
# IMPORTS
# ============================================================

from intent_classifier import IntentClassifier

from information_extractor import (
    extract_skills,
    extract_experience,
    extract_availability,
    extract_salary
)

from answer_validator import validate_answer

from answer_understanding_engine import (
    AnswerUnderstandingEngine
)


# ============================================================
# INTENT CLASSIFICATION TESTS
# ============================================================

def test_skill_intent():

    classifier = IntentClassifier()

    result = classifier.classify(
        "I have experience with Python and SQL."
    )

    assert result["intent"] == "skills"


def test_experience_intent():

    classifier = IntentClassifier()

    result = classifier.classify(
        "I have 2 years of experience."
    )

    assert result["intent"] == "experience"


def test_availability_intent():

    classifier = IntentClassifier()

    result = classifier.classify(
        "I can join immediately."
    )

    assert result["intent"] == "availability"


def test_salary_intent():

    classifier = IntentClassifier()

    result = classifier.classify(
        "My expected salary is 4 LPA."
    )

    assert result["intent"] == "salary_expectation"


# ============================================================
# INFORMATION EXTRACTION TESTS
# ============================================================

def test_skill_extraction():

    result = extract_skills(
        "I know Python, SQL, Excel and Power BI."
    )

    assert "Python" in result
    assert "SQL" in result
    assert "Excel" in result
    assert "Power BI" in result


def test_experience_extraction():

    result = extract_experience(
        "I have 2 years of experience."
    )

    assert "2" in result["values"]


def test_availability_extraction():

    result = extract_availability(
        "I am available to join immediately."
    )

    assert result["status"] == "immediate"


def test_salary_extraction():

    result = extract_salary(
        "I expect 4 LPA."
    )

    assert result["amount"] == 4.0
    assert result["unit"] == "LPA"


# ============================================================
# ANSWER VALIDATION TESTS
# ============================================================

def test_vague_answer():

    result = validate_answer(
        "I don't know.",
        "skills"
    )

    assert result["status"] == "vague"
    assert result["vague"] is True
    assert result["missing"] is False
    assert result["off_topic"] is False


def test_off_topic_answer():

    result = validate_answer(
        "I like watching movies and playing games.",
        "skills"
    )

    assert result["status"] == "off_topic"
    assert result["off_topic"] is True
    assert result["vague"] is False


# ============================================================
# COMPLETE ANSWER UNDERSTANDING TEST
# ============================================================

def test_complete_understanding():

    engine = AnswerUnderstandingEngine()

    result = engine.understand(
        "I have experience with Python and SQL."
    )

    assert result["intent"] == "skills"

    assert "Python" in (
        result["extracted_information"]["skills"]
    )

    assert "SQL" in (
        result["extracted_information"]["skills"]
    )

    assert result["validation"]["status"] == "valid"