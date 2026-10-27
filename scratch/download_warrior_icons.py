import json, os, urllib.request

with open('data/warrior_talents.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

icons = set(t['icon'].lower() for t in data['talents'])
for b in data.get('builds', []):
    icons.add(b['ikona'].lower())

os.makedirs('static/icons/talents', exist_ok=True)
downloaded = 0
failed = 0

for icon in icons:
    target_png = os.path.join('static/icons/talents', f'{icon}.png')
    if os.path.exists(target_png):
        continue
    urls = [
        f'https://octowow.st/db/images/icons/large/{icon}.png',
        f'https://wow.zamimg.com/images/wow/icons/large/{icon}.jpg'
    ]
    saved = False
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    with open(target_png, 'wb') as out_f:
                        out_f.write(resp.read())
                    downloaded += 1
                    saved = True
                    break
        except Exception:
            pass
    if not saved:
        failed += 1

print(f"Downloaded {downloaded} warrior talent icons, failed: {failed}")
