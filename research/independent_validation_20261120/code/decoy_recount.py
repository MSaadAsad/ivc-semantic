#!/usr/bin/env python3
"""Recount existing decoy tests and keep paired testers together in permutations."""
from collections import defaultdict
import numpy as np
from scipy.stats import beta
import validate as v

def main():
    key={r['item']:r for r in v.read('work_data/decoy/KEY_do_not_open.csv')};ids=sorted(key,key=int);real=np.array([key[i]['real_or_decoy']=='real' for i in ids]);strata=defaultdict(list)
    for j,i in enumerate(ids):strata[(key[i]['job_class'],key[i]['freq_band'])].append(j)
    rng=np.random.default_rng(v.SEED+5);res={}
    for phase,files,field in [('blind',['results_A.csv','results_B.csv'],'outcome'),('replay',['replay_A.csv','replay_B.csv'],'final')]:
        hits=defaultdict(int);eligible=defaultdict(int)
        for file in files:
            for r in v.read('work_data/decoy/'+file):
                if r[field]=='too few':continue
                eligible[r['item']]+=1;hits[r['item']]+=r[field]=='came true'
        h=np.array([hits[i] for i in ids]);n=np.array([eligible[i] for i in ids])
        def stat(mask):return h[mask].sum()/n[mask].sum()-h[~mask].sum()/n[~mask].sum()
        obs=float(stat(real));null=[]
        for _ in range(5000):
            rp=real.copy()
            for ix in strata.values():rp[ix]=rng.permutation(real[ix])
            null.append(float(stat(rp)))
        res[phase]={'real_hits':int(h[real].sum()),'real_eligible':int(n[real].sum()),'decoy_hits':int(h[~real].sum()),'decoy_eligible':int(n[~real].sum()),'real_minus_decoy_pass_rate':obs,'p_real_better_item_stratified':(1+sum(x>=obs-1e-12 for x in null))/5001,'null_mean':float(np.mean(null)),'null_95pct_interval':list(map(float,np.quantile(null,[.025,.975]))),'interpretation':'Reanalysis of existing testers, not a new blind experiment. Item is kept intact across testers; labels permuted within job/frequency cells. Original matching and exchangeability assumptions remain.'}
        v.csvout('decoy_'+phase+'_item_null.csv',[dict(replicate=i,real_minus_decoy=x) for i,x in enumerate(null)])
    v.save('decoy_recount.json',res)
if __name__=='__main__':main()
