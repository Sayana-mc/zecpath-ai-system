from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 900})
    page.on("console", lambda msg: print("CONSOLE:", msg.text))
    page.on("pageerror", lambda err: print("PAGEERROR:", err))

    page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
    page.fill("#authUsername", "recruiter-d41-52")
    page.fill("#authPassword", "Password123!LongEnough")
    page.click("#loginForm button[type=submit]")
    page.wait_for_timeout(2000)
    
    # Locate row for C001
    c001_row = page.locator("#candidateRows tr:has-text('Candidate C001')")
    screening_details = c001_row.locator("details:has(summary:has-text('Screening report'))")
    print("Found screening details:", screening_details.count())
    
    # Open details
    screening_details.evaluate("el => el.open = true")
    screening_details.evaluate("el => el.dispatchEvent(new Event('toggle'))")
    page.wait_for_timeout(2000)
    
    # Check inner HTML of screening_details
    html = screening_details.inner_html()
    print("Screening details length:", len(html))
    if "AI Screening Report" in html:
        print("[SUCCESS] AI Screening Report rendered inside details!")
    else:
        print("Details HTML snippet:", html[:300])

    browser.close()
