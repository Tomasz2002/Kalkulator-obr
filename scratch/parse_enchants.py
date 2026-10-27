import json, re

with open('WarriorSim-TurtleWoW-master/js/data/enchants.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()[:957]

content = "".join(lines)
m = re.search(r'var\s+enchant\s*=\s*(\{[\s\S]*?\n\s*\});', content)
if m:
    raw = m.group(1)
    raw = re.sub(r'//.*', '', raw)
    raw = re.sub(r'(\b[a-zA-Z0-9_]+\b)\s*:', r'"\1":', raw)
    raw = re.sub(r',\s*([\]}])', r'\1', raw)
    try:
        data = json.loads(raw)
        print("Enchant slots:", list(data.keys()))
        for k, v in data.items():
            print(f"{k}: {len(v)} enchants, e.g. {v[0].get('name')}")
    except Exception as e:
        print("JSON parse error:", e)
        with open('scratch/enchants_raw.json', 'w', encoding='utf-8') as out:
            out.write(raw)
