from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    try:
        page.goto("http://127.0.0.1:8000/docs", timeout=10000)
        print("Success, title:", page.title())
    except Exception as e:
        print("Error:", e)
    browser.close()
