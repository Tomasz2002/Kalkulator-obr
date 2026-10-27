import re

with open('turtle-core-patch_1171/sql/old_migrations/20220729121659_world.sql', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'spell_template' in line and 'VALUES' in line:
            m = re.match(r"INSERT INTO `spell_template` VALUES \((\d+),", line)
            if m:
                spell_id = int(m.group(1))
                strings = re.findall(r"'([^']*)'", line)
                if strings:
                    name = strings[0]
                    desc = strings[2] if len(strings) > 2 else ''
                    full = (name + ' ' + desc).lower()
                    if any(w in full for w in ['lawbringer', 'redemption', 'dreadnaught', 'might', 'wrath']) and any(k in full for k in ['armor', 'battlegear', 'aegis', 'set', 'bonus', 'piece']):
                        print(f'{spell_id}: {name} | {desc}')
