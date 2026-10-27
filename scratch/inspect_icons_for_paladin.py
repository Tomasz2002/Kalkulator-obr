import json

with open('data/item_icons.json', 'r', encoding='utf-8') as f:
    icons = json.load(f)

pal_icons = {}
for iid, icon in icons.items():
    if any(k in icon.lower() for k in ['law', 'judg', 'redemp']):
        pal_icons[int(iid)] = icon

print(f"Total matching paladin icons in item_icons.json: {len(pal_icons)}")
for iid in sorted(pal_icons.keys()):
    print(f"{iid}: {pal_icons[iid]}")
