"""Word-label associations with recorded material, findspot, layers and depth.

Frozen word labels; known-copy event deduplication; whole-table max-|T| tests.
No archaeological meanings are inferred from a successful association.
"""
import argparse, ast, collections, csv, hashlib, json, math, re, time
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits

BASE=Path(__file__).resolve().parent;REPO=BASE.parents[2]
FAMILIES=['material','city','excavation_area','room_or_building','recorded_layer','depth']
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rs,fields=None):
    rs=list(rs)
    if not rs and not fields:return
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def known(s):return str(s or '').strip().casefold() not in {'','-','--','- -','none','unknown','nan','0'}
def clean(s):return re.sub(r'\s+',' ',str(s)).strip()
def unit_depth(raw):
    m=re.fullmatch(r'\s*(-\d+(?:\.\d+)?)\s*(ft|m|cm)\s*',raw or '',re.I)
    if not m:return None
    return -float(m[1])*{'ft':.3048,'m':1.,'cm':.01}[m[2].lower()]
def metadata_features(metadata):
    first={}
    for r in rows(metadata):first.setdefault(r['id'].split('.')[0],r)
    source=rows(REPO/'work_data/sem/objects_lipi.csv')
    events=[]
    for r in source:
        if r['is_event_rep']!='True':continue
        m=first[r['stone_id']]
        signs=set(re.findall(r'(?<!\d)\d{3}(?!\d)',r['full_text']))
        length=sum(len([s for s in f.split('-') if s]) for f in r['full_text'].split('|'))
        e=dict(event_id=r['event_id'],object_id=r['stone_id'],reference=r['cisi'],city=r['site'],kind=r['kind'],
            material=clean(m['material']).capitalize() if known(m['material']) else '',
            area=clean(m['area-section']) if known(m['area-section']) else '',
            block=clean(m['block-house']) if known(m['block-house']) else '',
            room=clean(m['room-grid']) if known(m['room-grid']) else '',
            period=clean(m['period']) if known(m['period']) else '',
            phase=clean(m['phase']) if known(m['phase']) else '',depth_raw=m['depth'],
            depth_m=unit_depth(m['depth']) if r['site']=='Mohenjo-daro' else None,
            length_bin='1' if length<=1 else '2–3' if length<=3 else '4–6' if length<=6 else '7+',
            full_text=r['full_text'],signs=signs,batch_size=int(r['batch_size']))
        e['excavation_area']=e['city']+' | area '+e['area'] if e['area'] else ''
        if e['room']:
            e['room_or_building']=e['city']+' | area '+(e['area'] or '?')+' | block/house '+(e['block'] or '?')+' | room/grid '+e['room']
        elif e['block']:
            e['room_or_building']=e['city']+' | area '+(e['area'] or '?')+' | block/house '+e['block']
        else:e['room_or_building']=''
        e['location_labels']=[]
        if e['block']:e['location_labels'].append(e['city']+' | area '+(e['area'] or '?')+' | block/house '+e['block'])
        if e['room']:e['location_labels'].append(e['city']+' | area '+(e['area'] or '?')+' | block/house '+(e['block'] or '?')+' | room/grid '+e['room'])
        labels=[k+'='+e[k] for k in ['phase','period'] if e[k]]
        e['recorded_layer']=e['city']+' | '+('; '.join(labels)) if labels else ''
        events.append(e)
    assert len(events)==4476
    return events
