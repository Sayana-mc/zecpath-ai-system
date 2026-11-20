"""Real end-to-end verification, load testing, and screenshot capture for Days 56-60."""

from __future__ import annotations

import html
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BASE_URL = "http://127.0.0.1:8000"
AUTH = ("recruiter-d41-52", "Password123!LongEnough")

SHOT_DIRS = {
    56: ROOT / "day56_full_system_simulation" / "screenshots",
    57: ROOT / "day57_debugging_stabilization" / "screenshots",
    58: ROOT / "day58_advanced_feature_proposal" / "screenshots",
    59: ROOT / "day59_api_integration" / "screenshots",
    60: ROOT / "day60_performance_scalability" / "screenshots",
}


def run_day56_simulation_outputs() -> dict:
    from src import auth, database
    from src.simulation_pipeline import system_simulation_pipeline

    orig_db = os.environ.get("ZECPATH_DB_PATH")
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["ZECPATH_DB_PATH"] = str(Path(tmpdir) / "day56_sim.sqlite3")
        database.initialize_database()
        salt, pw_hash = auth.hash_recruiter_password("SimPass123!")
        database.upsert_recruiter_account("sim_recruiter", salt, pw_hash, role="admin", tenant_id="default_tenant")

        profiles = [
            {
                "candidate": {"name": "Arun Kumar (Sim)", "email": "arun.sim@zecpath.example", "skills": ["Python", "FastAPI", "SQL", "Docker"], "ats_score": 91.0, "screening_score": 88.0, "hr_interview_score": 86.0, "technical_interview_score": 90.0, "machine_test_score": 92.0},
                "opening": {"title": "Python Developer", "requirements": ["Python", "FastAPI", "SQL"]},
                "human": {"human_score": 90.0, "human_decision": "SELECTED", "notes": "Consistent strong performance across all 5 stages."},
            },
            {
                "candidate": {"name": "Rahul Menon (Sim)", "email": "rahul.sim@zecpath.example", "skills": ["React", "Node.js"], "ats_score": 70.0, "screening_score": 68.0, "hr_interview_score": 66.0, "technical_interview_score": 64.0, "machine_test_score": 65.0},
                "opening": {"title": "MERN Stack Developer", "requirements": ["React", "Node.js", "MongoDB"]},
                "human": {"human_score": 68.0, "human_decision": "HOLD_REVIEW", "notes": "Borderline depth; requires follow-up system design check."},
            },
            {
                "candidate": {"name": "Anjali Nair (Sim)", "email": "anjali.sim@zecpath.example", "skills": ["Excel", "Python"], "ats_score": 52.0, "screening_score": 55.0, "hr_interview_score": 58.0, "technical_interview_score": 50.0, "machine_test_score": 48.0},
                "opening": {"title": "Data Analyst", "requirements": ["SQL", "Python", "Statistics"]},
                "human": {"human_score": 53.0, "human_decision": "REJECTED", "notes": "Insufficient SQL & statistical modeling readiness."},
            },
            {
                "candidate": {"name": "Neha Thomas (Sim)", "email": "neha.sim@zecpath.example", "skills": ["SQL", "Python", "Pandas"], "ats_score": 88.0, "screening_score": 86.0, "hr_interview_score": 85.0, "technical_interview_score": 87.0, "machine_test_score": 89.0},
                "opening": {"title": "Data Analyst", "requirements": ["SQL", "Python", "Pandas"]},
                "human": {"human_score": 82.0, "human_decision": "HOLD_REVIEW", "notes": "Human reviewer requested extra domain SQL case verification despite strong AI fit."},
            },
        ]

        sim_results = []
        human_evals = []
        for p in profiles:
            res = system_simulation_pipeline.simulate_candidate_pipeline(
                candidate_data=p["candidate"],
                opening_data=p["opening"],
                recruiter_id="sim_recruiter",
            )
            sim_results.append(res)
            human_evals.append(p["human"])

        comparison = system_simulation_pipeline.compare_ai_vs_human_evaluations(sim_results, human_evals)

    if orig_db is None:
        os.environ.pop("ZECPATH_DB_PATH", None)
    else:
        os.environ["ZECPATH_DB_PATH"] = orig_db

    (ROOT / "day56_full_system_simulation" / "day56_ai_vs_human_comparison.json").write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )
    (ROOT / "day56_full_system_simulation" / "day56_test_results.json").write_text(
        json.dumps({"simulated_candidates": len(sim_results), "results": sim_results}, indent=2), encoding="utf-8"
    )
    return {"sim_results": sim_results, "comparison": comparison}


