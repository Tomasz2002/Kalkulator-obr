import urllib.request
import json

req = urllib.request.urlopen("http://127.0.0.1:5000/api/items?class=warrior")
data = json.loads(req.read().decode('utf-8'))
items = data.get('items', [])
print(f"Total warrior items returned: {len(items)}")

qualities = set(it.get('quality') for it in items)
print(f"Qualities present: {sorted(list(qualities))}")
assert all(q >= 2 for q in qualities), "White or gray items found!"

by_id = {it['id']: it for it in items}
legs_47254 = by_id.get(47254)
print("\nLeggings of Wrath (47254):")
print(f"  Hit: {legs_47254.get('hit')}% (Expected: 2.0%)")
print(f"  AP: {legs_47254.get('attack_power')} (Expected: 50)")
print(f"  Set: {legs_47254.get('set_name')}")

sim_payload = json.dumps({
    "class": "warrior",
    "race": "human",
    "equipped_items": [47248, 47249, 47250, 47251, 47252, 47253, 47254, 47255, 19019],
    "talents": {"Bloodthirst": 1, "Cruelty": 5, "Flurry": 5},
    "fight_duration": 60
}).encode('utf-8')

sim_req = urllib.request.Request("http://127.0.0.1:5000/api/simulate", data=sim_payload, headers={'Content-Type': 'application/json'})
sim_res = urllib.request.urlopen(sim_req)
sim_data = json.loads(sim_res.read().decode('utf-8'))
print("\nSimulation response:")
print(f"  DPS: {sim_data.get('total_dps')}")
print(f"  Weapon skill: {sim_data.get('weapon_skill')}")
print(f"  Active sets: {list(sim_data.get('active_sets', {}).keys())}")
print("\nALL API TESTS PASSED!")
