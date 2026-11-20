"""Playwright screenshot capture for Days 51-55 (UI, Swagger APIs, PDF/HTML, and real pytest terminal outputs)."""

from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "http://127.0.0.1:8000"

DIRS = {
    51: ROOT / "day51_cross_round_aggregation" / "screenshots",
    52: ROOT / "day52_final_recommendation_ai" / "screenshots",
    53: ROOT / "day53_hiring_intelligence_report" / "screenshots",
    54: ROOT / "day54_optimization_refinement" / "screenshots",
    55: ROOT / "day55_security_ai_governance" / "screenshots",
}


def _ensure_dirs() -> None:
    for d in DIRS.values():
        d.mkdir(parents=True, exist_ok=True)


def _login_ui(page: Page, username: str, password: str) -> None:
    page.goto(BASE_URL, wait_until="networkidle")
    if page.locator("#signOutButton").is_visible():
        page.click("#signOutButton")
        page.wait_for_selector("#loginForm", state="visible")
    page.fill("#authUsername", username)
    page.fill("#authPassword", password)
    page.click('#loginForm button[type="submit"]')
    page.wait_for_selector("#workspace", state="visible", timeout=15000)
    page.wait_for_timeout(1200)


def _click_tab(page: Page, tab_id: str) -> None:
    page.click(f'.tab-btn[data-tab="{tab_id}"]')
    page.wait_for_timeout(700)


def _capture_terminal_pytest(page: Page, cmd: list[str], out_path: Path, title: str) -> None:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    output_text = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    cmd_str = " ".join(cmd)
    rendered_html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><style>
