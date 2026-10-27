import os
import re

search_terms = ['47008', '47024', '47001', 'Word of Recall', 'item_template']
migrations_dir = 'turtle-core-patch_1171/sql/old_migrations'

found_matches = []
for fname in os.listdir(migrations_dir):
    if not fname.endswith('.sql'):
        continue
    fpath = os.path.join(migrations_dir, fname)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if '47008' in content or '47024' in content or '47016' in content:
        found_matches.append((fname, content))

print(f"Found in {len(found_matches)} migration files:")
for fname, content in found_matches:
    print(f"\n--- {fname} ---")
    for line in content.splitlines():
        if any(k in line for k in ['47008', '47024', '47016', '47001', '47002', '47005', '47006', '47007', '47022']):
            print(line[:160])
