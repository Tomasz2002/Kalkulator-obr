import urllib.request
import json

req = urllib.request.Request('http://127.0.0.1:5000/api/races')
with urllib.request.urlopen(req) as resp:
    races = json.loads(resp.read().decode('utf-8'))
    print('Human warrior racial text:', races['warrior'][0]['racial_text'])
    print('Human warrior sword skill:', races['warrior'][0]['sword_skill'])
    print('Orc warrior racial text:', races['warrior'][1]['racial_text'])
    print('Orc warrior axe skill:', races['warrior'][1]['axe_skill'])

req = urllib.request.Request('http://127.0.0.1:5000/api/items?class=warrior')
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    items = data['items']
    items_by_id = {it['id']: it for it in items}
    helm_might = items_by_id.get(16866)
    chest_might = items_by_id.get(47242)
    breast_might = items_by_id.get(16865)

    print('\nHelm of Might (16866):')
    if helm_might and helm_might.get('set'):
        print('  Set name:', helm_might['set']['name'])
        print('  Pieces count:', len(helm_might['set']['pieces']))
        print('  Piece IDs:', helm_might['set']['pieces'])

    print('\nChestplate of Might (47242):')
    if chest_might and chest_might.get('set'):
        print('  Set name:', chest_might['set']['name'])
        print('  Pieces count:', len(chest_might['set']['pieces']))
        print('  Piece IDs:', chest_might['set']['pieces'])

    print('\nBreastplate of Might (16865):')
    if breast_might and breast_might.get('set'):
        print('  Set name:', breast_might['set']['name'])
        print('  Pieces count:', len(breast_might['set']['pieces']))
        print('  Piece IDs:', breast_might['set']['pieces'])

sim_payload = {
    'character_class': 'warrior',
    'race': 'human',
    'equipped_items': [16866, 16865, 16861, 16863, 16864, 16867, 16868, 16862],
    'fight_duration': 60,
    'talents': {}
}
req = urllib.request.Request(
    'http://127.0.0.1:5000/api/simulate',
    data=json.dumps(sim_payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    sim_res = json.loads(resp.read().decode('utf-8'))
    print('\nSimulation result status:', sim_res.get('status'))
    print('Simulated DPS:', sim_res.get('dps'))
    print('Active sets in sim:', sim_res.get('gear_totals', {}).get('active_sets'))
