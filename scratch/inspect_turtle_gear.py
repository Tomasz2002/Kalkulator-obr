import re

with open('WarriorSim-TurtleWoW-master/js/data/gear_turtle.js', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'\{\s*"name":\s*"([^"]+)"[^}]+?"id":\s*(\d+)', re.DOTALL)
matches = pattern.findall(text)
print('Total matches:', len(matches))
for name, item_id in matches:
    iid = int(item_id)
    if 47240 <= iid <= 47275:
        print(f'{iid}: {name}')
