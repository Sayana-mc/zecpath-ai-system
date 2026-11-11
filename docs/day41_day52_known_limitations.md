# Day 41–52 Known Limitations & Future Enhancements

## Known System Limitations

1. **Sandboxed Code Execution for Machine Tests:**
   - Current machine test scoring executes unit assertions and heuristics within the in-process Python runtime. While safe for standardized algorithms, multi-tenant untrusted user code should ideally execute inside containerized micro-sandboxes (e.g., Docker, Firecracker, or gVisor) with resource quotas.

2. **Heuristic Keyword and Structural Parsing in Technical Depth Evaluation:**
   - The depth classifier relies on semantic depth tokens, code length, and architectural connector heuristics. While highly explainable, transparent, and reproducible, it can be paired with fine-tuned embedding-based semantic similarity models in future iterations.

3. **Client-Side Browser Event Telemetry:**
   - Integrity detection expects well-formed event telemetry payloads (`tab_switch`, `window_blur`, `external_audio`) from frontend instrumentation. In low-bandwidth or disconnected network conditions, events are batched and posted retroactively.

4. **Retention Window Scheduling:**
   - The compliance engine computes the 180-day retention and purge deadlines. Scheduled deletion jobs must be invoked via automated cron runners (e.g., Celery Beat or systemd timers) to physically purge expired records from SQLite.

---

## Planned Enhancements (Post Day 52)

- **Interactive IDE Sandbox Integration:** Embedding Monaco editor and WebAssembly-based code runners in the recruiter/candidate interface.
- **Multilingual Technical Evaluations:** Expanding technical interview question sets and answers to French, Spanish, German, and Hindi.
- **Enterprise Single Sign-On (SSO):** SAML 2.0 / OIDC integrations for recruiter enterprise logins.

