# ZecPath AI Hiring System — Expected Demo Results Matrix

**Document Version:** 1.0.0  
**Target Environment:** Localhost / Staging Demo  
**Dataset Reference:** `demo_data/candidates/candidates.json`, `demo_data/resumes/`  

This document provides the authoritative, ground-truth expected score ranges, stage gates, risk flags, and final recommendations for each candidate archetype during the system demonstration.

---

## 1. Candidate Cohort Summary Matrix

| ID | Name | Target Role | Key Profile Archetype | ATS Score | Cross-Round Fit | AI Recommendation | Recruiter Action |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|
| `CAND-001` | Aarav Sharma | Senior Python Backend Architect | Ideal Senior Match (6.5 yrs, full stack async) | **91.5%** | **90.6%** | **SELECTED** | APPROVE (Fast-track) |
| `CAND-002` | Priya Patel | Senior Python Backend Architect | Analytical switch to backend (strong SQL, learning async) | **76.8%** | **74.2%** | **HOLD_REVIEW** | HOLD (Tech Deep-dive) |
| `CAND-003` | Rohan Verma | Senior Python Backend Architect | Junior Dev lacking core backend prerequisites | **51.2%** | **48.5%** | **REJECTED** | REJECT (Feedback Sent) |
| `CAND-004` | Ananya Iyer | Machine Learning Platform Engineer | Stellar ML/PyTorch skills, junior experience (2.5 yrs) | **88.4%** | **89.1%** | **SELECTED** | APPROVE (L3 Offer) |
| `CAND-005` | Vikram Malhotra | Full Stack Software Developer | Solid engineer missing Docker & cloud deployments | **71.5%** | **70.8%** | **HOLD_REVIEW** | HOLD (DevOps Check) |
| `CAND-006` | Sneha Kulkarni | Senior Python Backend Architect | Physics PhD switcher, high algorithmic aptitude | **79.2%** | **81.4%** | **HOLD_REVIEW** | ADVANCE (System Design) |
| `CAND-007` | Devendra Singh | Senior Python Backend Architect | Complex multi-column PDF layout edge case | **86.0%** | **85.3%** | **SELECTED** | APPROVE (Layout Pass) |
| `CAND-008` | Kavita Nair | Senior Python Backend Architect | High legacy exp (12 yrs Java/C++), low Python fit | **58.4%** | **56.0%** | **REJECTED** | REJECT (Role Mismatch) |

---

## 2. Granular Stage-by-Stage Breakdown

---

### Candidate 1: Aarav Sharma (`CAND-001`)
* **Role Applied:** Senior Python Backend Architect
* **Profile:** 6.5 Years experience at CloudScale Systems, B.Tech CS. Expert in Python, FastAPI, PostgreSQL, Docker, Redis.
* **ATS Scoring:**
  * Skills Fit (40%): **95.0%** (5/5 required matched)
  * Semantic Match (25%): **91.2%** (Cosine similarity 0.91)
  * Experience Relevance (20%): **90.0%** (6.5 yrs vs 5.0 yrs required)
  * Education & Certs (15%): **88.0%** (Accredited CS degree)
  * **Composite ATS Score: 91.5%**
* **Conversational Screening:**
  * Intent Accuracy: 0.96 (Direct, concise responses)
  * Hesitation / Uncertainty: Low (Filler count: 2)
  * Screening Score: **89.0%**
* **HR & Technical Interviews:**
  * HR Adaptive Score: **87.5%** (High collaboration, STAR response structure)
  * Technical Interview: **91.0%** (Accuracy 92%, Depth: deep, Reasoning: 88%)
  * Machine Coding Test: **92.5%** (Task: Resilient Async Queue, 0 test failures)
* **Integrity & Malpractice:**
  * Flag: `FALSE` | Trust Score: 0.98
