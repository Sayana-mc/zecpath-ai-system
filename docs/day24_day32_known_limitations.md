# Day 24–32 Known Limitations and Transparent Trade-offs

## 1. Speech-to-Text Provider Constraints
- **Local Faster-Whisper:** Requires local C++ runtimes (`ctranslate2` and `ffmpeg`). In environments lacking these binary runtimes, the system safely falls back to a deterministic transcription adapter.
- **Hosted Cloud Providers (Deepgram, Whisper API):** Supported via abstract provider interface (`STTIntegration`), but requires active API keys set in environment variables (`STT_API_KEY`).

## 2. Intent Classification and Entity Extraction
- **Rule- and Keyword-Based Model:** The current Day 25 comprehension engine uses keyword-based heuristics rather than fine-tuned transformer token classification. Complex phrasing with double negatives or figurative language may default to `unknown` intent and trigger clarification.
- **Language Support:** Full semantic scoring and intent classification are currently optimized for English (`en`). Multilingual inputs are detected, but questions currently default to English screening question datasets.

## 3. Behavioral and Sentiment Evaluation
- **Lexical Sentiment:** Sentiment is computed using word polarity dictionaries, which may misinterpret self-deprecating humor or technical problem-solving terminology (e.g., "killing bugs", "crashing servers") without recruiter oversight.
- **Pacing & Hesitation:** Pacing is sensitive to short utterances; therefore, words-per-minute is only evaluated on responses with significant word counts.

