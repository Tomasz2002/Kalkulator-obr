import urllib.request
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0",
    "Cookie": "phpbb3_3p6u9_u=1; phpbb3_3p6u9_k=; phpbb3_3p6u9_sid=454afb9a430c7fd3d54e75be0cfc3231; __bf_clearance_v2=e4fa044b4c4c34f06e2f60f378cbb39ede547be7310dadcb1b7e3766fd703ac4; XSRF-TOKEN=eyJpdiI6IlNTcm5DUkx1NW9JeVNiN1ZWZG9CWkE9PSIsInZhbHVlIjoibnpQZHg1ajk3QTdBNCtFdm9OdkV5MHhxcVpKcWxKQkdvVHd3dkhqdUpEMnJuaittTnB0RFlocllZM0l5WHFNS0QyWXJHQjQxRlNiK1RqV0xtSDU1YzdzM0VNdytYSmEyV1RuNWM5Ris5R1crUmd0eTJNSTg2M0NqcjVFblNBMlgiLCJtYWMiOiI2OTcyY2I4Mjk0ODYzNzNjN2NiZWVkM2IzNjBhNTQzNDBhZDg0NDlkYTc3MDA2MzdlMTI2M2IwMGZjNzAwNjI2IiwidGFnIjoiIn0%3D; octowow_session=eyJpdiI6IlN6WEo0akR1RGEvSm9mTkNBNUR6QWc9PSIsInZhbHVlIjoiaGprQVFyS2h3eFVSWGJGTkt0OXNHTmVEWVY5Vm9KU0YyNGxWZ2lzVXhDZHVMVkRQUWZmSG9QaU5NN0s3RlhaTVJoelZCZUxEdzdPcnU1ZXFKRUJsOVo4WmRVZklXN1dGRWVQS3lNaEhDaVhDbysvSmtHc1hHbldEVmhtMCtDVGMiLCJtYWMiOiI4NmIzNDc5OGY3N2VkN2VjMmZiN2NjZDRhMzY0ZmEyNmQ5YWJmZGFmYmFjZTMxNTQ2NDE3YzYyMDM2Y2I2YzRkIiwidGFnIjoiIn0%3D",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl,en-US;q=0.9,en;q=0.8",
}

with open("items_db.json", "r", encoding="utf-8") as f:
    items = json.load(f)["items"]
needed_ids = set(str(it["id"]) for it in items)

icon_map = {}

queries = [
    "items=4.4",
    "items=4.3",
    "items=4.2",
    "items=4.1",
    "items=4.0",
    "items=4.-8",
    "items=4.4&qu=4",
    "items=4.4&qu=3",
    "items=4.4&qu=2",
    "items=4.3&qu=4",
    "items=4.3&qu=3",
    "items=4.2&qu=4",
    "items=4.0&qu=4",
    "items=4.0&qu=3",
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
    "items=2&qu=5",
    "items=4&qu=5"
]

for q in queries:
    url = f"https://octowow.st/db/?{q}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r"_\[(\d+)\]\s*=\s*\{[^}]*icon:\s*['\"]([^'\"]+)['\"]", html)
            for i_id, icon in matches:
                icon_map[i_id] = icon
            print(f"Query {q:16} -> {len(matches)} icons in page. Total unique gathered: {len(icon_map)}")
    except Exception as e:
        print(f"Error {q}: {e}")

matched = set(icon_map.keys()) & needed_ids
print(f"Matched {len(matched)} / {len(needed_ids)} items from DB!")
