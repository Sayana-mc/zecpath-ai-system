import json
import requests
from playwright.sync_api import sync_playwright

AUTH = ("recruiter-d41-52", "Password123!LongEnough")
BASE = "http://127.0.0.1:8000"

# First, create a real interview in the backend via requests so we have a 100% valid session
res = requests.post(
    f"{BASE}/api/v1/hr-interviews",
    auth=AUTH,
    json={
        "candidate_id": "cand_arun_kumar",
        "opening_id": "job_python_lead",
        "experience_level": "EXPERIENCED",
        "role_type": "TECHNICAL",
        "recruiter_id": "recruiter-d41-52"
    }
)
print("Create interview status:", res.status_code)
created_data = res.json()
print("Created interview data:", created_data)
interview_id = created_data.get("interview_id")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 920})
    page.goto(f"{BASE}/docs", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    # Authorize
    auth_btn = page.locator("button.authorize").first
    if auth_btn.is_visible():
        auth_btn.click()
        page.wait_for_timeout(300)
        page.locator("input[name='username']").first.fill("recruiter-d41-52")
        page.locator("input[name='password']").first.fill("Password123!LongEnough")
        page.locator(".auth-btn-wrapper button.modal-btn.auth").first.click()
        page.wait_for_timeout(300)
        page.locator("button.btn-done").first.click()
        page.wait_for_timeout(300)

    # Now open GET /api/v1/hr-interviews/{interview_id}/questions
    op = page.locator(".opblock-get:has-text('/api/v1/hr-interviews/{interview_id}/questions')").first
    op.scroll_into_view_if_needed()
    if not op.locator(".opblock-body").is_visible():
        op.locator(".opblock-summary").click()
        page.wait_for_timeout(400)

    try_btn = op.locator("button.try-out__btn").first
    if "Cancel" not in try_btn.text_content():
        try_btn.click()
        page.wait_for_timeout(300)

    # Find the input for interview_id
    inp = op.locator("input[placeholder='interview_id']").first
    print("Found input count:", inp.count())
    inp.fill("")
    inp.fill(interview_id)
    page.wait_for_timeout(300)

    # Click execute
    exec_btn = op.locator("button.execute").first
    exec_btn.click()
    page.wait_for_timeout(1500)

    # Let's inspect what is in the live response
    live_resp = op.locator(".live-responses-table").first
    print("Live resp visible:", live_resp.is_visible())
    if live_resp.is_visible():
        print("Live resp text snippet:\n", live_resp.text_content()[:300])

    # Take screenshot of the actual server response
    live_resp.scroll_into_view_if_needed()
    page.screenshot(path="test_live_swagger.png")
    print("Saved test_live_swagger.png")

    browser.close()
