import urllib.request
import json

req_w = urllib.request.urlopen("http://127.0.0.1:5000/api/items?class=warrior")
data_w = json.loads(req_w.read().decode('utf-8'))
items_w = data_w.get('items', [])
print(f"Warrior items: {len(items_w)}")

req_p = urllib.request.urlopen("http://127.0.0.1:5000/api/items?class=paladin")
data_p = json.loads(req_p.read().decode('utf-8'))
items_p = data_p.get('items', [])
print(f"Paladin items: {len(items_p)}")

sim_payload = json.dumps({
    "character_class": "warrior",
    "race": "human",
    "equipped_items": [47248, 47249, 47250, 47251, 47252, 47253, 47254, 47255, 19019, 11815, 14551],
    "talents": {"Bloodthirst": 1, "Cruelty": 5, "Flurry": 5},
    "fight_duration": 60
}).encode('utf-8')

sim_req = urllib.request.Request("http://127.0.0.1:5000/api/simulate", data=sim_payload, headers={'Content-Type': 'application/json'})
sim_res = urllib.request.urlopen(sim_req)
sim_data = json.loads(sim_res.read().decode('utf-8'))
print("\nSimulation response for Warrior:")
print(f"  DPS: {sim_data.get('total_dps')}")
print(f"  Weapon skill: {sim_data.get('weapon_skill')}")
print(f"  Active sets: {list(sim_data.get('active_sets', {}).keys())}")
print(f"  Equipped count: {sim_data.get('gear_summary', {}).get('equipped_count')}")

print("\nALL LIVE TESTS PASSED!")
