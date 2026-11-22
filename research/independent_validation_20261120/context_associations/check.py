"""Verify statistical moments, sample units, contrasts and reported findspots."""
import itertools,json,math
from pathlib import Path
import numpy as np
import run
OUT=Path(__file__).resolve().parent/'results'
summary=json.loads((OUT/'summary.json').read_text())
assert summary['n_events']==4476 and summary['n_words']==81 and summary['total_tests']==7773
assert summary['permutations']==49999
events=run.rows(OUT/'events.csv');assert len({r['object_id'] for r in events})==4476
formula_counts=run.collections.Counter(r['full_text'] for r in events)
assert abs(sum(1/formula_counts[r['full_text']] for r in events)-len(formula_counts))<1e-8
# Compare the closed-form conditional expectation/variance with every possible
# label ordering, including the weighted-feature sensitivity.
y=np.array([[0.],[1.],[1.]])
for x in [np.array([[1.],[0.],[1.]]),np.array([[.5],[0.],[1.]])]:
    mu,sd=run.moments(x,y,[np.arange(3)])
    scores=np.array([(x.T@y[list(p)])[0,0] for p in itertools.permutations(range(3))])
    assert np.isclose(mu[0,0],scores.mean())
    assert np.isclose(sd[0,0]**2,scores.var())
tests=run.rows(OUT/'all_associations.csv');assert len(tests)==7773
assert len({(r['family'],r['word_id'],r['target']) for r in tests})==len(tests)
for r in tests:
    p=float(r['p_conditional']);m=float(r['p_maxT_axis']);g=float(r['p_FWER_six_axes'])
    assert 1/50000-1e-12<=p<=m+1e-12<=1+1e-12
    assert np.isclose(g,min(1.,6*m))
    if r['family']!='depth':
        a=int(r['observed_word_target_events']);n=int(r['word_events']);t=int(r['target_events']);N=int(r['eligible_events'])
        assert 0<=a<=min(n,t)<=N
        assert np.isclose(float(r['target_share_word_events']),a/n)
        assert np.isclose(float(r['target_share_other_events']),(t-a)/(N-n))
significant=run.rows(OUT/'significant_associations.csv');assert len(significant)==summary['total_primary_significant']
for axis in summary['axes']:
    z=np.load(OUT/(axis['family']+'_nulls.npz'))
    assert len(z['primary_maxima'])==len(z['formula_weighted_maxima'])==49999
    for r in [x for x in significant if x['family']==axis['family']]:
        p=(1+np.sum(z['primary_maxima']>=abs(float(r['standardized_effect']))-1e-12))/50000
        assert np.isclose(float(r['p_FWER_six_axes']),min(1.,6*p))
        p=(1+np.sum(z['formula_weighted_maxima']>=abs(float(r['formula_weighted_effect']))-1e-12))/50000
        assert np.isclose(float(r['formula_weighted_p_FWER_six_axes']),min(1.,6*p))
raw=run.rows(OUT/'material_descriptive.csv')
tax=next(r for r in raw if r['word_id']=='845_vari' and r['target']=='Copper')
assert tax['observed_word_target_events']=='29' and tax['word_events']=='38'
assert tax['adjustable']=='False' and np.isclose(float(tax['expected_word_target_events']),29)
catalogue={(r['catalogue'],r['face_id']):r for r in run.rows(OUT.parents[1]/'translation_catalogue/results/all_inscriptions.csv')}
occs=run.rows(OUT/'all_finding_occurrences.csv')
for r in occs:
    original=catalogue[('Lipi',r['face_id'])]
    assert r['found_at']==original['found_at'] and r['recorded_stratigraphy']==original['recorded_stratigraphy']
for i,f in enumerate(significant):
    ids={r['object_id'] for r in occs if r['finding_index']==str(i)}
    expected=int(f['word_events']) if f['family']=='depth' else int(f['observed_word_target_events'])
    assert len(ids)==expected,(f['word_id'],len(ids),expected)
assert all(r['family']!='recorded_layer' or r['target'].split(' | ',1)[1].startswith(('phase=','period=')) for r in tests)
print('Verified all 7,773 contrasts, 4,476 event identities, exact permutation moments, both null arrays, 29/38 tax/copper counts and every reported finding occurrence against recorded findspots.')
