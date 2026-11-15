from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")
    page.click(".btn.authorize")
    page.wait_for_selector(".modal-ux")
    page.fill(".modal-ux input[type=text]", "recruiter-d41-52")
    page.fill(".modal-ux input[type=password]", "Password123!LongEnough")
    page.click(".modal-ux button.auth.authorize")
    page.click(".modal-ux button.btn-done")
    print("Authorized successfully!")

    # Now let's find Screening Questions and execute GET /api/v1/screening/questions
    print("Tags present:")
    for el in page.query_selector_all(".opblock-tag"):
        print(" -", el.inner_text().split("\n")[0])
    browser.close()

