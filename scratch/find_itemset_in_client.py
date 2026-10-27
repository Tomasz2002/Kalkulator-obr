import mpyq, os

mpq_dir = r'C:\Octo wow gowno\Data'
for fname in sorted(os.listdir(mpq_dir)):
    if fname.lower().endswith('.mpq'):
        p = os.path.join(mpq_dir, fname)
        try:
            a = mpyq.MPQArchive(p)
            for f in a.files:
                fn = f.decode('utf-8', errors='ignore') if isinstance(f, bytes) else str(f)
                if 'itemset' in fn.lower() or 'spell.dbc' in fn.lower():
                    print(f'{fname}: {fn}')
        except Exception as e:
            pass