def words(events):
    ps=json.loads((BASE.parent/'frozen/proposals.json').read_text())
    tree=ast.parse((REPO/'work_scripts/key6b_readings_key5_atlas.py').read_text())
    meta=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SIGN_META' for t in n.targets)))
    families=collections.defaultdict(list);root_to_family={}
    def root(p):
        s=p['root_or_gloss'];s=re.sub(r'\[(?:BRACKET|ROOF|CAGE)\]','',s)
        s=re.split(r'\s*\[|\s*\(',s)[0];return clean(s)
    for p in ps:
        if p['sign'] in meta:root_to_family.setdefault(root(p),meta[p['sign']][3])
    for p in ps:
        key=meta[p['sign']][3] if p['sign'] in meta else root_to_family.get(root(p),'new:'+root(p))
        families[key].append(p)
    semantics={r['sign']:r for r in rows(BASE.parent/'ivc_language_test/results/semantics_catalogue.csv')}
    result=[]
    for key,pp in sorted(families.items()):
        ss={p['sign'] for p in pp}
        present=np.array([bool(ss&e['signs']) for e in events])
        if present.sum()<10:continue
        original=pp[0]['short_gloss'];label=original
        if len(label)>70:
            c=next((semantics[p['sign']] for p in pp if p['sign'] in semantics),None)
            if c:label=c['proposed_intended_meaning'] if c['kind'] in {'bridge','polysemy'} else c['proposed_picture_or_first_meaning']
            elif '595' in ss:label='bale tax / marked bale'
            elif '175' in ss:label='sit / tribute (alternative readings)'
            else:label=pp[0]['root_or_gloss']
        result.append(dict(word_id=key,proposed_meaning=label,original_frozen_label=original,proposed_root=pp[0]['root_or_gloss'],
            signs='; '.join(sorted(ss)),events=int(present.sum()),numeral=all(p['semantic_class']=='NUM' for p in pp),mask=present))
    return result
def setup(events,family):
    if family=='depth':
        selected=[i for i,e in enumerate(events) if e['depth_m'] is not None and e['area']]
    else:selected=[i for i,e in enumerate(events) if known(e[family])]
    es=[events[i] for i in selected]
    if family=='depth':
        areas=collections.defaultdict(list)
        for i,e in enumerate(es):areas[(e['city'],e['area'])].append(i)
        keep={k for k,ix in areas.items() if len(ix)>=20}
        selected=[i for i in selected if (events[i]['city'],events[i]['area']) in keep];es=[events[i] for i in selected]
        areas=collections.defaultdict(list)
        for i,e in enumerate(es):areas[(e['city'],e['area'])].append(i)
        y=np.zeros((len(es),1))
        for ix in areas.values():y[ix,0]=rankdata([es[i]['depth_m'] for i in ix],method='average')/(len(ix)+1)
        targets=['Deeper within the same Mohenjo-daro excavation area']
    else:
        counts=collections.Counter(v for e in es for v in e['location_labels']) if family=='room_or_building' else collections.Counter(e[family] for e in es)
        minimum=8 if family=='room_or_building' else 20
        targets=sorted(k for k,n in counts.items() if n>=minimum)
        y=np.array([[k in e['location_labels'] if family=='room_or_building' else e[family]==k for k in targets] for e in es],dtype=float)
    bins=collections.defaultdict(list)
    for i,e in enumerate(es):
        if family=='material':key=(e['city'],e['kind'],e['length_bin'])
        elif family=='city':key=(e['kind'],e['material'],e['length_bin'])
        elif family=='excavation_area':key=(e['city'],e['kind'],e['material'],e['length_bin'])
        else:key=(e['city'],e['area'],e['kind'],e['material'],e['length_bin'])
        bins[key].append(i)
    return selected,es,y,targets,[np.array(ix) for _,ix in sorted(bins.items())]
def moments(x,y,bins):
    mu=np.zeros((x.shape[1],y.shape[1]));var=np.zeros_like(mu)
    for ix in bins:
        n=len(ix);a=x[ix].sum(0);q=y[ix].mean(0)
        mu+=a[:,None]*q[None,:]
        if n>1:
            # General weighted-feature variance; reduces to hypergeometric variance
            # for binary sign presence. Works for nominal outcomes and depth ranks.
            sx2=(x[ix]**2).sum(0)-a*a/n
            sy2=((y[ix]-q)**2).sum(0)
            var+=sx2[:,None]*sy2[None,:]/(n-1)
    sd=np.sqrt(np.maximum(var,0));sd[sd<1e-10]=np.inf
    return mu,sd
