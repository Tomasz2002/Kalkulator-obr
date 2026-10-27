import os

targets = ['47254', '47242', 'Leggings of Wrath', 'Armor of Wrath', 'Armor of Might']
found = []

for root, dirs, files in os.walk('turtle-core-patch_1171'):
    for f in files:
        if f.endswith('.sql') or f.endswith('.cpp') or f.endswith('.h'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    for t in targets:
                        if t in content:
                            found.append((t, path))
            except Exception as e:
                pass

for t, p in found:
    print(f"Target '{t}' found in {p}")
