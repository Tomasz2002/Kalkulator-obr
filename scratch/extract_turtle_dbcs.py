import mpyq, struct, zlib, bz2, os

def extract_file_from_mpq(archive_path, file_to_extract, out_path):
    a = mpyq.MPQArchive(archive_path)
    fn = file_to_extract.encode('utf-8') if isinstance(file_to_extract, str) else file_to_extract
    h = a.get_hash_table_entry(fn)
    if not h:
        for f in a.files:
            if f.lower() == fn.lower():
                h = a.get_hash_table_entry(f)
                break
    if not h:
        raise ValueError(f'File {file_to_extract} not found in {archive_path}')
    b = a.block_table[h.block_table_index]
    a.file.seek(b.offset)
    sec = a.file.read(b.archived_size)
    ss = 4096
    if b.flags & mpyq.MPQ_FILE_SINGLE_UNIT:
        if len(sec) == b.size:
            decomp = sec
        else:
            ctype = sec[0]
            if ctype == 2: decomp = zlib.decompress(sec[1:], 15)
            elif ctype == 16: decomp = bz2.decompress(sec[1:])
            else: raise ValueError(f'Unknown ctype {ctype}')
    else:
        num_sectors = (b.size + ss - 1) // ss
        offsets = struct.unpack(f'<{num_sectors + 1}I', sec[:(num_sectors + 1)*4])
        decomp = bytearray()
        for i in range(num_sectors):
            s = sec[offsets[i]:offsets[i+1]]
            if len(s) == ss or (i == num_sectors - 1 and len(s) == (b.size % ss)):
                decomp.extend(s)
            else:
                ctype = s[0]
                cdata = s[1:]
                if ctype == 2:
                    decomp.extend(zlib.decompress(cdata, 15))
                elif ctype == 16:
                    decomp.extend(bz2.decompress(cdata))
                else:
                    raise ValueError(f'Unknown ctype {ctype} at sector {i}')
    with open(out_path, 'wb') as f:
        f.write(decomp)
    print(f'Extracted {file_to_extract} to {out_path}: {len(decomp)} bytes (expected {b.size})')

os.makedirs('data/turtle_dbc', exist_ok=True)
extract_file_from_mpq('scratch/patch-X.mpq', b'dbfilesclient\\ItemSet.dbc', 'data/turtle_dbc/ItemSet.dbc')
extract_file_from_mpq('scratch/patch-X.mpq', b'dbfilesclient\\Spell.dbc', 'data/turtle_dbc/Spell.dbc')
