import json, re

with open('WarriorSim-TurtleWoW-master/js/data/enchants.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()[:957]

content = "".join(lines)
m = re.search(r'var\s+enchant\s*=\s*(\{[\s\S]*?\n\s*\});', content)
raw = m.group(1)
raw = re.sub(r'//.*', '', raw)
raw = re.sub(r'(\b[a-zA-Z0-9_]+\b)\s*:', r'"\1":', raw)
raw = re.sub(r',\s*([\]}])', r'\1', raw)

ench_data = json.loads(raw)

ranged_enchants = [
    {"id": 18282, "name": "Biznicks 247x Accurascope (+3% Hit)", "hit": 3},
    {"id": 10548, "name": "Sniper Scope (+7 Damage)", "bonusdmg": 7},
    {"id": 10546, "name": "Deadly Scope (+5 Damage)", "bonusdmg": 5},
    {"id": 4407, "name": "Standard Scope (+3 Damage)", "bonusdmg": 3},
    {"id": 4406, "name": "Crude Scope (+1 Damage)", "bonusdmg": 1}
]
ench_data["ranged"] = ranged_enchants

with open('data/enchants.json', 'w', encoding='utf-8') as f:
    json.dump(ench_data, f, indent=2)

print("Saved data/enchants.json with slots:", list(ench_data.keys()))
