# Module Reference

Logical module guide; verify real filenames and integration status in the current repository.

## Resume ingestion and validation
Validate document metadata and file constraints, then create a processing job. Test missing/unsupported/oversized files, duplicates, and authorization failures.

## Resume extraction and parsing
Earlier proof-of-concept context mentions PyMuPDF and python-docx. Handle corrupt files, empty extraction, scanned PDFs needing OCR, and parser failures. Confirm current dependencies.

## AI inference
Earlier proof-of-concept context mentions Gemini and RAG/ChromaDB. Verify the active branch's provider/model settings before treating this as live. Test timeouts, rate limits, malformed responses, and retry rules.

## Screening/scoring
Produce a validated score/recommendation using approved criteria. Keep evidence references, model/criteria versions, and review status. Test score boundaries and missing evidence.

## Interview analysis
Process interview-related inputs where implemented. Test missing input, timeouts, output validation, and operational completion metrics.

## Persistence
Store workflow status, document references, validated results, and audit records. Test update consistency, duplicate records, and access boundaries.

## API/orchestration
Validate and authorize requests, invoke modules, return stable responses, and propagate correlation IDs. Test contracts and idempotency.

## Observability
Day 61 local prototype files: `src/observability.py` and `src/main.py` within that separate package. It demonstrates logs, metrics, alerts, and audit records using synthetic events.

## Performance helpers
Day 60 prototype demonstrates batching, bounded concurrency, TTL/LRU cache, and synthetic benchmarking. Verify whether these helpers are integrated into the main pipeline.

## Human review and audit
Allow authorized review of evidence and record outcomes. Production audit storage should be protected against unauthorized modification.
