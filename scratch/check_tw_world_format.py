import zipfile

with zipfile.ZipFile('turtle-core-patch_1171/sql/world_1171_release.zip', 'r') as z:
    with z.open('tw_world.sql') as f:
        count = 0
        for line in f:
            line_str = line.decode('utf-8', errors='ignore')
            if 'item_template' in line_str:
                print(line_str[:150])
                count += 1
                if count > 10:
                    break
