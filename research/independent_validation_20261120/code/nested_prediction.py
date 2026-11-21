#!/usr/bin/env python3
"""Nested grouped-CV sensitivity; choose regularization inside training folds."""
import json, math
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
import validate as v
from semantic_sensitivity import EXT

def fit(feats,tr,te,y,C):
    dv=DictVectorizer();X=dv.fit_transform([feats[i] for i in tr]);Xt=dv.transform([feats[i] for i in te]);m=LogisticRegression(C=C,max_iter=1500,solver='lbfgs',tol=1e-7);m.fit(X,y[tr]);assert list(m.classes_)==list(v.CLASSES);return m.predict_proba(Xt)
def main():
    objects=[r for r in v.read('work_data/sem/objects_lipi.csv') if r['is_event_rep']=='True'];y=np.array([r['kind'] if r['kind'] in v.TARGETS else 'other' for r in objects]);groups=np.array([r['full_text'] for r in objects]);v.CLASSES=np.array(sorted(set(v.TARGETS+['other'])));mapping={s:EXT[s][0] if s in EXT else r['semantic_domain'] for s,r in v.LEX.items()};out={};preds={};Cs=[.1,1.,10.]
    for mode in ['context','roles','semantic','identity','identity_semantic']:
        feats=v.features(objects,mode,mapping);pred=np.zeros((len(y),len(v.CLASSES)));chosen=[]
        for fold,(tr,te) in enumerate(GroupKFold(n_splits=5).split(y,y,groups)):
            scores=[]
            for C in Cs:
                ip=np.zeros((len(tr),len(v.CLASSES)))
                for itr,ite in GroupKFold(n_splits=3).split(tr,y[tr],groups[tr]):ip[ite]=fit(feats,tr[itr],tr[ite],y,C)
                scores.append(v.score(y[tr],ip)['log_loss_nats'])
            C=Cs[int(np.argmin(scores))];chosen.append({'fold':fold,'C':C,'inner_log_losses':scores});pred[te]=fit(feats,tr,te,y,C)
        preds[mode]=pred;out[mode]={'score':v.score(y,pred),'selected_C':chosen};print(mode,out[mode]['score'],flush=True)
    # Conditional cluster-bootstrap intervals. This does not make reused semantic discovery blind.
    inds=[np.flatnonzero(groups==g) for g in sorted(set(groups))];rng=np.random.default_rng(v.SEED+88);ya=np.searchsorted(v.CLASSES,y);contrasts={}
    for a,b in [('semantic','identity'),('identity_semantic','identity'),('semantic','roles')]:
        delta=-np.log(np.maximum(preds[a][np.arange(len(y)),ya],1e-15))+np.log(np.maximum(preds[b][np.arange(len(y)),ya],1e-15));tot=np.array([delta[ix].sum() for ix in inds]);n=np.array([len(ix) for ix in inds]);bs=[]
        for _ in range(2000):ix=rng.integers(0,len(inds),len(inds));bs.append(float(tot[ix].sum()/n[ix].sum()))
        contrasts[a+'_minus_'+b]={'delta_nats':float(delta.mean()),'CI95_conditional_group_bootstrap':list(map(float,np.quantile(bs,[.025,.975])))}
    out['paired_comparisons']=contrasts;out['scope']='Exploratory nested regularization sensitivity after the fixed-C result; every C choice uses outer-training data only. Whole formula strings remain grouped. Original semantic discovery used the corpus.';v.save('nested_prediction.json',out)
if __name__=='__main__':
    with threadpool_limits(limits=1):main()
