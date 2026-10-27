import mpyq

a = mpyq.MPQArchive('scratch/patch-X.mpq')
print(f'Total files in patch-X.mpq: {len(a.files)}')
for f in a.files:
    fn = f.decode('utf-8', errors='ignore') if isinstance(f, bytes) else str(f)
    if fn.lower().endswith('.dbc') or 'item' in fn.lower() or 'spell' in fn.lower() or 'set' in fn.lower():
        print(fn)
