import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

by_id = db['by_id']
tank_sets = {
    "Might Tank (209)": [16864, 16861, 16865, 16863, 16866, 16867, 16868, 16862],
    "Wrath Tank (218)": [16959, 16966, 16964, 16963, 16962, 16961, 16965, 16960],
    "Dread Tank (523)": [22423, 22416, 22421, 22422, 22418, 22417, 22419, 22420, 23059]
}

for sname, pieces in tank_sets.items():
    print(f"\n=== {sname} ===")
    for pid in pieces:
        it = by_id.get(str(pid))
        if not it:
            print(f"  ID {pid}: MISSING")
        else:
            print(f"  ID {pid}: {it['name']} | Str:{it.get('strength')} Agi:{it.get('agility')} Sta:{it.get('stamina')} Hit:{it.get('hit')} Crit:{it.get('crit')} Armor:{it.get('armor')}")
