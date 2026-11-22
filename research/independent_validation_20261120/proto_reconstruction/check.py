"""Check complete coverage and prevent source/level/phoneme conflation."""
import collections, csv, gzip, json
from pathlib import Path
import run
BASE=Path(__file__).resolve().parent; OUT=BASE/'results'
def rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
summary=json.loads((OUT/'summary.json').read_text())
with gzip.open(OUT/'input_table.csv.gz','rt',encoding='utf-8-sig') as f:source=list(csv.DictReader(f))
assert len(source)==summary['source_records']==15629
original={r['id_pdr']:r for r in source}
assert original['6460']['number']=='4876'
assert run.form('*wil-')==run.form('*wil')
assert run.form('mīn')!=run.form('min')
assert run.form('kāl')!=run.form('kaḷ')
assert run.form('miHn')!=run.form('mīn')
assert not run.concrete('kurVwi')
try:run.terms_rx([''])
except ValueError:pass
else:raise AssertionError('An empty meaning must not match the entire dictionary')
direct=rows(OUT/'direct_meaning_reconstructions.csv')
reps={r['sign']:r for r in json.loads((BASE.parent/'ivc_language_test/claims.json').read_text())['claims']}
for r in direct:
    c=reps[r['sign']];side='b' if any(t.strip() for t in c['b']) else 'a'
    assert run.terms_rx(c[side]).search(r['meaning'])
    assert not c[side+'_entries'] or r['number'] in c[side+'_entries']
recipes=rows(OUT/'all_existing_pair_recipes.csv')
assert len(recipes)==178 and len({r['claim_id'] for r in recipes})==178
assert len({r['sign'] for r in recipes})==93
for w in rows(OUT/'equal_form_witnesses.csv'):
    a=original[w['picture_record']];b=original[w['target_record']]
    assert a['reference']==b['reference']==w['reference']
    assert a['source_classification']==b['source_classification']==w['ancestral_level']
    assert w['comparison_form'] in run.forms(a['reconstruction'])
    assert w['comparison_form'] in run.forms(b['reconstruction'])
    if w['qualified']=='True':assert run.concrete(w['comparison_form'])
pairs=rows(OUT/'pair_summary.csv')
fixed=[r for r in pairs if r['panel']=='fixed48']
assert len(fixed)==48
assert {r['sign'] for r in fixed if r['qualified_published_PD_equal']=='True'}=={'892','413','540'}
sprout=next(r for r in fixed if r['sign']=='760')
assert sprout['published_PD_equal']=='True' and sprout['qualified_published_PD_equal']=='False'
assert next(r for r in fixed if r['sign']=='220')['published_PD_equal']=='False'
signs=rows(OUT/'all_163_sign_results.csv')
assert len(signs)==163 and len({r['sign'] for r in signs})==163
corpus=rows(OUT/'all_inscriptions_reconstruction_screen.csv')
original_corpus=rows(BASE.parent/'translation_catalogue/results/all_inscriptions.csv')
assert len(corpus)==len(original_corpus)==9252
assert {(r['catalogue'],r['face_id']) for r in corpus}=={(r['catalogue'],r['face_id']) for r in original_corpus}
assert all(r['translation_independently_validated']=='False' for r in corpus)
assert all(r['all_words_dated_to_Indus_period']=='False' for r in corpus)
assert sum(bool(r['PD_equal_pair_signs']) for r in corpus)==summary['corpus_records_with_at_least_one_PD_equal_pair']
for row in corpus:
    assert set(row['PD_equal_pair_signs'].split('; '))-{''} <= set(row['sign_sequence'].split('-'))
assert len(rows(OUT/'full_table_equal_form_pairs.csv'))==summary['full_table_equal_form_pairs']
print('Verified 15,629 source records, 178 pair recipes, 163 sign values and all 9,252 corpus observations; source/level separation, phonemic distinctions, source correction and semantic exclusion hold.')
