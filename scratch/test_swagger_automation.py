import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 950})
    page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")
    print("Swagger UI Title:", page.title())

    # Find auth endpoint
    auth_op = page.locator(".opblock").filter(has_text="/api/v1/auth/session").filter(has_text="POST").first
    auth_op.locator(".opblock-summary").click()
    page.wait_for_timeout(600)

    # Click Try it out
    auth_op.locator("button.try-out__btn").click()
    page.wait_for_timeout(600)

    # Fill JSON
    login_payload = json.dumps({"username": "recruiter-d41-52", "password": "Password123!LongEnough"})
    auth_op.locator("textarea.body-param__text").fill(login_payload)

    # Click Execute
    auth_op.locator("button.execute").click()
    page.wait_for_timeout(2000)

    status = auth_op.locator(".response-col_status").first.text_content()
    resp_el = auth_op.locator(".response-col_description pre.microlight")
    resp_text = resp_el.first.text_content() if resp_el.count() > 0 else ""
    print("Executed Login via Swagger! Status:", status.strip())
    print("Response Body:", resp_text.strip()[:100])

    browser.close()

