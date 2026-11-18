# Day 50 – Machine Test AI Design Screenshot Manifest

- **Day:** Day 50
- **Verification Date:** 2026-11-15
- **Execution Environment:** Live Running ZecPath Backend (`http://127.0.0.1:8000`)
- **Browser Used:** Chromium (Google Chrome via Playwright)

## SCREENSHOT VERIFICATION TABLE

| Screenshot | Feature | Capture source | Actual execution verified | Status |
|---|---|---|---|---|
| `01_machine_test_task_catalogue.png` | Machine test task catalogue (Coding, Debugging, System Design) | Swagger UI (`GET /machine-tests/assignments`) | Yes | **VERIFIED** |
| `02_coding_problem_selection.png` | Coding problem selection with difficulty & test cases | Swagger UI (`GET /machine-tests/assignments`) | Yes | **VERIFIED** |
| `03_task_instructions_time_limit.png` | Task instructions, constraints, and configured time limit | Swagger UI Assignment Details | Yes | **VERIFIED** |
| `04_candidate_code_submission.png` | Candidate solution code submission | Swagger UI (`POST /machine-tests/assignments/{id}/submit`) | Yes | **VERIFIED** |
| `05_execution_result.png` | Execution result evaluation against test suite | Swagger UI Response Table | Yes | **VERIFIED** |
| `06_test_case_results.png` | Individual test case pass/fail results | Swagger UI Response Table | Yes | **VERIFIED** |
| `07_code_evaluation_breakdown.png` | Code evaluation breakdown (Correctness, Efficiency, Time Score) | Swagger UI Response Table | Yes | **VERIFIED** |
| `08_compilation_runtime_error_handling.png` | Compilation and runtime error handling safeguards | Swagger UI Response Table | Yes | **VERIFIED** |
| `09_time_limit_handling.png` | Time-limit adherence and elapsed-time scoring | Swagger UI Response Table | Yes | **VERIFIED** |
| `10_machine_test_api_response.png` | Complete machine test submission API response JSON | Swagger UI Response Table | Yes | **VERIFIED** |
