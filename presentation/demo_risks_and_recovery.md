# ZecPath AI Hiring System — Demo Risks & Emergency Recovery Guide

**Document Version:** 1.0.0  
**Phase:** Day 67 Mock Demo Day  
**Purpose:** Pre-defined failure modes, emergency actions, and fallback workarounds for live demonstrations.

---

## 1. Risk Matrix Overview

| Risk ID | Failure Scenario | Probability | Impact | Immediate Mitigation Action |
|:---:|:---|:---:|:---:|:---|
| **RSK-01** | Uvicorn server crash or port conflict | Low | Critical | Rapid restart on alternate port (`8001`) or restart script. |
| **RSK-02** | SQLite database lock or file corruption | Low | High | Instant restore from `data/ats.sqlite3.backup` or run seeder. |
| **RSK-03** | Browser UI caching stale assets | Medium | Low | Hard refresh (`Ctrl + Shift + R`) or open Incognito window. |
| **RSK-04** | Candidate resume upload timeout | Low | Medium | Use pre-seeded candidate `CAND-001` already present in database. |
| **RSK-05** | ML / Embedding inference latency spike | Low | Low | Engine automatically falls back to deterministic keyword/synonym matcher. |
| **RSK-06** | Observability alert banner false alarm | Low | Low | Explain live alert threshold dynamics as a feature of the system. |

---

## 2. Emergency Recovery Playbooks

### Playbook 1: Uvicorn Server Not Responding
* **Symptom:** Browser shows `This site can't be reached` or `ERR_CONNECTION_REFUSED`.
* **Action:**
  1. Open a terminal in the project root:
     ```bash
     .venv\Scripts\python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
     ```
  2. If port 8000 is occupied, kill the existing process or switch to 8001:
     ```bash
     .venv\Scripts\python -m uvicorn src.main:app --host 127.0.0.1 --port 8001
     ```
  3. Reload `http://127.0.0.1:8001/` in the presenter browser.

---

### Playbook 2: Database State Inconsistency or Missing Candidates
* **Symptom:** Candidate list is empty or shows corrupt scoring records.
* **Action:**
  1. Re-seed demo database instantly:
     ```bash
     .venv\Scripts\python -m src.init_demo_data
     ```
  2. This script drops and re-creates all 4 job openings, 8 candidates, multi-round scores, dossiers, and audit events in under 3.5 seconds.
  3. Refresh the browser page. All 8 archetypes will be immediately restored.

---

### Playbook 3: Presentation Network or Internet Disconnection
* **Symptom:** Wi-Fi disconnects in the conference room.
* **Impact Assessment:** **Zero Impact.**
* **Explanation:** The entire ZecPath AI Hiring System runs **100% locally** (FastAPI backend, SQLite database, deterministic embeddings, regex taxonomy, and static dashboard assets). It does not depend on external cloud APIs, OpenAI tokens, or WAN internet access.
* **Action:** Continue the presentation uninterrupted on `localhost`. Highlight this to stakeholders as a premier **data sovereignty and air-gapped security feature**.

---

### Playbook 4: Live File Upload Failure
* **Symptom:** Drag-and-drop resume upload fails due to an unexpected file format.
* **Action:**
  1. Transition smoothly without pausing:
     *"While we can ingest live uploads, let's look at Candidate Aarav Sharma, who was ingested through our batch pipeline earlier this morning."*
  2. Click on `CAND-001` to immediately demonstrate the parsed output and score decomposition.

