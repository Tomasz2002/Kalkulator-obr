import json

with open("scratch/paladin_talents.json", "r", encoding="utf-8") as f:
    pal = json.load(f)

print("Trees:", pal["trees"])
for tree_idx, tree_name in enumerate(pal["trees"]):
    talents = [t for t in pal["t"] if t["tree"] == tree_idx]
    print(f"\n--- Tree {tree_idx}: {tree_name} ({len(talents)} talents) ---")
    for t in sorted(talents, key=lambda x: (x["row"], x["col"])):
        req = f" [Req: {t['req']}]" if "req" in t else ""
        print(f"Row {t['row']}, Col {t['col']} (pos {t['pos']}): {t['name']} ({t['ranks']} ranks, icon: {t['icon']}){req}")

with open("scratch/builds.json", "r", encoding="utf-8") as f:
    builds = json.load(f)

print("\n--- PALADIN BUILDS ---")
for b in builds:
    print(f"Build: {b.get('nazwa')} ({b.get('typ')}) - icon: {b.get('ikona')} - points: {b.get('punkty')}")
