import json
import re

with open(r"C:\Users\Tomas\.gemini\antigravity-ide\brain\52fdd071-d17b-4c15-a127-03cf4f3c6584\.system_generated\steps\1177\content.md", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r"const DANE = ({.*?});\s*const", text, re.DOTALL)
if not m:
    m = re.search(r"const DANE = ({.*?});", text, re.DOTALL)

if m:
    dane_str = m.group(1)
    dane = json.loads(dane_str)
    paladin = dane.get("paladin")
    with open("scratch/paladin_talents.json", "w", encoding="utf-8") as out:
        json.dump(paladin, out, indent=2, ensure_ascii=False)
    print("Paladin trees:", paladin.get("trees"))
    print("Total talents:", len(paladin.get("t", [])))
    print("Builds:", list(paladin.get("builds", {}).keys()) if "builds" in paladin else "No builds in obj")
else:
    print("DANE regex not matched")

m2 = re.search(r"const BUILDY = ({.*?});", text, re.DOTALL)
if m2:
    buildy = json.loads(m2.group(1))
    print("BUILDY keys:", list(buildy.keys()))
    with open("scratch/builds.json", "w", encoding="utf-8") as out:
        json.dump(buildy.get("paladin", {}), out, indent=2, ensure_ascii=False)
