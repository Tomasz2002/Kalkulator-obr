import json

with open('data/item_icons.json', 'r', encoding='utf-8') as f:
    icons = json.load(f)

for iid_str, icon in sorted(icons.items(), key=lambda x: int(x[0])):
    iid = int(iid_str)
    if (47000 <= iid <= 47300) or (70500 <= iid <= 70600):
        print(f"{iid}: {icon}")
