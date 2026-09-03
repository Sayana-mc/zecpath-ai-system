from document_reader import extract_text
from text_cleaner import clean_text
from section_normalizer import normalize_sections


def process_resume(file_path):

    # Step 1: Extract
    raw_text = extract_text(file_path)

    # Step 2: Clean
    cleaned_text = clean_text(raw_text)

    # Step 3: Normalize section headings
    normalized_text = normalize_sections(cleaned_text)

    return {
        "raw_text": raw_text,
        "cleaned_text": normalized_text
    }