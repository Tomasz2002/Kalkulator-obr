with open(r"C:\Users\Tomas\.gemini\antigravity-ide\brain\52fdd071-d17b-4c15-a127-03cf4f3c6584\.system_generated\steps\1177\content.md", "r", encoding="utf-8") as f:
    text = f.read()

import re
for m in re.finditer(r"backgroundImage", text):
    start = max(0, m.start() - 50)
    end = min(len(text), m.end() + 150)
    print("MATCH:", text[start:end])
