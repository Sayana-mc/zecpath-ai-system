"""Capture genuine browser, Swagger, PDF, and terminal screenshots for Days 61-70."""

from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "http://127.0.0.1:8000"
AUTH = ("recruiter-d41-52", "Password123!LongEnough")
EVIDENCE_ROOT = ROOT / "final_submission" / "10_Screenshots_and_Evidence"


def _capture_terminal(page, cmd: list[str], out_path: Path, title: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    output_text = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    cmd_str = " ".join(cmd)
    rendered = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body {{ margin:0; padding:24px; background:#0b1120; color:#e2e8f0; font-family:Consolas,'Courier New',monospace; font-size:13px; }}
.win {{ border:1px solid #334155; border-radius:8px; overflow:hidden; background:#0f172a; }}
.bar {{ background:#1e293b; padding:10px 16px; font-weight:bold; color:#94a3b8; border-bottom:1px solid #334155; }}
pre {{ margin:0; padding:18px; white-space:pre-wrap; line-height:1.45; color:#d1fae5; }}
.cmd {{ color:#38bdf8; font-weight:bold; margin-bottom:10px; }}
</style></head><body><div class="win"><div class="bar">{html.escape(title)} (exit code: {proc.returncode})</div>
<pre><div class="cmd">PS C:\\Users\\sayan\\Documents\\zecpath-ai-system&gt; {html.escape(cmd_str)}</div>{html.escape(output_text.strip())}</pre>
</div></body></html>"""
    page.set_content(rendered)
    page.wait_for_timeout(200)
    page.screenshot(path=str(out_path), full_page=True)


def main() -> None:
    folders = [
        "Day_61_Monitoring", "Day_62_Documentation", "Day_63_Demo_Dataset",
        "Day_64_Internal_Review", "Day_65_Feature_Polish", "Day_66_Presentation",
        "Day_67_Mock_Demo", "Day_68_Testing", "Day_69_Submission", "Day_70_Final_Demo",
    ]
    for f in folders:
        (EVIDENCE_ROOT / f).mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Login
        page.goto(BASE_URL, wait_until="networkidle")
        page.fill("#authUsername", AUTH[0])
        page.fill("#authPassword", AUTH[1])
        page.click('#loginForm button[type="submit"]')
        page.wait_for_selector("#workspace", state="visible", timeout=15000)
        page.wait_for_timeout(1200)

        # Day 63: Candidate profiles UI
        page.select_option("#openingSelect", "open_python_dev")
        page.wait_for_timeout(700)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_63_Demo_Dataset" / "day63_candidate_profiles_ui.png"))

        # Day 61: Monitoring UI
        page.locator("#monitoringSection").scroll_into_view_if_needed()
        page.click("#refreshMonitoringButton")
        page.wait_for_timeout(800)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_61_Monitoring" / "day61_monitoring_dashboard.png"))

        # Day 64: Walkthrough (Cross-Round & Final Recommendation)
        page.click('.tab-btn[data-tab="tab-cross-round"]')
        page.wait_for_timeout(600)
        page.select_option("#d51CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(600)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_64_Internal_Review" / "day64_cross_round_walkthrough_ui.png"))

        page.click('.tab-btn[data-tab="tab-recommendation"]')
        page.wait_for_timeout(600)
        page.select_option("#d52CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(600)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_64_Internal_Review" / "day64_final_recommendation_walkthrough_ui.png"))

        # Day 65: Polished Report UI
        page.click('.tab-btn[data-tab="tab-report"]')
        page.wait_for_timeout(600)
        page.select_option("#d53CandidateSelect", "cand_arun_kumar")
        page.wait_for_timeout(700)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_65_Feature_Polish" / "day65_polished_candidate_report_ui.png"))

        # Day 67: Demo Optimization UI
        page.click('.tab-btn[data-tab="tab-optimization"]')
        page.wait_for_timeout(600)
        page.click("#d54RunBtn")
        page.wait_for_timeout(900)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_67_Mock_Demo" / "day67_demo_optimization_ui.png"))

        # Day 70: Governance Audit Verified UI + Chrome PDF
        page.click('.tab-btn[data-tab="tab-governance"]')
        page.wait_for_timeout(600)
        page.click("#d55VerifyAuditBtn")
        page.wait_for_timeout(800)
        page.locator("#d55AuditVerifyBanner").scroll_into_view_if_needed()
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_70_Final_Demo" / "day70_governance_audit_verified_ui.png"))

        page.goto(f"{BASE_URL}/api/v1/candidates/cand_arun_kumar/hiring-intelligence-report/pdf", wait_until="load")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_70_Final_Demo" / "day70_final_demo_pdf_report.png"))

        # Day 62 & 61 Swagger Docs
        page.goto(f"{BASE_URL}/docs", wait_until="networkidle")
        page.wait_for_selector(".opblock", timeout=15000)
        page.screenshot(path=str(EVIDENCE_ROOT / "Day_62_Documentation" / "day62_swagger_documentation.png"))

        op = page.locator('.opblock.opblock-get:has([data-path="/api/v1/monitoring/dashboard"])').first
        op.scroll_into_view_if_needed()
        op.locator(".opblock-summary-control").click()
        page.wait_for_timeout(300)
        op.locator("button.try-out__btn").click()
        page.wait_for_timeout(200)
        op.locator("button.execute").click()
        op.locator(".responses-wrapper .live-responses-table").wait_for(state="visible", timeout=15000)
        page.wait_for_timeout(400)
        op.screenshot(path=str(EVIDENCE_ROOT / "Day_61_Monitoring" / "day61_swagger_monitoring_dashboard.png"))

        # Terminal Evidence
        term = context.new_page()
        _capture_terminal(term, [sys.executable, "-m", "pytest", "day61_ai_monitoring_observability/tests/", "-v"], EVIDENCE_ROOT / "Day_61_Monitoring" / "day61_monitoring_tests_terminal.png", "Day 61 Monitoring Tests")
        _capture_terminal(term, [sys.executable, "scripts/seed_days51_55_demo_data.py"], EVIDENCE_ROOT / "Day_63_Demo_Dataset" / "day63_dataset_seed_terminal.png", "Day 63 Demo Dataset Seeding")
        _capture_terminal(term, [sys.executable, "-m", "pytest", "day65_final_enhancements_feature_polish/tests/", "tests/test_ats_scoring_engine.py", "-v"], EVIDENCE_ROOT / "Day_65_Feature_Polish" / "day65_day65_tests_terminal.png", "Day 65 Feature Polish Tests")
        _capture_terminal(term, [sys.executable, "scripts/build_day66_presentation.py"], EVIDENCE_ROOT / "Day_66_Presentation" / "day66_pptx_generation_terminal.png", "Day 66 PowerPoint Generation")
        _capture_terminal(term, [sys.executable, "-m", "pytest", "tests/test_day53_day60.py", "tests/test_day51_55_comprehensive.py", "-v"], EVIDENCE_ROOT / "Day_68_Testing" / "day68_backend_test_results.png", "Day 68 Regression Verification")
        _capture_terminal(term, ["powershell", "-NoProfile", "-Command", "Get-ChildItem final_submission -Depth 1 | Select-Object Name"], EVIDENCE_ROOT / "Day_69_Submission" / "day69_final_submission_structure_terminal.png", "Day 69 Final Submission Structure")

        browser.close()
    print("Captured all Days 61-70 evidence screenshots.")


if __name__ == "__main__":
    main()
