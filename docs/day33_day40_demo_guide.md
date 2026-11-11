# Days 33–40: AI HR Interview Recruiter Demo Guide

This guide walks through testing and verifying the AI HR Interview subsystem using both the web UI dashboard and REST APIs.

---

## 1. Web Dashboard Walkthrough

1. **Start the Application:**
   ```powershell
   .venv\Scripts\python -m uvicorn src.main:app --reload --port 8000
   ```
2. **Access the Recruiter Dashboard:**
   - Open your browser to `http://127.0.0.1:8000`.
   - Log in using configured recruiter credentials or create an initial account.
3. **Select an Opening & Candidate:**
   - Select an active job opening from the dropdown.
   - Navigate to the Candidates panel.
4. **Launch an AI HR Interview:**
   - Expand the **AI HR Interview** drawer on a candidate card.
   - Choose Experience Level (`Fresher` or `Experienced`).
   - Choose Track (`Technical` or `Non-Technical`).
   - Click **Launch HR Interview**.
5. **Manage & Review Interview:**
   - Click **Start Interview** to begin questioning.
   - Click **Complete & Evaluate** to compute scores and generate the executive report.
   - Click **View HTML Report** to inspect the 11-section candidate dossier in a clean, print-ready layout.
   - In the Recruiter Decision form, choose `PROCEED`, `HOLD`, or `REJECT`, enter your notes, and click **Record Decision**.

---

## 2. CLI / Curl Walkthrough

### 2.1 Create an Interview Session
```bash
curl -X POST http://127.0.0.1:8000/api/v1/hr-interviews \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": "<CANDIDATE_ID>", "opening_id": "<OPENING_ID>", "experience_level": "EXPERIENCED", "role_type": "TECHNICAL"}'
```

### 2.2 Submit Candidate Answer
```bash
curl -X POST http://127.0.0.1:8000/api/v1/hr-interviews/<INTERVIEW_ID>/answers \
  -H "Content-Type: application/json" \
  -d '{"question_id": "<QUESTION_ID>", "answer_text": "In my previous project, we migrated to microservices..."}'
```

### 2.3 Conclude Interview & View Report
```bash
curl -X POST http://127.0.0.1:8000/api/v1/hr-interviews/<INTERVIEW_ID>/complete
curl http://127.0.0.1:8000/api/v1/hr-interviews/<INTERVIEW_ID>/report?format=html
```

