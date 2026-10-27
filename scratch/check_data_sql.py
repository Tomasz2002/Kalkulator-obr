targets = ['47254', '47242', 'Leggings of Wrath', 'Chestplate of Might']
with open('data/item_template.sql', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        for t in targets:
            if t in line:
                print(f"[{t}]: {line[:300]}")
