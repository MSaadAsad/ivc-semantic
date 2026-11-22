"""Verify the specimen crosswalk, conditioning limits, and archived conditional p values."""
import csv,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent;OUT=BASE/'results'
def rows(name):return list(csv.DictReader((OUT/name).open()))
allrows=rows('copper845_all_copper_tablets.csv');tax=rows('copper845_29_specimens.csv')
assert len(allrows)==150 and len(tax)==29
assert len({r['object_id'] for r in allrows})==150
assert {r['object_id'] for r in tax}=={r['object_id'] for r in allrows if r['has_845']=='1'}
assert all(r['city']=='Mohenjo-daro' and r['has_407']=='1' and r['kind']=='ctab' and r['material']=='Copper' for r in tax)
cat=list(csv.DictReader((BASE.parent/'translation_catalogue/results/all_inscriptions.csv').open()))
source={r['face_id'].split('.')[0]:r for r in cat if r['catalogue']=='Lipi'}
for r in allrows:
    for k in ['found_at','recorded_stratigraphy','excavation_number']:
        assert r[k]==source[r['object_id']][k],(r['object_id'],k)
fam=rows('copper845_remainder_families.csv')
assert len(fam)==90 and sum(int(r['objects']) for r in fam)==150
assert not any(int(r['with_845']) and int(r['without_845']) for r in fam)
s=json.loads((OUT/'copper845_summary.json').read_text());assert s['sign845_unique_recorded_formulas']==13
assert (s['tax_objects_with_area'],s['tax_objects_with_room_or_grid'],s['tax_objects_with_recorded_layer'])==(21,10,4)
stats=rows('copper845_comparisons.csv');nulls=np.load(OUT/'copper845_nulls.npz')
for i,r in enumerate(stats):
    if 'remainder_family' in r['controls']:
        assert r['p_conditional']=='' and r['objects_in_mixed_strata']=='0'
    if r['p_conditional']=='':assert str(i) not in nulls;continue
    v=nulls[str(i)];assert len(v)==19999
    p=(1+np.sum(v>=float(r['statistic'])-1e-10))/20000
    assert np.isclose(p,float(r['p_conditional']))
    assert np.isclose(min(1,12*p),float(r['p_bonferroni_12']))
assert len(stats)==22
print('Verified all 150 tablets, 29 exact findspot joins, 90 unmatched remainder families and all archived conditional p values.')