* **Cross-Round Unified Fit:** **90.6%**
* **AI Final Recommendation:** `SELECTED` (Confidence: 0.94)
* **Recruiter Prime Action:** **APPROVED**

---

### Candidate 2: Priya Patel (`CAND-002`)
* **Role Applied:** Senior Python Backend Architect
* **Profile:** 3.5 Years experience primarily as Data Analyst / BI Developer. Strong Python and SQL, but lacks production FastAPI async microservice experience.
* **ATS Scoring:**
  * Skills Fit (40%): **70.0%** (Python, SQL, PostgreSQL matched; FastAPI, Docker missing)
  * Semantic Match (25%): **78.5%**
  * Experience Relevance (20%): **80.0%**
  * Education & Certs (15%): **85.0%** (B.S. Statistics & Informatics)
  * **Composite ATS Score: 76.8%**
* **Conversational Screening:**
  * Intent Accuracy: 0.88
  * Hesitation: Moderate (Filler count: 7)
  * Screening Score: **75.0%**
* **HR & Technical Interviews:**
  * HR Adaptive Score: **82.0%** (Strong analytical mindset)
  * Technical Interview: **72.0%** (Accuracy 75%, Depth: shallow on concurrency)
  * Machine Coding Test: **70.0%** (Functional solution, suboptimal algorithmic complexity)
* **Integrity & Malpractice:**
  * Flag: `FALSE` | Trust Score: 0.95
* **Cross-Round Unified Fit:** **74.2%**
* **AI Final Recommendation:** `HOLD_REVIEW` (Confidence: 0.82)
* **Recruiter Prime Action:** **HOLD** (Recommend intermediate backend assessment or consider for Lead Data Analyst role)

---

### Candidate 3: Rohan Verma (`CAND-003`)
* **Role Applied:** Senior Python Backend Architect
* **Profile:** 1.0 Year experience as Junior Web Developer. Basic Django/Flask script knowledge. Missing Docker, PostgreSQL architecture, Redis, async event handling.
* **ATS Scoring:**
  * Skills Fit (40%): **42.0%** (Only basic Python detected)
  * Semantic Match (25%): **55.0%**
  * Experience Relevance (20%): **40.0%** (1.0 yr vs 5.0 yrs required)
  * Education & Certs (15%): **78.0%** (B.E. Information Technology)
  * **Composite ATS Score: 51.2%**
* **Hard Threshold Eligibility:**
  * Minimum Experience Gate: FAILED (< 3.0 yrs hard floor)
  * Status: `INELIGIBLE` (Recruiter bypass available)
* **Interview Simulation (Demonstration of Low-Fit Pipeline):**
  * Screening Score: **52.0%** (Significant hesitation, off-topic answers)
  * HR Adaptive Score: **58.0%**
  * Technical Interview: **44.0%** (Shallow conceptual responses)
  * Machine Test: **40.0%** (Incomplete async queue implementation)
* **Cross-Round Unified Fit:** **48.5%**
* **AI Final Recommendation:** `REJECTED` (Confidence: 0.91)
* **Recruiter Prime Action:** **REJECTED** (Automated respectful feedback and developmental guidance dispatched)

---

### Candidate 4: Ananya Iyer (`CAND-004`)
* **Role Applied:** Machine Learning Platform Engineer
* **Profile:** 2.5 Years experience. PyTorch, CUDA, FastAPI, Docker, Ray, Kubernetes. Master's in Artificial Intelligence.
* **ATS Scoring:**
  * Skills Fit (40%): **96.0%** (PyTorch, FastAPI, Docker, MLflow, Ray matched)
  * Semantic Match (25%): **92.0%**
  * Experience Relevance (20%): **75.0%** (2.5 yrs vs 3.0 yrs preferred)
  * Education & Certs (15%): **95.0%** (M.S. in AI)
  * **Composite ATS Score: 88.4%**
* **Conversational Screening:**
  * Screening Score: **90.0%** (Flawless articulation of distributed model training)
