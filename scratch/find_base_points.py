import struct

with open('data/extracted_client_dbc/patch-5.mpq_Spell.dbc', 'rb') as f:
    header = f.read(20)
    magic, records, fields, rec_size, str_size = struct.unpack('<4sIIII', header)
    data = f.read(records * rec_size)
    strings = f.read(str_size)

# 9317 is Increase Healing 31 -> base value is 30 or 31
# 18037 is Increase Healing 57 -> base value is 56 or 57
# 14054 is Increase Spell Dam 27 -> base value is 26 or 27
# 23213 is Increase Spell Dam 57 -> base value is 56 or 57
# 7598 is Increased Critical 2 -> base value is 1 or 2
# 7599 is Increased Critical 3 -> base value is 2 or 3
# 8815 is Haste 2 -> base value is 1 or 2

targets = [9317, 18037, 14054, 23213, 7598, 7599, 8815, 51801, 51806, 51807, 51820, 51823]
spells_data = {}
for i in range(records):
    rec = data[i*rec_size : (i+1)*rec_size]
    spell_id = struct.unpack('<I', rec[:4])[0]
    if spell_id in targets:
        ints = struct.unpack(f'<{fields}i', rec)
        spells_data[spell_id] = ints

# Let's find which column has 30 or 31 in 9317, 56 or 57 in 18037, 26 or 27 in 14054
for col in range(fields):
    vals = [spells_data[sid][col] for sid in [9317, 18037, 14054, 23213]]
    if vals in ([30, 56, 26, 56], [31, 57, 27, 57]):
        print(f'Column {col} matches base points! Values: {vals}')

# Let's print all values of 51801, 51806, 51807, 51820, 51823, 51805, 51803, 51815, 21882
for sid in [51801, 51806, 51807, 51820, 51823, 51805, 51803, 51815, 21882, 13675, 13676, 28325]:
    ints = spells_data.get(sid)
    if not ints:
        for i in range(records):
            rec = data[i*rec_size : (i+1)*rec_size]
            s_id = struct.unpack('<I', rec[:4])[0]
            if s_id == sid:
                ints = struct.unpack(f'<{fields}i', rec)
                spells_data[sid] = ints
                break
    # print non-zero interesting values (base points, trigger spells)
    print(f'Spell {sid}: base_col58={ints[58]}, base_col59={ints[59]}, base_col60={ints[60]}, die_col61={ints[61]}, die_col62={ints[62]}, die_col63={ints[63]}')
    # check columns around 50..70
    print(f'  cols 50..70: {list(ints[50:71])}')
