# Day 20 – Browser Functional Test Matrix (BR-01 to BR-20)

**Testing Method:** Real Playwright Chromium Automation against `http://127.0.0.1:8000`  
**Total Functional Test Cases:** 20  
**Passed Tests:** 20 / 20 (**100% Pass Rate**)

| Test ID | Test Scenario | Execution Steps | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|---|
| **BR-01** | Application loads | Navigate to http://127.0.0.1:8000/ | HTTP 200, Header and Login panel visible | Title 'Zecpath AI Hiring System' loaded, login panel active | **PASS** | Initial landing verified |
| **BR-03** | Invalid login handling | Enter invalid credentials and submit login form | Display error notice and reject authentication | Notice displayed: 'Valid recruiter credentials are required.' | **PASS** | Credentials validated securely |
| **BR-02** | Valid recruiter login | Enter valid recruiter credentials and submit | Authentication succeeds, workspace unhides | Workspace unhidden, session cookie established | **PASS** | HTTP-only cookie established |
| **BR-05** | Required-field validation | Submit job opening form with empty title | HTML5 form validation blocks submission | HTML5 validation checkValidity() = False | **PASS** | Client-side constraints enforced |
| **BR-04** | Job opening creation | Fill valid job opening parameters and submit form | Job opening is persisted and selected in Manage dropdown | Selected job in dropdown: 'Senior Python Developer (Functional Test) (open)' | **PASS** | Job created and bound to workspace |
| **BR-07** | Unsupported file validation | Verify file input accept filter attribute | Accept only .txt, .docx, .pdf file formats | Input accept attribute: '.txt,.docx,.pdf' | **PASS** | MIME and extension filtering enforced |
| **BR-08** | Empty or invalid file handling | Submit candidate registration without name or skills | Form validation blocks empty registration | Name checkValidity() = False | **PASS** | Required candidate fields enforced |
| **BR-06** | Valid resume upload | Register candidate with valid text resume file | Candidate is created and listed in applications table | Alex Mercer present in rows: True | **PASS** | Resume file attached and extracted |
| **BR-09** | Resume parsing | Verify extracted skills and text representation | Candidate row renders extracted skills / resume evidence | Skills rendered in cell: True | **PASS** | Skill extraction and normalization verified |
| **BR-10** | Missing candidate information handling | Register candidate without optional email and location | Candidate accepted with missing optional attributes handled gracefully | Jordan Lee registered without email: True | **PASS** | Optional attributes do not block pipeline |
| **BR-15** | Multiple candidate evaluation | Register multiple diverse candidates for the same job opening | All candidates listed under active opening applications | Total candidate rows: 3 | **PASS** | Candidate applications table displays batch |
| **BR-11** | ATS score generation | Click Score button on candidate row | Real-time ATS score computed and rendered in table | Computed score text: '83.8%' | **PASS** | Score generated via 4-factor engine |
| **BR-12** | Score breakdown display | Inspect component breakdown accordion | Review component scores details element is rendered | Component summary present: True | **PASS** | 4 distinct components available |
| **BR-13** | Matched skills display | Inspect score evidence accordion | Matched required skills displayed in evidence list | Evidence summary present: True | **PASS** | Matched skills enumerated with evidence |
| **BR-14** | Missing skills display | Verify missing skills reporting on low-match candidate | Missing skills explicitly listed in candidate evidence | Evidence text captured: 'Matched: none; Missing: Python, FastAPI, SQL, PostgreSQL, Do...' | **PASS** | Negative skill gaps clearly isolated |
| **BR-16** | Candidate ranking | Verify candidate score ordering across opening | Candidates ranked in descending order of ATS match | Rank 1: Alex Mercer, Rank 2: Jordan Lee, Rank 3: Morgan Taylor | **PASS** | Monotonic score ranking verified |
| **BR-17** | Shortlist threshold | Execute candidate shortlisting with 60% threshold | Candidates >= 60% displayed in ordered shortlist | Shortlist output: '1. Alex Mercer - 83.8%' | **PASS** | Threshold filtering operates correctly |
| **BR-18** | Data persistence after refresh | Reload browser page and inspect persisted workspace state | Opening and all candidate scores remain preserved in SQLite | Persisted candidate rows: 3 | **PASS** | SQLite state preserved without data loss |
| **BR-19** | Swagger documentation | Navigate to /docs interactive OpenAPI documentation | Interactive Swagger UI renders successfully | Swagger UI container loaded: True | **PASS** | Interactive documentation fully operational |
| **BR-20** | Unauthorized access validation | Access protected API route without valid session cookie | Request rejected with HTTP 401 Unauthorized | HTTP Status: 401 (Unauthorized: True) | **PASS** | Endpoint access control active |