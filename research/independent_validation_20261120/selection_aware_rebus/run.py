"""Replay the same finite meaning/normalizer/promotion search in every fake dictionary."""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

if os.environ.get('PYTHONHASHSEED') != '0':
    os.execve(sys.executable, [sys.executable]+sys.argv, dict(os.environ, PYTHONHASHSEED='0'))
import numpy as np

BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]
spec=importlib.util.spec_from_file_location('expanded_rebus_engine',BASE.parent/'expanded_rebus_test/run.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)

POLICIES=['Fixed48','SoundChoice48','MeaningChoice48','MeaningAndSound48',
          'GlobalSound48','CandidatePromotion48','UncappedCandidateYield','NaiveFixedRealWinners48']
KINDS=['entry_stratified','legacy_cluster']

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory():
    path=BASE.parent/'expanded_rebus_test/cases.json'
    frozen=json.loads(path.read_text());cases=[]
    for panel,cc in frozen['panels'].items():
        cases.extend(dict(c,panel=panel) for c in cc)
    primary=[c['sign'] for c in frozen['panels']['fixed48']]
    assert len(primary)==len(set(primary))==48
    assert [c['sign'] for c in cases[:48]]==primary
    groups={}
    for i,c in enumerate(cases):groups.setdefault(c['sign'],[]).append(i)
    groups=dict(sorted(groups.items()))
    return frozen,cases,primary,groups

def case_mask(ids):return sum(1<<int(i) for i in ids)

def scored_masks(mode_bits,poly_bits,primary_masks,all_masks,winners):
    modes=[b|poly_bits for b in mode_bits]
    combined=modes[0]|modes[1]|modes[2]
    original=(1<<48)-1
    exact_meanings=sum(bool(modes[0]&g) for g in primary_masks)
    all_meanings=sum(bool(combined&g) for g in primary_masks)
    global_mode=max(sum(bool(bits&g) for g in primary_masks) for bits in modes)
    uncapped=sum(bool(combined&g) for g in all_masks)
    naive=sum(bool(modes[mi]&(1<<idx)) for idx,mi in winners)
    return np.array([E.POPCOUNT(modes[0]&original),E.POPCOUNT(combined&original),
                     exact_meanings,all_meanings,global_mode,min(48,uncapped),uncapped,naive],dtype=np.int16)

def choose_winners(mode_bits,poly_bits,primary,groups):
    modes=[b|poly_bits for b in mode_bits];out=[]
    for sign in primary:
        hits=[(i,mi) for i in groups[sign] for mi,bits in enumerate(modes) if bits&(1<<i)]
        out.append(hits[0] if hits else (groups[sign][0],0))
    return out

def uniform_masks(L,AP,BP,permutation=None):
    out=[]
    for mode in E.MODES:
        u,v=L.edges[mode]
        if permutation is not None:u,v=permutation[u],permutation[v]
        if not len(u):out.append(0);continue
        bits=(AP[u]&BP[v])|(AP[v]&BP[u])
        out.append(E.mask_integer(np.bitwise_or.reduce(bits,axis=0)))
    return out

def null_scores(L,AP,BP,poly,primary_masks,all_masks,winners,n,kind,seed):
    out=np.zeros((n,len(POLICIES)),dtype=np.int16)
    rng=np.random.default_rng(seed);groups=E.strata(L)
    for t in range(n):
        perm=(L.make_cluster_perm(rng) if kind=='legacy_cluster' else E.entry_perm(L,groups,rng))
        bits=uniform_masks(L,AP,BP,perm)
        out[t]=scored_masks(bits,poly,primary_masks,all_masks,winners)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True)
    ap.add_argument('--n',type=int,default=9999)
    ap.add_argument('--output',type=Path,default=BASE/'results');args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    frozen,cases,primary,groups=inventory()
    for path,digest in frozen['input_sha256'].items():assert sha(REPO/path)==digest,path
    built=json.loads((args.cache/'built.json').read_text())
    for path,digest in {**built['code'],**built['inputs']}.items():assert sha(REPO/path)==digest,path
    primary_masks=[case_mask(groups[s]) for s in primary]
    all_masks=[case_mask(ids) for ids in groups.values()]
    E.engine.TMP_LEX=str(args.cache)
    summaries=[];recipes=[];promotion=[];saved={};times=[];whole=time.monotonic()
    for li,(language,name,is_de) in enumerate(E.engine.PRIMARY_7_FAMILIES):
        start=time.monotonic();L=E.engine.CleanCognateLex(language,name,is_de=is_de)
        A,B,P,_=E.match_inputs(L,cases)
        AP,BP=E.packed_columns(A),E.packed_columns(B)
        poly=case_mask(np.flatnonzero(np.diag(P)))
        bits=uniform_masks(L,AP,BP)
        winners=choose_winners(bits,poly,primary,groups)
        observed=scored_masks(bits,poly,primary_masks,all_masks,winners)
        if language=='Dravidian':assert observed[0]==38
        if language=='Sumerian':assert observed[0]==11
        assert observed[3]==observed[7]
        saved[language+'_observed']=observed
        saved[language+'_mode_bits']=np.array([[bool(b&(1<<i)) for i in range(len(cases))] for b in bits])
        saved[language+'_polysemy']=np.diag(P)
        for sign,(idx,mi) in zip(primary,winners):
            success=bool((bits[mi]|poly)&(1<<idx))
            recipes.append(dict(language=language,sign=sign,success=success,
                chosen_panel=cases[idx]['panel'],chosen_case_index=idx,normalizer=E.MODES[mi],
                chosen_title=cases[idx]['title'],
                original_title=cases[primary.index(sign)]['title'],
                recorded_candidate_rows=len(groups[sign]),
                pure_polysemy=bool(poly&(1<<idx)),
                phonetic_match=bool(bits[mi]&(1<<idx)),
                a_en=cases[idx]['a_en'],b_en=cases[idx]['b_en']))
        every_winner=choose_winners(bits,poly,list(groups),groups)
        ids_with_hits=[]
        for sign,(idx,mi) in zip(groups,every_winner):
            success=bool((bits[mi]|poly)&(1<<idx))
            if success:ids_with_hits.append(sign)
            promotion.append(dict(language=language,sign=sign,success=success,
                chosen_case_index=idx,chosen_panel=cases[idx]['panel'],normalizer=E.MODES[mi],
                chosen_title=cases[idx]['title'],in_original48=sign in primary))
        selected=set(ids_with_hits[:48])
        for r in promotion:
            if r['language']==language:r['promoted_at_cap48']=r['sign'] in selected
        print(language,'real policies',observed.tolist(),'preparation seconds',round(time.monotonic()-start,2),flush=True)
        for ki,kind in enumerate(KINDS):
            seed=2026112100+li*101+ki*10001
            values=null_scores(L,AP,BP,poly,primary_masks,all_masks,winners,args.n,kind,seed)
            saved[language+'_'+kind]=values
            for pi,policy in enumerate(POLICIES):
                v=values[:,pi];obs=int(observed[pi]);lo,hi=np.quantile(v,[.025,.975])
                summaries.append(dict(language=language,dictionary=name,entries=L.E,policy=policy,null=kind,
                    primary=policy=='MeaningAndSound48',valid_inferential_endpoint=pi<7,
                    denominator=len(groups) if policy=='UncappedCandidateYield' else 48,observed=obs,
                    n_controls=args.n,null_mean=float(v.mean()),null_sd=float(v.std()),
                    null_025=float(lo),null_975=float(hi),exceedances=int(np.sum(v>=obs)),
                    p=E.pvalue(obs,v),excess=obs-float(v.mean()),seed=seed,
                    fake_ge_old38=int(np.sum(values[:,3]>=38)),
                    fake_ge_old38_fraction=float(np.mean(values[:,3]>=38))))
        times.append(dict(language=language,seconds=round(time.monotonic()-start,3)))
        print(language,'done seconds',times[-1]['seconds'],flush=True)
    for kind in KINDS:
        rr=[r for r in summaries if r['null']==kind and r['primary']]
        for r,adj in zip(rr,E.holm([r['p'] for r in rr])):r['p_holm_primary7']=float(adj)
        rr=[r for r in summaries if r['null']==kind and r['valid_inferential_endpoint']]
        for r,adj in zip(rr,E.holm([r['p'] for r in rr])):r['p_holm_global49']=float(adj)
    conservative=[]
    for language,_,_ in E.engine.PRIMARY_7_FAMILIES:
        rr=[r for r in summaries if r['language']==language and r['primary']]
        conservative.append(dict(language=language,observed=rr[0]['observed'],p_larger_of_two_nulls=max(r['p'] for r in rr)))
    for r,adj in zip(conservative,E.holm([r['p_larger_of_two_nulls'] for r in conservative])):
        r['p_holm_larger_primary7']=float(adj)
    for r in summaries:
        r.setdefault('p_holm_primary7','');r.setdefault('p_holm_global49','')
    E.write_csv(args.output/'summary.csv',summaries)
    E.write_csv(args.output/'chosen_readings.csv',recipes)
    E.write_csv(args.output/'candidate_promotions.csv',promotion)
    E.write_csv(args.output/'conservative_primary.csv',conservative)
    np.savez_compressed(args.output/'search_nulls.npz',**saved)
    manifest=dict(n_controls=args.n,policies=POLICIES,null_kinds=KINDS,
        n_source_rows=len(cases),n_candidate_sign_ids=len(groups),primary_signs=primary,
        source_cases_sha256=sha(BASE.parent/'expanded_rebus_test/cases.json'),
        plan_sha256=sha(BASE/'PLAN.md'),runner_sha256=sha(Path(__file__)),
        reused_engine_sha256=sha(BASE.parent/'expanded_rebus_test/run.py'),
        lexical_inputs=built,
        dictionaries={name:sha(args.cache/(name+'.tsv')) for _,name,_ in E.engine.PRIMARY_7_FAMILIES},
        language_times=times,total_seconds=round(time.monotonic()-whole,3))
    (args.output/'run.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('COMPLETE seconds',manifest['total_seconds'],flush=True)

if __name__=='__main__':main()
