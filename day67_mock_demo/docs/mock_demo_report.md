# Day 67 Mock Demo Execution Report

- **Execution Type:** Scripted local mock demo rehearsal against `http://127.0.0.1:8000` (internal self-review; no external stakeholders participated).
- **Evidence Log:** `day67_mock_demo/output/rehearsal_execution_log.txt`
- **Screenshots:** 12 verified PNGs in `day67_mock_demo/screenshots/` (`screenshot_manifest.md`).

## Rehearsal Results
1. Server health (`GET /api/v1/health`) returned `200 OK`.
2. Day 63 dataset (`demo_data/`) loaded and verified (`8` archetypes).
3. Live resume upload (`202 Accepted`) + ATS scoring (`83.17`) + Cross-Round (`77.94%`) + Final Recommendation (`HOLD_REVIEW`, confidence `82.5`) + Human Review (`APPROVED`) + Hiring Intelligence Report (`report_20a28b8f4031`) executed cleanly.
4. Error & validation handling verified: invalid file upload (`400`), nonexistent candidate (`404`), unauthenticated `/openings` (`401`), and invalid browser login banner.
