# Day 19 — ATS Knowledge Transfer

## Target Audience

New developers joining the ZecPath ATS project. This document provides a code-level walkthrough of the ATS subsystem.

## Prerequisites

- Python 3.12+, FastAPI, Pydantic v2, SQLite
- Familiarity with async/await, dependency injection
- Basic understanding of embeddings, cosine similarity

## Code Walkthrough: Request to Response

### 1. Application Entry Point (`src/main.py`)

```python
# Lifespan: DB init + interrupted job recovery
@asynccontextmanager
async def lifespan(_: FastAPI):
    database.initialize_database()
    interrupted = database.fail_interrupted_processing_jobs()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(system_router)  # /auth, /health
app.include_router(router)         # /api/v1/* (requires auth)
```

**Key points:**
- Single FastAPI app (`src.main:app`)
- Two routers: `system_router` (public), `router` (protected)
- SQLite initialized on startup
- Interrupted background jobs marked FAILED

---

### 2. Authentication Flow (`src/auth.py`)

```python
# Login → session cookie
POST /api/v1/auth/session
    verify_recruiter_credentials(username, password)
    create_recruiter_session(token, username, lifetime)
    response.set_cookie(key="zecpath_session", ...)

# Protected routes use:
dependencies=[Depends(require_recruiter)]
```

**Session stored in:** `recruiter_sessions` table (token_hash, expires_at)

---

### 3. Resume Upload (`src/api.py:527-593`)

```python
@router.post("/resumes/upload")
async def upload_resume(background_tasks, file, candidate_id):
    # 1. Validate file type, size, candidate
    # 2. Save to uploads/{job_id}.{ext}
    # 3. create_job(filename, candidate_id, job_id) → processing_jobs (QUEUED)
    # 4. background_tasks.add_task(process_resume_job, ...)
    # 5. Return 202 with job_id
```

**Background task (`process_resume_job`):**
```python
def process_resume_job(job_id, file_path, filename, candidate_id):
    update_job(job_id, "PROCESSING")
    parsed_text = parse_resume(file_path)        # Day 5 extraction
    resume_data = extract_resume_data(parsed_text)  # Day 8-11 extraction
    save_candidate_resume(candidate_id, filename, parsed_text, resume_data)
    update_job(job_id, "COMPLETED", result={...})
```

---

### 4. Resume Parsing (`src/services.py`)

```python
def parse_resume(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf": return _parse_pdf(file_path)
    if ext == ".docx": return _parse_docx(file_path)
    return Path(file_path).read_text(encoding="utf-8")
```

**Uses:** `pymupdf` (PDF), `python-docx` (DOCX)

---

### 5. Data Extraction (`src/resume_analysis.py`)

```python
def extract_resume_data(text: str) -> dict:
    # 1. Section segmentation (Day 8)
    sections = segment_resume_sections(text)
    # 2. Skill extraction (Day 9)
    skills = extract_skills(sections.get("skills", ""))
    # 3. Experience parsing (Day 10)
    experience = parse_experience(sections.get("experience", ""))
    # 4. Education parsing (Day 11)
    education = parse_education(sections.get("education", ""))
    # 5. Certifications
    certs = extract_certifications(sections.get("certifications", ""))
    return {"skills": skills, "experience": experience, ...}
```

**Returns:** Structured dict with skills, experience_years, experience[], education[], certifications[]

---

### 6. ATS Scoring (`src/integrated_scoring.py`)

```python
def calculate_integrated_score(candidate, opening) -> (float, dict):
    # 1. Build matching text from resume_data
    matching_text = build_resume_matching_text(resume_text, resume_data)
    
    # 2. Component scores (Day 13 parameters)
    skill_result = skill_match_score({skills: all_skills}, opening)
    experience_result = experience_relevance_score({years: exp_years}, opening)
    education_result = education_alignment_score({education: degree}, opening)
    
    # 3. Semantic similarity (Day 12)
    if matching_text:
        resume_emb, job_emb = _embedding_engine().encode_many([matching_text, job_text])
        semantic_similarity = cosine_similarity(resume_emb, job_emb)
    
    # 4. Weighted breakdown (Day 13)
    breakdown = generate_score_breakdown(skill, exp, edu, semantic, job_title)
    
    # 5. Exact skill evidence
    exact_evidence = calculate_candidate_match(candidate_with_matching_text, opening)
    
    # 6. Build evidence dict
    evidence = {...}
    return breakdown["final_score"], evidence
```

