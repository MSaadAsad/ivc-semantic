#!/usr/bin/env python3
"""Consistency checks for real IDs, frozen roots, sampling and reported statistics."""
import csv,hashlib,json,math
import numpy as np
import validate as v

def main():
    for p,h in v.DESIGN['input_sha256'].items():assert hashlib.sha256((v.REPO/p).read_bytes()).hexdigest()==h,p
    original={r['sign']:r['root_or_gloss'] for r in v.read('work_data/key6a/master_lexicon_after_key6a.csv')};assert len(original)==len(v.LEX)==163
    assert all(v.LEX[s]['root_or_gloss']==r for s,r in original.items())
    source={(r['catalogue'],r['id']):r for r in v.read('work_data/reader_v3/corpus_soundfree_readings.csv')}
    rows=v.read('research/independent_validation_20261120/results/inscription_tests_60.csv');assert len(rows)==60
    assert len({r['exact_sequence'] for r in rows})==60;assert len({(r['catalogue'],r['object_id']) for r in rows})==60
    for r in rows:
        assert source[(r['catalogue'],r['catalogue_id'])]['signs']==r['exact_sequence']
        assert r['literal_frozen_roots']==' ; '.join(s+'='+original[s] for s in v.tok(r['exact_sequence']))
        assert r['validated_translation']=='False'
    evidence=v.read('research/independent_validation_20261120/results/sign_evidence_45.csv');assert len(evidence)==45
    cells=v.read('research/independent_validation_20261120/results/all_sign_artifact_contrasts.csv');assert len(cells)==540
    q=v.bh([float(r['p_enrichment']) for r in cells]);assert all(abs(float(r['q_BH_all_540'])-float(a))<1e-12 for r,a in zip(cells,q))
    # Regression examples for the upstream dropped-token defect.
    bad=[{'signs':'740-X82-740'},{'signs':'X393'}]
    assert v.coverage(bad)['tokens']==4 and v.coverage(bad)['fully_assigned']==0
    assert v.coverage(bad,True)['tokens']==2 and v.coverage(bad,True)['fully_assigned']==1
    pred=v.read('research/independent_validation_20261120/results/prediction_by_event.csv')
    byseq={}
    for r in pred:byseq.setdefault(r['full_text'],set()).add(r['fold'])
    assert all(len(x)==1 for x in byseq.values())
    maxcells=v.read('research/independent_validation_20261120/results/site_maxT_all540.csv');assert len(maxcells)==540
    assert all(0<float(r['p_FWER_two_corpora'])<=1 for r in maxcells)
    print('PASS: 163 frozen roots, 60 source-bound sequences/objects, 45 signs, 540 contrasts, BH values, grouped folds, max-T outputs, unknown-token regression.')
if __name__=='__main__':main()
