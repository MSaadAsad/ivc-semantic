"""Run the existing rebus engine against fixed known-script semantic inputs.

This runner never reads truth.json. Source builders write only to --cache.
"""
import argparse, collections, csv, hashlib, importlib, itertools, json, re, sys, time, os
from pathlib import Path
if os.environ.get('PYTHONHASHSEED')!='0':
    os.execve(sys.executable,[sys.executable]+sys.argv,dict(os.environ,PYTHONHASHSEED='0'))
import numpy as np
BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]
sys.path.insert(0,str(REPO/'work_scripts'))

def csvout(name,rows):
    if not rows:return
    with (BASE/'results'/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);args=ap.parse_args()
    args.cache.mkdir(parents=True,exist_ok=True);(BASE/'results').mkdir(exist_ok=True)
    touched=set()
    def audit(event,data):
        if event=='open' and isinstance(data[0],str):
            p=Path(data[0])
            if p.is_absolute() and str(p).startswith(str(REPO/'work_data')):touched.add(p)
    sys.addaudithook(audit)
    spec=json.loads((BASE/'cases.json').read_text());cases=spec['primary_cases']+spec['secondary_cases']
    import typo_00_lexicons as build
    import key2a_rebus_lock as engine
    build.TMP_LEX=str(args.cache);build.OUT_DIR=str(args.cache)
    engine.TMP_LEX=str(args.cache)
    stamp=args.cache/'built.json'
    codehash={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in ['work_scripts/typo_00_lexicons.py','work_scripts/key2a_rebus_lock.py']}
    cached=json.loads(stamp.read_text()) if stamp.exists() else {}
    valid=cached.get('code')==codehash and cached.get('python_hash_seed')=='0' and bool(cached.get('inputs')) and all((REPO/p).exists() and hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h for p,h in cached.get('inputs',{}).items())
    if not valid:
        t=time.monotonic()
        for name in ['build_dravidian','build_indo_aryan','build_elamite','build_sumerian','build_akkadian','build_burushaski']:
            ret=getattr(build,name)();print(name,round(time.monotonic()-t,2),flush=True)
            if name=='build_indo_aryan':build.build_munda(*ret)
        engine.build_fixed_pdrav_2branch()
    else:touched.update(REPO/p for p in cached['inputs'])
    summary=[];matrix=[];witness=[];blocks=[];perms=[];edge_stats=[]
    for family,dname,german in engine.PRIMARY_7_FAMILIES:
        L=engine.CleanCognateLex(family,dname,is_de=german)
        aa=np.array([L.match_regex_bool(re.compile(c['a_de' if german else 'a_en'],re.I)) for c in cases])
        bb=np.array([L.match_regex_bool(re.compile(c['b_de' if german else 'b_en'],re.I)) for c in cases])
        senses_a=[L.match_regex_per_sense(re.compile(c['a_de' if german else 'a_en'],re.I)) for c in cases]
        senses_b=[L.match_regex_per_sense(re.compile(c['b_de' if german else 'b_en'],re.I)) for c in cases]
        poly=np.array([any(aa[k,i] and bb[k,i] and any(a!=b for a in senses_a[k][i] for b in senses_b[k][i]) for i in range(L.E)) for k in range(len(cases))])
        same=(aa&bb).any(axis=1)
        all_hits={}
        for mode in ['phon_exact','phon_stem','ascii_exact']:
            hit=engine.eval_edges_vectorized(L,mode,aa,bb)
            U,V=L.edges[mode];valid=L.cid_int[U]!=L.cid_int[V]
            alt=((aa[:,U]&bb[:,V])|(aa[:,V]&bb[:,U])).any(axis=1) if len(U) else np.zeros(len(cases),bool)
            all_hits[mode]=hit;all_hits[mode+'_entry_only']=alt
            edge_stats.append(dict(language=family,mode=mode,total_homophone_edges=len(U),eligible_distinct_cluster_edges=int(valid.sum()),blocked_shared_cluster_edges=int((~valid).sum())))
            for k,c in enumerate(cases):
                for u,v in zip(U,V):
                    if not ((aa[k,u] and bb[k,v]) or (aa[k,v] and bb[k,u])):continue
                    if not aa[k,u]:u,v=v,u
                    shared=sorted(set(getattr(L,{'phon_exact':'phons','phon_stem':'phon_stems','ascii_exact':'asciis'}[mode])[u])&set(getattr(L,{'phon_exact':'phons','phon_stem':'phon_stems','ascii_exact':'asciis'}[mode])[v]))
                    row=dict(language=family,case=c['id'],mode=mode,a_eid=L.eids[u],b_eid=L.eids[v],a_cluster=L.cids[u],b_cluster=L.cids[v],a_forms='; '.join(L.phons[u]),b_forms='; '.join(L.phons[v]),key='; '.join(shared),a_gloss='; '.join(L.senses[u]),b_gloss='; '.join(L.senses[v]),accepted_original=bool(L.cid_int[u]!=L.cid_int[v]))
                    witness.append(row)
                    if not row['accepted_original']:blocks.append(row)
        all_hits['poly_or_phon']=all_hits['phon_exact']|poly
        all_hits['same_entry_or_phon']=all_hits['phon_exact']|same
        all_hits['entry_only_or_same_entry']=all_hits['phon_exact_entry_only']|same
        for k,c in enumerate(cases):
            matrix.append(dict(language=family,case=c['id'],primary=k<3,a_entries=int(aa[k].sum()),b_entries=int(bb[k].sum()),both_domains=bool(aa[k].any() and bb[k].any()),distinct_sense_polysemy=bool(poly[k]),same_entry_coattestation=bool(same[k]),**{m:bool(h[k]) for m,h in all_hits.items()}))
            for side,mask in [('A',aa[k]),('B',bb[k])]:
                for i in np.flatnonzero(mask):
                    witness.append(dict(language=family,case=c['id'],mode='domain_'+side,a_eid=L.eids[i],b_eid='',a_cluster=L.cids[i],b_cluster='',a_forms='; '.join(L.phons[i]),b_forms='',key='',a_gloss='; '.join(L.senses[i]),b_gloss='',accepted_original='not a scored bridge'))
        for mode,h in all_hits.items():
            summary.append(dict(language=family,lexicon=dname,entries=L.E,mode=mode,primary_hits=int(h[:3].sum()),primary_both_domains=int((aa[:3].any(axis=1)&bb[:3].any(axis=1)).sum()),secondary_TI_rib=bool(h[3])))
        for perm in itertools.permutations(range(3)):
            b=bb[list(perm)];a=aa[:3]
            h=engine.eval_edges_vectorized(L,'phon_exact',a,b)
            U,V=L.edges['phon_exact'];alt=((a[:,U]&b[:,V])|(a[:,V]&b[:,U])).any(axis=1) if len(U) else np.zeros(3,bool)
            co=(a&b).any(axis=1)
            perms.append(dict(language=family,permutation=''.join(map(str,perm)),identity=perm==(0,1,2),full_derangement=all(i!=p for i,p in enumerate(perm)),original_hits=int(h.sum()),entry_only_hits=int(alt.sum()),entry_or_same_entry_hits=int((alt|co).sum())))
        print(family,[(r['mode'],r['primary_hits']) for r in summary if r['language']==family],flush=True)
    csvout('case_scores.csv',matrix);csvout('language_scores.csv',summary);csvout('witnesses.csv',witness);csvout('blocked_bridges.csv',blocks);csvout('permutation_controls.csv',perms);csvout('edge_eligibility.csv',edge_stats)
    inputs={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(touched) if p.is_file()}
    stamp.write_text(json.dumps(dict(code=codehash,python_hash_seed='0',inputs=inputs),indent=2)+'\n')
    source=dict(code=codehash,python_hash_seed='0',runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),inputs=inputs,cases_sha256=hashlib.sha256((BASE/'cases.json').read_bytes()).hexdigest(),generated_lexica={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.cache.glob('*.tsv'))})
    (BASE/'results/run_inputs.json').write_text(json.dumps(source,indent=2)+'\n')

if __name__=='__main__':main()
