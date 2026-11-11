# Day 23 — Transcript Metadata Standards

## Overview

Establishes the formatting, timestamp, confidence, and provenance rules for voice transcripts.

---

## 1. Standards

1. **Timestamps**:
   - Stored in ISO 8601 UTC format (`YYYY-MM-DDTHH:MM:SS.sssZ`) or milliseconds from conversation start.
   - When speech recognition timestamps are unavailable, fields MUST be explicitly `null` rather than fabricated.
2. **Confidence Scores**:
   - Scaled between `0.0` and `1.0`.
   - Populated only when the speech-to-text acoustic model reports a genuine token/segment confidence. If text is entered manually, confidence is recorded as `null` or `1.0` (manual entry).
3. **Sequence Ordering**:
   - Every segment has a positive integer `sequence_number`.
   - Segments within a session must be monotonically increasing without gaps or duplicates.
4. **Speaker Attribution**:
   - `AI`: Automated voice agent / question prompt.
   - `CANDIDATE`: Candidate response.
   - `SYSTEM`: Call events (e.g., ringing, silence detected, interruption).

