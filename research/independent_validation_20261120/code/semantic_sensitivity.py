#!/usr/bin/env python3
"""Exploratory sensitivity after the initial result: extend the taxonomy to Key6A.

Assignments use the upstream proposed senses, never the artifact labels. This
extension is a reporting/feature choice, not an independently established meaning.
"""
import json, math
from collections import defaultdict
import numpy as np
from threadpoolctl import threadpool_limits
import validate as v
EXT={
'142':['Textile/Trade','blacksmith/metal craft'], '595':['Tax/Levy','tax-marked bale'],
'350':['Civic/House','settlement/enclosure'], '460':['Textile/Trade','garland'],
'482':['Title/Rank','king/chief'], '480':['Granary/Measure','metal/vessel unit'],
'335':['Granary/Measure','grain-bin unit'], '540':['Vessel/Pot','capacity vessel/drum'],
'630':['Granary/Measure','granary/store-enclosure'], '171':['Granary/Measure','weight standard'],
'632':['Granary/Measure','same proposed value as 630'], '831':['Granary/Measure','paddy grain'],
'165':['Vessel/Pot','cauldron'], '104':['Tax/Levy','collect/levy'],
'495':['Textile/Trade','same proposed value as 503'], '175':['Tax/Levy','same proposed tribute value as 176'],
'555':['Grammar/Civic','same proposed district value as 550'], '491':['Textile/Trade','same proposed value as 495'],
'463':['Textile/Trade','same proposed value as 460'], '637':['Granary/Measure','same proposed value as 630'],
'634':['Granary/Measure','same proposed value as 630'], '635':['Granary/Measure','same proposed value as 630'],
'833':['Granary/Measure','same proposed value as 831']}
def main():
    (v.BASE/'frozen/semantic_extensions_sensitivity.json').write_text(json.dumps({'status':'Exploratory taxonomy extension after initial predictive result; not preregistered','source':'Key6A frozen roots and promotions_wave4.csv','mapping':EXT},ensure_ascii=False,indent=2)+'\n')
    lipi=[r for r in v.read('work_data/sem/objects_lipi.csv') if r['is_event_rep']=='True'];v.CLASSES=np.array(sorted(set(v.TARGETS+['other'])))
    mapping={s:EXT[s][0] if s in EXT else r['semantic_domain'] for s,r in v.LEX.items()}; res={};pfull=None
    for C in [.1,1.,10.]:
        v.DESIGN['C']=C; block={}
        for mode in ['context','roles','semantic','identity','identity_semantic']:
            p,y,fold,group=v.cv_predict(lipi,mode,mapping);block[mode]=v.score(y,p)
            if C==1 and mode=='semantic':pfull=p
        res[str(C)]=block;print('C',C,block,flush=True)
    v.DESIGN['C']=1.;rng=np.random.default_rng(v.SEED+199);strata=defaultdict(list)
    for s,r in v.LEX.items():strata[(r['structure_class'],int(math.log2(max(1,int(r['intact_4163_tokens'])))),r['root_or_gloss'].count('/'),r['root_or_gloss'].count('-'))].append(s)
    null=[]
    for b in range(199):
        rival={}
        for ss in strata.values():
            for s,t in zip(sorted(ss),rng.permutation(sorted(ss))):rival[s]=mapping[t]
        p,_,_,_=v.cv_predict(lipi,'semantic',rival);null.append(v.score(y,p)['log_loss_nats'])
    obs=v.score(y,pfull)['log_loss_nats'];res['matched_rivals_full163']={'n':199,'observed_log_loss':obs,'null_mean':float(np.mean(null)),'null_sd':float(np.std(null,ddof=1)),'p':(1+sum(x<=obs+1e-12 for x in null))/200,'null_95pct_interval':list(map(float,np.quantile(null,[.025,.975])))}
    v.csvout('matched_rival_full163_scores.csv',[dict(replicate=i,log_loss_nats=x) for i,x in enumerate(null)])
    v.save('semantic_sensitivity.json',res)
if __name__=='__main__':
    with threadpool_limits(limits=1):main()
