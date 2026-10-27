with open(r"C:\Users\Tomas\.gemini\antigravity-ide\brain\52fdd071-d17b-4c15-a127-03cf4f3c6584\.system_generated\steps\1177\content.md", "r", encoding="utf-8") as f:
    text = f.read()

import re
print("Found 'arrow'?", "arrow" in text.lower())
print("Found 'strzalka'?", "strzalka" in text.lower())
print("Found 'wymag'?", "wymag" in text.lower())

for m in re.finditer(r"function\s+odblokowany\b|function\s+klik\b|function\s+odklik\b|function\s+rysuj\b", text):
    start = m.start()
    end = min(len(text), start + 800)
    print("FUNC:", text[start:end])
