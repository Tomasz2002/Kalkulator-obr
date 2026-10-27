import os

for root, dirs, files in os.walk('turtle-core-patch_1171/sql'):
    for f in files:
        if 'might' in f.lower() or 'wrath' in f.lower() or 'item' in f.lower() or 'set' in f.lower() or 'warrior' in f.lower():
            print(os.path.join(root, f))
