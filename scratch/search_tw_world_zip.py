import zipfile
import re

targets = [47240, 47241, 47242, 47243, 47244, 47245, 47246, 47247,
           47248, 47249, 47250, 47251, 47252, 47253, 47254, 47255,
           47261, 47262, 47263, 47264, 47265, 47266, 47267, 47268, 47269]

target_strs = {str(t): t for t in targets}

with zipfile.ZipFile('turtle-core-patch_1171/sql/world_1171_release.zip', 'r') as z:
    with z.open('tw_world.sql') as f:
        for line in f:
            line_str = line.decode('utf-8', errors='ignore')
            if 'INSERT INTO `item_template`' in line_str or 'item_template' in line_str:
                for ts in target_strs:
                    if f"({ts}," in line_str or f"({ts} ," in line_str or f",{ts}," in line_str:
                        print(f"Found {ts} in tw_world.sql: {line_str[:200]}...")
