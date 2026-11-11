# Day 24–32 Database Schema Changes

## Overview
All database changes have been applied additively to the root SQLite database engine (`src/database.py`). Existing candidate, job, resume, and ATS score records have been 100% preserved.

## New Tables Added

### 1. `screening_audio`
Stores metadata and file references for candidate voice uploads:
- `audio_id` (TEXT PRIMARY KEY)
- `session_id` (TEXT NOT NULL, FOREIGN KEY to `screening_sessions`)
- `question_id` (TEXT)
- `file_path` (TEXT NOT NULL)
- `file_size_bytes` (INTEGER NOT NULL)
- `duration_seconds` (REAL)
- `mime_type` (TEXT NOT NULL)
- `source` (TEXT NOT NULL)
- `status` (TEXT NOT NULL: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`)
- `created_at`, `updated_at` (TEXT)

### 2. `screening_transcripts`
Stores raw and cleaned transcriptions:
- `transcript_id` (TEXT PRIMARY KEY)
- `session_id` (TEXT NOT NULL)
- `audio_id` (TEXT)
- `question_id` (TEXT)
- `raw_text` (TEXT NOT NULL)
- `cleaned_text` (TEXT NOT NULL)
- `language` (TEXT)
- `language_probability` (REAL)
- `partial_answer` (INTEGER: 0 or 1)
- `processing_version` (TEXT NOT NULL)
- `segment_count` (INTEGER NOT NULL)
- `created_at`, `updated_at` (TEXT)

### 3. `screening_answers`
Stores intent classification and entity extraction results:
- `answer_id` (TEXT PRIMARY KEY)
- `session_id` (TEXT NOT NULL)
- `transcript_id` (TEXT)
- `question_id` (TEXT NOT NULL)
- `question_text` (TEXT NOT NULL)
- `expected_intent` (TEXT NOT NULL)
- `detected_intent` (TEXT)
- `answer_status` (TEXT NOT NULL)
- `raw_answer` (TEXT NOT NULL)
- `cleaned_answer` (TEXT NOT NULL)
- `extracted_information` (TEXT NOT NULL: serialized JSON)
- `intent_confidence` (REAL)
- `needs_clarification` (INTEGER)
- `is_off_topic` (INTEGER)
- `created_at`, `updated_at` (TEXT)

### 4. `screening_question_scores`
Stores multi-parameter scores per question:
- `score_id` (TEXT PRIMARY KEY)
- `session_id`, `answer_id`, `question_id` (TEXT NOT NULL)
- `clarity_score`, `relevance_score`, `completeness_score`, `consistency_score` (INTEGER)
- `weighted_score`, `normalized_score` (REAL)
- `explanation` (TEXT)
- `human_review_required` (INTEGER)
- `scoring_version` (TEXT)
- `created_at`, `updated_at` (TEXT)

### 5. `screening_aggregate_scores`
Stores aggregate session-level scoring:
- `aggregate_id` (TEXT PRIMARY KEY)
- `session_id`, `candidate_id` (TEXT NOT NULL)
- `overall_score` (REAL NOT NULL)
- `score_status` (TEXT NOT NULL)
- `questions_evaluated`, `questions_answered`, `questions_missing` (INTEGER)
- `human_review_required` (INTEGER)
- `scoring_version` (TEXT)
- `created_at`, `updated_at` (TEXT)

### 6. `behavioral_analysis`
Stores non-verbal and verbal communication metrics:
- `analysis_id` (TEXT PRIMARY KEY)
- `session_id`, `answer_id` (TEXT NOT NULL)
- `sentiment` (TEXT), `sentiment_score` (REAL)
- `confidence_score` (REAL)
- `hesitation_count`, `uncertainty_count` (INTEGER)
- `contradiction_detected` (INTEGER), `contradiction_details` (TEXT)
- `response_length_category`, `words_per_minute`, `pace_category` (TEXT)
- `created_at`, `updated_at` (TEXT)

### 7. `screening_reports_full`
Stores completed recruiter screening reports:
- `report_id` (TEXT PRIMARY KEY)
- `session_id`, `candidate_id`, `opening_id` (TEXT NOT NULL)
- `report_json` (TEXT NOT NULL: serialized JSON)
- `html_report` (TEXT)
- `pdf_report` (BLOB)
- `version` (INTEGER), `status` (TEXT)
- `created_at`, `updated_at` (TEXT)

