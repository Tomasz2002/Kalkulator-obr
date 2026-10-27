import json

with open("scratch/paladin_talents.json", "r", encoding="utf-8") as f:
    pal = json.load(f)

for t in pal["t"]:
    tree_name = pal["trees"][t["tree"]]
    print(f"[{tree_name}] {t['name']} ({t['ranks']} ranks): {t['desc']}")
