"""Conditional dictionary-overlap controls; no test of the Indus language."""
import argparse, collections, csv, json
from pathlib import Path
import numpy as np
from analyze import BASE, LANGS, load

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);a=ap.parse_args()
    rows,_,_=load(a.cache,None)
    incidence=collections.defaultdict(set)
    for r in rows:
        if r['source']=='dedr_new.csv' and r['entry'] and r['flag']!='loan':incidence[r['entry']].add(r['language'])
    claims=json.loads((BASE/'claims.json').read_text())['claims']
    target={eid for c in claims for eid in c['a_entries']+c['b_entries']}
    assert target<=incidence.keys()
    ids=sorted(incidence);ii={v:i for i,v in enumerate(ids)}
    endpoints=['Brahui','Kurukh','Malto','any_northern','Kurukh_and_Malto','all_three_northern']
    def values(s):
        n=[l in s for l in ['Brahui','Kurukh','Malto']]
        return n+[any(n),n[1] and n[2],all(n)]
    x=np.array([values(incidence[e]) for e in ids],dtype=int)
    # Exact documentation breadth and Tamil attestation, held fixed jointly.
    pools=collections.defaultdict(list);numbers=collections.Counter()
    for eid in ids:pools[len(incidence[eid]),'Tamil' in incidence[eid]].append(ii[eid])
    for eid in target:numbers[len(incidence[eid]),'Tamil' in incidence[eid]]+=1
    observed=x[[ii[e] for e in target]].sum(axis=0)
    rng=np.random.default_rng(20261120);draws=np.zeros((4999,len(endpoints)),dtype=int)
    for key,n in numbers.items():
        pool=np.array(pools[key])
        for b in range(len(draws)):draws[b]+=x[rng.choice(pool,size=n,replace=False)].sum(axis=0)
    p=(1+(draws>=observed).sum(axis=0))/5000
    order=np.argsort(p);adj=np.empty(len(p));prev=0
    for k,j in enumerate(order):prev=max(prev,min(1,float(p[j]*(len(p)-k))));adj[j]=prev
    out=dict(unique_fixed_etyma=len(target),numeric_dictionary_groups=len(ids),draws=4999,seed=20261120,
        matching='Exact number of the 22 documented varieties AND Tamil presence; distinct root groups sampled without replacement within stratum.',
        interpretation='Exploratory etymological documentation control only. Not a semantic or archaeological validation, nor a language-identification probability.',
        endpoints=[dict(name=n,observed=int(observed[j]),expected=float(draws[:,j].mean()),p_enrichment=float(p[j]),holm_p=float(adj[j])) for j,n in enumerate(endpoints)])
    (BASE/'results/northern_controls.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
