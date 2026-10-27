import os

for root, dirs, files in os.walk('turtle-core-patch_1171/sql'):
    print(root, len(files))
