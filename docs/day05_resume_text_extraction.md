# Day 5 — Resume text extraction

## Current root behavior

`src.services.parse_resume` extracts UTF-8 TXT, text-based PDF via pypdf, and
DOCX paragraphs and table cells. Upload validation checks extension, MIME
type, non-empty content, and a 5 MiB limit. Processing is reported using a
job ID and explicit QUEUED/PROCESSING/COMPLETED/FAILED state. A parser error
does not become a success-shaped response; the temporary upload is deleted
after processing.

## Limitations

The root response does not retain original binaries, page count, warnings,
extraction engine version, or a full extraction timestamp. Image-only/scanned
PDFs have no OCR path and are reported as unreadable when no text can be
extracted. Complex columns, repeated headers/footers, and layout fidelity are
not guaranteed. DOCX hyperlinks and advanced layout semantics are not
preserved. Extraction tests cover common valid and malformed cases, but do
not certify arbitrary resume layouts.

See `tests/test_api.py` upload cases and the stage-specific extraction code in
`day5_extraction/`. No external OCR dependency is installed or claimed.
