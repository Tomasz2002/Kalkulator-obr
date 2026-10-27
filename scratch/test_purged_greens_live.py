import urllib.request
import json

req_w = urllib.request.urlopen("http://127.0.0.1:5000/api/items?class=warrior")
data_w = json.loads(req_w.read().decode('utf-8'))
items_w = data_w.get('items', [])
print(f"Warrior items: {len(items_w)}")
w_qualities = set(it.get('quality') for it in items_w)
print(f"Warrior qualities: {sorted(list(w_qualities))}")
assert all(q >= 3 for q in w_qualities), "Qualities below 3 found in warrior items!"

req_p = urllib.request.urlopen("http://127.0.0.1:5000/api/items?class=paladin")
data_p = json.loads(req_p.read().decode('utf-8'))
items_p = data_p.get('items', [])
print(f"Paladin items: {len(items_p)}")
p_qualities = set(it.get('quality') for it in items_p)
print(f"Paladin qualities: {sorted(list(p_qualities))}")
assert all(q >= 3 for q in p_qualities), "Qualities below 3 found in paladin items!"

req_e = urllib.request.urlopen("http://127.0.0.1:5000/api/enchants")
data_e = json.loads(req_e.read().decode('utf-8'))
print(f"Enchants available slots: {len(data_e)}")
assert len(data_e) >= 10, "Enchants missing!"

print("\nALL VERIFICATIONS PASSED!")
