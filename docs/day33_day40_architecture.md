# Days 33–40: End-to-End System Architecture

## 1. Architectural Overview

```mermaid
flowchart TD
    User["Recruiter Dashboard UI / API Client"]
    
    subgraph REST API Layer [src/api.py]
        API1["POST /api/v1/hr-interviews"]
        API2["POST /api/v1/hr-interviews/{id}/start"]
        API3["POST /api/v1/hr-interviews/{id}/answers"]
        API4["POST /api/v1/hr-interviews/{id}/follow-ups"]
        API5["POST /api/v1/hr-interviews/{id}/complete"]
        API6["GET /api/v1/hr-interviews/{id}/report"]
        API7["POST /api/v1/hr-interviews/{id}/decision"]
    end

    subgraph Pipeline Orchestration [src/hr_interview_pipeline.py]
        Pipe["HRInterviewPipeline"]
    end

    subgraph Core AI Engines
        E1["HRInterviewEngine (Day 33)"]
        E2["HRFollowUpEngine (Day 34)"]
        E3["HRCommunicationEvaluator (Day 35)"]
        E4["HRConfidenceAnalyzer (Day 36)"]
        E5["HRScoringEngine (Day 37)"]
        E6["HRAptitudeEngine (Day 38)"]
        E7["HRSummaryGenerator (Day 39)"]
        E8["HRInterviewSimulator (Day 40)"]
    end

    subgraph SQLite Storage [src/database.py]
        DB1["hr_interview_sessions"]
        DB2["hr_interview_questions"]
        DB3["hr_interview_responses"]
        DB4["hr_interview_followups"]
        DB5["hr_communication_evaluations"]
        DB6["hr_behavioral_signals"]
        DB7["hr_aptitude_evaluations"]
        DB8["hr_interview_scores"]
        DB9["hr_interview_reports"]
    end

    User --> API1 & API2 & API3 & API4 & API5 & API6 & API7
    API1 & API2 & API3 & API4 & API5 & API6 & API7 --> Pipe
    Pipe --> E1 & E2 & E3 & E4 & E5 & E6 & E7 & E8
    E1 --> DB1 & DB2
    E2 --> DB4
    E3 --> DB5
    E4 --> DB6
    E5 --> DB8
    E6 --> DB7
    E7 --> DB9
```

## 2. Core Separation of Responsibilities
1. **ATS Document Processing (Days 1–23):** Parses resumes, extracts sections, executes semantic embedding match against job requirements.
2. **Screening Subsystem (Days 24–32):** Handles initial audio transcription, speech-to-text, and threshold eligibility rules.
3. **HR Interview Subsystem (Days 33–40):** Handles multi-turn interview dialogue, behavioral probing, communication nuance, aptitude, and executive recruiter dossiers.

