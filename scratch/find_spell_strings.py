import struct
import json

with open('data/extracted_client_dbc/patch-5.mpq_Spell.dbc', 'rb') as f:
    header = f.read(20)
    magic, records, fields, rec_size, str_size = struct.unpack('<4sIIII', header)
    data = f.read(records * rec_size)
    strings = f.read(str_size)

def get_str(offset):
    if offset >= len(strings) or offset <= 0: return ''
    end = strings.find(b'\x00', offset)
    return strings[offset:end].decode('utf-8', errors='ignore')

for i in range(records):
    rec = data[i*rec_size : (i+1)*rec_size]
    spell_id = struct.unpack('<I', rec[:4])[0]
    if spell_id in [48030, 15465, 14056, 7597, 15464]:
        ints = struct.unpack(f'<{fields}I', rec)
        found_strs = []
        for idx in range(120, min(190, fields)):
            s = get_str(ints[idx])
            if s and len(s) > 2:
                found_strs.append((idx, s))
        print(f"Spell {spell_id}: {json.dumps(found_strs, ensure_ascii=True)}")
