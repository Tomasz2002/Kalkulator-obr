import re

targets = ['47240', '47241', '47242', '47243', '47244', '47245', '47246', '47247',
           '47248', '47249', '47250', '47251', '47252', '47253', '47254', '47255',
           '47261', '47262', '47263', '47264', '47265', '47266', '47267', '47268', '47269']

path = 'turtle-core-patch_1171/sql/old_migrations/20220729121659_world.sql'

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line_no, line in enumerate(f, 1):
        for t in targets:
            if f"({t}," in line or f"({t} ," in line or f",{t}," in line:
                print(f"Line {line_no} [{t}]: {line[:300]}")
