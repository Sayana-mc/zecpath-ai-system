with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [l.strip() for l in text.splitlines() if any(k in l.lower() for k in ['monitor', 'audit', 'review', 'flag', 'integrity'])]
for m in matches[:30]:
    print(m)
