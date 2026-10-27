with open('src/calculators/warrior.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('#') or '//' in line or '/*' in line or '*/' in line:
        print(f"Line {idx}: {line.rstrip()}")
