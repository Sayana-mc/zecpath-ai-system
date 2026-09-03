# ZECPATH AI-POWERED JOB PORTAL
# DAY 7 - AI DATA PIPELINE & STORAGE DESIGN

## 1. Objective

The objective of Day 7 is to design how AI-related data flows, connects, is stored, versioned, and evolves across the Zecpath recruitment platform.

The design connects the Day 5 Resume Text Extraction Engine and Day 6 Job Description Parsing System with future ATS scoring, AI screening, interview evaluation, hiring decisions, and model improvement.

---

## 2. Major Components

The pipeline contains the following major components:

1. Resume Upload
2. Resume Storage
3. Resume Text Extraction
4. Candidate Profile
5. Job Description
6. Job Description Parser
7. Structured Job Profile
8. Candidate-Job Matching
9. ATS Score
10. AI Screening
11. Screening Report
12. Interview
13. Interview Result
14. Hiring Decision
15. Dataset Versioning
16. Model Evaluation and Retraining

---

## 3. Data Flow

Resume Upload
    ->
Resume Storage
    ->
Resume Text Extraction
    ->
Candidate Profile
    ->
Candidate-Job Matching
    ->
ATS Score
    ->
AI Screening
    ->
Screening Report
    ->
Interview
    ->
Interview Result
    ->
Hiring Decision
    ->
Versioned Dataset
    ->
Model Evaluation / Retraining

Job Description
    ->
JD Parser
    ->
Structured Job Profile
    ->
Candidate-Job Matching

---

## 4. Storage Design

Original resumes are stored in PDF or DOCX format.

Structured AI data is stored in JSON format.

Training and evaluation datasets can be stored using JSONL, CSV, or Parquet depending on the downstream machine learning requirements.

Storage categories:

resumes/
parsed_profiles/
ats_scores/
screening_reports/
interview_results/
datasets/

---

## 5. Storage Structure

storage/
|
+-- resumes/
|
+-- parsed_profiles/
|
+-- ats_scores/
|
+-- screening_reports/
|
+-- interview_results/
|
+-- datasets/
    |
    +-- training/
    +-- validation/
    +-- evaluation/

---

## 6. Metadata Standards

Candidate ID:
CAND001

Job ID:
JD001

Application ID:
APP001

Interview ID:
INT001

Model Version:
ats-model-v1.0

Pipeline Version:
v1.0

Data Version:
v1

Timestamp:
ISO 8601 format

Status:
uploaded, processing, completed, failed, shortlisted, rejected, selected, on_hold

---

## 7. Resume Data

Resume storage maintains the original uploaded document and associated metadata.

Example:

Candidate ID: CAND001
Application ID: APP001
File Type: PDF
Extraction Status: completed
Extractor Version: resume-extractor-v1.0

---

## 8. Candidate Profile

Candidate profiles contain structured information extracted from resumes.

Typical fields:

- Candidate ID
- Application ID
- Name
- Location
- Current Role
- Experience
- Skills
- Education
- Certifications
- Projects
- Source
- Profile Version

---

## 9. ATS Score

The ATS scoring object contains:

- Candidate ID
- Job ID
- Application ID
- Model Version
- Overall Score
- Skill Match Score
- Experience Match Score
- Education Match Score
- Matched Skills
- Missing Skills
- Recommendation

---

## 10. Screening Report

The screening report stores:

- Candidate ID
- Job ID
- Application ID
- Screening Score
- Model Version
- Strengths
- Weaknesses
- Recommendation
- Status

---

## 11. Interview Result

The interview result stores:

- Candidate ID
- Job ID
- Application ID
- Interview ID
- Interview Date
- Model Version
- Technical Score
- Communication Score
- Problem Solving Score
- Overall Score
- Recommendation
- Status

---

## 12. AI Data Lifecycle

### Stage 1 - Upload

Candidate uploads a PDF or DOCX resume.

### Stage 2 - Storage

Original document is preserved.

### Stage 3 - Extraction

The Day 5 extraction engine extracts raw and cleaned text.

### Stage 4 - Candidate Profile

Resume information is transformed into structured candidate data.

### Stage 5 - JD Parsing

The Day 6 parser transforms the job description into an AI-readable job profile.

### Stage 6 - Matching

Candidate and job profiles are compared.

### Stage 7 - ATS Score

The matching engine produces scores and recommendations.

### Stage 8 - Screening

Shortlisted candidates undergo AI-assisted screening.

### Stage 9 - Interview

Interview results are stored.

### Stage 10 - Hiring Decision

The system records selected, rejected, or on-hold status.

### Stage 11 - Dataset Versioning

Validated data can be included in versioned datasets.

### Stage 12 - Model Improvement

Versioned datasets can be used for future model evaluation and retraining.

---

## 13. Versioning Strategy

Dataset versions:

dataset-v1
dataset-v2
dataset-v3

Model versions:

ats-model-v1.0
ats-model-v1.1
ats-model-v2.0

Pipeline versions:

v1.0
v1.1
v2.0

Each model should record the dataset and pipeline versions used.

Example:

Model:
ats-model-v2.0

Dataset:
dataset-v3

Pipeline:
v1.2

---

## 14. Retraining Lifecycle

New Recruitment Data
    ->
Data Validation
    ->
Data Cleaning
    ->
Dataset Versioning
    ->
Training Dataset
    ->
Model Training
    ->
Model Evaluation
    ->
Performance Comparison
    ->
Model Approval
    ->
New Model Version
    ->
Production Deployment

---

## 15. Day 5 Integration

Day 5 provides:

- Resume extraction
- Raw text
- Cleaned text
- Extraction status

These outputs become the input for candidate profile creation.

---

## 16. Day 6 Integration

Day 6 provides:

- Job role
- Required skills
- Preferred skills
- Experience
- Education
- Responsibilities
- Structured job profile

These outputs become the job-side input for candidate-job matching.

---

## 17. Day 7 Contribution

Day 7 connects the previous modules into a complete AI data architecture.

Day 5:
Resume Extraction

Day 6:
JD Parsing

Day 7:
AI Data Pipeline and Storage

Future:
ATS Matching
AI Screening
Interview
Hiring Decision
Model Improvement

---

## 18. Conclusion

Day 7 establishes the data architecture required for the Zecpath AI-powered recruitment platform.

The architecture defines how recruitment data moves from resume upload to final hiring decision and how AI-related data can be stored, tracked, versioned, evaluated, and reused for future model improvement.

The metadata standard provides traceability through Candidate ID, Job ID, Application ID, Model Version, Pipeline Version, Data Version, Timestamp, and Status.

This design provides a foundation for implementing the future ATS, AI screening, interview evaluation, and machine learning components.