* **HR & Technical Interviews:**
  * HR Adaptive Score: **88.0%**
  * Technical Interview: **94.0%** (Deep understanding of pipeline parallelization)
  * Machine Test: **92.0%** (High-throughput inference worker)
* **Cross-Round Unified Fit:** **89.1%**
* **AI Final Recommendation:** `SELECTED` (Confidence: 0.93)
* **Recruiter Prime Action:** **APPROVED** (Fast-track to final offer)

---

### Candidate 5: Vikram Malhotra (`CAND-005`)
* **Role Applied:** Full Stack Software Developer
* **Profile:** 4.5 Years experience. Python, Django, React, PostgreSQL. Missing Docker and AWS cloud deployment skills.
* **ATS Scoring:**
  * Composite ATS: **71.5%**
* **Cross-Round Unified Fit:** **70.8%**
* **AI Final Recommendation:** `HOLD_REVIEW` (Flagged for missing DevOps skills)
* **Recruiter Prime Action:** **HOLD** (Assign targeted Docker take-home test)

---

### Candidate 6: Sneha Kulkarni (`CAND-006`)
* **Role Applied:** Senior Python Backend Architect
* **Profile:** Ph.D. in Computational Physics. 2.0 Years tech industry experience. Extreme algorithmic mastery, transitioning into enterprise SaaS architecture.
* **ATS Scoring:**
  * Composite ATS: **79.2%** (High education, lower industry tenure)
* **Cross-Round Unified Fit:** **81.4%** (Technical and coding scores pulled composite above threshold)
* **AI Final Recommendation:** `HOLD_REVIEW` (Borderline fit due to experience duration)
* **Recruiter Prime Action:** **ADVANCE** (Recruiter override based on top 1% coding score)

---

### Candidate 7: Devendra Singh (`CAND-007`)
* **Role Applied:** Senior Python Backend Architect
* **Profile:** 5.5 Years experience. Multi-column, modern graphic design resume layout with skill chips and nested sidebars.
* **ATS Parsing Verification:**
  * Segmentation Engine: Successfully isolated Experience, Education, and Skills tables without interleaving artifacts.
  * Extracted Skills: Python, FastAPI, Docker, PostgreSQL, Redis, Kubernetes (100% extracted).
  * Composite ATS Score: **86.0%**
* **Cross-Round Unified Fit:** **85.3%**
* **AI Final Recommendation:** `SELECTED`
* **Recruiter Prime Action:** **APPROVED** (Validates parser layout robustness)

---

### Candidate 8: Kavita Nair (`CAND-008`)
* **Role Applied:** Senior Python Backend Architect
* **Profile:** 12.0 Years enterprise Java / C++ engineering experience. Attempting transition to Python backend architecture without demonstrated Python portfolio.
* **ATS Scoring:**
  * Experience Fit: 100.0% (12 years)
  * Skills Fit: 35.0% (Only incidental Python scripting detected)
  * Semantic Match: 45.0%
  * Composite ATS Score: **58.4%**
* **Cross-Round Unified Fit:** **56.0%**
* **AI Final Recommendation:** `REJECTED` (Skill misalignment for senior role)
* **Recruiter Prime Action:** **REJECTED** (Re-routed to Java Staff Engineer requisition)

---

## 3. Demo Quality & Verification Summary

* **Decision Diversity:** 4 Selected, 2 Hold, 2 Rejected.
* **Corner Cases Covered:**
  * Under-qualified junior (CAND-003)
  * High-skill junior (CAND-004)
  * Skill gaps with strong soft skills (CAND-002, CAND-005)
  * Academic switcher with exceptional aptitude (CAND-006)
  * Non-standard multi-column resume layout (CAND-007)
  * High-experience low-skill mismatch (CAND-008)
* **Human Override Primacy:** Demonstrated on CAND-006 (Advancing academic candidate despite 2-year tenure flag).

