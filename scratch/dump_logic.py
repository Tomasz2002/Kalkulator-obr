with open(r"C:\Users\Tomas\.gemini\antigravity-ide\brain\52fdd071-d17b-4c15-a127-03cf4f3c6584\.system_generated\steps\1177\content.md", "r", encoding="utf-8") as f:
    text = f.read()

import re
m = re.search(r"<script>(.*?)</script>", text, re.DOTALL)
if m:
    script = m.group(1)
    dane_idx = script.find("const DANE =")
    buildy_idx = script.find("const BUILDY =")
    after_buildy = script.find("let klasa =")
    print("Found script logic from index:", after_buildy)
    with open("scratch/octowow_script_logic.js", "w", encoding="utf-8") as out:
        out.write(script[after_buildy:])
