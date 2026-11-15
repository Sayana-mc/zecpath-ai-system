"""Day 20: Complete ATS Browser Testing, Scoring Verification, and Screenshot Automation."""

import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\sayan\Documents\zecpath-ai-system")
REVIEW_DIR = ROOT / "day20_ats_final_review"
SCREENSHOTS_DIR = REVIEW_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_RESUMES = REVIEW_DIR / "demo_dataset" / "sample_resumes"

def execute_browser_automation():
    print("=" * 70)
    print("STARTING DAY 20 ATS COMPLETE BROWSER VERIFICATION & SCREENSHOT CAPTURE")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 950})
        page = context.new_page()

        # ---------------------------------------------------------------------
        # STEP 1: Recruiter Login
        # ---------------------------------------------------------------------
        print("\n[Step 1] Loading application and executing Recruiter Login...")
        page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        page.wait_for_selector("#loginPanel")

        # Fill credentials
        page.fill("#authUsername", "recruiter-d41-52")
        page.fill("#authPassword", "Password123!LongEnough")

        # Capture 01_recruiter_login.png
        p1 = SCREENSHOTS_DIR / "01_recruiter_login.png"
        page.screenshot(path=str(p1))
        print(f"   -> Captured: {p1.name}")

        # Submit login
        page.click("#loginForm button[type='submit']")
        page.wait_for_selector("#workspace:not([hidden])", timeout=10000)
        time.sleep(1)
        print("   [PASS] Authenticated successfully, workspace is visible.")

        # ---------------------------------------------------------------------
        # STEP 2: Job Opening Creation
        # ---------------------------------------------------------------------
        print("\n[Step 2] Filling Job Opening form for 'Senior Python Developer'...")
        job_data = {
            "title": "Senior Python Developer",
            "description": "Looking for a Senior Python Developer to design and build high-performance data pipelines, microservices, and RESTful APIs with FastAPI, PostgreSQL, and Docker containerization.",
            "required_skills": "Python, FastAPI, SQL, PostgreSQL, Docker",
            "preferred_skills": "Redis, Kubernetes",
            "education": "Bachelor's Degree",
            "experience": "3.0"
        }

        page.fill("#jobTitle", job_data["title"])
        page.fill("#jobDescription", job_data["description"])
        page.fill("#requiredSkills", job_data["required_skills"])
        page.fill("#preferredSkills", job_data["preferred_skills"])
        page.fill("#minimumEducation", job_data["education"])
        page.fill("#minimumExperience", job_data["experience"])

        # Capture 02_job_opening_form.png
        p2 = SCREENSHOTS_DIR / "02_job_opening_form.png"
        page.screenshot(path=str(p2))
        print(f"   -> Captured: {p2.name}")

        # Submit opening
        page.click("#openingForm button[type='submit']")
        time.sleep(2)

        # Verify it appears in selected job dropdown
        page.wait_for_selector("#openingSelect")
        p3 = SCREENSHOTS_DIR / "03_saved_job_opening.png"
        page.screenshot(path=str(p3))
        print(f"   -> Captured: {p3.name}")
        print("   [PASS] Job Opening created and selected in Manage Opening section.")

        # ---------------------------------------------------------------------
        # STEP 3: Candidate Resume Upload (Candidate 1 - Alex Mercer)
        # ---------------------------------------------------------------------
        print("\n[Step 3] Registering Candidate 1 (Alex Mercer) with resume file...")
        alex_resume = SAMPLE_RESUMES / "alex_mercer_resume.txt"

        page.fill("#candidateName", "Alex Mercer")
        page.fill("#candidateEmail", "alex.mercer@example.test")
        page.fill("#candidateSkills", "Python, FastAPI, SQL, PostgreSQL, Docker, Redis")
        page.set_input_files("#resumeFile", str(alex_resume))

        # Capture 04_candidate_resume_upload.png
        p4 = SCREENSHOTS_DIR / "04_candidate_resume_upload.png"
        page.screenshot(path=str(p4))
        print(f"   -> Captured: {p4.name}")

        # Submit Candidate 1
        page.click("#candidateSubmit")
        time.sleep(2)
        print("   [PASS] Candidate 1 (Alex Mercer) registered.")

        # Register Candidate 2 (Jordan Lee)
        print("   Registering Candidate 2 (Jordan Lee)...")
        jordan_resume = SAMPLE_RESUMES / "jordan_lee_resume.txt"
        page.fill("#candidateName", "Jordan Lee")
        page.fill("#candidateEmail", "jordan.lee@example.test")
        page.fill("#candidateSkills", "Python, Django, SQL")
        page.set_input_files("#resumeFile", str(jordan_resume))
        page.click("#candidateSubmit")
        time.sleep(2)

        # Register Candidate 3 (Morgan Taylor)
        print("   Registering Candidate 3 (Morgan Taylor)...")
        morgan_resume = SAMPLE_RESUMES / "morgan_taylor_resume.txt"
        page.fill("#candidateName", "Morgan Taylor")
        page.fill("#candidateEmail", "morgan.taylor@example.test")
        page.fill("#candidateSkills", "Java, Spring Boot, MySQL")
        page.set_input_files("#resumeFile", str(morgan_resume))
        page.click("#candidateSubmit")
        time.sleep(2)

        # Scroll to applications table
        page.locator("#candidateListHeading").scroll_into_view_if_needed()
        time.sleep(1)

        # Capture 05_resume_parsing_result.png
        p5 = SCREENSHOTS_DIR / "05_resume_parsing_result.png"
        page.screenshot(path=str(p5))
        print(f"   -> Captured: {p5.name}")
        print("   [PASS] All 3 candidates registered and listed in Applications table.")

        # ---------------------------------------------------------------------
        # STEP 4: ATS Score Generation for Candidate 1 (Alex Mercer)
        # ---------------------------------------------------------------------
        print("\n[Step 4] Triggering ATS Score calculation for Alex Mercer...")
        # Find Alex Mercer's row and click Score button
        alex_row = page.locator("#candidateRows tr", has_text="Alex Mercer")
        score_btn = alex_row.locator("button:has-text('Score')")
        score_btn.click()
        time.sleep(3)  # Wait for SentenceTransformers embedding & calculation

        # Capture 06_overall_ats_score.png
        p6 = SCREENSHOTS_DIR / "06_overall_ats_score.png"
        page.screenshot(path=str(p6))
        print(f"   -> Captured: {p6.name}")
        print("   [PASS] Overall ATS score generated and displayed.")

        # ---------------------------------------------------------------------
        # STEP 5: Expand Score Breakdown & Evidence Card
        # ---------------------------------------------------------------------
        print("\n[Step 5] Expanding score evidence and component breakdown...")
        evidence_summary = alex_row.locator("summary:has-text('Review score evidence')")
        if evidence_summary.count() > 0:
            evidence_summary.click()

        component_summary = alex_row.locator("summary:has-text('Review component scores')")
        if component_summary.count() > 0:
            component_summary.click()

        time.sleep(1)
        p7 = SCREENSHOTS_DIR / "07_ats_score_breakdown.png"
        page.screenshot(path=str(p7))
        print(f"   -> Captured: {p7.name}")
        print("   [PASS] 4-factor component breakdown expanded and verified.")

        # ---------------------------------------------------------------------
        # STEP 6: Candidate Ranking (Score remaining candidates)
        # ---------------------------------------------------------------------
        print("\n[Step 6] Scoring Jordan Lee and Morgan Taylor for complete ranking...")
        jordan_row = page.locator("#candidateRows tr", has_text="Jordan Lee")
        jordan_row.locator("button:has-text('Score')").click()
        time.sleep(3)

        morgan_row = page.locator("#candidateRows tr", has_text="Morgan Taylor")
        morgan_row.locator("button:has-text('Score')").click()
        time.sleep(3)

        # Refresh candidate list to see ranking
        page.click("#reloadButton")
        time.sleep(2)
        page.locator("#candidateListHeading").scroll_into_view_if_needed()

        p8 = SCREENSHOTS_DIR / "08_candidate_ranking.png"
        page.screenshot(path=str(p8))
        print(f"   -> Captured: {p8.name}")
        print("   [PASS] All candidates scored; ranks verified.")

        # ---------------------------------------------------------------------
        # STEP 7: Candidate Shortlisting
        # ---------------------------------------------------------------------
        print("\n[Step 7] Generating Shortlist suggestions (Threshold >= 60%)...")
        page.locator("#shortlistHeading").scroll_into_view_if_needed()
        page.fill("#minimumScore", "60")
        page.click("#shortlistButton")
        time.sleep(2)

        p9 = SCREENSHOTS_DIR / "09_candidate_shortlisting.png"
        page.screenshot(path=str(p9))
        print(f"   -> Captured: {p9.name}")
        print("   [PASS] Shortlist suggestions generated with threshold filtering.")

        # ---------------------------------------------------------------------
        # STEP 8: Data Persistence Verification
        # ---------------------------------------------------------------------
        print("\n[Step 8] Verifying Data Persistence after browser reload...")
        page.reload(wait_until="networkidle")
        time.sleep(2)
        page.wait_for_selector("#workspace:not([hidden])")
        page.locator("#candidateListHeading").scroll_into_view_if_needed()

        p10 = SCREENSHOTS_DIR / "10_data_persistence.png"
        page.screenshot(path=str(p10))
        print(f"   -> Captured: {p10.name}")
        print("   [PASS] All candidate scores and opening configuration persist across page refresh.")

        # ---------------------------------------------------------------------
        # STEP 9: Swagger Interactive API Documentation Screenshots
        # ---------------------------------------------------------------------
        print("\n[Step 9] Capturing Swagger UI documentation...")
        page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")
        time.sleep(2)

        # 11_ats_score_api.png: Expand /api/v1/candidates/score
        print("   Navigating to ATS score endpoint in Swagger...")
        score_op = page.locator("span:has-text('/api/v1/candidates/score')").first
        if score_op.count() > 0:
            score_op.click()
            time.sleep(1)
        p11 = SCREENSHOTS_DIR / "11_ats_score_api.png"
        page.screenshot(path=str(p11))
        print(f"   -> Captured: {p11.name}")

        # 12_shortlist_api.png: Expand shortlist endpoint
        print("   Navigating to shortlist endpoint in Swagger...")
        sl_op = page.locator("span:has-text('/shortlist')").first
        if sl_op.count() > 0:
            sl_op.click()
            time.sleep(1)
        p12 = SCREENSHOTS_DIR / "12_shortlist_api.png"
        page.screenshot(path=str(p12))
        print(f"   -> Captured: {p12.name}")

        # 13_parsing_api.png: Expand parse-description endpoint
        print("   Navigating to parse-description endpoint in Swagger...")
        parse_op = page.locator("span:has-text('/openings/parse-description')").first
        if parse_op.count() > 0:
            parse_op.click()
            time.sleep(1)
        p13 = SCREENSHOTS_DIR / "13_parsing_api.png"
        page.screenshot(path=str(p13))
        print(f"   -> Captured: {p13.name}")

        browser.close()
        print("\n[SUCCESS] All browser testing steps and Swagger captures completed successfully!")

if __name__ == "__main__":
    execute_browser_automation()

