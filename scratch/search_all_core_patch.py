import os

targets = ['51899', '53200', '52401', '53202', '53203', '52322', '53204', '23561', '23562', '21838']
found = []

for root, dirs, files in os.walk('turtle-core-patch_1171'):
    for f in files:
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                s = fp.read()
                for t in targets:
                    if t in s:
                        found.append((t, path))
        except:
            pass

for t, p in found[:30]:
    print(f"Found {t} in {p}")