**Key components:**
- `_embedding_engine()` — LRU cached `EmbeddingEngine(local_files_only=True)`
- `cosine_similarity` — from Day 12
- `generate_score_breakdown` — from Day 13, role-specific weights

---

### 7. Score Persistence (`src/api.py:640-698`)

```python
@router.post("/candidates/score")
def score_candidate(request):
    candidate = _candidate_or_404(request.candidate_id)
    opening = _opening_or_404(request.job_id)
    
    calculate_candidate_match(candidate, opening)  # Exact matching
    score, evidence = calculate_integrated_score(candidate, opening)
    
    evidence["scored_at"] = current_timestamp()
    evidence["scoring_version"] = "day9-12-13-v1"
    
    save_candidate_score(candidate_id, score, evidence)
    
    # Compute ranking
    scored = [c for c in list_candidates(job_id) if c["score"]]
    scored.sort(key=lambda c: (-c["score"], c["name"]))
    ranking = index of this candidate + 1
    
    return ScoreResponse(score=score, evidence=evidence, ranking=ranking, ...)
```

---

### 8. Shortlisting (`src/api.py:987-1019`)

```python
@router.post("/openings/{opening_id}/shortlist")
def shortlist_opening(opening_id, request):
    candidates = [c for c in list_candidates(opening_id) 
                  if c["score"] and c["score"] >= request.minimum_score]
    candidates.sort(key=lambda c: (-c["score"], c["name"]))
    
    return ShortlistResponse(
        candidates=[ShortlistedCandidate(candidate_id=c["candidate_id"], 
                                         score=c["score"], rank=i+1)
                    for i, c in enumerate(candidates)],
        human_review_required=True
    )
```

---

### 9. Eligibility Evaluation (`src/eligibility.py`)

```python
def evaluate_eligibility(candidate, opening, configuration, version, evaluation_id, evaluated_at):
    # Fingerprint for re-evaluation detection
    rules = {}
    missing_information = []
    review_reasons = []
    explicit_failures = []
    
    # 1. ATS Score
    if not score_is_current: → REVIEW
    elif score < minimum: → REJECTED (explicit)
    else: → PASS
    
    # 2. Mandatory Skills
    candidate_skills = profile ∪ resume_extraction
    missing = required - candidate_skills
    if missing: → REVIEW (not proof of absence)
    else: → PASS
    
    # 3. Experience
    if no parsed experience: → REVIEW
    elif < minimum: → REJECTED
    elif > maximum: → REVIEW
    else: → PASS
    
    # 4. Location/Work Mode
    # Checks allowed_locations, remote_allowed, relocation_required
    
    # 5. Availability
    # Checks latest_start_date vs candidate availability_date
    
    # Decision
    if explicit_failures: status = "REJECTED"
    elif missing_information or review_reasons: status = "REVIEW"
    else: status = "ELIGIBLE"
    
    return {...}
```

**Fingerprint re-evaluation** in `src/api.py:130-162`:
```python
def _evaluate_and_persist_eligibility(candidate, opening, config):
    fingerprint = _eligibility_fingerprint(candidate, opening, config["version"])
    result = evaluate_eligibility(...)
    save_eligibility_evaluation(result, fingerprint)
    return result

GET /eligibility:
    latest = get_latest_eligibility_evaluation(...)
    if latest.fingerprint != current_fingerprint:
        return _evaluate_and_persist_eligibility(...)  # Re-evaluate
    return latest
```

---

### 10. Screening Questions (`src/screening_questions.py`)

```python
def load_dataset() -> dict:
    with DATASET_PATH.open() as f:
        dataset = json.load(f)
    errors = validate_dataset(dataset)
    if errors: raise ValueError(...)
    return dataset

def get_questions(role_id, category, language, mandatory, active_only):
    dataset = load_dataset()
    for q in dataset["questions"]:
        if filters match:
            translation = q["translations"][language]
            if translation["status"] == "AVAILABLE":
                yield {**q, "question_text": translation["question_text"], "language": language}
```

**Dataset:** `data/screening/hr_screening_questions.json`
- 17 questions, 2 populated roles (DATA_ANALYST, SOFTWARE_DEVELOPER)
- 13 roles registered, 7 categories
- Translations: en (all), ml/hi (HR001, HR006 only)