def run_day60_load_and_cache_benchmarks() -> dict:
    from src.batch_processing import run_scalability_benchmark

    # 1. Local TTLCache + tracemalloc benchmark
    local_bench = run_scalability_benchmark(sample_count=50, concurrency_levels=[1, 5, 10, 25])

    # 2. Cold vs Warm batch API benchmark on live server
    payload = {
        "resumes": [
            {"candidate_id": f"load_c_{i}", "text": f"Candidate {i % 5} skilled in Python FastAPI SQL Docker AWS"}
            for i in range(20)
        ],
        "batch_size": 5,
        "max_concurrency": 4,
    }
    t0 = time.perf_counter()
    r_cold = requests.post(f"{BASE_URL}/api/v1/resumes/batch-process", json=payload, auth=AUTH, timeout=15)
    cold_ms = round((time.perf_counter() - t0) * 1000, 2)

    t1 = time.perf_counter()
    r_warm = requests.post(f"{BASE_URL}/api/v1/resumes/batch-process", json=payload, auth=AUTH, timeout=15)
    warm_ms = round((time.perf_counter() - t1) * 1000, 2)

    # 3. Live HTTP concurrent load test (1, 5, 10, 25 concurrent workers)
    load_levels = [1, 5, 10, 25]
    load_results = []
    for workers in load_levels:
        total_reqs = workers * 2
        latencies = []
        failures = 0

        def _hit(_idx: int) -> float:
            s = time.perf_counter()
            resp = requests.get(f"{BASE_URL}/api/v1/candidates/cand_arun_kumar/cross-round-evaluation", auth=AUTH, timeout=15)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}")
            return (time.perf_counter() - s) * 1000.0

        wall_t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = [pool.submit(_hit, i) for i in range(total_reqs)]
            for f in futs:
                try:
                    latencies.append(f.result())
                except Exception:
                    failures += 1
        wall_sec = max(0.001, time.perf_counter() - wall_t0)
        latencies.sort()
        avg_ms = round(sum(latencies) / max(1, len(latencies)), 2)
        p95_ms = round(latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))], 2) if latencies else 0.0
        load_results.append({
            "concurrency": workers,
            "total_requests": total_reqs,
            "successful": len(latencies),
            "failed": failures,
            "avg_latency_ms": avg_ms,
            "p95_latency_ms": p95_ms,
            "throughput_rps": round(len(latencies) / wall_sec, 2),
        })

    comparison = {
        "batch_cache_comparison": {
            "cold_run_ms": cold_ms,
            "cold_cache_hits": r_cold.json().get("cache_hits") if r_cold.ok else 0,
            "warm_run_ms": warm_ms,
            "warm_cache_hits": r_warm.json().get("cache_hits") if r_warm.ok else 0,
            "warm_cache_hit_rate": r_warm.json().get("cache_hit_rate") if r_warm.ok else 0.0,
        },
        "local_scalability_benchmark": local_bench,
        "live_http_load_test": load_results,
    }
    (ROOT / "day60_performance_scalability" / "day60_before_after_comparison.json").write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )
    return comparison


def _capture_terminal(page: Page, cmd: list[str], out_path: Path, title: str) -> None:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    output_text = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    cmd_str = " ".join(cmd)
    rendered_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
