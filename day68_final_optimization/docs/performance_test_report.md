# Day 68 Performance Test Report

- **Environment:** Local Windows 11, Python 3.12, single-worker Uvicorn (`127.0.0.1:8000`), SQLite (`248` openings, `216` candidates in DB).
- **Source:** `day68_final_optimization/output/api_validation_results.json`

## Measured Endpoint Latencies (Single Local Run)
- `GET /api/v1/health`: **13.9 ms**
- `GET /api/v1/openings` (10x repeated avg): **256.58 ms**
- `GET /api/v1/candidates`: **296.57 ms**
- `POST /api/v1/resumes/upload`: **268.19 ms**
- `POST /api/v1/ats/score`: **230.17 ms**
- `POST /api/v1/cross-round-evaluation`: **323.35 ms**
- `POST /api/v1/final-recommendation`: **295.23 ms**
- `POST /api/v1/hiring-intelligence-report`: **344.66 ms**
- **5x Concurrent `GET /api/v1/candidates`:** All `5` returned HTTP `200` (`486.62 ms – 818.46 ms`).

*Note: Local single-node measurements do not constitute production scalability proof.*
