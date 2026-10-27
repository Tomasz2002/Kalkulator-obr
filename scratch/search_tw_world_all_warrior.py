import zipfile
import json

warrior_set_ids = [209, 1003, 218, 2003, 523, 3002, 189, 511, 496]

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

all_warrior_item_ids = set()
for sid in warrior_set_ids:
    s = octo_sets.get(str(sid))
    if s and 'pieces' in s:
        all_warrior_item_ids.update(s['pieces'])

print(f"Checking {len(all_warrior_item_ids)} items in tw_world.sql...")

found_sql = {}

with zipfile.ZipFile('turtle-core-patch_1171/sql/world_1171_release.zip', 'r') as z:
    with z.open('tw_world.sql') as f:
        for line in f:
            if b"INSERT INTO `item_template`" in line:
                for item_id in all_warrior_item_ids:
                    prefix = f"({item_id},".encode('ascii')
                    if prefix in line:
                        found_sql[item_id] = line.decode('utf-8', errors='ignore')

print(f"Found in tw_world.sql: {len(found_sql)} out of {len(all_warrior_item_ids)}")
missing = sorted(list(all_warrior_item_ids - set(found_sql.keys())))
print(f"Missing from tw_world.sql: {missing}")
for k, v in list(found_sql.items())[:5]:
    print(f"Item {k}: {v[:120]}")
