import json

with open('data/races.json', 'r', encoding='utf-8') as f:
    races_data = json.load(f)

with open('data/races.json', 'w', encoding='utf-8') as f:
    json.dump(races_data, f, indent=2)

print("Verified data/races.json")