body {{ margin:0; padding:24px; background:#0b1120; color:#e2e8f0; font-family:Consolas,'Courier New',monospace; font-size:13px; }}
.win {{ border:1px solid #334155; border-radius:8px; overflow:hidden; background:#0f172a; }}
.bar {{ background:#1e293b; padding:10px 16px; font-weight:bold; color:#94a3b8; border-bottom:1px solid #334155; }}
pre {{ margin:0; padding:18px; white-space:pre-wrap; line-height:1.45; color:#d1fae5; }}
.cmd {{ color:#38bdf8; font-weight:bold; margin-bottom:10px; }}
</style></head><body><div class="win"><div class="bar">{html.escape(title)} (exit code: {proc.returncode})</div>
<pre><div class="cmd">PS C:\\Users\\sayan\\Documents\\zecpath-ai-system&gt; {html.escape(cmd_str)}</div>{html.escape(output_text.strip())}</pre>
</div></body></html>"""
    page.set_content(rendered_html)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out_path), full_page=True)


def _swagger_execute(page: Page, method: str, api_path: str, out_path: Path, path_params: dict[str, str] | None = None, body_json: str | None = None) -> None:
    if "/docs" not in page.url:
        page.goto(f"{BASE_URL}/docs", wait_until="networkidle")
    page.wait_for_selector(".opblock", timeout=15000)
    op = page.locator(f'.opblock.opblock-{method.lower()}:has([data-path="{api_path}"])').first
    op.scroll_into_view_if_needed()
    if "is-open" not in (op.get_attribute("class") or ""):
        op.locator(".opblock-summary-control").click()
        page.wait_for_timeout(300)
    try_btn = op.locator("button.try-out__btn")
    if try_btn.is_visible() and "Try it out" in (try_btn.inner_text() or ""):
        try_btn.click()
        page.wait_for_timeout(250)
    if path_params:
        for k, v in path_params.items():
            inp = op.locator(f'tr[data-param-name="{k}"] input')
            if inp.count() > 0:
                inp.first.fill(v)
    if body_json is not None:
        ta = op.locator("textarea.body-param__text")
        if ta.count() > 0:
            ta.first.fill(body_json)
    op.locator("button.execute").click()
    op.locator(".responses-wrapper .live-responses-table").wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(400)
    op.scroll_into_view_if_needed()
    op.screenshot(path=str(out_path))


def capture_all_screenshots() -> None:
    for d in SHOT_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Login to real application
        page.goto(BASE_URL, wait_until="networkidle")
        page.fill("#authUsername", AUTH[0])
        page.fill("#authPassword", AUTH[1])
        page.click('#loginForm button[type="submit"]')
        page.wait_for_selector("#workspace", state="visible", timeout=15000)
        page.wait_for_timeout(1200)

        # Day 56: End-to-End Dashboard, ATS, Cross-Round, Recommendation
        page.select_option("#openingSelect", "open_python_dev")
        page.wait_for_timeout(800)
        page.screenshot(path=str(SHOT_DIRS[56] / "01_actual_application_dashboard.png"))

        page.locator("#candidateTable").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        page.screenshot(path=str(SHOT_DIRS[56] / "02_candidate_ats_and_eligibility.png"))

        page.click('.tab-btn[data-tab="tab-cross-round"]')
        page.wait_for_timeout(600)
        page.select_option("#d51CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(600)
        page.screenshot(path=str(SHOT_DIRS[56] / "03_cross_round_aggregation_ui.png"))

        page.click('.tab-btn[data-tab="tab-recommendation"]')
        page.wait_for_timeout(600)
        page.select_option("#d52CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(600)
        page.screenshot(path=str(SHOT_DIRS[56] / "04_final_recommendation_and_human_review.png"))

        # Day 60: Observability & Monitoring UI
        page.click('.tab-btn[data-tab="tab-ats"]')
        page.wait_for_timeout(500)
        page.locator("#monitoringSection").scroll_into_view_if_needed()
        page.click("#refreshMonitoringButton")
        page.wait_for_timeout(800)
        page.screenshot(path=str(SHOT_DIRS[60] / "01_observability_monitoring_ui.png"))

        # Swagger executions for Days 56-60
        _swagger_execute(
            page, "POST", "/api/v1/simulation/benchmark",
            SHOT_DIRS[56] / "05_swagger_simulation_benchmark.png",
            body_json='{"simulations":[{"candidate_id":"cand_arun_kumar","unified_fit_score":89.75,"ai_recommendation":"SELECTED"}],"human_evaluations":[{"human_score":90.0,"human_decision":"SELECTED"}]}',
        )
        _swagger_execute(
            page, "POST", "/api/v1/candidates/{candidate_id}/coaching",
            SHOT_DIRS[58] / "01_swagger_post_candidate_coaching.png",
            path_params={"candidate_id": "cand_rahul_menon"},
        )
        _swagger_execute(
            page, "GET", "/api/v1/candidates/{candidate_id}/coaching",
            SHOT_DIRS[58] / "02_swagger_get_candidate_coaching.png",
            path_params={"candidate_id": "cand_rahul_menon"},
        )
        _swagger_execute(
            page, "POST", "/api/v1/candidates/{candidate_id}/cross-round-evaluation",
            SHOT_DIRS[59] / "01_swagger_cross_round_api.png",
            path_params={"candidate_id": "cand_arun_kumar"},
            body_json='{"target_role":"python_developer","force_recalculate":false}',
        )
        _swagger_execute(
            page, "GET", "/api/v1/candidates/{candidate_id}/hiring-intelligence-report",
            SHOT_DIRS[59] / "02_swagger_hiring_report_api.png",
            path_params={"candidate_id": "cand_arun_kumar"},
        )
        _swagger_execute(
            page, "POST", "/api/v1/resumes/batch-process",
            SHOT_DIRS[60] / "02_swagger_batch_resume_process.png",
            body_json='{"resumes":[{"candidate_id":"b1","text":"Python FastAPI SQL Docker"},{"candidate_id":"b2","text":"React Node MongoDB"}],"batch_size":2,"max_concurrency":2}',
        )
        _swagger_execute(
            page, "GET", "/api/v1/monitoring/dashboard",
            SHOT_DIRS[60] / "03_swagger_monitoring_dashboard.png",
        )

        # Terminal test screenshots
        term = context.new_page()
        _capture_terminal(term, [sys.executable, "-m", "pytest", "day56_full_system_simulation/tests/", "tests/test_day53_day60.py", "-k", "day56", "-v"], SHOT_DIRS[56] / "06_day56_tests_terminal.png", "Day 56 Simulation Tests")
        _capture_terminal(term, [sys.executable, "-m", "pytest", "day57_debugging_stabilization/tests/", "tests/test_day57_edge_cases.py", "-v"], SHOT_DIRS[57] / "01_day57_edge_case_tests_terminal.png", "Day 57 Debugging & Edge-Case Tests")
        _capture_terminal(term, [sys.executable, "-m", "pytest", "day58_advanced_feature_proposal/tests/", "tests/test_day53_day60.py", "-k", "day58", "-v"], SHOT_DIRS[58] / "03_day58_coaching_tests_terminal.png", "Day 58 Feature Proposal & Coaching Tests")
        _capture_terminal(term, [sys.executable, "-m", "pytest", "day59_api_integration_planning/tests/", "-v"], SHOT_DIRS[59] / "03_day59_api_integration_tests_terminal.png", "Day 59 API Integration Tests")
        _capture_terminal(term, [sys.executable, "-m", "pytest", "day60_performance_scalability/tests/", "tests/test_day53_day60.py", "-k", "day60", "-v"], SHOT_DIRS[60] / "04_day60_performance_tests_terminal.png", "Day 60 Performance & Scalability Tests")

        browser.close()
    print("Captured all Days 56-60 verification screenshots.")


if __name__ == "__main__":
    d56 = run_day56_simulation_outputs()
    d60 = run_day60_load_and_cache_benchmarks()
    capture_all_screenshots()
    print(json.dumps({"day56_evaluated": d56["comparison"]["total_evaluated"], "day60_load_levels": len(d60["live_http_load_test"])}, indent=2))
