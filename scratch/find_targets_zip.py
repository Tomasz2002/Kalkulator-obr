import zipfile

targets = ['47254', '47242', 'Leggings of Wrath', 'Chestplate of Might', 'Breastplate of Might', 'Armor of Wrath']

with zipfile.ZipFile('turtle-core-patch_1171/sql/world_1171_release.zip', 'r') as z:
    with z.open('tw_world.sql') as f:
        for line in f:
            line_str = line.decode('utf-8', errors='ignore')
            for t in targets:
                if t in line_str:
                    print(f"[{t}]: {line_str[:250]}")
