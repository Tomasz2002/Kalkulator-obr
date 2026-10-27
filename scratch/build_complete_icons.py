import concurrent.futures
import json
import os
import re
import urllib.request

cookies_str = "phpbb3_3p6u9_u=1; phpbb3_3p6u9_k=; phpbb3_3p6u9_sid=454afb9a430c7fd3d54e75be0cfc3231; __bf_clearance_v2=e4fa044b4c4c34f06e2f60f378cbb39ede547be7310dadcb1b7e3766fd703ac4; XSRF-TOKEN=eyJpdiI6IlNTcm5DUkx1NW9JeVNiN1ZWZG9CWkE9PSIsInZhbHVlIjoibnpQZHg1ajk3QTdBNCtFdm9OdkV5MHhxcVpKcWxKQkdvVHd3dkhqdUpEMnJuaittTnB0RFlocllZM0l5WHFNS0QyWXJHQjQxRlNiK1RqV0xtSDU1YzdzM0VNdytYSmEyV1RuNWM5Ris5R1crUmd0eTJNSTg2M0NqcjVFblNBMlgiLCJtYWMiOiI2OTcyY2I4Mjk0ODYzNzNjN2NiZWVkM2IzNjBhNTQzNDBhZDg0NDlkYTc3MDA2MzdlMTI2M2IwMGZjNzAwNjI2IiwidGFnIjoiIn0%3D; octowow_session=eyJpdiI6IlN6WEo0akR1RGEvSm9mTkNBNUR6QWc9PSIsInZhbHVlIjoiaGprQVFyS2h3eFVSWGJGTkt0OXNHTmVEWVY5Vm9KU0YyNGxWZ2lzVXhDZHVMVkRQUWZmSG9QaU5NN0s3RlhaTVJoelZCZUxEdzdPcnU1ZXFKRUJsOVo4WmRVZklXN1dGRWVQS3lNaEhDaVhDbysvSmtHc1hHbldEVmhtMCtDVGMiLCJtYWMiOiI4NmIzNDc5OGY3N2VkN2VjMmZiN2NjZDRhMzY0ZmEyNmQ5YWJmZGFmYmFjZTMxNTQ2NDE3YzYyMDM2Y2I2YzRkIiwidGFnIjoiIn0%3D"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0"

octo_headers = {
    "User-Agent": user_agent,
    "Cookie": cookies_str,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl,en-US;q=0.9,en;q=0.8",
}

with open("items_db.json", "r", encoding="utf-8") as f:
    items_data = json.load(f)["items"]

paladin_items = [it for it in items_data if "paladin" in it.get("classes", ["paladin"])]
needed_ids = {str(it["id"]): it for it in paladin_items}

icon_map = {}
icons_path = "data/item_icons.json"
if os.path.exists(icons_path):
    try:
        with open(icons_path, "r", encoding="utf-8") as f:
            icon_map = json.load(f)
    except Exception:
        pass

print(f"Loaded {len(icon_map)} existing icons. Need {len(needed_ids)} Paladin items.")

categories = [
    "items=4&slot=1",
    "items=4&slot=2",
    "items=4&slot=3",
    "items=4&slot=16",
    "items=4&slot=5",
    "items=4&slot=9",
    "items=4&slot=10",
    "items=4&slot=6",
    "items=4&slot=7",
    "items=4&slot=8",
    "items=4&slot=11",
    "items=4&slot=12",
    "items=4&slot=14",
    "items=4&slot=23",
    "items=4&slot=28",
    "items=4.4",
    "items=4.3",
    "items=4.2",
    "items=4.1",
    "items=4.0",
    "items=2.0",
    "items=2.1",
    "items=2.2",
    "items=2.4",
    "items=2.5",
    "items=2.6",
    "items=2.7",
    "items=2.8",
    "items=2.10",
    "items=2&qu=4",
    "items=2&qu=3",
    "items=4&qu=4",
    "items=4&qu=3",
]

for cat in categories:
    url = f"https://octowow.st/db/?{cat}"
    try:
        req = urllib.request.Request(url, headers=octo_headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r"_\[(\d+)\]\s*=\s*\{[^}]*icon:\s*['\"]([^'\"]+)['\"]", html)
            for i_id, ic in matches:
                icon_map[i_id] = ic
    except Exception as e:
        print(f"Error cat {cat}: {e}")

missing = [i_id for i_id in needed_ids if i_id not in icon_map]
print(f"After category scrape: {len(set(icon_map.keys()) & set(needed_ids.keys()))}/{len(needed_ids)} matched. Missing: {len(missing)}")

custom_missing = [i_id for i_id in missing if int(i_id) > 30000]
vanilla_missing = [i_id for i_id in missing if int(i_id) <= 30000]
print(f"Custom missing: {len(custom_missing)}, Vanilla missing: {len(vanilla_missing)}")

def fetch_octo_item(i_id):
    url = f"https://octowow.st/db/?item={i_id}"
    req = urllib.request.Request(url, headers=octo_headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r"icon:\s*['\"]([^'\"]+)['\"]", html)
            if m:
                return i_id, m.group(1)
    except Exception:
        pass
    return i_id, None

def fetch_wowhead_item(i_id):
    url = f"https://nether.wowhead.com/tooltip/item/{i_id}"
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "icon" in data:
                return i_id, data["icon"]
    except Exception:
        pass
    return i_id, None

if custom_missing:
    print(f"Fetching {len(custom_missing)} custom items from OctoWoW...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        results = ex.map(fetch_octo_item, custom_missing)
        for i_id, ic in results:
            if ic:
                icon_map[i_id] = ic

if vanilla_missing:
    print(f"Fetching {len(vanilla_missing)} vanilla items from Wowhead API...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        results = ex.map(fetch_wowhead_item, vanilla_missing)
        for i_id, ic in results:
            if ic:
                icon_map[i_id] = ic

os.makedirs("data", exist_ok=True)
with open(icons_path, "w", encoding="utf-8") as f:
    json.dump(icon_map, f, indent=2)

matched_final = set(icon_map.keys()) & set(needed_ids.keys())
print(f"DONE! Total mapped Paladin items: {len(matched_final)} / {len(needed_ids)} ({len(matched_final)/len(needed_ids)*100:.1f}%)")
