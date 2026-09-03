import pymupdf


def extract_text_from_pdf(file_path):
    """
    Extract raw text from a PDF resume.
    """

    document = pymupdf.open(file_path)

    pages = []

    for page in document:
        text = page.get_text("text")
        pages.append(text)

    document.close()

    return "\n".join(pages)