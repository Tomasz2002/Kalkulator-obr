import mpyq, os

archive = mpyq.MPQArchive('turtle-core-patch_1171/tools/7010enUS.mpq')
patch_x = archive.read_file(b'Data\\patch-X.mpq')
out_path = 'scratch/patch-X.mpq'
with open(out_path, 'wb') as f:
    f.write(patch_x)

print(f'Extracted patch-X.mpq: {os.path.getsize(out_path)} bytes')

archive_x = mpyq.MPQArchive(out_path)
print(f'Total files in patch-X.mpq: {len(archive_x.files)}')
dbc_files = [f for f in archive_x.files if b'.dbc' in f.lower() or b'dbc' in f.lower()]
for d in dbc_files:
    print(d)
