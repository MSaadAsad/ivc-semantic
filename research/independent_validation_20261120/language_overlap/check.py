"""Source-specific checks for the meaning-matched comparison."""
import csv
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
OUT=BASE/'results'
def read(p):
    with p.open() as f:return list(csv.DictReader(f))

provenance=json.loads((BASE/'external/dravlex/provenance.json').read_text())
for p in provenance['files']:
    assert hashlib.sha256((BASE/'external/dravlex'/p['path']).read_bytes()).hexdigest()==p['sha256']
forms=read(BASE/'external/dravlex/cldf/forms.csv')
assert len(forms)==2127
assert any(f['Language_ID']=='Brahui' and f['Parameter_ID']=='30_fish' and f['Loan']=='true' for f in forms)
rows=read(OUT/'dravlex_concept_scores.csv')
def cell(lang,concept):
    return next(r for r in rows if r['language']==lang and r['concept']==concept and r['exclude_flagged_loans']=='True')
assert cell('Brahui','26_eye')['matched_forms']=='xan'
assert cell('Brahui','42_horn')['matched']=='True'
assert cell('Tamil','42_horn')['matched']=='False'
assert cell('Malto','30_fish')['matched']=='True'
assert cell('Brahui','30_fish')['matched']=='False'
assert cell('Kurukh','80_star')['matched']=='True'
assert cell('Malto','80_star')['matched']=='True'
assert cell('Tamil','54_moon')['scorable']=='False'
assert cell('Tamil','74_sit')['scorable']=='False'
assert cell('Tamil','72_see')['manual_anchor']=='True'
summary=json.loads((OUT/'summary.json').read_text())
assert summary['dravlex']['scorable_concepts']==11
for lg in ('Brahui','Kurukh','Malto'):
    rr=[r for r in rows if r['language']==lg and r['exclude_flagged_loans']=='True' and r['scorable']=='True']
    assert len(rr)==11 and all(r['recorded']=='True' for r in rr)
    assert sum(r['matched']=='True' for r in rr)==5
for r in summary['dedr']['results']:
    assert r['attested_target_etyma']<=r['target_etyma']==73
    assert 0<r['conditional_p_upper']<=r['p_holm_all42']<=1
assert len(summary['dedr']['results'])==42
assert summary['dravlex']['holm_significant_pairs']==0
print('Passed pinned-source, sound-different cognate, loan flag, counterexample, missing-anchor and accounting checks.')
