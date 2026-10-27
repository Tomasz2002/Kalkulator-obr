import mpyq

with open('venv/Lib/site-packages/mpyq.py') as f:
    code = f.read()
if 'Unsupported:' not in code:
    code = code.replace('raise RuntimeError("Unsupported compression type.")', 'raise RuntimeError(f"Unsupported: {ord(data[0:1])}")')
    with open('venv/Lib/site-packages/mpyq.py', 'w') as f:
        f.write(code)

import mpyq
a = mpyq.MPQArchive('turtle-core-patch_1171/tools/7010enUS.mpq')
try:
    a.read_file(b'Data\\patch-X.mpq')
except Exception as e:
    print('Caught:', e)
