import urllib.request
import json

sim_payload = json.dumps({
    "character_class": "paladin",
    "race": "human",
    "equipped_items": [47024, 47025, 47026, 47027, 47028, 47029, 47030, 47031, 19019],
    "talents": {"improved_judgement": 2, "conviction": 5, "sanctity_aura": 1, "improved_sor": 5},
    "fight_duration": 60
}).encode('utf-8')

sim_req = urllib.request.Request("http://127.0.0.1:5000/api/simulate", data=sim_payload, headers={'Content-Type': 'application/json'})
sim_res = urllib.request.urlopen(sim_req)
sim_data = json.loads(sim_res.read().decode('utf-8'))
print("Simulation response for Paladin with Judgement Battlegear:")
print(f"  Class: {sim_data.get('character_class')}")
print(f"  DPS: {sim_data.get('total_dps')}")
print(f"  Active sets: {list(sim_data.get('active_sets', {}).keys())}")
for sid, s in sim_data.get('active_sets', {}).items():
    print(f"    Set {sid}: {s.get('name')} ({s.get('equipped_count')}/{s.get('total_pieces')})")
    for b in s.get('active_bonuses', []):
        print(f"      {b.get('text')}")
