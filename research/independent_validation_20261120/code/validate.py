#!/usr/bin/env python3
"""Retrospective, language-blind checks of frozen IVC semantic proposals.

No repository analysis code is imported. No proposal is fitted or edited.
Run from any directory: python /path/to/this/validate.py
"""
import csv, hashlib, json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import fisher_exact
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, accuracy_score
from sklearn.model_selection import GroupKFold
from threadpoolctl import threadpool_limits
BASE=Path(__file__).resolve().parents[1]; REPO=BASE.parents[1]; OUT=BASE/'results'
DESIGN=json.loads((BASE/'frozen/design.json').read_text()); SEED=DESIGN['seed']
LEX={r['sign']:r for r in json.loads((BASE/'frozen/proposals.json').read_text())}
SIGNS=DESIGN['selected_signs']; TARGETS=DESIGN['targets']
NUM={s for s,r in LEX.items() if r['semantic_class']=='NUM'}

def read(p):
    with (REPO/p).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))
def save(name, obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def csvout(name, rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n"); w.writeheader(); w.writerows(rows)
def tok(s): return [x.strip().zfill(3) if x.strip().isdigit() else x.strip() for x in s.split('-') if x.strip()]
def allfaces(r): return [tok(x) for x in r['full_text'].split('|')]
def event_signs(r): return set(s for f in allfaces(r) for s in f)
def bh(p):
    p=np.asarray(p); order=np.argsort(p); q=np.empty(len(p)); q[order]=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1]; return np.minimum(1,q)
def coverage(rows, filtered=False):
    fs=[tok(r['signs']) for r in rows]
    if filtered: fs=[[s for s in f if s.isdigit()] for f in fs]
    fs=[f for f in fs if f]; total=sum(map(len,fs)); hit=sum(s in LEX for f in fs for s in f)
    full=[f for f in fs if all(s in LEX for s in f)]
    return dict(faces=len(fs),tokens=total,assigned_tokens=hit,assigned_pct=100*hit/total,fully_assigned=len(full),fully_assigned_pct=100*len(full)/len(fs),fully_assigned_length3plus=sum(len(f)>=3 for f in full))
def effect(a,b,c,d):
    # Haldane-Anscombe log-OR interval is descriptive, not a hierarchical CI.
    vals=np.array([a,b,c,d],dtype=float)+.5; odds=float(vals[0]*vals[3]/(vals[1]*vals[2])); se=math.sqrt(sum(1/vals)); return odds,math.exp(math.log(odds)-1.96*se),math.exp(math.log(odds)+1.96*se)
def known(v): return str(v).strip() not in {'','-','--','- -','0','None','Unknown','nan'}
def assoc(corpora):
    cells=[]
    for cat,objects in corpora.items():
        sets=[event_signs(r) for r in objects]
        for s in SIGNS:
            x=np.array([s in z for z in sets])
            for kind in TARGETS:
                y=np.array([r['kind']==kind for r in objects]); a=int(sum(x&y)); b=int(sum(x&~y)); c=int(sum(~x&y)); d=int(sum(~x&~y)); orr,lo,hi=effect(a,b,c,d)
                cells.append(dict(catalogue=cat,sign=s,target=kind,a=a,b=b,c=c,d=d,odds_ratio_HA=orr,ci95_low=lo,ci95_high=hi,p_enrichment=float(fisher_exact([[a,b],[c,d]],alternative='greater').pvalue)))
    qs=bh([r['p_enrichment'] for r in cells])
    for r,q in zip(cells,qs):r['q_BH_all_540']=float(q)
    csvout('all_sign_artifact_contrasts.csv',cells)
    # Select a target in Lipi only. The second catalogue is a retrospective replication.
    chosen={s:min((r for r in cells if r['catalogue']=='Lipi' and r['sign']==s),key=lambda r:r['p_enrichment'])['target'] for s in SIGNS}
    rng=np.random.default_rng(SEED)
    strat=[]
    for cat,objects in corpora.items():
        X=np.array([[s in event_signs(r) for s in SIGNS] for r in objects],dtype=np.int16)
        kinds=np.array([r['kind'] for r in objects]); sites=defaultdict(list)
        for i,r in enumerate(objects): sites[r['site']].append(i)
        bins=[np.array(v) for _,v in sorted(sites.items())]
        Y=np.array([kinds==chosen[s] for s in SIGNS],dtype=np.int16).T
        obs=(X*Y).sum(axis=0); sums=np.zeros((DESIGN['n_permutations'],len(SIGNS)),dtype=np.int16)
        for b in range(DESIGN['n_permutations']):
            perm=np.arange(len(objects))
            for ix in bins: perm[ix]=rng.permutation(ix)
            sums[b]=(X*Y[perm]).sum(axis=0)
        np.savez_compressed(OUT/('site_permutation_'+cat+'.npz'),null=sums,observed=obs,signs=np.array(SIGNS))
        for j,s in enumerate(SIGNS):
            p=(1+int(sum(sums[:,j]>=obs[j])))/(1+len(sums))
            strat.append(dict(catalogue=cat,sign=s,target=chosen[s],observed=int(obs[j]),null_mean=float(sums[:,j].mean()),null_sd=float(sums[:,j].std(ddof=1)),excess_events=float(obs[j]-sums[:,j].mean()),p_site=p,p_site_bonf540=min(1,p*540)))
    csvout('selected_site_permutations.csv',strat)
    return cells,chosen,strat

def features(objects, mode, mapping=None):
    mapping=mapping or {s:r['semantic_domain'] for s,r in LEX.items()}
    result=[]
    for r in objects:
        fs=allfaces(r); seq=[s for f in fs for s in f]; z={'site='+r['site']:1.,'log_length':math.log1p(len(seq)),'faces='+str(min(len(fs),4)):1.}
        for f in fs:
            for i,s in enumerate(f):
                pos='solo' if len(f)==1 else ('initial' if i==0 else ('final' if i==len(f)-1 else 'middle'))
                if mode in ('roles','identity_roles'):
                    key='role:'+LEX.get(s,{}).get('structure_class','UNKNOWN')+':'+pos;z[key]=z.get(key,0)+1.
                if mode in ('semantic','identity_semantic'):
                    key='semantic:'+mapping.get(s,'UNKNOWN');z[key]=z.get(key,0)+1.
                if mode in ('identity','identity_roles','identity_semantic'):
                    key='sign:'+s;z[key]=z.get(key,0)+1.
        result.append(z)
    return result

def fit_predict(train_feats,test_feats,y):
    vec=DictVectorizer(sort=True); X=vec.fit_transform(train_feats); Xt=vec.transform(test_feats)
    model=LogisticRegression(C=DESIGN['C'],max_iter=1500,solver='lbfgs',tol=1e-7)
    model.fit(X,y); return model.predict_proba(Xt),model.classes_

def score(y,p): return {'log_loss_nats':float(log_loss(y,p,labels=CLASSES)),'accuracy':float(accuracy_score(y,CLASSES[p.argmax(axis=1)]))}
def cv_predict(objects,mode,mapping=None):
    feats=features(objects,mode,mapping); y=np.array([r['kind'] if r['kind'] in TARGETS else 'other' for r in objects]); preds=np.zeros((len(objects),len(CLASSES)))
    groups=np.array([r['full_text'] for r in objects]); folds=np.full(len(objects),-1)
    for fold,(tr,te) in enumerate(GroupKFold(n_splits=DESIGN['folds']).split(np.zeros(len(y)),y,groups)):
        p,c=fit_predict([feats[i] for i in tr],[feats[i] for i in te],y[tr]); assert list(c)==list(CLASSES);preds[te]=p; folds[te]=fold
        assert not (set(groups[tr])&set(groups[te]))
    return preds,y,folds,groups

def prediction(lipi,mah):
    global CLASSES
    CLASSES=np.array(sorted(set(TARGETS+['other'])))
    modes=['context','roles','semantic','identity','identity_roles','identity_semantic']; summary={}; allpred={}
    groups=None
    for mode in modes:
        p,y,folds,groups=cv_predict(lipi,mode);allpred[mode]=p
        trainfeat=features(lipi,mode);testfeat=features(mah,mode); ext,c=fit_predict(trainfeat,testfeat,y); ym=np.array([r['kind'] if r['kind'] in TARGETS else 'other' for r in mah]); assert list(c)==list(CLASSES)
        novel=np.array([r['full_text'] not in set(x['full_text'] for x in lipi) for r in mah])
        summary[mode]={'lipi_grouped_cv':score(y,p),'mah_all_retrospective':score(ym,ext),'mah_novel_full_text':score(ym[novel],ext[novel]),'mah_novel_n':int(sum(novel))}
        print('Prediction',mode,summary[mode]['lipi_grouped_cv'],flush=True)
    # Identity names can be changed by an exact column permutation. Prove that with a fresh refit.
    feats=features(lipi,'identity'); v=DictVectorizer(); X=v.fit_transform(feats); rng=np.random.default_rng(SEED); colperm=rng.permutation(X.shape[1]); rename=np.zeros_like(allpred['identity'])
    for tr,te in GroupKFold(n_splits=5).split(X,y,groups):
        m=LogisticRegression(C=1,max_iter=1500,solver='lbfgs',tol=1e-7);m.fit(X[tr][:,colperm],y[tr]);rename[te]=m.predict_proba(X[te][:,colperm])
    summary['opaque_bijective_renaming']={'max_absolute_probability_difference':float(np.max(np.abs(rename-allpred['identity']))),'score':score(y,rename),'interpretation':'Any unique word labels are a recoding of signs. This is an information-equivalence control, not a false-language experiment.'}
    # Match sign frequency octave, structural class, alternatives and hyphen complexity exactly.
    strata=defaultdict(list)
    for s,r in LEX.items():
        n=int(r['intact_4163_tokens']); root=r['root_or_gloss']; complexity=(root.count('/'),root.count('-'))
        strata[(r['structure_class'],int(math.log2(max(n,1))),complexity)].append(s)
    strata=[sorted(v) for _,v in sorted(strata.items(),key=lambda kv:str(kv[0]))]
    frozenmap={s:r['semantic_domain'] for s,r in LEX.items()}; null=[]; rivals=[]
    for b in range(DESIGN['rival_vocabulary_count']):
        mapping={}; changed=0; transfers={}
        for ss in strata:
            dst=rng.permutation(ss)
            for s,t in zip(ss,dst):mapping[s]=frozenmap[t];transfers[s]=str(t);changed+=s!=t
        p,_,_,_=cv_predict(lipi,'semantic',mapping)
        null.append(score(y,p)['log_loss_nats']);rivals.append({'replicate':b,'moved_signs':changed,'different_semantic_domains':sum(mapping[s]!=frozenmap[s] for s in LEX),'donor_by_sign':transfers})
    obs=summary['semantic']['lipi_grouped_cv']['log_loss_nats']; beat=sum(x<=obs+1e-12 for x in null)
    summary['matched_rival_semantic_compression']={'n':len(null),'observed_log_loss':obs,'null_mean':float(np.mean(null)),'null_sd':float(np.std(null,ddof=1)),'null_95pct_interval':list(map(float,np.quantile(null,[.025,.975]))),'p_one_sided_lower_is_better':(1+beat)/(1+len(null)),'nontrivial_strata':sum(len(s)>1 for s in strata),'movable_signs':sum(len(s) for s in strata if len(s)>1),'mean_moved_signs':float(np.mean([r['moved_signs'] for r in rivals])),'mean_changed_domains':float(np.mean([r['different_semantic_domains'] for r in rivals])),'matching':'Exact structure class, log2 frequency octave, slash count and hyphen count; semantic category counts and complete lexical entries preserved by permutation. Weighted category token mass is not exactly preserved.'}
    csvout('matched_rival_scores.csv',[dict(replicate=i,log_loss_nats=x,moved_signs=rivals[i]['moved_signs'],changed_domains=rivals[i]['different_semantic_domains']) for i,x in enumerate(null)])
    (BASE/'frozen/rival_vocabularies.json').write_text(json.dumps(rivals,ensure_ascii=False,indent=2)+'\n')
    # Paired cluster bootstrap of CV log-loss differences, entire formula groups resampled.
    idx={g:np.flatnonzero(groups==g) for g in sorted(set(groups))};groupidx=list(idx.values()); bootrng=np.random.default_rng(SEED+1); ci={}
    for a,b in [('semantic','context'),('semantic','roles'),('semantic','identity'),('identity_semantic','identity'),('identity_roles','identity')]:
        ya=np.searchsorted(CLASSES,y); delta=-np.log(np.maximum(allpred[a][np.arange(len(y)),ya],1e-15))+np.log(np.maximum(allpred[b][np.arange(len(y)),ya],1e-15)); sums=np.array([delta[ix].sum() for ix in groupidx]); ns=np.array([len(ix) for ix in groupidx]);bs=[]
        for _ in range(2000):ix=bootrng.integers(0,len(ns),len(ns));bs.append(float(sums[ix].sum()/ns[ix].sum()))
        ci[a+'_minus_'+b]={'mean_log_loss_difference_nats':float(delta.mean()),'cluster_bootstrap_95pct_CI':list(map(float,np.quantile(bs,[.025,.975]))),'negative_favors':a,'scope':'Conditional on fitted CV models, not uncertainty over discovery, tuning, or excavation sampling.'}
    summary['paired_comparisons']=ci
    csvout('prediction_by_event.csv',[{'id':r['stone_id'],'site':r['site'],'kind':r['kind'],'full_text':r['full_text'],'fold':int(folds[i]),**{m+'_prob_true':float(allpred[m][i,np.searchsorted(CLASSES,y[i])]) for m in modes}} for i,r in enumerate(lipi)])
    save('predictive_validation.json',summary)
    return summary

# Explicit rival interpretations; none is inferred from the phonetic match.
ALTERNATIVES={
'740':'household/institution marker; genitive or terminal classifier; vessel designation; personal-name element',
'700':'capacity/counting unit; ration class; vessel type; administrative classifier',
'400':'rank or title; closure/classifier; craft mark; name ending (junior is unverified)',
'220':'fish commodity; emblem/name component; star-name; semantic classifier',
'520':'title/classifier; personal-name ending; object type; deity or emblem',
'390':'textile commodity; plant commodity; office/merchant class; name component',
'407':'textile subtype; office/estate class; botanical commodity; distinct tree sign',
'176':'institution/emblem; title; fiscal category; name component',
'845':'tablet-series classifier; commodity class; fiscal category; workshop emblem',
'142':'craft/official designation; person-with-tool icon; proper name; ordinal qualifier',
'595':'marked bundle/container; workshop/series marker; tax-marked bale; commodity subtype',
'060':'linker/postposition; slot marker; title connector; classifier, without a known sound',
'550':'place/institution name; heading; district; compound name element',
'482':'title modifier; institutional identifier; name suffix; chief/king',
'335':'metrological rung; container class; commodity classifier; fixed formula element',
'480':'unit of quantity; container classifier; commodity; ordinal/name component',
'171':'unit or load; transaction class; commodity classifier; name element',
'350':'enclosure/settlement; pastoral commodity; office; place-name',
'923':'elephant emblem; ivory/tusk commodity; tablet-series identifier; proper name',
'850':'metal commodity; eye emblem/name; status marker; craft class',
'615':'land/estate class; textile craft; copper-tablet series; name element',
'705':'measure; container; ship or voyage; office/name classifier',
'861':'heading; weight/share; institution; place-name',
'820':'fraction/unit; heading; cart emblem; institution',
'415':'name modifier; title; branch/office identifier; commodity qualifier',
'900':'lunar/calendar word; emblem/name; quantity operator; heading',
'920':'heading; lunar/calendar variant; institution name; place marker',
'590':'bundle/container; commodity classifier; office or institution; textile bale',
'741':'marked-vessel class; numeral-modified institutional marker; person/name class; single household',
'760':'name element; commodity/plant class; junior rank; kinship/scion',
'368':'heading or grant marker; flag/emblem; office; name element',
'840':'pair/unit; contract or pact; emblem; commodity/name qualifier',
'806':'plant commodity; grain; estate or agricultural class; name element',
'255':'crocodile emblem/name; principal/first; class or office; commodity',
}

def sign_report(rows,corpora,cells,chosen,strat):
    signs=[]
    for s in SIGNS:
        rr=LEX[s]; sub=[r for r in rows if r['intact']=='True' and s in tok(r['signs'])]; occ=[(tok(r['signs']),i) for r in sub for i,t in enumerate(tok(r['signs'])) if t==s];n=len(occ)
        left=Counter(f[i-1] for f,i in occ if i>0);right=Counter(f[i+1] for f,i in occ if i+1<len(f)); final=sum(i==len(f)-1 for f,i in occ); initial=sum(i==0 for f,i in occ); adj=sum((i>0 and f[i-1] in NUM)or(i+1<len(f) and f[i+1] in NUM) for f,i in occ)
        l=next(r for r in cells if r['sign']==s and r['catalogue']=='Lipi' and r['target']==chosen[s]);m=next(r for r in cells if r['sign']==s and r['catalogue']=='Mahadevan' and r['target']==chosen[s]);st=next(r for r in strat if r['sign']==s and r['catalogue']=='Lipi')
        num=rr['semantic_class']=='NUM'; alternatives=ALTERNATIVES.get(s,'quantity or ordinal (if strokes); structural/class marker; proper-name component; related allograph with unverified sound' if num else 'commodity or institution classifier; title/name component; graphic variant; exact proposed sense')
        supporting=f"{final}/{n} final, {initial}/{n} initial; numeral-adjacent {adj}/{n}. Strongest Lipi artifact contrast: {chosen[s]} {l['a']}/{l['a']+l['b']} sign-bearing events vs {l['c']}/{l['c']+l['d']} others, OR {l['odds_ratio_HA']:.2f} (95% {l['ci95_low']:.2f}–{l['ci95_high']:.2f}), BH q={l['q_BH_all_540']:.3g}."
        counter=f"Same target in second transcription: {m['a']}/{m['a']+m['b']} vs {m['c']}/{m['c']+m['d']}, OR={m['odds_ratio_HA']:.2f}, q={m['q_BH_all_540']:.3g}. Site-stratified Lipi p={st['p_site']:.4g}; neither object class nor position identifies a word."
        if s=='740': counter+=' A final classifier or genitive predicts the same final-position observation; household requires an independent household linkage.'
        if s in {'923','255'}:counter+=' Animal/copper-tablet copies must also be collapsed by text family before claiming iconographic identification.'
        if s in {'700','335','480','171','705'}:counter+=' Co-occurrence with strokes can support quantity-related function; it supplies neither a litre value nor pronunciation.'
        signs.append(dict(sign=s,proposed_root=rr['root_or_gloss'],proposed_gloss=rr['short_gloss'],shape=rr['shape'],intact_tokens=n,faces=len(sub),final_tokens=final,initial_tokens=initial,numeral_adjacent_tokens=adj,top_left=json.dumps(left.most_common(4)),top_right=json.dumps(right.most_common(4)),strongest_supporting_observation=supporting,strongest_counterevidence=counter,alternatives=alternatives,confidence='Plausible quantity notation; exact value and sound unvalidated' if num else 'Structural/artifact association measurable; precise meaning and sound unvalidated',provenance='Repository-derived metadata and transcription, not independently authenticated catalogue observations'))
    csvout('sign_evidence_45.csv',signs)
    lines=['# Evidence for 45 signs','', 'Frozen proposal roots are quoted as hypotheses. All supporting measurements here exclude phonetic evidence. Artifact association p-values are exploratory and cannot certify the proposed word. BH correction covers all 540 sign × target × corpus contrasts; site-permutation Bonferroni results are supplied separately.','', '| Sign | Proposed root | Strongest supporting observation | Counterevidence/limit | Explicit alternatives | Assessment |','|---|---|---|---|---|---|']
    for r in signs:lines.append('| '+' | '.join(str(r[k]).replace('|',' / ').replace('\n',' ') for k in ['sign','proposed_root','strongest_supporting_observation','strongest_counterevidence','alternatives','confidence'])+' |')
    (BASE/'reports/sign_evidence.md').write_text('\n'.join(lines)+'\n')
    return signs

def inscriptions(rows,corpora):
    lookup={}
    for cat,objects in corpora.items():
        for r in objects:lookup[(cat,r['stone_id'] if cat=='Lipi' else r['textnum'])]=r
    freq=Counter(r['signs'] for r in rows if r['intact']=='True'); seqsites=defaultdict(set)
    for r in rows:seqsites[r['signs']].add(r['site'])
    excluded={'176-740-400','415-220-520'}
    # Exclude every sequence already selected in dedicated upstream showcase CSVs.
    files=['work_data/key3a/test3a3_anthology_20.csv','work_data/key4b/test4b2_newly_unlocked_inscriptions.csv','work_data/key5a/newly_glossed_inscriptions.csv','work_data/key6a/newly_glossed_wave4.csv']
    for p in files:
        for r in read(p):
            for key in ('signs','sequence','sign_sequence','raw_signs'):
                if key in r and r[key]:excluded.add(r[key])
    candidates=[]
    for r in rows:
        f=tok(r['signs'])
        if r['intact']!='True' or not 3<=len(f)<=9 or r['signs'] in excluded or not all(s in LEX for s in f):continue
        stone=r['id'].split('.')[0];obj=lookup.get((r['catalogue'],stone))
        if not obj: continue
        candidates.append((r,obj))
    candidates.sort(key=lambda pair:(-len(seqsites[pair[0]['signs']]),-freq[pair[0]['signs']],hashlib.sha256((pair[0]['catalogue']+pair[0]['id']).encode()).hexdigest()))
    selected=[]; seen=set(); usedobjects=set(); bysite=Counter(); bycat=Counter()
    # Deterministic diversity pass; then fill to sixty without diversity limits.
    for limited in (True,False):
        for r,o in candidates:
            key=(r['catalogue'],r['id'].split('.')[0])
            if r['signs'] in seen or key in usedobjects:continue
            if limited and (bysite[r['site']]>=15 or bycat[r['catalogue']]>=40):continue
            seen.add(r['signs']);usedobjects.add(key);bysite[r['site']]+=1;bycat[r['catalogue']]+=1
            f=tok(r['signs']);literal=' ; '.join(s+'='+LEX[s]['root_or_gloss'] for s in f);gloss=' ; '.join(s+'='+LEX[s]['short_gloss'] for s in f)
            kinds={LEX[s]['semantic_class'] for s in f};pred=[];rival=[]
            if kinds&{'ACCT','TAX'}:pred.append('independent quantity/transaction context or commodity residue should agree with proposed accounting sense');rival.append('unit or transaction-class identifier predicts the same numeral associations')
            if kinds&{'MARITIME'}:pred.append('predict a maritime-use context after controlling for site and object kind');rival.append('portable merchant/institution marker can travel to the same sites')
            if kinds&{'HOUSE','KIN','GUILD'}:pred.append('repeat on independent objects linked to the same household or institution');rival.append('terminal classifier or name element predicts recurrent formula without household identity')
            if kinds&{'TITLE'}:pred.append('predict independently recorded status/use, conditional on city, text length and workshop');rival.append('seal series or office class can predict size without a specific rank word')
            if not pred:pred.append('specific proposed sense must predict independently labelled usage beyond sign identity and position');rival.append('structural/name classifier accounts for the recorded sequence')
            if f[-1]=='740':grammar='Conditional nominal phrase ending in the proposed house/possessive marker; internal compounds and case relations remain ambiguous.'
            elif LEX[f[-1]]['semantic_class']=='TITLE':grammar='Conditional name/office phrase ending in a proposed title; proper-name boundaries and case relations remain ambiguous.'
            elif any(s in NUM for s in f):grammar='Conditional quantity + entity/account phrase; unit, counted entity and name boundaries remain ambiguous.'
            else:grammar='Conditional concatenation of proposed nominal values; no independently established grammar selects a unique sentence.'
            selected.append(dict(test_id='S%03d'%(len(selected)+1),catalogue=r['catalogue'],catalogue_id=r['id'],reference=r['ref_id'],source_path='work_data/reader_v3/corpus_soundfree_readings.csv',object_record_path='work_data/sem/objects_lipi.csv' if r['catalogue']=='Lipi' else 'work_data/sem/objects_mah_new.csv',object_id=key[1],object_type=o['kind'],site=r['site'],findspot_raw=o.get('area_raw',o.get('locus','')),house_or_level_raw=o.get('bh_raw',o.get('level','')),room_raw=o.get('rg_raw',''),iconography=o.get('seal_animal',o.get('ctab_animal','')),exact_sequence=r['signs'],literal_frozen_roots=literal,literal_proposed_senses=gloss,conditional_grammar=grammar,ambiguity='All readings remain hypotheses; root alternatives are retained verbatim; no case endings or missing words are supplied.',recurring_faces_in_intact_corpus=freq[r['signs']],sites_sharing_sequence='; '.join(sorted(seqsites[r['signs']])),prediction='; '.join(pred),alternative_prediction='; '.join(rival),control_result='Same sequence, recurrence and metadata remain true under opaque bijective labels. No independent semantic ground truth available for a per-inscription success score.',new_prediction_status='Prospective prediction only; recorded context already used in upstream research. Additional to selected showcase CSVs, not untouched training evidence.',validated_translation=False,source_authentication='Catalogue identifiers and sequence verified against committed CSV, not every original photograph/excavation catalogue.'))
            if len(selected)==60:break
        if len(selected)==60:break
    assert len(selected)==60
    csvout('inscription_tests_60.csv',selected)
    save('inscription_selection.json',{'excluded_showcase_sequences':len(excluded),'selection_rule':'Fully assigned intact 3–9 sign faces, exclude dedicated upstream showcase CSVs and two prompt examples, unique sequence and object, recurrence/cross-site priority, capped diversity pass then fill','selected_n':len(selected),'by_site':dict(bysite),'by_catalogue':dict(bycat),'all_have_independent_semantic_truth':False})
    lines=['# Sixty additional frozen-mapping inscription tests','', 'These are real corpus records selected without changing the vocabulary. Additional means outside dedicated showcase CSVs, not unseen by the original researchers. No row is claimed as an independently verified translation. Exact IDs, joins, raw contexts, alternatives and prediction/control results are in `../results/inscription_tests_60.csv`.','']
    for r in selected:
        lines+=['## '+r['test_id']+' — '+r['catalogue']+' '+r['catalogue_id']+' / '+r['reference'],'',r['exact_sequence']+' — '+r['site']+', '+r['object_type']+'. Findspot: '+r['findspot_raw']+'; house/level: '+r['house_or_level_raw']+'.','', '**Frozen roots:** '+r['literal_frozen_roots'],'','**Conditional grammar:** '+r['conditional_grammar'],'','**Prediction:** '+r['prediction'],'','**Rival:** '+r['alternative_prediction'],'','**Result:** '+r['control_result'],'']
    (BASE/'reports/inscription_tests.md').write_text('\n'.join(lines).rstrip()+'\n')

def main():
    OUT.mkdir(exist_ok=True)
    for p,h in DESIGN['input_sha256'].items():assert hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h,p
    allrows=read('work_data/reader_v3/corpus_soundfree_readings.csv'); rows=[r for r in allrows if r['catalogue']=='Lipi' or r['partnered']=='False']
    lipi=[r for r in rows if r['catalogue']=='Lipi' and r['intact']=='True'];mah=[r for r in rows if r['catalogue']!='Lipi' and r['intact']=='True'];assert len(lipi)==3600 and len(mah)==627
    cov={label:{'all_tokens_retained':coverage(rr),'upstream_numeric_filter':coverage(rr,True)} for label,rr in [('lipi_intact',lipi),('mah_unpartnered_intact',mah),('combined_intact',lipi+mah),('all_faces',rows)]}
    false=[]
    for r in mah:
        a=tok(r['signs']); b=[s for s in a if s.isdigit()]
        if b and all(s in LEX for s in b) and not all(s in LEX for s in a):false.append({'catalogue_id':r['id'],'signs':r['signs']})
    cov['falsely_full_faces']=false;save('coverage_latest163.json',cov)
    corpora={'Lipi':[r for r in read('work_data/sem/objects_lipi.csv') if r['is_event_rep']=='True'],'Mahadevan':[r for r in read('work_data/sem/objects_mah_new.csv') if r['is_event_rep']=='True']}
    save('input_inventory.json',{'base_commit':DESIGN['base_commit'],'corpus_rows':len(allrows),'analysis_rows_without_partner_duplicates':len(rows),'events':{c:len(r) for c,r in corpora.items()},'event_kind_counts':{c:dict(Counter(x['kind'] for x in r)) for c,r in corpora.items()},'independent_semantic_truth_fields':[],'python':sys.version,'numpy':np.__version__})
    print('Coverage and inventory complete',flush=True)
    cells,chosen,strat=assoc(corpora);sign_report(rows,corpora,cells,chosen,strat);inscriptions(rows,corpora); print('Sign and inscription tables complete',flush=True)
    with threadpool_limits(limits=1):prediction(corpora['Lipi'],corpora['Mahadevan'])
    print('All validation outputs written',flush=True)
if __name__=='__main__':main()
