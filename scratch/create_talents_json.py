import json

with open("scratch/paladin_talents.json", "r", encoding="utf-8") as f:
    pal = json.load(f)

with open("scratch/builds.json", "r", encoding="utf-8") as f:
    builds = json.load(f)

data = {
    "trees": pal["trees"],
    "talents": pal["t"],
    "builds": builds
}

with open("data/paladin_talents.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved data/paladin_talents.json successfully with", len(data["talents"]), "talents and", len(data["builds"]), "builds.")
