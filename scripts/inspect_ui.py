with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section\s+id=[\'"]([^\'"]+)[\'"]', text)
print("Sections:", sections)

buttons = re.findall(r'<button\s+id=[\'"]([^\'"]+)[\'"]', text)
print("Buttons:", buttons)
