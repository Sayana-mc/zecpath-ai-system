"""Playwright verification for Phase 2 (Browser Login/Logout/Protected Routes) & Phase 4 (E2E Demo)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "screenshots" / "login_verification"
BASE_URL = "http://127.0.0.1:8000"


def _clear_login_attempts() -> None:
    db_path = ROOT / "data" / "zecpath.sqlite3"
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM recruiter_login_attempts")
        conn.commit()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _clear_login_attempts()

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Login page (unauthenticated)
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_selector("#loginForm", state="visible", timeout=10000)
        page.screenshot(path=str(OUT_DIR / "01_login_page.png"))

        # 2. Invalid login rejected
        page.fill("#authUsername", "recruiter-d41-52")
        page.fill("#authPassword", "WrongPassword123!")
        page.click('#loginForm button[type="submit"]')
        page.wait_for_timeout(900)
        err_text = page.locator("#notice").inner_text()
        assert "Valid recruiter credentials are required" in err_text or "Too many" in err_text, err_text
        page.screenshot(path=str(OUT_DIR / "02_invalid_login_error.png"))

        # Clear attempts so valid login stays clean
        _clear_login_attempts()

        # 3. Valid login -> Recruiter dashboard
        page.fill("#authUsername", "recruiter-d41-52")
        page.fill("#authPassword", "Password123!LongEnough")
        page.click('#loginForm button[type="submit"]')
        page.wait_for_selector("#workspace", state="visible", timeout=15000)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT_DIR / "03_successful_login_dashboard.png"))

        # 4. E2E ATS & Eligibility view in dashboard
        page.select_option("#openingSelect", "open_python_dev")
        page.wait_for_timeout(800)
        page.locator("#candidateTable").scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT_DIR / "04_e2e_ats_and_candidates_table.png"))

        # 5. Logout & Protected route verification (401 after logout)
        page.evaluate("window.scrollTo(0, 0)")
        page.click("#signOutButton")
        page.wait_for_selector("#loginForm", state="visible", timeout=10000)
        protected_status = page.evaluate("""async () => {
            const r = await fetch('/api/v1/openings');
            return r.status;
        }""")
        assert protected_status == 401, f"Expected 401 after logout, got {protected_status}"
        page.screenshot(path=str(OUT_DIR / "05_logout_and_protected_route_401.png"))

        browser.close()

    _clear_login_attempts()
    print(f"Login & E2E verification passed; protected route post-logout HTTP={protected_status}")


if __name__ == "__main__":
    main()
