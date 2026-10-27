import os

targets = ['51899', '53200', '52401', '53203', '52322', '53204', 'Armor of Wrath', 'Armor of Might']
found = []

for root, dirs, files in os.walk('turtle-core-patch_1171/src'):
    for f in files:
        if f.endswith(('.cpp', '.h')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                s = fp.read()
                for t in targets:
                    if t in s:
                        found.append((t, path))

for t, p in found:
    print(f"Found {t} in {p}")
