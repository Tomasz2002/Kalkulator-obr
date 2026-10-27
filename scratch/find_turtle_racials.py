import struct, re

with open('data/Spell.dbc', 'rb') as f:
    header = f.read(20)
    magic, rec_count, field_count, rec_size, string_size = struct.unpack('<4sIIII', header)
    data = f.read(rec_count * rec_size)
    strings = f.read(string_size)

def get_str(offset):
    if offset <= 0 or offset >= len(strings): return ''
    end = strings.find(b'\x00', offset)
    if end == -1: end = len(strings)
    return strings[offset:end].decode('utf-8', errors='ignore')

racial_terms = ['Sword Specialization', 'Mace Specialization', 'Axe Specialization', 'Bow Specialization', 'Gun Specialization', 'Blood Fury', 'Berserking', 'Stoneform', 'The Human Spirit', 'Endurance', 'Expansive Mind', 'Quickness']

for i in range(rec_count):
    row = data[i * rec_size : (i + 1) * rec_size]
    vals = struct.unpack(f'<{field_count}i', row)
    name = get_str(vals[120])
    desc = get_str(vals[138])
    bp = [vals[76], vals[77], vals[78]]
    for term in racial_terms:
        if name.lower() == term.lower():
            for idx, bp_val in enumerate(bp):
                desc = desc.replace(f"$s{idx+1}", str(bp_val + 1))
            print(f"Spell {vals[0]}: Name='{name}', bp={bp[:3]}, Desc='{desc}'")
