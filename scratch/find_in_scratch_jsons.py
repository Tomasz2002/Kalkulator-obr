import os, json

for root, dirs, files in os.walk('scratch'):
    for f in files:
        if f.endswith('.json'):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                    if '47240' in content or '47248' in content:
                        print(f"Found in {p} (size {os.path.getsize(p)})")
            except:
                pass
