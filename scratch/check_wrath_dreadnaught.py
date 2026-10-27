import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print('--- Tank Wrath (218) ---')
for iid in [16963, 16961, 16966, 16959, 16964, 16960, 16962, 16965]:
    it = db['by_id'].get(str(iid), {})
    sname = it.get('set', {}).get('name') if it.get('set') else 'None'
    print(f"{iid}: {it.get('name')} ({it.get('slot')}) -> set: {sname}")

print('\n--- DPS Wrath (2003) ---')
for iid in [47248, 47249, 47250, 47251, 47252, 47253, 47254, 47255]:
    it = db['by_id'].get(str(iid), {})
    sname = it.get('set', {}).get('name') if it.get('set') else 'None'
    print(f"{iid}: {it.get('name')} ({it.get('slot')}) -> set: {sname}")

print('\n--- Tank Dreadnaught (523) ---')
for iid in [22418, 22419, 22416, 22417, 22421, 22420, 22422, 22423, 23059]:
    it = db['by_id'].get(str(iid), {})
    sname = it.get('set', {}).get('name') if it.get('set') else 'None'
    print(f"{iid}: {it.get('name')} ({it.get('slot')}) -> set: {sname}")

print('\n--- DPS Dreadnaught (3002) ---')
for iid in [47261, 47262, 47263, 47264, 47265, 47266, 47267, 47268, 47269]:
    it = db['by_id'].get(str(iid), {})
    sname = it.get('set', {}).get('name') if it.get('set') else 'None'
    print(f"{iid}: {it.get('name')} ({it.get('slot')}) -> set: {sname}")
