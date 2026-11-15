import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day35_communication_skill_evaluation"
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)


from communication_scorer import CommunicationScorer


def test_fluency_score():

    scorer = CommunicationScorer()

    score = scorer.calculate_fluency(
        "I worked on several data analysis projects."
    )

    assert score > 0


def test_grammar_score():

    scorer = CommunicationScorer()

    score = scorer.calculate_grammar(
        "I worked on Python projects."
    )

    assert score == 20


def test_vocabulary_score():

    scorer = CommunicationScorer()

    score = scorer.calculate_vocabulary(
        "Python SQL Excel Power BI data analysis projects"
    )

    assert score > 0


def test_clarity_score():

    scorer = CommunicationScorer()

    score = scorer.calculate_clarity(
        "I worked on data analysis projects. "
        "I used Python and SQL."
    )

    assert score > 0


def test_filler_detection():

    scorer = CommunicationScorer()

    fillers = scorer.detect_fillers(
        "Um, I basically worked on Python."
    )

    assert "um" in fillers
    assert "basically" in fillers


def test_structure_score():

    scorer = CommunicationScorer()

    score = scorer.calculate_structure(
        "I worked on data projects. "
        "I used Python and SQL to analyze data."
    )

    assert score > 0


def test_complete_evaluation():

    scorer = CommunicationScorer()

    result = scorer.evaluate(
        "I worked on several data analysis projects. "
        "I used Python and SQL to generate useful insights."
    )

    assert "communication_score" in result
    assert 0 <= result["communication_score"] <= 100


def test_score_range():

    scorer = CommunicationScorer()

    result = scorer.evaluate(
        "I know Python and SQL."
    )

    assert 0 <= result["communication_score"] <= 100