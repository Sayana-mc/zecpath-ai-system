from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from document_reader import extract_text
from text_cleaner import clean_text
from section_normalizer import normalize_sections


def test_pdf_extraction():

    pdf_files = list(
        Path(__file__).resolve().parents[1]
        .joinpath("input")
        .glob("*.pdf")
    )

    assert len(pdf_files) > 0

    text = extract_text(str(pdf_files[0]))

    assert isinstance(text, str)
    assert len(text.strip()) > 0


def test_docx_extraction():

    docx_files = list(
        Path(__file__).resolve().parents[1]
        .joinpath("input")
        .glob("*.docx")
    )

    assert len(docx_files) > 0

    text = extract_text(str(docx_files[0]))

    assert isinstance(text, str)
    assert len(text.strip()) > 0


def test_bullet_normalization():

    text = "Skills\n• Python\n• SQL"

    cleaned = clean_text(text)

    assert "•" not in cleaned
    assert "- Python" in cleaned


def test_section_normalization():

    text = """
    Skills
    Python, SQL

    Work Experience
    ABC Technologies
    """

    normalized = normalize_sections(text)

    assert "SKILLS" in normalized
    assert "EXPERIENCE" in normalized