# Day 2 — Engine input/output specification

| Engine | Required input | Output | Validation / failure behavior | Versioning today |
|---|---|---|---|---|
| Resume extraction | supported PDF/DOCX/TXT upload ≤5 MiB | extracted text, filename, processing status | format/MIME/size/empty/corrupt checks; FAILED state on parser error | No persisted parser version |
| Resume profile | extracted text | section strings, skills, work dates, education, certificates | rule-based; missing fields empty/None; no model confidence schema | extraction method string |
| Job profile | title, description, required/preferred skills, optional education/years | opening record | Pydantic bounds; at least one required skill | No JD parser/version in root |
| Semantic match | sanitized resume text and job title/description/skills/requirements | cosine similarity [0,1] or unavailable/error | local model required; explicit 503 on model failure | `all-MiniLM-L6-v2` constant; package range in requirements |
| ATS score | skill, experience, education, semantic component values and job title | final score, component weights/contributions/classification | component scores normalized to 0–100; missing inputs contribute zero | Python role weights; no stored formula version |
| Ranking | opening ID and persisted scores | candidate ID, score, rank | job-scoped; deterministic score/name tie ordering | No ranking snapshot/version |
| Screening report | bounded list of questions/answers/intents | keyword/regex extraction and review flags | request schema validation; no score/recommendation | Method label `day25_keyword_and_regex_rules` |

No external model endpoint, webhook, or asynchronous result-retrieval API beyond
the local processing-job status route exists. Proposed service splitting is
not part of the current deployment.