def run_family(events,ws,family,B,seed,out):
    start=time.monotonic();selected,es,y,targets,bins=setup(events,family)
    if not targets:return [],dict(family=family,events=len(es),targets=0,tests=0)
    x=np.array([w['mask'][selected] for w in ws],dtype=float).T
    # Each exact whole-object formula receives a total weight of one across the
    # corpus. Weights use no material, site, layer or depth label.
    formula_counts=collections.Counter(e['full_text'] for e in events)
    weights=np.array([1/formula_counts[e['full_text']] for e in es])
    wx=x*weights[:,None]
    matrices=[x,wx];sparse_x=[sparse.csr_matrix(a.T) for a in matrices]
    mus=[];sds=[];obs=[];zs=[];maxima=[np.zeros(B),np.zeros(B)];exceed=[np.zeros((len(ws),len(targets)),int) for _ in range(2)]
    for a in matrices:
        mu,sd=moments(a,y,bins);o=a.T@y;z=(o-mu)/sd
        mus.append(mu);sds.append(sd);obs.append(o);zs.append(z)
    variable=(x.sum(0)>=5)&(x.sum(0)<len(es)-1)
    valid=[np.isfinite(sd)&variable[:,None] for sd in sds]
    rng=np.random.default_rng(seed);movable=[ix for ix in bins if len(ix)>1]
    for b in range(B):
        perm=np.arange(len(es))
        for ix in movable:perm[ix]=rng.permutation(ix)
        yp=y[perm]
        for k in range(2):
            z=np.abs((sparse_x[k]@yp-mus[k])/sds[k]);z[~valid[k]]=0
            maxima[k][b]=z.max(initial=0)
            exceed[k]+=(z>=np.abs(zs[k])-1e-12)&valid[k]
    np.savez_compressed(out/(family+'_nulls.npz'),primary_maxima=maxima[0],formula_weighted_maxima=maxima[1])
    records=[];descriptive=[];cov=y.sum(0);nx=x.sum(0)
    for i,w in enumerate(ws):
        for j,target in enumerate(targets):
            if nx[i]>0 and nx[i]<len(es):
                a=float(obs[0][i,j])
                descriptive.append(dict(family=family,word_id=w['word_id'],proposed_meaning=w['proposed_meaning'],proposed_root=w['proposed_root'],signs=w['signs'],numeral=w['numeral'],target=target,eligible_events=len(es),
                    word_events=int(nx[i]),other_events=len(es)-int(nx[i]),target_events=int(cov[j]) if family!='depth' else '',
                    observed_word_target_events=int(a) if family!='depth' else '',
                    other_target_events=int(cov[j]-a) if family!='depth' else '',
                    target_share_word_events=a/nx[i] if family!='depth' else '',
                    target_share_other_events=(cov[j]-a)/(len(es)-nx[i]) if family!='depth' else '',
                    expected_word_target_events=float(mus[0][i,j]) if family!='depth' else '',
                    adjustable=bool(valid[0][i,j]),
                    adjustment_status='Tested with recorded context controls' if valid[0][i,j] else 'No separable within-group contrast, or fewer than five eligible word occurrences'))
            if not valid[0][i,j]:continue
            a=float(obs[0][i,j]);p=(1+int(np.sum(maxima[0]>=abs(zs[0][i,j])-1e-12)))/(B+1)
            wp=(1+int(np.sum(maxima[1]>=abs(zs[1][i,j])-1e-12)))/(B+1) if valid[1][i,j] else 1.
            rec=dict(family=family,word_id=w['word_id'],proposed_meaning=w['proposed_meaning'],proposed_root=w['proposed_root'],signs=w['signs'],numeral=w['numeral'],
                target=target,eligible_events=len(es),word_events=int(nx[i]),target_events=int(cov[j]) if family!='depth' else '',
                observed_word_target_events=int(a) if family!='depth' else '',
                expected_word_target_events=float(mus[0][i,j]) if family!='depth' else '',
                target_share_word_events=a/nx[i] if family!='depth' else '',
                target_share_other_events=(cov[j]-a)/(len(es)-nx[i]) if family!='depth' else '',
                mean_local_depth_rank_word=a/nx[i] if family=='depth' else '',
                mean_local_depth_rank_other=(cov[j]-a)/(len(es)-nx[i]) if family=='depth' else '',
                standardized_effect=float(zs[0][i,j]),direction='enriched / deeper' if zs[0][i,j]>0 else 'depleted / shallower',
                p_conditional=(1+int(exceed[0][i,j]))/(B+1),p_maxT_axis=p,p_FWER_six_axes=min(1.,len(FAMILIES)*p),
                formula_weighted_effect=float(zs[1][i,j]),formula_weighted_p_FWER_six_axes=min(1.,len(FAMILIES)*wp),
                formula_weighted_same_direction=bool(zs[0][i,j]*zs[1][i,j]>0),
                status='Exploratory association of a proposed word/sign group; not semantic validation')
            records.append(rec)
    summary=dict(family=family,events=len(es),targets=len(targets),words=len(ws),tests=len(records),
        conditioning_groups=len(bins),movable_events=sum(len(ix) for ix in movable),
        primary_global_significant=sum(r['p_FWER_six_axes']<.05 for r in records),
        also_formula_weighted_significant=sum(r['p_FWER_six_axes']<.05 and r['formula_weighted_p_FWER_six_axes']<.05 and r['formula_weighted_same_direction'] for r in records),
        permutations=B,seconds=round(time.monotonic()-start,3))
    print(json.dumps(summary),flush=True)
    write(out/(family+'_associations.csv'),records)
    write(out/(family+'_descriptive.csv'),descriptive)
    return records,summary
