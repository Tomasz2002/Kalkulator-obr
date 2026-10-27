import struct, json

with open('data/itemcache.wdb', 'rb') as f:
    magic = f.read(4)
    build = struct.unpack('<I', f.read(4))[0]
    locale = f.read(4)
    record_size = struct.unpack('<I', f.read(4))[0]
    data = f.read()

offset = 0
custom_items = []
while offset < len(data):
    if offset + 4 > len(data): break
    item_id = struct.unpack('<I', data[offset:offset+4])[0]
    if item_id == 0: break
    rec_len = struct.unpack('<I', data[offset+4:offset+8])[0]
    chunk = data[offset+8 : offset+8+rec_len]
    offset += 8 + rec_len
    
    idx = 0
    def read_str(d, p):
        end = d.find(b'\x00', p)
        return d[p:end].decode('utf-8', errors='replace'), end + 1
    
    name, idx = read_str(chunk, idx)
    name2, idx = read_str(chunk, idx)
    name3, idx = read_str(chunk, idx)
    name4, idx = read_str(chunk, idx)
    
    fixed = chunk[idx:]
    if len(fixed) < 440: continue
    
    display_id, item_type, item_subclass, unk1, quality, flags, buy_price, sell_price, inv_type, allowable_class, allowable_race, item_level, req_level, req_skill, req_skill_rank, req_spell, req_honor_rank, req_city_rank, req_rep_faction, req_rep_rank, max_count, stackable, container_slots, num_stats = struct.unpack('<24I', fixed[:96])
    
    if inv_type > 0 and item_id < 100000:
        custom_items.append({
            'entry': item_id,
            'name': name,
            'quality': quality,
            'inv_type': inv_type,
            'allowable_class': allowable_class,
            'item_level': item_level,
            'req_level': req_level
        })

print(f"Total custom equipment items: {len(custom_items)}")
might_items = [it for it in custom_items if 'Might' in it['name'] or 'Wrath' in it['name']]
print(f"Might/Wrath items: {len(might_items)}")
for it in might_items[:10]:
    print(it)

judgement_items = [it for it in custom_items if 'Judgement' in it['name'] or 'Lawbringer' in it['name']]
print(f"Judgement/Lawbringer items: {len(judgement_items)}")
for it in judgement_items[:10]:
    print(it)
