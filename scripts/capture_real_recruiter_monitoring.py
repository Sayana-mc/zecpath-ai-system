from playwright.sync_api import sync_playwright
import shutil

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 920})
    page.goto("http://127.0.0.1:8000/", timeout=15000)
    page.wait_for_timeout(500)

    # Sign in
    page.locator("#loginUsername").fill("recruiter-d41-52")
    page.locator("#loginPassword").fill("Password123!LongEnough")
    page.locator("#loginButton, button[type='submit']:has-text('Sign in'), button:has-text('Sign in')").first.click()
    page.wait_for_timeout(1000)

    # Select opening
    op_sel = page.locator("#manageOpeningSelect, #openingSelect").first
    if op_sel.is_visible():
        op_sel.evaluate("(el, id) => { el.value = id; el.dispatchEvent(new Event('change', { bubbles: true })); }", "job_python_lead")
        page.wait_for_timeout(800)

    # Click refresh monitoring button
    ref_btn = page.locator("#refreshMonitoringButton").first
    if ref_btn.is_visible():
        ref_btn.click()
        page.wait_for_timeout(500)

    # Scroll to monitoring & decision audit section
    mon_sec = page.locator("#monitoringSection").first
    if mon_sec.is_visible():
        mon_sec.scroll_into_view_if_needed()
    else:
        page.evaluate("window.scrollTo(0, 600)")
    page.wait_for_timeout(400)

    target_path = "day49_integrity_detection/screenshots/07_recruiter_review_interface.png"
    mirror_path = "day49_malpractice_integrity_detection/screenshots/07_recruiter_review_interface.png"
    page.screenshot(path=target_path)
    shutil.copy2(target_path, mirror_path)
    print(f"Captured genuine recruiter review interface to {target_path} and {mirror_path}!")
    browser.close()
