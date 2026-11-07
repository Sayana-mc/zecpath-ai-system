# Root resume upload and extraction

## Supported flow

`POST /api/v1/resumes/upload` accepts a multipart `file` and optional
`candidate_id`. The root application supports TXT, DOCX and text-based PDF up
to 5 MiB. It rejects unsupported extensions, known mismatched MIME types,
empty input and oversized input. `application/octet-stream` is allowed for
compatibility; the actual parser must still successfully read the format.
Client MIME metadata is not a security guarantee.

The application reduces the supplied filename to a basename and writes the
temporary upload to a UUID-named path under `uploads/`, never using the
filename as the storage path. It creates a processing-job row, then the
in-process FastAPI background task extracts text. It removes the temporary
file in a `finally` block. `GET /api/v1/jobs/{job_id}` exposes the processing
state and safe error message. `POST /api/v1/resumes/parse` returns the retained
text and structured details after successful processing.

## Structured extraction and storage

The root extraction calls:

- Day 9 skill dictionary/alias extraction.
- Day 10 work-history/date parsing and total detected experience.
- Day 11 education parsing.

Candidate rows keep the original filename, extracted text, structured
`resume_data`, score and score evidence. Uploads are deleted after extraction;
the original binary is not retained and there is no reprocess-from-original
operation. Processing status/result/error is stored in `processing_jobs`.
Restart marks queued/in-progress jobs failed rather than claiming success.
Candidate deletion redacts text from retained processing results.

The current structured result does **not** extract all contact details,
certifications, projects, achievements, skills provenance corrections, or
candidate confirmation workflows. Data not parsed remains absent; the root
does not invent it. No OCR is implemented: scanned-image PDFs commonly fail
with no-readable-text. PDF/DOCX parsers do not execute uploaded scripts.

## Failure behavior and constraints

Extension/MIME mismatch is HTTP 400, an empty upload is HTTP 400, over 5 MiB
is HTTP 413, and parser errors leave an explicit FAILED processing job. The
background worker is in-process, not durable; retry and duplicate-content
handling are absent. Candidate association is checked before queueing and
again before storing extracted text. File bytes and extracted applicant data
are not encrypted.

Tests cover TXT/DOCX/PDF text parsing, invalid format, MIME mismatch, empty and
large files, structured data persistence, interrupted jobs and candidate
deletion during processing. These checks do not certify every malicious or
malformed file.
