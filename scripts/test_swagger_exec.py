from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 920})
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

    # Open GET /api/v1/hr-interviews
    op = page.locator(".opblock-get:has-text('/api/v1/hr-interviews')").first
    op.scroll_into_view_if_needed()
    if not op.locator(".opblock-body").is_visible():
        op.locator(".opblock-summary").click()
        page.wait_for_timeout(400)

    try_btn = op.locator("button.try-out__btn").first
    if "Cancel" not in try_btn.text_content():
        try_btn.click()
        page.wait_for_timeout(300)

    # Execute
    op.locator("button.execute").first.click()
    page.wait_for_timeout(1500)

    # Find live response elements
    print("live-responses-table count:", op.locator(".live-responses-table").count())
    print("response-col_status count:", op.locator(".live-responses-table .response-col_status").count())
    if op.locator(".live-responses-table .response-col_status").count() > 0:
        print("Status text:", op.locator(".live-responses-table .response-col_status").first.text_content())
        # Let's inspect the JSON body
        print("Body text snippet:", op.locator(".live-responses-table pre").first.text_content()[:200])

    # Scroll live response table into view
    op.locator(".live-responses-table").first.scroll_into_view_if_needed()
    page.screenshot(path="test_live_swagger_success.png")
    print("Screenshot saved to test_live_swagger_success.png")
    browser.close()
