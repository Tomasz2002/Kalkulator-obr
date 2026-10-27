import urllib.request
import re
import json

url = 'https://octowow.st/db/?itemsets'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0',
    'Cookie': 'phpbb3_3p6u9_u=1; phpbb3_3p6u9_k=; phpbb3_3p6u9_sid=454afb9a430c7fd3d54e75be0cfc3231; __bf_clearance_v2=e4fa044b4c4c34f06e2f60f378cbb39ede547be7310dadcb1b7e3766fd703ac4; XSRF-TOKEN=eyJpdiI6IlNTcm5DUkx1NW9JeVNiN1ZWZG9CWkE9PSIsInZhbHVlIjoibnpQZHg1ajk3QTdBNCtFdm9OdkV5MHhxcVpKcWxKQkdvVHd3dkhqdUpEMnJuaittTnB0RFlocllZM0l5WHFNS0QyWXJHQjQxRlNiK1RqV0xtSDU1YzdzM0VNdytYSmEyV1RuNWM5Ris5R1crUmd0eTJNSTg2M0NqcjVFblNBMlgiLCJtYWMiOiI2OTcyY2I4Mjk0ODYzNzNjN2NiZWVkM2IzNjBhNTQzNDBhZDg0NDlkYTc3MDA2MzdlMTI2M2IwMGZjNzAwNjI2IiwidGFnIjoiIn0%3D; octowow_session=eyJpdiI6IlN6WEo0akR1RGEvSm9mTkNBNUR6QWc9PSIsInZhbHVlIjoiaGprQVFyS2h3eFVSWGJGTkt0OXNHTmVEWVY5Vm9KU0YyNGxWZ2lzVXhDZHVMVkRQUWZmSG9QaU5NN0s3RlhaTVJoelZCZUxEdzdPcnU1ZXFKRUJsOVo4WmRVZklXN1dGRWVQS3lNaEhDaVhDbysvSmtHc1hHbldEVmhtMCtDVGMiLCJtYWMiOiI4NmIzNDc5OGY3N2VkN2VjMmZiN2NjZDRhMzY0ZmEyNmQ5YWJmZGFmYmFjZTMxNTQ2NDE3YzYyMDM2Y2I2YzRkIiwidGFnIjoiIn0%3D',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

m = re.search(r'new Listview\(\{template: \'itemset\',id: \'itemsets\',data: (\[.*?\])\}\);', html)
if m:
    raw_json = m.group(1)
    raw_json = re.sub(r'(\b[a-zA-Z_0-9]+\b):', r'"\1":', raw_json)
    raw_json = raw_json.replace("'", '"')
    try:
        data = json.loads(raw_json)
        print('Parsed sets successfully. Total sets:', len(data))
        with open('scratch/octowow_all_sets.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print('JSON parse error:', e)
        entries = re.findall(r'\{name:\s*[\'"]([^\'"]+)[\'"],pieces:\[([^\]]+)\],[^\}]*id:\s*(\d+)', m.group(1))
        print('Regex extracted sets:', len(entries))
        parsed = []
        for name, pieces_str, sid in entries:
            pieces = [int(x.strip()) for x in pieces_str.split(',') if x.strip().isdigit()]
            parsed.append({'id': int(sid), 'name': name[1:] if name[0].isdigit() else name, 'pieces': pieces})
        with open('scratch/octowow_all_sets.json', 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=2)
else:
    print('Listview not found')
