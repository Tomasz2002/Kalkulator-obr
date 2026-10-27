with open(r"C:\Users\Tomas\.gemini\antigravity-ide\brain\52fdd071-d17b-4c15-a127-03cf4f3c6584\.system_generated\steps\1177\content.md", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r"backgroundImage\s*=\s*['\"][^'\"]+['\"]|\.src\s*=\s*['\"][^'\"]+['\"]|url\([^)]+\)", text)
for m in matches[:20]:
    print(m)

icon_matches = re.findall(r"[^'\"]*icon[^'\"]*\.(?:jpg|png)", text, re.IGNORECASE)
for m in icon_matches[:20]:
    print("icon:", m)
