import time

from src.noisy_resume_handler import normalize_noisy_text
from src.entity_optimizer import detect_skills


def test_text_normalization_speed():

    text = (
        "Python SQL Power BI "
        * 1000
    )

    start = time.perf_counter()

    normalize_noisy_text(text)

    elapsed = time.perf_counter() - start

    assert elapsed < 1.0


def test_entity_detection_speed():

    text = (
        "Python SQL Power BI "
        "TensorFlow Pandas NumPy "
        * 1000
    )

    start = time.perf_counter()

    detect_skills(text)

    elapsed = time.perf_counter() - start

    assert elapsed < 1.0