body {{ margin:0; padding:24px; background:#0b1120; color:#e2e8f0; font-family:Consolas,'Courier New',monospace; font-size:13px; }}
.win {{ border:1px solid #334155; border-radius:8px; overflow:hidden; background:#0f172a; box-shadow:0 10px 30px rgba(0,0,0,0.5); }}
.bar {{ background:#1e293b; padding:10px 16px; font-weight:bold; color:#94a3b8; border-bottom:1px solid #334155; }}
pre {{ margin:0; padding:18px; white-space:pre-wrap; line-height:1.45; color:#d1fae5; }}
.cmd {{ color:#38bdf8; font-weight:bold; margin-bottom:10px; }}
</style></head>
<body><div class="win"><div class="bar">{html.escape(title)} (exit code: {proc.returncode})</div>
<pre><div class="cmd">PS C:\\Users\\sayan\\Documents\\zecpath-ai-system&gt; {html.escape(cmd_str)}</div>{html.escape(output_text.strip())}</pre>
</div></body></html>"""
    page.set_content(rendered_html)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out_path), full_page=True)


def _swagger_execute(
    page: Page,
    method: str,
    api_path: str,
    out_path: Path,
    path_params: dict[str, str] | None = None,
    body_json: str | None = None,
) -> None:
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
        for param_name, val in path_params.items():
            inp = op.locator(f'tr[data-param-name="{param_name}"] input')
            if inp.count() > 0:
                inp.first.fill(val)
    if body_json is not None:
        ta = op.locator("textarea.body-param__text")
        if ta.count() > 0:
            ta.first.fill(body_json)
    exec_btn = op.locator("button.execute")
    exec_btn.click()
    op.locator(".responses-wrapper .live-responses-table").wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(400)
    op.scroll_into_view_if_needed()
    op.screenshot(path=str(out_path))


def main() -> None:
    _ensure_dirs()
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Login as admin recruiter
        _login_ui(page, "recruiter-d41-52", "Password123!LongEnough")

        # -------------------- DAY 51 UI --------------------
        _click_tab(page, "tab-cross-round")
        page.select_option("#d51CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(700)
        page.screenshot(path=str(DIRS[51] / "01_recruiter_cross_round_ui_arun_kumar.png"))

        page.select_option("#d51CandidateSelect", "cand_vivek_raj")
        page.wait_for_timeout(700)
        page.screenshot(path=str(DIRS[51] / "02_recruiter_cross_round_incomplete_vivek_raj.png"))

        page.select_option("#d51CandidateSelect", "cand_neha_thomas")
        page.wait_for_timeout(700)
        page.locator("#d51SaveWeightsBtn").scroll_into_view_if_needed()
        page.screenshot(path=str(DIRS[51] / "03_recruiter_role_weight_config_ui.png"))

        page.select_option("#d51CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(500)
        page.click("#d51RecalcBtn")
        page.wait_for_timeout(900)
        page.locator("#d51HistoryTable").scroll_into_view_if_needed()
        page.screenshot(path=str(DIRS[51] / "04_recruiter_cross_round_recalculation_history.png"))

        # -------------------- DAY 52 UI --------------------
        _click_tab(page, "tab-recommendation")
        page.select_option("#d52CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(700)
        page.screenshot(path=str(DIRS[52] / "01_recommendation_ui_selected_arun.png"))

        page.select_option("#d52CandidateSelect", "cand_rahul_menon")
        page.wait_for_timeout(700)
        page.screenshot(path=str(DIRS[52] / "02_recommendation_ui_hold_review_rahul.png"))

        page.select_option("#d52CandidateSelect", "cand_anjali_nair")
        page.wait_for_timeout(700)
        page.screenshot(path=str(DIRS[52] / "03_recommendation_ui_eligibility_rejected_anjali.png"))

        page.select_option("#d52CandidateSelect", "cand_rahul_menon")
        page.wait_for_timeout(600)
        page.fill("#d52DecisionNotes", "Hold for additional MERN system design review.")
        page.click("#d52SubmitDecisionBtn")
        page.wait_for_timeout(900)
        page.locator("#d52HistoryBox").scroll_into_view_if_needed()
        page.screenshot(path=str(DIRS[52] / "04_recommendation_ui_human_decision_audit.png"))

        # -------------------- DAY 53 UI --------------------
        _click_tab(page, "tab-report")
        page.select_option("#d53CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(800)
        page.screenshot(path=str(DIRS[53] / "01_report_ui_overview_arun.png"))

        page.evaluate("window.scrollTo(0, 750)")
        page.wait_for_timeout(300)
        page.screenshot(path=str(DIRS[53] / "02_report_ui_sections_scroll.png"))
        page.evaluate("window.scrollTo(0, 0)")

        page.select_option("#d53CandidateSelect", "cand_vivek_raj")
        page.wait_for_timeout(800)
        page.screenshot(path=str(DIRS[53] / "03_report_ui_incomplete_vivek.png"))

        # -------------------- DAY 54 UI --------------------
        _click_tab(page, "tab-optimization")
        page.click("#d54RunBtn")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(DIRS[54] / "01_optimization_ui_metrics_and_sweep.png"))

        page.evaluate("window.scrollTo(0, 420)")
        page.wait_for_timeout(400)
        page.screenshot(path=str(DIRS[54] / "02_optimization_ui_confusion_and_latency.png"))

        page.evaluate("window.scrollTo(0, 0)")
        page.fill("#d54StrongMin", "85")
        page.click("#d54RunBtn")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(DIRS[54] / "03_optimization_ui_custom_threshold_run.png"))

        # Monitoring section on ATS tab
        _click_tab(page, "tab-ats")
        page.locator("#monitoringSection").scroll_into_view_if_needed()
        page.click("#refreshMonitoringButton")
        page.wait_for_timeout(800)
        page.screenshot(path=str(DIRS[54] / "07_system_observability_ui.png"))

        # -------------------- DAY 55 UI --------------------
        _click_tab(page, "tab-governance")
        page.evaluate("window.scrollTo(0, 0)")
        page.select_option("#d55ConsentCandidate", "cand_arun_kumar")
        page.wait_for_timeout(700)
        page.screenshot(path=str(DIRS[55] / "01_governance_ui_admin_overview.png"))

        page.click("#d55VerifyAuditBtn")
        page.wait_for_timeout(800)
        page.locator("#d55AuditVerifyBanner").scroll_into_view_if_needed()
        page.screenshot(path=str(DIRS[55] / "02_governance_ui_rbac_and_audit_verified.png"))

        page.evaluate("window.scrollTo(0, 0)")
        page.select_option("#d55ConsentCandidate", "cand_neha_thomas")
        page.wait_for_timeout(500)
        page.select_option("#d55ConsentPurpose", "audio_recording")
        page.click("#d55RevokeConsentBtn")
        page.wait_for_timeout(700)
        page.select_option("#d55ConsentPurpose", "ai_assessment")
        page.click("#d55GrantConsentBtn")
        page.wait_for_timeout(800)
        page.screenshot(path=str(DIRS[55] / "03_governance_ui_consent_revoked_and_granted.png"))

        # Day 53 Direct HTML, Markdown, PDF views (authenticated session cookie)
        page.goto(f"{BASE_URL}/api/v1/candidates/cand_arun_kumar/hiring-intelligence-report/html", wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=str(DIRS[53] / "04_report_html_view_arun.png"))

        page.goto(f"{BASE_URL}/api/v1/candidates/cand_arun_kumar/hiring-intelligence-report/markdown", wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=str(DIRS[53] / "06_report_markdown_view.png"))

        page.goto(f"{BASE_URL}/api/v1/candidates/cand_arun_kumar/hiring-intelligence-report/pdf", wait_until="load")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(DIRS[53] / "05_report_pdf_chrome_preview.png"))

        # -------------------- SWAGGER API EXECUTIONS --------------------
        _swagger_execute(
            page,
            "POST",
            "/api/v1/candidates/{candidate_id}/cross-round-evaluation",
            DIRS[51] / "05_swagger_post_cross_round_evaluation.png",
            path_params={"candidate_id": "cand_arun_kumar"},
            body_json='{"target_role": "python_developer", "force_recalculate": false}',
        )
        _swagger_execute(
            page,
            "PUT",
            "/api/v1/role-weights/{role_key}",
            DIRS[51] / "06_swagger_put_role_weights.png",
            path_params={"role_key": "python_developer"},
            body_json='{"weights": {"ats": 15, "screening": 15, "hr_interview": 15, "technical_interview": 30, "machine_test": 25}, "min_required_stages": 3}',
        )
        _swagger_execute(
            page,
            "GET",
            "/api/v1/candidates/{candidate_id}/cross-round-evaluation",
            DIRS[51] / "07_swagger_get_cross_round_history.png",
            path_params={"candidate_id": "cand_vivek_raj"},
        )

        _swagger_execute(
            page,
            "POST",
            "/api/v1/candidates/{candidate_id}/final-recommendation",
            DIRS[52] / "05_swagger_post_final_recommendation.png",
            path_params={"candidate_id": "cand_rahul_menon"},
            body_json='{"target_role": "mern_developer"}',
        )
        _swagger_execute(
            page,
            "GET",
            "/api/v1/decision-thresholds",
            DIRS[52] / "07_swagger_get_decision_thresholds.png",
        )
        # Fetch a real recommendation_id for Rahul Menon via API in page
        rec_id = page.evaluate("""async () => {
            const r = await fetch('/api/v1/candidates/cand_rahul_menon/final-recommendation');
            const d = await r.json();
            return d[0]?.recommendation_id || '';
        }""")
        if rec_id:
            _swagger_execute(
                page,
                "POST",
                "/api/v1/final-recommendations/{recommendation_id}/decision",
                DIRS[52] / "06_swagger_post_recruiter_decision.png",
                path_params={"recommendation_id": rec_id},
                body_json='{"recruiter_decision": "APPROVED", "notes": "Confirmed via Swagger review"}',
            )

        _swagger_execute(
            page,
            "POST",
            "/api/v1/candidates/{candidate_id}/hiring-intelligence-report",
            DIRS[53] / "07_swagger_post_generate_report.png",
            path_params={"candidate_id": "cand_neha_thomas"},
        )
        _swagger_execute(
            page,
            "GET",
            "/api/v1/candidates/{candidate_id}/hiring-intelligence-report/history",
            DIRS[53] / "08_swagger_get_report_history.png",
            path_params={"candidate_id": "cand_arun_kumar"},
        )

        _swagger_execute(
            page,
            "POST",
            "/api/v1/optimization/run",
            DIRS[54] / "04_swagger_post_optimization_run.png",
            body_json='{"strong_threshold": 80.0, "potential_threshold": 60.0}',
        )
        _swagger_execute(
            page,
            "GET",
            "/api/v1/optimization/history",
            DIRS[54] / "05_swagger_get_optimization_history.png",
        )
        _swagger_execute(
            page,
            "GET",
            "/api/v1/monitoring/dashboard",
            DIRS[54] / "06_swagger_get_monitoring_dashboard.png",
        )

        _swagger_execute(
            page,
            "GET",
            "/api/v1/governance/whoami",
            DIRS[55] / "05_swagger_get_governance_whoami.png",
        )
        _swagger_execute(
            page,
            "GET",
            "/api/v1/audit/verify",
            DIRS[55] / "06_swagger_get_audit_verify.png",
        )
        _swagger_execute(
            page,
            "POST",
            "/api/v1/candidates/{candidate_id}/consent",
            DIRS[55] / "07_swagger_post_candidate_consent.png",
            path_params={"candidate_id": "cand_arun_kumar"},
            body_json='{"purpose": "ai_assessment", "granted": true, "consent_version": "consent-v2", "notes": "Swagger consent check"}',
        )
        _swagger_execute(
            page,
            "GET",
            "/api/v1/governance/retention-policies",
            DIRS[55] / "08_swagger_get_retention_policies.png",
        )

        # -------------------- JUNIOR RECRUITER RBAC 403 UI --------------------
        _login_ui(page, "junior_recruiter", "JuniorDemo123!")
        _click_tab(page, "tab-governance")
        page.wait_for_function("document.getElementById('d55ActorBadge')?.textContent?.includes('junior_recruiter')", timeout=10000)
        page.click("#d55VerifyAuditBtn")
        page.wait_for_timeout(800)
        page.locator("#d55AuditVerifyBanner").scroll_into_view_if_needed()
        page.screenshot(path=str(DIRS[55] / "04_governance_ui_junior_recruiter_403.png"))

        # -------------------- TERMINAL PYTEST SCREENSHOTS --------------------
        term_page = context.new_page()
        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "day51_cross_round_aggregation_engine/tests/", "-v"], DIRS[51] / "08_day51_unit_tests_terminal.png", "Day 51 Unit Tests")
        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "tests/test_day51_55_comprehensive.py", "-k", "test_day51_role_weights", "-v"], DIRS[51] / "09_day51_integration_tests_terminal.png", "Day 51 Integration Tests")

        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "day52_final_recommendation_ai/tests/", "-v"], DIRS[52] / "08_day52_unit_tests_terminal.png", "Day 52 Unit Tests")
        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "tests/test_day51_55_comprehensive.py", "-k", "test_day52", "-v"], DIRS[52] / "09_day52_integration_tests_terminal.png", "Day 52 Integration Tests")

        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "day53_hiring_intelligence_report/tests/", "-v"], DIRS[53] / "09_day53_unit_tests_terminal.png", "Day 53 Unit Tests")
        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "tests/test_day51_55_comprehensive.py", "-k", "test_day53", "-v"], DIRS[53] / "10_day53_integration_tests_terminal.png", "Day 53 Integration Tests")

        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "day54_optimization_refinement/tests/", "-v"], DIRS[54] / "08_day54_unit_tests_terminal.png", "Day 54 Unit Tests")
        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "tests/test_day51_55_comprehensive.py", "-k", "test_day54", "-v"], DIRS[54] / "09_day54_integration_tests_terminal.png", "Day 54 Integration Tests")

        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "day55_security_ai_governance/tests/", "-v"], DIRS[55] / "09_day55_unit_tests_terminal.png", "Day 55 Unit Tests")
        _capture_terminal_pytest(term_page, [sys.executable, "-m", "pytest", "tests/test_day51_55_comprehensive.py", "-k", "test_day55", "-v"], DIRS[55] / "10_day55_integration_tests_terminal.png", "Day 55 Integration Tests")

        browser.close()
    print("Captured all 47 screenshots for Days 51-55.")


if __name__ == "__main__":
    main()
