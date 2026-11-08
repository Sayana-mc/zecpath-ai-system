# Day 1 — AI module inventory

Statuses refer to actual root integration, not the existence of a day folder.
Rule-based components are not described as machine learning.

| Module | Purpose / input → output | Current implementation and dependencies | Status |
|---|---|---|---|
| Resume parser | PDF/DOCX/TXT → extracted text | `src/services.py`; pypdf and python-docx | Integrated; no OCR |
| Resume section classifier | Text → named section strings/headings | Day 8 segmentation; now called by `src/resume_analysis.py` | Partial; no layout model or measured accuracy |
| Skill extraction | Resume text/sections → canonical skill records | Day 9 dictionary and aliases | Integrated, deterministic rules |
| Experience parser | Work-history text → dated roles and total duration | Day 10 date/role patterns; now unions overlapping dated intervals | Integrated, deterministic and incomplete for irregular layouts |
| Education parser | Education text → degree/field/institution/year | Day 11 patterns | Integrated, deterministic |
| Certification parser | Certification text → name/category/year | Day 11 rules; now included in the resume profile | Extraction integrated; scoring relevance is not |
| Job description parser | Structured JD → normalized role/requirements | Day 6 prototype accepts already-structured fields | Not integrated; root recruiter enters structured requirements |
| Semantic matching | Resume/job text → cosine similarity | Day 12 `all-MiniLM-L6-v2`, sentence-transformers, cosine similarity | Integrated when local model is available; single overall similarity |
| ATS scoring | Components/weights → score and breakdown | Day 13 component helpers and active Python role weights | Integrated heuristic; not employment-validated |
| Candidate ranking | Saved job-specific scores → stable rank | Root API sorts persisted candidate scores | Integrated; no pagination |
| Shortlisting | Score cutoff → recruiter review suggestions | Root endpoint accepts a cutoff and flags human review | Integrated as suggestions; no three-zone policy or auto-reject |
| Fairness safeguards | Exclude non-job-related personal data; expose limitations | Root semantic input now removes labeled attributes/contact details; name remains display-only | Partial; incomplete de-identification and no subgroup evaluation |
| Screening AI | Answers → intent/fields/review flags | Day 25 keyword/regex rules | Limited root integration; not a validated score |
| Voice screening AI | Audio → transcript/answers | Day 24 prototype | Not integrated; model inference not certified |
| Interview intelligence / HR interview AI | Interview transcript → structured evaluation | Later day folders | Planned/prototype only; not root-integrated |
| Technical interview AI | Technical answers → rubric result | Later day folders | Planned/prototype only |
| Machine test evaluation AI | Submitted work → test/rubric report | Day 50 design/prototype | Not integrated |
| Behavior analysis AI | Audio/video/text signals → behavioral indicators | Day 27 prototype | Not integrated; no hiring use justified |
| Decision/recommendation AI | Multiple stages → recommendation | Day 21/52 prototypes | Not integrated; human decision remains necessary |
| Offer automation AI | Decision → offer workflow | No root implementation found | Missing |

No generative model or external AI service is configured in the root application.
