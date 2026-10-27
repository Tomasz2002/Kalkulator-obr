import mpyq, struct, zlib, bz2, os

a = mpyq.MPQArchive('turtle-core-patch_1171/tools/7010enUS.mpq')
h = a.get_hash_table_entry(b'Data\\patch-X.mpq')
b = a.block_table[h.block_table_index]
a.file.seek(b.offset)
sec = a.file.read(b.archived_size)

ss = 4096
num_sectors = (b.size + ss - 1) // ss
offsets = struct.unpack(f'<{num_sectors + 1}I', sec[:(num_sectors + 1)*4])

decompressed = bytearray()
for i in range(num_sectors):
    s = sec[offsets[i]:offsets[i+1]]
    if len(s) == ss or (i == num_sectors - 1 and len(s) == (b.size % ss)):
        decompressed.extend(s)
    else:
        ctype = s[0]
        cdata = s[1:]
        if ctype == 2:
            decompressed.extend(zlib.decompress(cdata, 15))
        elif ctype == 16:
            decompressed.extend(bz2.decompress(cdata))
        else:
            raise ValueError(f'Unknown ctype {ctype} at sector {i}')

out_path = 'scratch/patch-X.mpq'
with open(out_path, 'wb') as f:
    f.write(decompressed)

print(f'Successfully extracted patch-X.mpq: {len(decompressed)} bytes (expected {b.size})')
