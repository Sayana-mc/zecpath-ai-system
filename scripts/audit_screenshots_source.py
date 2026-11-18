import re

with open('scripts/regenerate_days45_50_authentic_screenshots.py', 'r') as f:
    text = f.read()

calls = list(re.finditer(r'save_shot\(page,\s*(\d+),\s*["\']([^"\']+)["\']\)', text))

for c in calls:
    day = c.group(1)
    fn = c.group(2)
    pos = c.start()
    snippet = text[max(0, pos-600):pos]
    if 'render_markdown_doc_in_browser' in snippet:
        t = 'DESIGN_DOC'
    elif 'render_terminal_in_browser' in snippet:
        t = 'HTML_TERMINAL'
    elif 'execute_swagger_op' in snippet:
        t = 'SWAGGER_EXEC'
    elif 'report/html' in snippet:
        t = 'HTML_REPORT'
    elif 'localhost:8000/' in snippet or 'cand_table' in snippet:
        t = 'WEB_UI'
    else:
        t = 'SWAGGER_VIEW'
    print(f"Day {day:2} | {fn:45} | {t}")
