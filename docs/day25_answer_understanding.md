# Day 25 — Answer Intent and Information Extraction Architecture

## 1. Overview
The Day 25 subsystem provides automated candidate response comprehension for voice- and text-based screening. It converts normalized screening answers into structured, validated semantic entities.

## 2. Core Components
- **Intent Classifier (`day25_answer_intent_engine/src/intent_classifier.py`):**
  - Identifies intent from candidate answers using normalized keyword matching and semantic heuristics.
  - Recognizes intents: `skills`, `experience`, `education`, `location`, `salary`, `notice_period`, `introduction`, `unknown`, and `missing`.
  - Produces an intent confidence score (0.0 to 1.0).
- **Information Extractor (`day25_answer_intent_engine/src/information_extractor.py`):**
  - Extracts structured entities based on detected intent:
    - `skills`: Technical keywords (e.g., Python, SQL, Docker, FastAPI).
    - `experience`: Numerical years of experience, past roles, seniority indicators.
    - `education`: Degrees (B.Tech, M.S., B.S.), institutions, graduation years.
    - `salary`: Numerical values, currency, expectation bounds.
    - `notice_period`: Days/months notice, immediate availability flags.
    - `location`: Current and preferred locations, relocation willingness.
- **Answer Validator (`day25_answer_intent_engine/src/answer_validator.py`):**
  - Evaluates response quality against expected intent.
  - Detects `missing` (empty or silence), `vague` ("not sure", "maybe", "no idea"), and `off_topic` (unrelated hobby/sports/entertainment keywords).
- **Root Application Integration (`src/answer_understanding_integration.py`):**
  - Connects the engine to the persistent database schema (`screening_answers` table).
  - Normalizes validation outputs (`needs_clarification`, `is_off_topic`) and serializes structured information into JSON payloads.

## 3. Data Flow
1. Question and answer passed into `understand_answer()`.
2. Classifier determines candidate intent and confidence.
3. Information extractor parses structured entities.
4. Validator detects quality anomalies (vague, off-topic, missing).
5. Result persisted in SQLite database `screening_answers` table with foreign key linkage to `screening_sessions`.

