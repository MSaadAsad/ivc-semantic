"""Check actual recovered synonyms and previously observed extraction failures."""
import csv
import gzip
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
OUT=BASE/'results'
def read(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))
br={r['eid']:r for r in read('brahui_full_inventory.csv')}
assert len(br)==274
assert 'xaning' in br['1443']['brahui'] and 'to see' in br['1443']['brahui']
assert 'bil' in br['5422']['brahui']
assert 'num' in br['3688']['brahui'] and 'nī' in br['3684']['brahui']
assert 'kalanḍ' in br['1305']['brahui'] and br['1305']['questioned']=='True'
assert 'tūbē' in br['3338']['brahui'] and br['3338']['questioned']=='True'
assert 'putunk' in br['4509']['brahui'] and 'muṭṭux' in br['4921']['brahui']
assert '4100' not in br  # Old parser counted an empty language label.
assert all(r['brahui'].strip() for r in br.values())
presence={r['eid']:r for r in read('all_group_presence.csv')}
assert 'Kur' in presence['399']['languages'].split()
assert 'Malt' in presence['399']['languages'].split()
assert 'Ka' in presence['399']['languages'].split()
assert any(r['eid']=='399' and r['char']=='(' for r in read('parenthesis_repairs.csv'))
pairs=read('all_language_pair_overlap.csv')
for r in pairs:
    rev=next(x for x in pairs if x['a']==r['b'] and x['b']==r['a'])
    assert r['shared']==rev['shared'] and r['jaccard']==rev['jaccard']
    assert int(r['shared'])<=min(int(r['a_groups']),int(r['b_groups']))
s=json.loads((OUT/'summary.json').read_text())
assert s['parser']['groups']==5558 and s['unquestioned_brahui_groups']==226
assert len(s['exact_breadth'])==20
assert all(r['unquestioned_eligible']<=r['eligible_brahui_groups']<=274 for r in s['exact_breadth'])
nulls=json.loads(gzip.decompress((OUT/'null_counts.json.gz').read_bytes()))
assert len(nulls)==20 and all(len(v)==1999 for v in nulls.values())
print('Passed recovered-synonym, empty-label, broken-bracket, qualified-comparison, symmetry and accounting checks.')
