import os

targets = ['Chestplate of Might', 'Leggings of Wrath', 'Crown of Might', 'Helmet of Wrath', 'Armor of Might', 'Armor of Wrath']
results = []

for root, dirs, files in os.walk('turtle-core-patch_1171/sql/old_migrations'):
    for f in files:
        if f.endswith('.sql'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                for t in targets:
                    if t in content:
                        results.append((t, path))

for t, p in results:
    print(f"[{t}] in {p}")
