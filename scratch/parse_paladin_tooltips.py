import json
import re

with open('scratch/paladin_custom_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

for iid_str, item in raw_data.items():
    tt = item.get('tooltip', '')
    sets = re.findall(r'<span class="q">\((\d+)\) Set: (.*?)</span>', tt)
    if sets:
        print(f"Set bonuses found in item {iid_str} ({item.get('name')}): {sets}")
        break

for sample_id in ['47000', '47008', '47016', '47024', '70571', '70580']:
    it = raw_data.get(sample_id, {})
    tt = it.get('tooltip', '')
    print(f"\n--- Tooltip for {sample_id} ({it.get('name')}) ---")
    clean = re.sub(r'<[^>]+>', '\n', tt)
    lines = [l.strip() for l in clean.splitlines() if l.strip()]
    print('\n'.join(lines[:25]))
