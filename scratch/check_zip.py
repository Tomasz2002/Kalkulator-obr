import zipfile

with zipfile.ZipFile('turtle-core-patch_1171/sql/world_1171_release.zip', 'r') as z:
    for name in z.namelist():
        print(name)