---

### 11. Transcript Storage (`src/database.py:1035-1132`)

```python
def save_transcript_segments(session_id, segments):
    for segment in segments:
        normalized = " ".join(raw_text.split())
        INSERT INTO transcript_segments (
            segment_id, session_id, question_id, speaker, raw_text,
            normalized_text, start_time, end_time, confidence, language,
            source, processing_version, sequence_number, created_at, updated_at
        ) VALUES (...)
    return SELECT * FROM transcript_segments WHERE session_id = ? ORDER BY sequence_number
```

**Validation in API (`src/api.py:862-939`):**
- Session status IN_PROGRESS or INTERRUPTED
- Sequence numbers strictly increasing from 1
- Speaker enum, confidence 0-1, timezone-aware timestamps
- question_id exists in dataset

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single SQLite database | Simplicity, no external deps for local deployment |
| BackgroundTasks for processing | No Redis/Celery needed for development |
| Score versioning in evidence | Traceability, debugging, reproducibility |
| Fingerprint-based re-evaluation | Avoids stale eligibility, automatic on data change |
| Human review required everywhere | Legal/ethical safeguard, not autonomous hiring |
| Conservative JD parser | Explicit headings only, no hallucination |
| Pending translations excluded | No machine translation, no mislabeling |
| Additive migrations only | Preserves existing data, no rollback complexity |

---

## Extension Points

| Extension | Where to Modify |
|-----------|-----------------|
| New resume format | `services.py::parse_resume()` |
| New skill synonym | `day9_skill_extraction/src/skill_normalizer.py` |
| New scoring component | `day13_ats_scoring/src/scoring_parameters.py` + `integrated_scoring.py` |
| New eligibility rule | `schemas.py::EligibilityConfigurationRequest` + `eligibility.py` |
| New question category | `data/screening/hr_screening_questions.json` + `question_category_mapping.json` |
| New transcript field | `schemas.py::TranscriptSegmentCreate` + `database.py::save_transcript_segments` |
| New answer type | `screening_questions.py::SUPPORTED_ANSWER_TYPES` |

---

## Testing Philosophy

- **Integration tests over unit tests** — Test full API flows
- **Synthetic data only** — No real candidate data in tests
- **Temporary database per test** — `tmp_path` fixture
- **Deterministic embeddings** — Monkeypatched in test fixture
- **Schema validation** — JSON Schema for questions/transcripts

---

## Common Pitfalls

1. **Forgetting score invalidation** — Any resume/candidate/job change must clear score
2. **Using stale ATS score** — Eligibility checks `scored_at` timestamp
3. **Missing ownership check** — Every candidate/job operation validates `candidate.opening_id == job_id`
4. **Naive datetimes in transcripts** — Must include timezone
5. **Assuming translation available** — Check `status == "AVAILABLE"` before use
6. **Background task exceptions** — Caught and logged, job marked FAILED
7. **SQLite foreign keys** — Enabled via `PRAGMA foreign_keys = ON`

---

## File Map for Quick Navigation

```
src/
├── main.py                    # App entry, lifespan
├── api.py                     # ALL routes (1000+ lines)
├── schemas.py                 # ALL Pydantic models
├── database.py                # ALL SQL, migrations
├── auth.py                    # Session, password, rate limit
├── services.py                # parse_resume, match, shortlist
├── resume_analysis.py         # extract_resume_data, build_matching_text
├── integrated_scoring.py      # Day 9-13 pipeline
├── eligibility.py             # Rule evaluation
├── screening_questions.py     # Dataset load, filter, validate
├── job_description_parser.py  # Explicit heading parser
├── ats_evaluation.py          # Metric helpers
└── validate_screening_dataset.py # CLI validator
```

---

## Onboarding Checklist

- [ ] Run `python -m pytest tests/ -v` — all green
- [ ] Start server, login via Swagger `/docs`
- [ ] Create opening, candidate, upload resume
- [ ] Score candidate, view evidence
- [ ] Configure eligibility, evaluate
- [ ] Query screening questions
- [ ] Create transcript session, add segments
- [ ] Read `docs/day16_day23_known_limitations.md`
- [ ] Review `src/database.py` for schema understanding