def write_occurrences(events,findings,out):
    examples=[]
    catalogue=rows(BASE.parent/'translation_catalogue/results/all_inscriptions.csv')
    by_obj=collections.defaultdict(list)
    for r in catalogue:
        if r['catalogue']=='Lipi':by_obj[r['face_id'].split('.')[0]].append(r)
    for ri,r in enumerate(findings):
        ss=set(r['signs'].split('; '))
        selected,_,_,_,_=setup(events,r['family']);eligible={events[i]['event_id'] for i in selected}
        matching=[e for e in events if e['event_id'] in eligible and e['signs']&ss and (r['family']=='depth' and e['depth_m'] is not None or r['family']=='room_or_building' and r['target'] in e['location_labels'] or r['family'] not in {'depth','room_or_building'} and e[r['family']]==r['target'])]
        # Store all matching objects, not a handful of selected showcase seals.
        for e in matching:
            faces=[c for c in by_obj[e['object_id']] if set(c['sign_sequence'].split('-'))&ss]
            for c in faces:examples.append(dict(finding_index=ri,family=r['family'],proposed_meaning=r['proposed_meaning'],word_id=r['word_id'],target=r['target'],object_id=e['object_id'],reference=c['reference'],face_id=c['face_id'],city=c['city'],found_at=c['found_at'],recorded_stratigraphy=c['recorded_stratigraphy'],material=c['material'],existing_proposed_translation=c['existing_proposed_translation'],sign_sequence=c['sign_sequence']))
    write(out/'all_finding_occurrences.csv',examples)
def main(args):
    start=time.monotonic();out=Path(args.output) if args.output else BASE/'results';out.mkdir(parents=True,exist_ok=True)
    events=metadata_features(args.lipi_metadata)
    if args.refresh_occurrences:
        write_occurrences(events,rows(out/'significant_associations.csv'),out);return
    ws=words(events)
    write(out/'word_groups.csv',[{k:v for k,v in w.items() if k!='mask'} for w in ws])
    write(out/'events.csv',[{**{k:v for k,v in e.items() if k!='signs'},'signs':'; '.join(sorted(e['signs']))} for e in events])
    all_results=[];summaries=[]
    for j,family in enumerate(FAMILIES):
        rs,ss=run_family(events,ws,family,args.permutations,202611220+j,out);all_results+=rs;summaries.append(ss)
    write(out/'all_associations.csv',all_results)
    findings=sorted([r for r in all_results if r['p_FWER_six_axes']<.05],key=lambda r:(r['p_FWER_six_axes'],-abs(r['standardized_effect'])))
    write(out/'significant_associations.csv',findings,fields=list(all_results[0]))
    write(out/'summary_by_axis.csv',summaries)
    write_occurrences(events,findings,out)
    summary=dict(event_unit='Existing Lipi physical-object / known-copy-batch representatives; all faces of one object combined.',
        n_events=len(events),n_words=len(ws),total_tests=len(all_results),permutations=args.permutations,
        axes=summaries,total_primary_significant=len(findings),
        both_primary_and_formula_weighted_significant=sum(r['formula_weighted_p_FWER_six_axes']<.05 and r['formula_weighted_same_direction'] for r in findings),
        source_metadata_sha256=hashlib.sha256(Path(args.lipi_metadata).read_bytes()).hexdigest(),
        seconds=round(time.monotonic()-start,3),
        interpretation='Retrospective proposed-word/sign associations; same corpus used in earlier work. No independent semantic labels or translated words established.')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lipi-metadata',required=True);ap.add_argument('--permutations',type=int,default=49999);ap.add_argument('--output');ap.add_argument('--refresh-occurrences',action='store_true');args=ap.parse_args()
    with threadpool_limits(limits=1):main(args)
