import os
import json
import urllib.request

os.makedirs("static/icons/talents", exist_ok=True)

with open("scratch/paladin_talents.json", "r", encoding="utf-8") as f:
    pal = json.load(f)

icons = set(t["icon"] for t in pal["t"])

with open("scratch/builds.json", "r", encoding="utf-8") as f:
    builds = json.load(f)

for b in builds:
    if b.get("ikona"):
        icons.add(b["ikona"])

print(f"Total unique icons to download: {len(icons)}")

headers = {"User-Agent": "Mozilla/5.0"}
downloaded = 0
for icon in sorted(icons):
    out_path = f"static/icons/talents/{icon}.png"
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        downloaded += 1
        continue
    url = f"https://octowow.prv.pl/talents/icons/{icon}.png"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(out_path, "wb") as f_out:
                f_out.write(data)
            downloaded += 1
    except Exception as e:
        print(f"Failed {icon}: {e}")

print(f"Successfully downloaded {downloaded}/{len(icons)} icons.")
