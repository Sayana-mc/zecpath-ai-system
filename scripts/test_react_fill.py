from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    context = browser.new_context(
        viewport={"width": 1366, "height": 920},
        http_credentials={"username": "recruiter-d41-52", "password": "Password123!LongEnough"}
    )
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/docs", timeout=15000)
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

    op = page.locator(".opblock-get:has-text('/api/v1/hr-interviews/{interview_id}/questions')").first
    op.scroll_into_view_if_needed()
    if not op.locator(".opblock-body").is_visible():
        op.locator(".opblock-summary").click()
        page.wait_for_timeout(300)

    try_btn = op.locator("button.try-out__btn").first
    if "Cancel" not in (try_btn.text_content() or ""):
        try_btn.click()
        page.wait_for_timeout(300)

    # Query active hr interview from backend API directly
    import requests
    hr_list = requests.get("http://127.0.0.1:8000/api/v1/hr-interviews", auth=("recruiter-d41-52", "Password123!LongEnough")).json()
    interview_id = hr_list[0]["interview_id"]
    print("Using real interview_id:", interview_id)

    inp = op.locator("input[placeholder='interview_id']").first
    inp.click()
    inp.fill(interview_id)
    page.wait_for_timeout(300)

    # Execute
    op.locator("button.execute").first.click()
    page.wait_for_timeout(1500)

    # Check live response
    live_resp = op.locator(".live-responses-table").first
    print("Live table visible:", live_resp.is_visible())
    if live_resp.is_visible():
        print("Status code text:", live_resp.locator(".response-col_status").first.text_content())
        live_resp.scroll_into_view_if_needed()
        page.screenshot(path="day45_04_verified_live.png")
        print("Saved day45_04_verified_live.png successfully!")

    browser.close()
