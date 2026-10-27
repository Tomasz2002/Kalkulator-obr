import re, os, glob

spell_entries = []

files = glob.glob('turtle-core-patch_1171/sql/**/*.sql', recursive=True)

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
                        spell_entries.append((spell_id, name, desc, path))

print(f'Total custom spells found: {len(spell_entries)}')

for sid, name, desc, p in spell_entries:
    full = (name + ' ' + desc).lower()
    if any(k in full for k in ['lawbringer', 'judg', 'redempt', 'holy shield', 'paladin', 'consecrat', 'seal', 'exorcism']):
        print(f'{sid}: {name} | {desc} (from {os.path.basename(p)})')
