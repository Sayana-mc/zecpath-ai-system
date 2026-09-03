from src.similarity_engine import (
    cosine_similarity,
    similarity_label,
)


def test_cosine_similarity():
    score = cosine_similarity(
        [1, 0],
        [1, 0]
    )

    assert round(score, 4) == 1.0


def test_different_vectors():
    score = cosine_similarity(
        [1, 0],
        [0, 1]
    )

    assert round(score, 4) == 0.0


def test_high_similarity_label():
    assert similarity_label(
        0.80
    ) == "HIGH"


def test_medium_similarity_label():
    assert similarity_label(
        0.60
    ) == "MEDIUM"


def test_low_similarity_label():
    assert similarity_label(
        0.30
    ) == "LOW"