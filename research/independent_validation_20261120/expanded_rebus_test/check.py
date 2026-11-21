"""Validate the expanded experiment against the source engine and explicit loops."""
import argparse
import csv
import json
import re
import numpy as np
import run as R

def read(name):
    return list(csv.DictReader((R.BASE/'results'/name).open()))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=R.Path,required=True)
    args=ap.parse_args();R.engine.TMP_LEX=str(args.cache)
    meta=json.loads((R.BASE/'results/run.json').read_text())
    assert meta['n_controls']==9999
    assert meta['runner_sha256']==R.hash_file(R.BASE/'run.py')
    assert meta['cases_sha256']==R.hash_file(R.BASE/'cases.json')
    assert meta['plan_sha256']==R.hash_file(R.BASE/'PLAN.md')
    for p,h in {**meta['source_inputs'],**meta['lexical_inputs']['code'],**meta['lexical_inputs']['inputs']}.items():
        assert R.hash_file(R.REPO/p)==h,p
    spec=json.loads((R.BASE/'cases.json').read_text())
    names=list(spec['panels']);offsets=[];cases=[]
    for panel,cc in spec['panels'].items():
        offsets.append((len(cases),len(cc)));cases.extend(cc)
        assert len({c['sign'] for c in cc})==len(cc)
    summary=read('summary.csv')
    assert len(summary)==6*7*3*2*2==504
    assert len(read('case_scores.csv'))==178*7
    master=read('master_scope.csv');assert len(master)==163
    assert len({r['sign'] for r in master})==163
    assert all(r['stored_hits']==r['reproduced_hits'] for r in read('reproduction.csv'))
    assert all(r['uniform_original']==r['uniform_reversed'] for r in read('row_order.csv'))
    data=np.load(R.BASE/'results/nulls_and_matrices.npz')
    for row in summary:
        l=row['language'];pi=names.index(row['panel']);mi=R.MODES.index(row['mode'])
        gi=R.GATES.index(row['gate']);ci=R.CHANNELS.index(row['channel']);obs=int(row['hits'])
        assert obs==int(data[l+'_observed'][pi,mi,gi,ci])
        for kind,column in [('domain','p_domain'),('entry_sound','p_entry_sound'),('legacy_sound','p_legacy_sound')]:
            null=data[l+'_'+kind][:,pi,mi,gi,ci]
            assert len(null)==9999
            assert abs(float(row[column])-R.pvalue(obs,null))<1e-12
        assert float(row['p_both_requirements'])==max(float(row['p_domain']),float(row['p_entry_sound']))
        assert 0<=obs<=int(row['both_domains'])<=int(row['n_pairs'])
    for l,_,_ in R.engine.PRIMARY_7_FAMILIES:
        for kind in ['domain','entry_sound','legacy_sound']:
            a=data[l+'_'+kind]
            assert np.all(a[:,:,:,1,:]>=a[:,:,:,0,:])
            assert np.all(a[:,:,:,:,1]>=a[:,:,:,:,0])
        for panel in names:
            matrix=data[l+'_matrix_'+panel]
            assert np.all(np.diagonal(matrix,axis1=-2,axis2=-1).sum(-1)==data[l+'_observed'][names.index(panel)])
            rng=np.random.default_rng(20261121+names.index(panel))
            for t in range(20):
                n=matrix.shape[-1];p=rng.permutation(n)
                # Explicit loop is independent of the runner's broadcast indexing.
                count=sum(int(matrix[0,1,1,i,p[i]]) for i in range(n))
                assert count==data[l+'_domain'][t,names.index(panel),0,1,1]
    # Validate packed scoring against the unmodified legacy scorer under real sound permutations.
    rng=np.random.default_rng(91803)
    for language,lexicon,is_de in R.engine.PRIMARY_7_FAMILIES:
        L=R.engine.CleanCognateLex(language,lexicon,is_de=is_de)
        assert R.hash_file(args.cache/(lexicon+'.tsv'))==meta['generated_lexica'][lexicon]
        # Include every panel, without requiring a fixed expected research result.
        ids=sorted(set([0,3,9,17,31,47,48,60,82,98,99,110,111,125,140,141,153,154,165,177]))
        chosen=[cases[i] for i in ids]
        A,B,P,ss=R.match_inputs(L,chosen)
        AP,BP=R.packed_columns(A),R.packed_columns(B)
        for t in range(13):
            perm=None if t==0 else L.make_cluster_perm(rng)
            for mode in R.MODES:
                legacy,uniform=R.edge_masks(L,mode,AP,BP,perm)
                oracle=R.engine.eval_edges_vectorized(L,mode,A,B,perm=perm)
                assert [bool(legacy & (1<<i)) for i in range(len(ids))]==oracle.tolist()
                assert (legacy | uniform)==uniform
        # Brute-force distinct-entry exact witnesses without the graph or packed representation.
        for k in range(len(ids)):
            found=any(a!=b and set(L.phons[a]) & set(L.phons[b])
                      for a in np.flatnonzero(A[k]) for b in np.flatnonzero(B[k]))
            packed=R.edge_masks(L,'phon_exact',AP,BP)[1]
            assert bool(packed & (1<<k))==bool(found)
            explicit_poly=any(any(a!=b for a in ss[0][k][e] for b in ss[1][k][e])
                              for e in range(L.E))
            assert explicit_poly==bool(P[k,k])
    adjusted=R.holm([float(r['p_both_requirements']) for r in summary])
    assert np.allclose(adjusted,[float(r['p_holm_global']) for r in summary])
    print('PASS: 504 cells; 1,246 case-language rows; 163-row scope; 9,999 controls per null; source reproduction; explicit/brute-force scoring; shared permutations; order invariance; multiplicity corrections.')

if __name__=='__main__':main()
