import os

found_files = []
for root, dirs, files in os.walk('turtle-core-patch_1171/sql'):
    for f in files:
        if f.endswith('.sql'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as sfile:
                c = sfile.read()
                if '47008' in c or '47024' in c or '47016' in c or '47001' in c or '47242' in c:
                    if 'item_template' in c:
                        found_files.append((fpath, len(c)))

print(f"Found {len(found_files)} files with item_template and target IDs:")
for fpath, sz in found_files[:20]:
    print(fpath, sz)
