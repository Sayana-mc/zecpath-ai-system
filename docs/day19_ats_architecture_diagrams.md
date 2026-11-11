# Day 19 — ATS Architecture Diagrams & System Topology

This document visualizes the complete system architecture, data flow, API lifecycle, scoring pipeline, ranking, and asynchronous processing models of the integrated ZecPath ATS subsystem.

---

## 1. Overall System Architecture

```mermaid
flowchart TD
    subgraph Client["Client Tier"]
        UI["Recruiter Dashboard (static/index.html)"]
        API_Client["API Consumer / Swagger Docs (/docs)"]
    end

    subgraph App["FastAPI Application Tier (src/api.py, src/main.py)"]
        Auth["Authentication & Session Middleware (src/auth.py)"]
        Routes["REST Endpoints (/api/v1/*)"]
        BG["Background Processing Tasks"]
    end

    subgraph Logic["AI & ATS Services Tier"]
        JD["Job Description Parser (src/job_description_parser.py)"]
        ResumeParser["Resume Extraction & Segmentation (src/resume_analysis.py)"]
        Semantic["Day 12 Sentence-Transformers (all-MiniLM-L6-v2)"]
        Scorer["Day 13 Weighted Scoring Engine (src/integrated_scoring.py)"]
        Eligibility["Day 21 Eligibility Engine (src/eligibility.py)"]
        QuestionBank["Day 22 Screening Question Engine (src/screening_questions.py)"]
    end

    subgraph Data["Persistence Tier (SQLite3)"]
        DB[(zecpath.sqlite3)]
        Openings["openings table"]
        Candidates["candidates table"]
        ProcessingJobs["processing_jobs table"]
        Sessions["screening_sessions table"]
        Segments["transcript_segments table"]
        Interactions["screening_interactions table"]
    end

    UI --> Auth
    API_Client --> Auth
    Auth --> Routes
    Routes --> JD
    Routes --> ResumeParser
    Routes --> Eligibility
    Routes --> QuestionBank
    Routes --> BG
    BG --> ResumeParser
    ResumeParser --> Semantic
    Semantic --> Scorer
    Scorer --> Candidates
    JD --> Openings
    Routes --> DB
```

---

## 2. Resume Processing & Scoring Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Recruiter as Recruiter
    participant API as FastAPI Router (/api/v1)
    participant Worker as Background Task
    participant Parser as Resume Analyzer (Day 8-11)
    participant Embedder as SentenceTransformer (Day 12)
    participant Scorer as Integrated Scoring (Day 13)
    participant DB as SQLite Database

    Recruiter->>API: POST /resumes/upload (File + candidate_id)
    API->>DB: INSERT processing_jobs (status='QUEUED')
    API-->>Recruiter: 202 Accepted (job_id, status='QUEUED')
    API->>Worker: Enqueue parse job

    Worker->>DB: UPDATE processing_jobs (status='PROCESSING')
    Worker->>Parser: Extract text (PDF/DOCX) & segment sections
    Parser-->>Worker: Extracted profile (skills, exp, edu, certs)
    Worker->>DB: UPDATE candidates (resume_text, resume_data)
    Worker->>DB: UPDATE processing_jobs (status='COMPLETED')

    Recruiter->>API: POST /ats/score (candidate_id, job_id)
    API->>DB: SELECT candidate & job requirements
    API->>Embedder: Encode sanitized candidate text & job text
    Embedder-->>API: Dense vector representations
    API->>Scorer: Calculate component & weighted scores
    Scorer-->>API: Final score, classification, explainable evidence
    API->>DB: UPDATE candidates (score, score_evidence)
    API-->>Recruiter: 200 OK (ScoreResponse with ranking & breakdown)
```

---

## 3. Eligibility Decision Flow

```mermaid
flowchart LR
    Start([Candidate Scored]) --> CheckConfig{Opening Rules Configured?}
    CheckConfig -- No --> RetErr[Return 409 Configuration Required]
    CheckConfig -- Yes --> CheckScore{ATS Score >= Min Score?}
    CheckScore -- Fails --> Reject[Status: REJECTED]
    CheckScore -- Passes --> CheckSkills{All Mandatory Skills Present?}
    CheckSkills -- Missing --> ReviewSkills[Status: REVIEW - Missing Evidence]
    CheckSkills -- Matched --> CheckExp{Experience within Min/Max Range?}
    CheckExp -- Below/Exceeds --> ReviewExp[Status: REVIEW - Experience Gap]
    CheckExp -- In Range --> CheckLoc{Location / Remote Allowed?}
    CheckLoc -- Mismatch --> RejectLoc[Status: REJECTED - Location Rule]
    CheckLoc -- Matches --> Eligible[Status: ELIGIBLE - Ready for Screening]
```

