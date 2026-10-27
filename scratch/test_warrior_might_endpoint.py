import urllib.request
import json

sim_payload = json.dumps({
    "character_class": "warrior",
    "race": "human",
    "equipped_items": [47240, 47241, 47242, 47243, 47244, 47245, 47246, 47247, 19019],
    "talents": {"Bloodthirst": 1, "Cruelty": 5, "Flurry": 5},
    "fight_duration": 60
}).encode('utf-8')

sim_req = urllib.request.Request("http://127.0.0.1:5000/api/simulate", data=sim_payload, headers={'Content-Type': 'application/json'})
sim_res = urllib.request.urlopen(sim_req)
sim_data = json.loads(sim_res.read().decode('utf-8'))
print("Simulation response for Warrior with Armor of Might:")
print(f"  Class: {sim_data.get('character_class')}")
print(f"  DPS: {sim_data.get('total_dps')}")
print(f"  Crit%: {sim_data.get('total_crit_percent')}%")
print(f"  Hit%: {sim_data.get('total_hit_percent')}%")
print(f"  Active sets: {list(sim_data.get('active_sets', {}).keys())}")
for sid, s in sim_data.get('active_sets', {}).items():
    print(f"    Set {sid}: {s.get('name')} ({s.get('equipped_count')}/{s.get('total_pieces')})")
    for b in s.get('active_bonuses', []):
        print(f"      {b.get('text')}")
