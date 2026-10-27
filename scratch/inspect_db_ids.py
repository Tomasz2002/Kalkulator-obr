import json

with open("items_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

items = db.get("items", [])
print("Total items in items_db.json:", len(items))

ids_by_slot = {}
for it in items:
    s = it["slot"]
    ids_by_slot.setdefault(s, []).append(it["id"])

for s, ids in sorted(ids_by_slot.items()):
    print(f"Slot {s}: {len(ids)} items")
