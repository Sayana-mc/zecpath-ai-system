# Project structure

| Path | Responsibility | Runtime status |
|---|---|---|
| `src/` | FastAPI app, auth, APIs, SQLite, schemas, resume analysis, score integration | Root application |
| `static/` | Same-origin HTML/CSS/JavaScript recruiter dashboard | Served by FastAPI |
| `ats_engine/` | Original ATS utility scorer | Imported by resume service helper |
| `day8_resume_section_segmentation/` | Resume heading/section rules | Called by root resume profile extraction |
| `day9_skill_extraction/` | Skill dictionary, normalization, evidence confidence | Called by root |
| `day10_experience_relevance/` | Experience date/role rules | Called by root |
| `day11_education_certification/` | Education/certification rules | Called by root |
| `day12_semantic_matching/` | Local sentence embeddings and similarity | Called by root when resume text is available |
| `day13_ats_scoring/` | Role weights, components, weighted score | Called by root |
| `day14_candidate_ranking/` | Standalone ranking exercise | Root has separate persisted ranking |
| `day15_fairness_bias_reduction/` | Prototype fairness utilities | Root currently implements only basic semantic-input masking |
| `day16+` | Later standalone exercises, designs, and reports | Not implied to be root-integrated |
| `datasets/test/` | Synthetic resume and JD fixtures | Safe non-production test data |
| `tests/` | Root API, score, fairness, and logging tests | Run with root pytest configuration |
| `data/` | Default SQLite location and existing data files | Do not use for destructive tests |
| `uploads/`, `logs/` | Temporary resume files and runtime logs | Runtime-generated; excluded from source control as configured |
| `docs/` | Architecture, setup, audit, and day deliverables | Documentation |

This layout deliberately preserves stage folders rather than moving code and
breaking their imports. The root application is the supported launch target:
`src.main:app`.
