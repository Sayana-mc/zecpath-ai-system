import numpy as np


def cosine_similarity(
    embedding_a,
    embedding_b
):
    """
    Calculate cosine similarity between
    two embedding vectors.
    """

    vector_a = np.asarray(
        embedding_a
    )

    vector_b = np.asarray(
        embedding_b
    )

    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )

    if denominator == 0:
        return 0.0

    score = np.dot(
        vector_a,
        vector_b
    ) / denominator

    return float(score)


def similarity_label(score):
    """
    Convert similarity score into
    an interpretable match label.
    """

    if score >= 0.70:
        return "HIGH"

    if score >= 0.50:
        return "MEDIUM"

    return "LOW"