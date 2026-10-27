import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print('--- Tank Might (209) ---')
for iid in [16866, 16868, 16865, 16861, 16863, 16864, 16867, 16862]:
    it = db['by_id'].get(str(iid), {})
    sname = it.get('set', {}).get('name') if it.get('set') else 'None'
    print(f"{iid}: {it.get('name')} ({it.get('slot')}) -> set: {sname}")

print('\n--- DPS Might (1003) ---')
for iid in [47240, 47241, 47242, 47243, 47244, 47245, 47246, 47247]:
    it = db['by_id'].get(str(iid), {})
    sname = it.get('set', {}).get('name') if it.get('set') else 'None'
    print(f"{iid}: {it.get('name')} ({it.get('slot')}) -> set: {sname}")
