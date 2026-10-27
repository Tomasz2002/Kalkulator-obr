import mpyq, os

for fname in ['patch-3.mpq', 'patch-4.mpq', 'patch-5.mpq', 'patch-O.mpq']:
    p = os.path.join(r'C:\Octo wow gowno\Data', fname)
    if os.path.exists(p):
        try:
            a = mpyq.MPQArchive(p)
            dbcs = [f.decode('utf-8', errors='ignore') if isinstance(f, bytes) else str(f) for f in a.files if b'.dbc' in f.lower()]
            print(f'{fname} DBCs ({len(dbcs)}): {dbcs[:10]}')
        except Exception as e:
            print(f'{fname} error: {e}')
