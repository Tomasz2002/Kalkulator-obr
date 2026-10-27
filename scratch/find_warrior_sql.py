import glob, os

files = glob.glob('turtle-core-patch_1171/sql/**/*.sql', recursive=True)

targets = ['47240', '47241', '47242', '47248', '47249', '47254', 'Armor of Might', 'Armor of Wrath', 'Spaulders of Might', 'Leggings of Wrath']

for p in files:
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        for lno, line in enumerate(f):
            for t in targets:
                if t in line:
                    print(f'{os.path.basename(p)}:{lno+1}: {line.strip()[:140]}')
