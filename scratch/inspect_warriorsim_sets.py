import re

def parse_sets(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    set_idx = text.find('var sets =')
    if set_idx == -1:
        return []
    block = text[set_idx:]
    pattern = re.compile(r'id:\s*(\d+),\s*name:\s*[\'"]([^\'"]+)[\'"],\s*items:\s*\[([^\]]+)\]', re.DOTALL)
    results = []
    for m in pattern.finditer(block):
        sid = int(m.group(1))
        sname = m.group(2)
        raw_items = [int(x.strip()) for x in m.group(3).split(',') if x.strip().isdigit()]
        results.append((sid, sname, raw_items))
    return results

sets_vanilla = parse_sets('WarriorSim-TurtleWoW-master/js/data/enchants.js')
sets_turtle = parse_sets('WarriorSim-TurtleWoW-master/js/data/enchants_turtle.js')

print('--- Sets in enchants.js (Vanilla) ---')
for sid, name, items in sets_vanilla:
    print(f"{sid}: '{name}' -> {len(items)} items: {items}")

print('\n--- Sets in enchants_turtle.js (Turtle) ---')
for sid, name, items in sets_turtle:
    print(f"{sid}: '{name}' -> {len(items)} items: {items}")
