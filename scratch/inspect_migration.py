with open('turtle-core-patch_1171/sql/old_migrations/20220729121659_world.sql', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for l in lines:
    if 'item_template' in l.lower() or '47001' in l or '47008' in l or '47024' in l or '47016' in l:
        print(l[:180])
