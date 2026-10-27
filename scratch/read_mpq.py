import mpyq

archive = mpyq.MPQArchive('turtle-core-patch_1171/tools/7010enUS.mpq')
files = archive.files
print(f'Total files: {len(files)}')
for f in files:
    print(f)
