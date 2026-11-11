# Day 23 — Voice Transcript Data Schema

## Purpose

Defines the structured format for capturing, storing, and retrieving speech-to-text transcripts generated during HR voice screening sessions.

---

## 1. Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ScreeningTranscript",
  "type": "object",
  "properties": {
    "session": {
      "type": "object",
      "properties": {
        "session_id": { "type": "string" },
        "candidate_id": { "type": "string" },
        "opening_id": { "type": "string" },
        "status": {
          "type": "string",
          "enum": ["CREATED", "IN_PROGRESS", "INTERRUPTED", "COMPLETED", "CANCELLED"]
        },
        "language": { "type": "string" },
        "started_at": { "type": ["string", "null"] },
        "completed_at": { "type": ["string", "null"] }
      },
      "required": ["session_id", "candidate_id", "opening_id", "status"]
    },
    "segments": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "segment_id": { "type": "string" },
          "session_id": { "type": "string" },
          "question_id": { "type": ["string", "null"] },
          "speaker": {
            "type": "string",
            "enum": ["AI", "CANDIDATE", "SYSTEM"]
          },
          "text": { "type": "string" },
          "start_time": { "type": ["string", "null"] },
          "end_time": { "type": ["string", "null"] },
          "confidence": { "type": ["number", "null"] },
          "sequence_number": { "type": "integer" }
        },
        "required": ["segment_id", "session_id", "speaker", "text", "sequence_number"]
      }
    },
    "interactions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "interaction_id": { "type": "string" },
          "session_id": { "type": "string" },
          "question_id": { "type": "string" },
          "candidate_answer": { "type": "string" },
          "validation_status": { "type": "string" }
        },
        "required": ["interaction_id", "session_id", "question_id", "candidate_answer"]
      }
    }
  },
  "required": ["session", "segments", "interactions"]
}
```

