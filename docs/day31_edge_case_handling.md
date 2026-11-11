# Day 31 — Edge Case and Failure Handling Architecture

## 1. Overview
Day 31 provides resilience and graceful degradation for real-world conversational screening conditions, including poor audio, silence, interruptions, and language mixing.

## 2. Handled Edge Cases & Strategies
1. **Silence / Empty Response:**
   - Detects absence of speech; does not immediately fail the candidate.
   - Triggers `handle_empty_transcript()`, returning `PROMPT_AGAIN` with polite guidance.
2. **Background Noise & Low STT Confidence:**
   - When STT confidence drops below threshold (<0.50), the system flags potential audio corruption.
   - Invokes `handle_low_confidence()`, prompting the candidate for clarification before scoring.
3. **Partial / Incomplete Answers:**
   - Detects sentences truncated mid-thought or containing fewer than 3 words.
   - Flags answer with `partial_answer=True` and issues a gentle follow-up prompt.
4. **Language Mixing / Code-Switching:**
   - Detects multi-language tokens (e.g. English mixed with regional language).
   - Preserves technical terminology in English while logging language distribution metadata.
5. **Technical Audio Upload Failures:**
   - Unsupported file extensions, corrupted headers, or oversized payloads (>50MB) return specific HTTP 400/413 errors with clear guidance.

## 3. Fallback & Safe Degradation
- If a live STT provider is unreachable or unconfigured, the system safely falls back to local faster-whisper or mock transcription adapter without crashing the interview session.
- Recruiter dashboard flags any edge-case recovery sessions with `human_review_required = True`.

