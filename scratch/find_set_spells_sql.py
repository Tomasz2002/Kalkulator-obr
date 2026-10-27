import re, glob, os

files = glob.glob('turtle-core-patch_1171/sql/**/*.sql', recursive=True)
set_spells = []

for path in files:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
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
                        if any(w in full for w in ['set:', 'set (', 'pieces', 'piece bonus', 'battlegear', 'aegis', 'armor set', 'tier 1', 'tier 2', 'tier 3', 't1', 't2', 't3']):
                            set_spells.append((spell_id, name, desc, os.path.basename(path)))

print(f'Total set spells found: {len(set_spells)}')
for s in set_spells:
    print(f'{s[0]}: {s[1]} | {s[2]} ({s[3]})')
