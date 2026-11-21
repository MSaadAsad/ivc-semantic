#!/usr/bin/env python3
"""Site-stratified max-T correction across the complete 45 x 6 x 2 family.

One-sided enrichment tests; shared site permutations preserve all sign dependencies.
Within-corpus max-T p-values are Bonferroni-adjusted over the two corpora.
"""
from collections import defaultdict
import numpy as np
from threadpoolctl import threadpool_limits
import validate as v

def main():
    results=[]; rng=np.random.default_rng(v.SEED+7)
    for cat,path in [('Lipi','work_data/sem/objects_lipi.csv'),('Mahadevan','work_data/sem/objects_mah_new.csv')]:
        objects=[r for r in v.read(path) if r['is_event_rep']=='True']; sites=defaultdict(list)
        for i,r in enumerate(objects):sites[r['site']].append(i)
        ixlist=[np.array(ix) for _,ix in sorted(sites.items())]; sets=[v.event_signs(r) for r in objects]
        X=np.array([[s in z for s in v.SIGNS] for z in sets],dtype=float);Y=np.array([[r['kind']==k for k in v.TARGETS] for r in objects],dtype=float)
        mu=np.zeros((len(v.SIGNS),len(v.TARGETS)));var=np.zeros_like(mu)
        for ix in ixlist:
            n=len(ix);a=X[ix].sum(0);p=Y[ix].mean(0);mu+=a[:,None]*p[None,:]
            if n>1:var+=(a*(n-a)/(n-1))[:,None]*(p*(1-p))[None,:]
        sd=np.sqrt(var);sd[sd<1e-12]=np.inf;obs=(X.T@Y-mu)/sd;maxima=[]
        for b in range(v.DESIGN['n_permutations']):
            perm=np.arange(len(objects))
            for ix in ixlist:perm[ix]=rng.permutation(ix)
            maxima.append(float(np.max((X.T@Y[perm]-mu)/sd)))
        np.savez_compressed(v.OUT/('maxT_null_'+cat+'.npz'),maxima=maxima,observed=obs,expected=mu,sd=sd)
        for i,s in enumerate(v.SIGNS):
            for j,k in enumerate(v.TARGETS):
                p=(1+int(sum(m>=obs[i,j]-1e-12 for m in maxima)))/(1+len(maxima))
                results.append(dict(catalogue=cat,sign=s,target=k,observed_events=int((X.T@Y)[i,j]),null_expectation=float(mu[i,j]),standardized_excess=float(obs[i,j]),p_maxT_within_corpus=p,p_FWER_two_corpora=min(1.,2*p)))
        print(cat,'complete',flush=True)
    v.csvout('site_maxT_all540.csv',results)
    v.save('site_maxT_summary.json',{'n_permutations':v.DESIGN['n_permutations'],'n_tests':len(results),'FWER_below_0_05':sum(r['p_FWER_two_corpora']<.05 for r in results),'interpretation':'Sign-artifact association after site control; not semantic identification. Exchangeability inside site remains an assumption; text-family dependence beyond known copy batches remains.'})
if __name__=='__main__':
    with threadpool_limits(limits=1):main()
