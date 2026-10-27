import struct
import json

with open('data/extracted_client_dbc/patch-5.mpq_Spell.dbc', 'rb') as f:
    header = f.read(20)
    magic, record_count, field_count, record_size, string_block_size = struct.unpack('<4sIIII', header)
    records_data = f.read(record_count * record_size)
    string_block = f.read(string_block_size)

def get_str(offset):
    if offset >= len(string_block): return ""
    end = string_block.find(b'\x00', offset)
    return string_block[offset:end].decode('utf-8', errors='replace')

for i in range(record_count):
    rec = records_data[i * record_size : (i + 1) * record_size]
    fields = struct.unpack(f'<{field_count}I', rec)
    spell_id = fields[0]
    if spell_id == 48030 or spell_id == 15465 or spell_id == 14056:
        name = get_str(fields[136])
        desc = get_str(fields[168])
        print(f"Spell {spell_id}: {name} | Desc: {desc}")
        print(f"  Effects: {fields[69]}, {fields[70]}, {fields[71]}")
        print(f"  BasePoints: {struct.unpack(f'<{field_count}i', rec)[72:75]}")
