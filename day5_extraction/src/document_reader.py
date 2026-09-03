from pathlib import Path

from pdf_reader import extract_text_from_pdf
from docx_reader import extract_text_from_docx


def extract_text(file_path):
    """
    Extract text based on file extension.
    """

    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension == ".docx":
        return extract_text_from_docx(file_path)

    else:
        raise ValueError(
            f"Unsupported file format: {extension}"
        )