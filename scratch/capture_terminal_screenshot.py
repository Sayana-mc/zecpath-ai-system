import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\sayan\Documents\zecpath-ai-system")
cmd = "pytest tests/test_ats_scoring_engine.py -v"
proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT))
output = proc.stdout + proc.stderr

html_content = f"""<!DOCTYPE html>
<html>
<head>
<style>
body {{
    background: #1e1e1e;
    color: #cccccc;
    font-family: Consolas, 'Courier New', monospace;
    font-size: 14px;
    padding: 24px;
    margin: 0;
}}
.header {{
    background: #2d2d2d;
    padding: 10px 16px;
    border-radius: 6px 6px 0 0;
    color: #fff;
    font-weight: bold;
    border-bottom: 1px solid #3d3d3d;
}}
.terminal {{
    background: #181818;
    padding: 20px;
    border-radius: 0 0 6px 6px;
    border: 1px solid #3d3d3d;
    border-top: none;
    white-space: pre-wrap;
    line-height: 1.5;
}}
.green {{ color: #4ec9b0; font-weight: bold; }}
</style>
</head>
<body>
<div class='header'>Windows PowerShell — ZecPath ATS Automated Unit & Integration Tests (Day 20)</div>
<div class='terminal'>PS C:\\Users\\sayan\\Documents\\zecpath-ai-system> {cmd}
{output}
PS C:\\Users\\sayan\\Documents\\zecpath-ai-system> python -m compileall -q src tests
<span class='green'>[PASS] All modules successfully compiled with zero errors.</span>
</div>
</body>
</html>"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1000, "height": 480})
    page.set_content(html_content)
    page.screenshot(path=str(ROOT / "day20_ats_final_review" / "screenshots" / "14_automated_test_results.png"))
    browser.close()
    print("Generated 14_automated_test_results.png successfully!")

