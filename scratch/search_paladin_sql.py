import re

pal_terms = ['lawbringer', 'judgement', 'judgment', 'redemption']

results = []
with open('data/item_template.sql', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        for t in pal_terms:
            if t in line.lower():
                m = re.search(r'\((\d+),\s*(\d+),\s*(\d+),\s*["\']([^"\']+)["\']', line)
                if m:
                    entry = int(m.group(1))
                    name = m.group(4)
                    results.append((entry, name, line))
                break

print(f"Found {len(results)} items in item_template.sql matching terms:")
for entry, name, line in sorted(results, key=lambda x: x[0]):
    print(f"{entry}: {name}")
