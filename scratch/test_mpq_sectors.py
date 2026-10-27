import mpyq

a = mpyq.MPQArchive('turtle-core-patch_1171/tools/7010enUS.mpq')
h = a.get_hash_table_entry(b'Data\\patch-X.mpq')
b = a.block_table[h.block_table_index]
a.file.seek(b.offset)
sec = a.file.read(b.archived_size)
import struct
num_sectors = (b.size + 4096 - 1) // 4096
offsets = struct.unpack(f'<{num_sectors + 1}I', sec[:(num_sectors + 1)*4])
for i in range(5):
    s = sec[offsets[i]:offsets[i+1]]
    print(f'sector {i}: len={len(s)}, byte0={hex(s[0]) if len(s) else "empty"}')
