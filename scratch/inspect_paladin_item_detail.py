import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for target_id in [47008, 47024, 47016, 47001, 47002, 47003, 47004, 47005, 47006, 47007, 47022]:
    it = db['by_id'].get(str(target_id))
    if it:
        print(f"\nItem {it['id']}: {it['name']} ({it.get('slot')})")
        print(f"  Armor: {it.get('armor')}, Str: {it.get('strength')}, Agi: {it.get('agility')}, Sta: {it.get('stamina')}, Int: {it.get('intellect')}, Spi: {it.get('spirit')}")
        print(f"  Spells: {it.get('spells')}")
        print(f"  Set_id: {it.get('set_id')}, Set: {it.get('set')}")
