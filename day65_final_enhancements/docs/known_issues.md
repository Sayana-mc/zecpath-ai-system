# Day 65 Known Issues & Limitations

1. **Candidate-Facing Assessment UI Not Present:** Screening, HR Interview, Technical Interview, and Machine Test stages are fully functional via `/api/v1/*` REST APIs and Swagger (`/docs`), while `static/index.html` provides the recruiter-facing workspace only.
2. **Machine-Test Execution Model:** `src/machine_test_engine.py` evaluates code via Python `ast` and static rubric heuristics rather than executing untrusted code inside an isolated container/micro-VM sandbox.
3. **Database Concurrency Ceiling:** Local SQLite (`data/zecpath.sqlite3`) is suitable for single-node demos; concurrent production writes require PostgreSQL.
4. **Synthetic Benchmark Scope:** Day 54 optimization metrics (`91.7%` at `selected_min=80.0`) are measured on a 12-case synthetic validation dataset, not real-world hiring outcomes.
5. **Existing Test DB Pollution:** Running `src/init_demo_data.py` against the default `data/zecpath.sqlite3` appends demo openings alongside historical test rows unless `--target-db` or `ZECPATH_DB_PATH` is isolated.
