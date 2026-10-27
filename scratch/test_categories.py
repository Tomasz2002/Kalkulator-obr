import urllib.request
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0",
    "Cookie": "phpbb3_3p6u9_u=1; phpbb3_3p6u9_k=; phpbb3_3p6u9_sid=454afb9a430c7fd3d54e75be0cfc3231; __bf_clearance_v2=e4fa044b4c4c34f06e2f60f378cbb39ede547be7310dadcb1b7e3766fd703ac4; XSRF-TOKEN=eyJpdiI6IlNTcm5DUkx1NW9JeVNiN1ZWZG9CWkE9PSIsInZhbHVlIjoibnpQZHg1ajk3QTdBNCtFdm9OdkV5MHhxcVpKcWxKQkdvVHd3dkhqdUpEMnJuaittTnB0RFlocllZM0l5WHFNS0QyWXJHQjQxRlNiK1RqV0xtSDU1YzdzM0VNdytYSmEyV1RuNWM5Ris5R1crUmd0eTJNSTg2M0NqcjVFblNBMlgiLCJtYWMiOiI2OTcyY2I4Mjk0ODYzNzNjN2NiZWVkM2IzNjBhNTQzNDBhZDg0NDlkYTc3MDA2MzdlMTI2M2IwMGZjNzAwNjI2IiwidGFnIjoiIn0%3D; octowow_session=eyJpdiI6IlN6WEo0akR1RGEvSm9mTkNBNUR6QWc9PSIsInZhbHVlIjoiaGprQVFyS2h3eFVSWGJGTkt0OXNHTmVEWVY5Vm9KU0YyNGxWZ2lzVXhDZHVMVkRQUWZmSG9QaU5NN0s3RlhaTVJoelZCZUxEdzdPcnU1ZXFKRUJsOVo4WmRVZklXN1dGRWVQS3lNaEhDaVhDbysvSmtHc1hHbldEVmhtMCtDVGMiLCJtYWMiOiI4NmIzNDc5OGY3N2VkN2VjMmZiN2NjZDRhMzY0ZmEyNmQ5YWJmZGFmYmFjZTMxNTQ2NDE3YzYyMDM2Y2I2YzRkIiwidGFnIjoiIn0%3D",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl,en-US;q=0.9,en;q=0.8",
}

for cat in ["2", "4", "4.0", "4.1", "4.2", "4.3", "4.4"]:
    url = f"https://octowow.st/db/?items={cat}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            icons = re.findall(r"_\[(\d+)\]\s*=\s*\{[^}]*icon:\s*['\"]([^'\"]+)['\"]", html)
            print(f"Cat {cat}: status {resp.status}, length {len(html)}, icons found: {len(icons)}")
    except Exception as e:
        print(f"Cat {cat} error: {e}")
