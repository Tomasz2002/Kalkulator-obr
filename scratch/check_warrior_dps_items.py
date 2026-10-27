import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

by_id = db['by_id']
check_ids = list(range(47240, 47256)) + list(range(47261, 47270))

for cid in check_ids:
    it = by_id.get(str(cid))
    if not it:
        print(f"ID {cid}: MISSING from items_db.json")
    else:
        print(f"ID {cid}: {it['name']} | Str:{it.get('strength')} Agi:{it.get('agility')} Sta:{it.get('stamina')} AP:{it.get('attack_power')} Hit:{it.get('hit')} Crit:{it.get('crit')} Armor:{it.get('armor')}")
        if it.get('spells'):
            print(f"   spells: {it['spells']}")
