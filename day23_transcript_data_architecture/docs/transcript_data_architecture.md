# Day 23 – Transcript Data Architecture

## Objective

Define how voice conversations are converted into structured,
AI-processable data for the ZecPath screening workflow.

## Architecture

Future Voice Call
        ↓
Speech-to-Text
        ↓
Raw Transcript
        ↓
Metadata Association
        ↓
Transcript Normalization
        ↓
Structured Transcript
        ↓
AI Screening Data
        ↓
Database Storage
        ↓
AI Analysis

## Metadata Standards

### Candidate ID
Identifies the candidate participating in the screening.

### Job ID
Identifies the job associated with the screening.

### Question ID
Connects the transcript interaction with the HR screening question
defined in the screening question dataset.

### Timestamp
Stores the time associated with each interaction.

### Confidence Level
Stores the confidence value associated with speech-to-text
transcription.

## Transcript Structure

Each transcript contains:

- Transcript ID
- Candidate ID
- Job ID
- Session ID
- Language
- Created timestamp
- Interaction records

Each interaction contains:

- Interaction ID
- Question ID
- Speaker
- Timestamp
- Raw transcript
- Normalized transcript
- Confidence level

## Normalization Rules

1. Remove unnecessary whitespace.
2. Normalize repeated spaces.
3. Normalize line breaks.
4. Preserve the original meaning.
5. Preserve technical terms.
6. Keep raw transcript separately.
7. Validate confidence values between 0 and 1.

## AI Screening Data

The normalized transcript is transformed into
AI-processable screening interaction records.

Each record connects:

Candidate → Job → Question → Answer → Timestamp → Confidence

## Database Design

The logical database structure is:

### Candidates
- candidate_id

### Jobs
- job_id

### Screening Sessions
- session_id
- candidate_id
- job_id
- created_at
- language

### Screening Interactions
- interaction_id
- session_id
- question_id
- speaker
- timestamp
- raw_text
- normalized_text
- confidence_level

The database implementation itself is not part of Day 23.
This document defines the logical schema for future implementation.

## Day 23 Deliverables

1. Voice transcript schema
2. AI screening data structure
3. Metadata standards documentation